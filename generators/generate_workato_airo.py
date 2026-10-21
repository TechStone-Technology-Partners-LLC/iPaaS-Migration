#!/usr/bin/env python3
"""
generate_workato_airo.py -- Build Workato recipes from a migration spec using
the LIVE AIRO MCP recipe builder, instead of assembling raw recipe JSON blind.

generate_workato.py POSTs hand-built JSON to the Workato REST API and has no
way to know what a real Workato connector/action looks like -- it drops in a
"Select an app and action" placeholder for anything it can't map by pattern
alone. This script drives a real Claude Agent SDK session with the
workato-airo-mcp-server wired in instead: the agent looks up actual Workato
connectors and actions live, validates each step's schema as it builds via
AIRO's recipe_builder_* tools, and only leaves a placeholder (with a
descriptive comment) when there's genuinely no live equivalent -- exactly how
`GLD Compliance Check` (recipe 78515291) was hand-built in a Claude Code
session earlier in this project. This closes that gap for every source this
project supports, not just webMethods.

Usage:
    python generate_workato_airo.py migration-specs/myproject.json --folder "My Folder"
    python generate_workato_airo.py migration-specs/myproject.json --folder 33854532 --dry-run

Auth:
- The AIRO MCP connection rides on Claude Code's own stored OAuth (same as
  gchat/session.py) -- no WORKATO_API_TOKEN is used for this path at all.
- The reasoning model itself uses claude_agent_sdk, which authenticates via
  the local Claude Code CLI session, NOT ANTHROPIC_API_KEY -- so this works
  even when the classic enrich_spec.py-style ANTHROPIC_API_KEY is unset.

Budget (override via .env):
    AIRO_GEN_MAX_COST_USD   (default 10.00)
    AIRO_GEN_MAX_TURNS      (default 200)
    AIRO_GEN_TURN_TIMEOUT_S (default 1800)

NOTE on --dry-run: AIRO's recipe_builder_init saves an empty recipe to
Workato the moment it's called -- live schema validation against the real
platform is the entire point, so there is no way to "build without touching
the platform" the way generate_workato.py's --dry-run can.

An earlier version of this script had --dry-run instruct the agent to build
everything but SKIP the final recipe_builder_push, intending to leave an
"unsaved draft to review before pushing." That was wrong and has been
removed: per AIRO's own tool contract, recipe_builder_push is required
before the agent replies at the end of EVERY turn, not a one-time finalize
step -- skipping it doesn't leave a recoverable draft, it just means the
built steps were never flushed anywhere. The agent always pushes now.

The platform's own real "not live yet" mechanism is `target_system` on the
push response: PLATFORM (written straight to the live recipe) or DRAFT (a
chat-owned draft -- the user must click Save in the Workato Recipe Editor to
publish it; no API/chat tool can do that for them). --dry-run no longer
changes agent behavior; it's accepted for backward CLI compatibility and
only affects the printed banner.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

# Windows cp1252 default encoding breaks on non-ASCII output -- and this
# script prints the AIRO agent's own free-form text verbatim, which can
# contain anything (em-dashes, arrows, checkmarks). Reconfigure stdout/stderr
# to UTF-8 so that content never crashes the print instead of just showing.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
    )
except ImportError:
    print("ERROR: claude_agent_sdk not installed. Run: pip install claude-agent-sdk", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
HEARTBEAT_S = 30


def load_env() -> None:
    """Minimal .env loader -- matches the pattern already used across this repo's scripts."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def get_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "")
    try:
        return float(raw) if raw else default
    except ValueError:
        return default


def get_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "")
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def resolve_or_create_folder(folder_name_or_id: str) -> str | None:
    """
    AIRO's MCP tools have no folder-create capability (only folder_list) --
    left to the agent alone, a requested folder that doesn't exist yet
    silently falls back to whatever existing folder looks closest, not a
    new one with the name you asked for. Resolve/create the target folder
    via Workato's plain REST API instead (same mechanism generate_workato.py
    already uses), so the agent gets handed a guaranteed-real folder ID up
    front. Returns the numeric folder ID, or None if this can't be done
    (missing WORKATO_API_TOKEN, insufficient permissions, network error,
    etc.) -- callers should fall back to letting the agent resolve the
    folder itself via its own folder_list tool in that case.
    """
    if folder_name_or_id.strip().isdigit():
        return folder_name_or_id.strip()

    token = os.environ.get("WORKATO_API_TOKEN", "").strip()
    if not token:
        return None

    base_url = os.environ.get("WORKATO_BASE_URL", "https://www.workato.com/api").strip().rstrip("/")
    if not base_url.endswith("/api"):
        base_url += "/api"

    try:
        import requests
    except ImportError:
        return None

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    try:
        r = requests.get(f"{base_url}/folders", headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        folders = data.get("items", data) if isinstance(data, dict) else data
        for folder in folders:
            if folder.get("name") == folder_name_or_id:
                return str(folder["id"])

        r = requests.post(f"{base_url}/folders", headers=headers,
                          json={"name": folder_name_or_id}, timeout=15)
        r.raise_for_status()
        return str(r.json()["id"])
    except Exception as e:
        print(f"  NOTE: could not resolve/create folder '{folder_name_or_id}' via REST API ({e}) "
              f"-- falling back to letting the agent pick an existing folder itself.", file=sys.stderr)
        return None


def build_prompt(spec_path: Path, folder: str, folder_confirmed: bool = False) -> str:
    # recipe_builder_push is NOT a one-time "finalize" step -- per AIRO's own
    # tool contract it's required before replying at the end of every turn.
    # An earlier version of this prompt told the agent to skip it under
    # --dry-run to leave a "reviewable draft" -- that doesn't exist as a
    # concept AIRO supports, and skipping push just meant built steps were
    # never flushed anywhere. Always push; let the platform's own
    # PLATFORM/DRAFT distinction (see STATUS BLOCK below) be the real
    # "is this live yet" signal instead of a homemade one.
    push_instruction = (
        "Build every recipe fully and call recipe_builder_push after each "
        "one (and again after resolving any inconsistencies -- push is "
        "required before you reply, every turn, not just once at the end)."
    )
    folder_instruction = (
        f"Target folder: use folder ID {folder} directly for every "
        f"recipe_builder_init call. This has already been resolved/created "
        f"for you via the Workato REST API before this session started -- "
        f"it is guaranteed to exist. No need to call folder_list yourself."
        if folder_confirmed else
        f'Call folder_list. Target folder: "{folder}". If a folder with '
        f"exactly this name or ID exists, use it. If not, pick the closest "
        f"reasonable match, and clearly say which folder you used and why "
        f"in your final summary -- AIRO has no folder-create tool, only "
        f"selection among existing folders."
    )
    return f"""You are building Workato recipes from an existing, already-analyzed
migration spec -- using the live AIRO recipe-builder MCP tools
(mcp__workato-airo-mcp-server__*), not by hand-assembling recipe JSON.

SPEC
Read the full migration spec at: {spec_path}
It is the canonical, platform-agnostic format this project's analyzers
produce: top-level `summary`, `connections`, `integrations` (a list of
flows, each with a `trigger` and ordered `steps`), `gaps`, and
`migration_notes`. Each entry in `integrations` needs to become one Workato
recipe.

FIRST STEPS
1. Read the spec file.
2. Call docs_get(id="guides:overview") then docs_get(id="guides:recipe-builder")
   and follow that workflow exactly for every recipe you build: discovery,
   connection resolution, trigger setup, step-by-step configuration,
   inconsistency handling, final push. Do not skip the discovery phase --
   use recipe_builder_search_connectors / recipe_builder_list_connector_operations
   to find the REAL Workato connector and action for each spec step, the way
   a person familiar with Workato would. Never guess a connector name.
3. {folder_instruction}

SHAPE SELECTION -- NATIVE FIRST, SCRIPTING LAST, NEVER LOSE LOGIC
For every piece of source logic, pick the Workato building block in this
order, falling to the next tier ONLY when the one above it genuinely can't
express the logic -- never for convenience or to save time:
1. A real connector trigger/action, resolved live (recipe_builder_search_connectors
   / recipe_builder_list_connector_operations). This is almost always the
   right choice for anything that talks to an external system.
2. Native control-flow and data blocks: if/elsif/else, foreach/repeat,
   error_handling, workato_variable (declare_variable/declare_list/
   insert_to_list/update_variables). Use these for branching, looping, and
   accumulating -- don't drop into a script to do what an `if` or `foreach`
   already does natively.
3. An inline Ruby formula (`ruby(...)` inside a single field's value, per
   `patterns:field-value-syntax` / `formulas:ruby-formulas`) for a short,
   single-field expression -- string concatenation, date math, type
   conversion, simple arithmetic, a one-line conditional. This is Workato's
   ONLY native inline-formula syntax (there is no JavaScript equivalent at
   the field level) -- it's a native mechanism, not a fallback to avoid, so
   still prefer it over a dedicated scripting step whenever the logic fits
   in one field.
4. A dedicated scripting step is the LAST resort -- only for source logic
   that's genuinely irreducible to the above (real multi-step custom
   algorithmic code with no native equivalent). Workato has two parallel
   built-in connectors for this, both no-connection-needed: **"JavaScript
   snippets by Workato" (`js_eval`)** and "Ruby snippets by Workato"
   (`workato_custom_code`). Prefer `js_eval` (JavaScript) over
   `workato_custom_code` (Ruby) for this tier -- use the Ruby one only if
   the logic genuinely needs something `js_eval` can't do. (This is
   separate from the inline `ruby()` field formula in tier 3 above, which
   has no JavaScript equivalent and stays as-is regardless of this
   preference.) When you do use either, translate the FULL original logic
   faithfully, not an approximation or a simplified version -- if you can't
   verify the translation preserves every branch/condition from the
   source, say so explicitly in the step's comment rather than silently
   shipping a partial port.
Before moving to the next step, check that whatever you built actually
reproduces the source behavior completely. A native construct that only
covers PART of the logic is not a finished translation -- either extend it
(e.g. add a formula alongside it) or escalate to the next tier. Losing
behavior silently is worse than flagging it as incomplete.

STEP COMMENTS -- KEEP THEM SHORT, NO SOURCE SYSTEM NAME
Every step's `comment` is ONE short line: name the shape/construct it
mirrors from the source and the purpose it serves, nothing else -- but
never name the source platform itself (not "Boomi", "MuleSoft", "Oracle
SOA", etc.). Example: "Mirrors the Combine Documents shape -- merges
collected records into one flat-file body." NOT "Mirrors Boomi's Combine
Documents shape...". Do NOT include source component IDs, full parameter
dumps (processtype=, profileType=, etc.), or multi-sentence explanations --
that level of detail belongs in your final summary, not on the recipe
canvas. For an incomplete step (requires_review/gaps/no live equivalent),
keep the same one-line style and just append a short "NEEDS REVIEW: <why>"
clause, not a paragraph of caveats.

BUILD, ONE RECIPE PER FLOW
For each entry in the spec's `integrations`:
- Name the recipe after what it actually DOES (its business function) -- e.g.
  "GLD Compliance Check", "Sync Funding Requests to Payment Processor". Reuse
  the flow's own name from the spec only if it's already clear and
  descriptive as-is. Do NOT prefix it with "MIG_", the source system name, or
  any other migration-tooling tag.
- Map its trigger to the closest live Workato trigger for that source type
  (an HTTP/webhook-style source -> API Platform or Recipe Function trigger
  per `connectors:api-platform` / `connectors:recipe-function`; a scheduled
  source -> a schedule trigger; a callable/sub-flow -> a Recipe Function;
  etc. -- use judgment from the spec's trigger details, and load the
  matching connector reference doc before configuring it).
- Map each step in order: connector actions to real Workato connector+action
  pairs (resolved live via recipe_builder_list_connector_operations);
  decision/branch steps to if/elsif/else; loops to foreach/repeat; try/catch
  constructs to error_handling; field mappings to datapills validated via
  recipe_builder_get_datapills -- never hand-author a datapill path.
- Where a step is already flagged `requires_review` or listed under `gaps`,
  or where no live Workato equivalent exists at all (this happens -- e.g. a
  connector needing a live authorized connection you don't have, exactly
  like the Oracle connector when the GLD Compliance recipe was built): add
  the connector/action step anyway if possible, leave a short `comment`
  flagging what's missing (see STEP COMMENTS above -- the full explanation
  goes in your final summary, not the comment), and note it there as a
  manual GUI step. Do not silently drop a step because it's hard.
- Use recipe_builder_select_connections for any connector that needs one; if
  the workspace has no connection for it, still configure everything else
  fully and note the missing connection in your summary.
- {push_instruction}

WHILE WORKING
Keep tool calls purposeful -- do not repeat an identical call more than
twice in a row (see the recipe-builder guide's "Avoiding Repetitive Tool
Calls" section). If you get stuck on one field after two real attempts,
record it as a known issue and move on rather than looping.

WHEN ALL FLOWS ARE DONE
Reply with ONE final summary, formatted in Markdown (it's rendered as
Markdown in a UI, not read as plain chat text) -- short, plain everyday
language, no jargon, no step-by-step build walkthroughs, no
architecture/design-decision explanations, no source component IDs or
field-level mapping detail. Use a real Markdown heading per recipe so
multiple recipes are visually separable, not one undifferentiated block of
text. For EVERY recipe you touched, follow exactly this shape:

### <Recipe Name>
<One-sentence plain-English description of what it does.>

- **Link:** <Workato recipe URL> (folder: <folder name>)
- **Status:** PLATFORM or DRAFT -- taken from the `target_system` your LAST
  recipe_builder_push call for that recipe returned. If DRAFT, add a bullet:
  "Click Save in the Workato Recipe Editor to publish this recipe" (there is
  no chat/API action that does this -- the user must click it themselves).
- **To finish setup:** up to 3 short bullets for anything that needs manual
  work in the Workato UI, phrased as the action to take (e.g. "Add your FTP
  login details", "Confirm the destination folder with whoever manages the
  source system") -- not the diagnostic reasoning behind it. Omit this bullet
  entirely if there's nothing left to do.

If something feels important to explain, fold it into one short clause
inside the relevant bullet rather than giving it its own paragraph. This is
the only output the calling script captures, so make it complete and
self-contained -- do not refer back to earlier messages in it -- but keep
total length proportional to the number of recipes, not to how much you did.
"""


async def run(spec_path: Path, folder: str, folder_confirmed: bool = False) -> tuple[str, float, bool]:
    """Drive one AIRO build session to completion. Returns (final_summary_text, cost_usd, is_error)."""
    # If ANTHROPIC_API_KEY is set (e.g. loaded from .env for enrich_spec.py),
    # the spawned Claude Code CLI subprocess inherits the full parent
    # environment and will prefer that key over this machine's own OAuth
    # login -- silently switching which account gets billed, and failing
    # outright if that key's account has no credit. Strip it so the AIRO
    # session always rides on OAuth, as documented above.
    os.environ.pop("ANTHROPIC_API_KEY", None)
    options = ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        permission_mode="bypassPermissions",
        setting_sources=["project"],
        max_turns=get_int("AIRO_GEN_MAX_TURNS", 200),
        # Auth rides on Claude Code's shared OAuth store, same as gchat/session.py
        mcp_servers={
            "workato-airo-mcp-server": {
                "type": "http",
                "url": "https://app.workato.com/airo_mcp",
            }
        },
    )
    turn_timeout_s = get_int("AIRO_GEN_TURN_TIMEOUT_S", 1800)
    max_cost = get_float("AIRO_GEN_MAX_COST_USD", 10.00)

    client = ClaudeSDKClient(options=options)
    await client.connect()

    final_text_parts: list[str] = []
    total_cost = 0.0
    is_error = False
    last_beat = time.monotonic()

    try:
        await client.query(build_prompt(spec_path, folder, folder_confirmed=folder_confirmed))
        async with asyncio.timeout(turn_timeout_s):
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock) and block.text.strip():
                            final_text_parts.append(block.text)
                            print(f"\n[agent] {block.text}\n")
                        elif isinstance(block, ToolUseBlock):
                            hint = ""
                            inp = block.input or {}
                            for key in ("connector", "action", "name", "path", "query"):
                                if key in inp:
                                    hint = str(inp[key])[:80]
                                    break
                            print(f"  -> {block.name} {hint}".rstrip())
                            if time.monotonic() - last_beat >= HEARTBEAT_S:
                                print(f"     ... still building (${total_cost:.2f} spent so far)")
                                last_beat = time.monotonic()
                elif isinstance(message, ResultMessage):
                    total_cost = message.total_cost_usd or total_cost
                    is_error = bool(message.is_error)
                    if total_cost >= max_cost:
                        print(
                            f"WARNING: cost limit reached (${total_cost:.2f} of ${max_cost:.2f}) "
                            f"-- the agent's turn ended; some flows may be incomplete",
                            file=sys.stderr,
                        )
    except TimeoutError:
        print(f"ERROR: AIRO build session timed out after {turn_timeout_s}s", file=sys.stderr)
        is_error = True
        try:
            await client.interrupt()
        except Exception:
            pass
    finally:
        await client.disconnect()

    return "\n\n".join(final_text_parts), total_cost, is_error


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build Workato recipes from a migration spec via the live AIRO MCP recipe builder."
    )
    ap.add_argument("spec_path", help="Path to the migration spec JSON")
    ap.add_argument("--folder", required=True, help="Target Workato folder name or ID")
    ap.add_argument(
        "--dry-run", action="store_true",
        help="No effect on AIRO builds (kept for CLI compatibility with other generators) -- "
             "AIRO always creates recipes live and always pushes. See module docstring.",
    )
    args = ap.parse_args()

    load_env()

    spec_path = Path(args.spec_path).resolve()
    if not spec_path.is_file():
        print(f"ERROR: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    flow_count = len(spec.get("integrations") or spec.get("flows") or [])

    print(f"Building {flow_count} recipe(s) from {spec_path.name} into Workato folder '{args.folder}' via AIRO...")
    print(f"Budget: ${get_float('AIRO_GEN_MAX_COST_USD', 10.00):.2f} max cost, "
          f"{get_int('AIRO_GEN_MAX_TURNS', 200)} max turns, "
          f"{get_int('AIRO_GEN_TURN_TIMEOUT_S', 1800)}s timeout")
    if args.dry_run:
        print("NOTE: --dry-run has no effect on AIRO builds -- it always creates and pushes recipes live. See --help.")

    # AIRO's own tools can't create a folder -- resolve/create it via the
    # plain REST API first so the agent gets a guaranteed-real ID instead of
    # silently falling back to an existing folder if the name doesn't exist.
    resolved_id = resolve_or_create_folder(args.folder)
    if resolved_id:
        print(f"  Folder '{args.folder}' resolved to ID {resolved_id} (created if it didn't already exist)")
        target_folder, folder_confirmed = resolved_id, True
    else:
        print(f"  Could not resolve/create folder via REST API -- the agent will pick an existing "
              f"folder itself if '{args.folder}' doesn't exist (see WORKATO_API_TOKEN in .env to fix this)")
        target_folder, folder_confirmed = args.folder, False

    summary, cost, is_error = asyncio.run(run(spec_path, target_folder, folder_confirmed=folder_confirmed))
    # Strip Markdown bold markers before matching -- more robust than trying
    # to anticipate every place the agent might put the "**" around
    # "Status:" (per build_prompt's required "- **Status:** PLATFORM" shape).
    recipe_statuses = re.findall(r"Status:?\s*(PLATFORM|DRAFT)", summary.replace("*", ""), re.IGNORECASE)
    recipe_statuses = [s.upper() for s in recipe_statuses]
    has_draft = "DRAFT" in recipe_statuses

    output_path = spec_path.parent / f"{spec_path.stem}_workato_airo_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generator": "generate_workato_airo",
                "spec": str(spec_path),
                "folder": args.folder,
                "cost_usd": cost,
                "is_error": is_error,
                "summary": summary,
                # Parsed from the agent's required "Status: PLATFORM|DRAFT"
                # lines (see build_prompt's WHEN ALL FLOWS ARE DONE section) --
                # the platform's own real "is this live" signal, since AIRO
                # always pushes now (see module docstring). A DRAFT recipe
                # needs a manual Save click in the Workato Recipe Editor;
                # nothing in this pipeline can do that for the user.
                "recipe_statuses": recipe_statuses,
                "has_draft": has_draft,
            },
            f,
            indent=2,
        )

    print(f"\n{'=' * 50}")
    print(summary or "(agent produced no final summary text -- check the log above for what happened)")
    print(f"{'=' * 50}")
    print(f"Cost: ${cost:.2f}")
    print(f"Output saved to: {output_path}")
    if has_draft:
        print("NOTE: One or more recipes landed as a DRAFT -- open each recipe in the Workato "
              "Recipe Editor and click Save to publish it. No automated step can do this.")

    if is_error:
        print("ERROR: AIRO build session ended in an error state", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
