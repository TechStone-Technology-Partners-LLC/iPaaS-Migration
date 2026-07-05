#!/usr/bin/env python3
"""
Direct webMethods IS → Workato recipe generator.

Reads ALL flow.xml files from the ns/ namespace tree of an extracted webMethods
package, identifies each independent entry-point service, and calls Claude once
per entry point to generate a focused, complete Workato recipe JSON.

Why per-entry-point?
  A webMethods package typically contains 2-4 independent callable services
  (SOAP, scheduled, batch). Generating one combined recipe produces a jumble;
  generating one recipe per entry point produces focused, deployable recipes.

Usage:
    python generators/generate_workato_from_wm.py <source_dir> \\
        --output-dir migration-specs/ \\
        [--project <name>] [--dry-run] [--model claude-sonnet-4-6]

Output:
    migration-specs/<project>_<service>_workato_recipe.json  (one per entry point)

Required env: ANTHROPIC_API_KEY
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from enrichers.enrich_webmethods import (
    collect_flow_xmls,
    find_entry_points,
    find_ns_root,
    resolve_service_chain,
    _get_client,
)


# ─── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM = """\
You are a Workato integration engineer building recipes via the Workato REST API.
You receive an enriched migration spec (the blueprint) and webMethods IS flow.xml context.
Return ONLY a valid JSON object — no markdown fences, no prose outside the JSON.
"""

PROMPT = """\
Build a Workato recipe for: "{entry_point}" (package: "{package_name}")

== MIGRATION BLUEPRINT — build your recipe to match this plan exactly ==
{spec_block}

== FLOW XML CONTEXT ({service_count} services — supporting detail only) ==
{xml_block}

== REQUIRED OUTPUT FORMAT ==
Return a JSON object with exactly these 4 top-level keys:
  "name"        — "MIG_WM_{safe_name}"
  "description" — paragraph describing what the recipe does, external systems called, and any gaps
  "code"        — trigger JSON object (see exact format below — NOT a string)
  "config"      — array of connection config entries (see format below — NOT a string)

== EXACT WORKATO STEP FORMATS — COPY THESE PATTERNS PRECISELY ==

CALLABLE RECIPE TRIGGER (use for SOAP/HTTP-callable services):
{{
  "number": 0, "keyword": "trigger", "provider": "workato", "name": "callable_recipe",
  "as": "callable_recipe", "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "dynamicPickListSelection": {{}}, "toggleCfg": {{}},
  "input": {{
    "http_method": "post",
    "request_url_suffix": "/<endpoint-slug>",
    "response_type": "dynamic",
    "input_fields_raw_schema": "[{{\"name\":\"field1\",\"type\":\"string\",\"optional\":false,\"label\":\"Field 1\"}},{{\"name\":\"field2\",\"type\":\"string\",\"optional\":true,\"label\":\"Field 2\"}}]"
  }},
  "block": [ <all recipe steps go here> ]
}}

SCHEDULED TRIGGER (use for batch/cron services):
{{
  "number": 0, "keyword": "trigger", "provider": "clock", "name": "scheduled_event",
  "as": "scheduled_event", "uuid": "550e8400-e29b-41d4-a716-446655440001",
  "dynamicPickListSelection": {{}}, "toggleCfg": {{}},
  "input": {{"interval": 60, "interval_unit": "minutes"}},
  "block": [ <all recipe steps go here> ]
}}

EACH LOOP — keyword is "each" (NEVER "foreach" — "foreach" produces a blank unrenderable step):
{{
  "number": 1, "keyword": "each", "as": "payment_loop", "title": "For each payment",
  "uuid": "550e8400-e29b-41d4-a716-446655440002",
  "input": {{
    "source": "[PILL: callable_recipe.payments_array]"
  }},
  "block": [ <child steps> ]
}}

IF / ELSE — conditions MUST be inside "input" (NEVER at the step's top level):
{{
  "number": 2, "keyword": "if", "title": "Check payment type",
  "uuid": "550e8400-e29b-41d4-a716-446655440003",
  "input": {{
    "type": "compound",
    "operand": "and",
    "conditions": [{{
      "operand": "equals",
      "lhs": "[PILL: payment_loop.type]",
      "rhs": "Check"
    }}]
  }},
  "block": [
    {{ <true-branch step> }},
    {{ "number": 5, "keyword": "else", "uuid": "550e8400-e29b-41d4-a716-446655440004",
       "block": [ <false-branch steps> ] }}
  ]
}}
For empty/present check: operand "is_empty" or "is_not_empty" (no "rhs" field needed).
For nested elseif: put another "if" step as the sole item inside the else block.

HTTP POST ACTION — the ONLY valid way to call external services:
{{
  "number": 3, "keyword": "action", "provider": "http", "name": "post",
  "as": "service_call", "title": "Call ExternalServiceName", "uuid": "550e8400-e29b-41d4-a716-446655440005",
  "dynamicPickListSelection": {{}}, "toggleCfg": {{}},
  "input": {{
    "url": "PLACEHOLDER — obtain from SME: ExternalServiceName",
    "content_type": "application/json",
    "payload": "{{\"field1\": \"[PILL: callable_recipe.field1]\", \"field2\": \"[PILL: payment_loop.amount]\", \"staticField\": \"static_value\"}}"
  }}
}}
CRITICAL: "payload" must be a JSON-serialized STRING (the value starts and ends with a quote
and the internal braces/quotes are escaped). NEVER write payload as a raw JSON object.

RESCUE / ERROR HANDLING — rescue is a STANDALONE SIBLING at the END of the parent block (NOT wrapped in monitor):
[
  {{ <step 1 — normal processing> }},
  {{ <step 2 — normal processing> }},
  {{ "number": 8, "keyword": "rescue", "uuid": "550e8400-e29b-41d4-a716-446655440007",
     "block": [ <error steps here> ] }}
]
The "rescue" step catches any error from its sibling steps above it. It is ALWAYS the last item in the block.
THERE IS NO "monitor" KEYWORD IN WORKATO. Do not wrap steps in monitor. Use only rescue as shown above.

CONFIG — one entry per unique external provider used:
  {{"keyword": "application", "provider": "http", "account_id": null, "skip_validation": true}}

== DATA PILL NOTATION ==
For all data references write placeholder strings like "[PILL: alias.field_name]" where:
  alias      = the "as" value of the step that produces the data
  field_name = the output field name from that step
Examples: "[PILL: callable_recipe.customerName]", "[PILL: payment_loop.amount]", "[PILL: step_response.status]"
The user will wire the actual Workato data pills in the GUI after the recipe is pushed.

== HARD RULES — ANY VIOLATION PRODUCES BLANK/BROKEN STEPS IN WORKATO ==
1. VALID providers for action steps: "http" ONLY. NEVER use "workato" as an action provider.
   There is NO workato/log_message, workato/set_variables, workato/extract_from_pipeline,
   or any other "workato/*" action type. These DO NOT EXIST and render as empty blank steps.
2. Loop keyword: "each" — NEVER "foreach". "foreach" is not a valid Workato keyword.
3. IF conditions: ALWAYS inside input.conditions — NEVER at the step top level.
4. HTTP payload: ALWAYS a JSON-serialized string (in quotes) — NEVER a raw JSON object.
5. Every "action" step MUST have "dynamicPickListSelection": {{}} and "toggleCfg": {{}}.
6. Trigger "as" MUST match provider/name: callable_recipe trigger → as "callable_recipe".
7. DO NOT emit "extended_input_schema" or "extended_output_schema" — rejected by Workato API.
8. For steps with no Workato equivalent (IS-internal debug, pub.flow:* services, etc.):
   Represent as a single HTTP POST with url="PLACEHOLDER — not migrated: <service-name>" and
   a descriptive title. Note the gap in the recipe description. Never invent fake provider/names.
9. Do not add a "comment" field to steps — Workato ignores it and it wastes tokens.
10. CRITICAL — input_fields_raw_schema field types: use ONLY type "string", "integer", or "boolean".
    NEVER use type "object" or type "array" — Workato silently wipes the ENTIRE trigger input
    schema when any field has these types, causing "Select an app and trigger event" to appear.
    If a field holds structured data, declare it as type "string" with a label like
    "(JSON string — caller serializes as JSON)".
11. Every "if" step MUST include an "else" sibling as the LAST item in its block,
    even if the false branch is a single no-op HTTP POST placeholder. An "if" without
    "else" may collapse or fail to render in Workato.
12. CRITICAL — do NOT use "monitor" keyword — it does NOT exist in Workato's recipe format.
13. SCHEDULED TRIGGER RULE — for clock/scheduled_event triggers, action steps that are direct
    children of the trigger block have their inputs silently dropped by Workato's API. ALL action
    steps must be inside a container (each loop, if block). For pre-loop initialization (e.g.
    get datetime, select batch), put them INSIDE the each loop as the first steps, before the
    main processing steps. Never put action steps at the top level of a scheduled recipe.
    "monitor" causes Workato to render the entire block as ONE blank unrecognized gray step,
    making the whole recipe appear blank. Use "rescue" as a standalone sibling step instead
    (see RESCUE / ERROR HANDLING example above).
"""


# ─── Per-entry-point recipe generator ────────────────────────────────────────

def _safe_name(service_key: str) -> str:
    """Convert a service key like 'GLDFundingEngine/MainFlows/processFundingRequest' to a safe filename part."""
    # Take just the last component (service name)
    last = service_key.split("/")[-1]
    return re.sub(r"[^A-Za-z0-9_]", "_", last)


# Max bytes per individual flow.xml snippet sent to Claude.
# 240KB total / 6 files = 40KB each at default; cap at 6KB so the full
# chain stays under ~8,000 input tokens (system + prompt template + XML).
_MAX_XML_BYTES = 6_000


def _trim_xml(xml: str, max_bytes: int = _MAX_XML_BYTES) -> str:
    """Truncate a flow.xml string to fit within the token budget."""
    if len(xml) <= max_bytes:
        return xml
    return xml[:max_bytes] + "\n<!-- [TRUNCATED -- showing first 6KB] -->"


def _build_spec_block(spec_integration: dict) -> str:
    """Format an enriched spec integration as a human-readable blueprint for the prompt."""
    if not spec_integration:
        return "(No enriched spec available — infer structure from flow XML above)"

    lines = []
    lines.append(f"Service name : {spec_integration.get('name', '?')}")
    trigger = spec_integration.get("trigger", {})
    lines.append(f"Trigger type : {trigger.get('type', '?')} — {trigger.get('label', '')}")

    steps = spec_integration.get("steps", [])
    if steps:
        lines.append(f"Steps ({len(steps)} total):")
        for s in steps:
            seq   = s.get("sequence", "?")
            stype = s.get("type", "?")
            label = s.get("label", "")
            det   = s.get("details", {})
            note  = ""
            if stype == "foreach" and det:
                note = f" — loop over {det.get('source_array', '?')}"
            elif stype in ("branch", "decision") and det:
                conds = det.get("branch_conditions", [])
                note  = " — " + " / ".join(str(c) for c in conds[:3]) if conds else ""
            elif stype == "connector_action" and det:
                svc = det.get("service_name", "")
                note = f" — calls {svc}" if svc else ""
            elif stype == "transform" and det:
                fields = det.get("mapping_fields", [])
                note   = f" — {len(fields)} field mappings" if fields else ""
            lines.append(f"  {seq}. [{stype}] {label}{note}")

    err = spec_integration.get("error_handling", {})
    if err.get("has_error_handler"):
        lines.append(f"Error handling: {err.get('strategy', 'catch and log')}")

    notes = spec_integration.get("migration_notes", "")
    if notes:
        lines.append(f"Migration notes: {notes}")

    return "\n".join(lines)


def generate_one(client, entry_point: str, service_chain: dict,
                 package_name: str, model: str,
                 spec_integration: dict = None) -> dict:
    """Call Claude to generate a Workato recipe for one entry-point service.

    Retries up to 3 times on 429 rate-limit errors with exponential backoff.
    spec_integration: matching integration dict from the enriched spec (optional but strongly recommended).
    """
    xml_block = ""
    for svc_key, xml in service_chain.items():
        trimmed = _trim_xml(xml)
        xml_block += f"\n\n### Service: {svc_key}\n```xml\n{trimmed}\n```"

    safe = _safe_name(entry_point).upper()
    spec_block = _build_spec_block(spec_integration)

    prompt = PROMPT.format(
        entry_point=entry_point,
        package_name=package_name,
        service_count=len(service_chain),
        xml_block=xml_block,
        spec_block=spec_block,
        safe_name=f"{package_name.upper()}_{safe}",
    )

    # Estimate token count (rough: 4 chars/token)
    est_tokens = (len(SYSTEM) + len(prompt)) // 4
    print(f"    Estimated input tokens: ~{est_tokens:,}")

    last_exc = None
    for attempt in range(1, 4):
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=8192,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            break
        except Exception as exc:
            last_exc = exc
            err_str = str(exc)
            if "429" in err_str or "rate_limit" in err_str.lower():
                wait = 30 * attempt   # 30s, 60s, 90s
                print(f"    Rate limit hit (attempt {attempt}/3) -- waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
    else:
        raise last_exc

    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$",           "", raw, flags=re.MULTILINE)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise ValueError(f"Claude returned non-JSON: {raw[:300]}")


# ─── Registration / startup service filter ───────────────────────────────────

_SKIP_PATTERNS = re.compile(
    r"(register|unregister|startup|shutdown|init|teardown)",
    re.IGNORECASE,
)

def _is_business_flow(service_key: str) -> bool:
    """Return False for registration/lifecycle helper services."""
    last = service_key.split("/")[-1]
    return not _SKIP_PATTERNS.search(last)


# ─── Main ─────────────────────────────────────────────────────────────────────

def _find_spec_integration(spec: dict, entry_point: str) -> dict:
    """Find the enriched spec integration that best matches an entry-point service key."""
    if not spec:
        return {}
    integrations = spec.get("integrations", [])
    if not integrations:
        return {}

    # Last component of the entry-point path (e.g. "processFundingRequest")
    ep_leaf = entry_point.split("/")[-1].lower()

    # Exact match on name (case-insensitive)
    for intg in integrations:
        if intg.get("name", "").lower() == ep_leaf:
            return intg

    # Partial match — name contains the leaf
    for intg in integrations:
        if ep_leaf in intg.get("name", "").lower():
            return intg

    # Reverse — leaf appears anywhere in name
    for intg in integrations:
        if intg.get("name", "").lower() in ep_leaf:
            return intg

    return {}


def generate(source_dir: str, output_dir: str, project_name: str = "",
             dry_run: bool = False, model: str = "claude-sonnet-4-6",
             spec_path: str = "") -> list[str]:
    """
    Generate one Workato recipe JSON per entry-point service.
    Returns list of saved recipe file paths.
    """
    src = Path(source_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Discover all flow.xml files in the ns/ tree
    flows = collect_flow_xmls(src)
    if not flows:
        print(f"  ERROR: No flow.xml files found. "
              f"Expected them under {src}/ns/ — check zip structure.", file=sys.stderr)
        sys.exit(1)

    pkg_name = project_name or src.name
    print(f"\n  Package : {pkg_name}")
    print(f"  Total services in ns/ tree: {len(flows)}")

    # Identify entry-point services (not invoked by any other service in package)
    all_entries = find_entry_points(flows, pkg_name)
    entries = [e for e in all_entries if _is_business_flow(e)]

    if not entries:
        # Fallback: use all flows that look like main services
        entries = [k for k in flows if _is_business_flow(k)][:5]
        print(f"  No clear entry points -- using top {len(entries)} business services")
    else:
        print(f"\n  Entry-point services ({len(entries)} recipes to generate):")
        for e in entries:
            print(f"    -> {e}")

    skipped = [e for e in all_entries if not _is_business_flow(e)]
    if skipped:
        print(f"\n  Skipped (registration/lifecycle): {', '.join(skipped)}")

    if dry_run:
        print(f"\n[DRY RUN] Would generate {len(entries)} recipe(s) via {model}")
        for ep in entries:
            chain = resolve_service_chain(ep, flows)
            kb = sum(len(v) for v in chain.values()) // 1024
            print(f"  {ep} -- {len(chain)} services in chain ({kb} KB)")
        return []

    # Load enriched spec if provided
    enriched_spec = {}
    if spec_path and os.path.isfile(spec_path):
        try:
            with open(spec_path, encoding="utf-8") as f:
                enriched_spec = json.load(f)
            n_intg = len(enriched_spec.get("integrations", []))
            print(f"  Enriched spec loaded: {spec_path} ({n_intg} integrations)")
        except Exception as e:
            print(f"  WARNING: Could not load spec {spec_path}: {e}", file=sys.stderr)
    else:
        # Auto-discover spec: migration-specs/<project>.json alongside output_dir
        auto_spec = Path(output_dir) / f"{pkg_name.lower()}.json"
        if not auto_spec.exists():
            # Also try migration-specs/<pkg_name>.json relative to source
            auto_spec = src.parent / "migration-specs" / f"{pkg_name.lower()}.json"
        if auto_spec.exists():
            try:
                with open(auto_spec, encoding="utf-8") as f:
                    enriched_spec = json.load(f)
                n_intg = len(enriched_spec.get("integrations", []))
                print(f"  Auto-loaded spec: {auto_spec} ({n_intg} integrations)")
            except Exception:
                pass

    client = _get_client()
    saved_paths = []

    for idx, entry_point in enumerate(entries, 1):
        print(f"\n  [{idx}/{len(entries)}] Generating recipe for: {entry_point}")

        if idx > 1:
            print(f"    (pausing 8s between recipes to respect rate limits...)")
            time.sleep(8)

        # Build the full service chain for this entry point
        chain = resolve_service_chain(entry_point, flows)

        # Cap at 4 services: entry point + 3 most-complex direct invocations.
        # Each flow.xml is trimmed to 6KB, so 4 services = ~24KB = ~6,000 tokens —
        # safely under the 10k input token limit with room for the prompt template.
        MAX_CHAIN = 4
        if len(chain) > MAX_CHAIN:
            prioritised = {k: v for k, v in chain.items() if k == entry_point}
            rest = sorted(
                [(k, v) for k, v in chain.items() if k != entry_point],
                key=lambda kv: len(kv[1]), reverse=True,
            )
            for k, v in rest[: MAX_CHAIN - len(prioritised)]:
                prioritised[k] = v
            chain = prioritised

        kb = sum(len(v) for v in chain.values()) // 1024
        print(f"    Services in chain: {len(chain)}  ({kb} KB of XML)")

        # Find matching spec integration for this entry point
        spec_intg = _find_spec_integration(enriched_spec, entry_point)
        if spec_intg:
            print(f"    Blueprint: spec integration '{spec_intg.get('name', '?')}' matched")
        else:
            print(f"    Blueprint: no spec match — using XML only")

        try:
            recipe = generate_one(client, entry_point, chain, pkg_name, model,
                                  spec_integration=spec_intg)
        except Exception as exc:
            print(f"    ERROR generating recipe: {exc}", file=sys.stderr)
            continue

        # Save recipe JSON
        safe = _safe_name(entry_point).lower()
        recipe_file = out / f"{pkg_name.lower()}_{safe}_workato_recipe.json"
        with open(recipe_file, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)

        step_count = len(recipe.get("code", {}).get("block", []))
        print(f"    Recipe: {recipe.get('name', '-')}")
        print(f"    Steps : {step_count} top-level")
        print(f"    Saved : {recipe_file}")
        saved_paths.append(str(recipe_file))

    print(f"\n  Generated {len(saved_paths)}/{len(entries)} recipe(s)")
    return saved_paths


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Direct webMethods IS -> Workato recipe generator (one recipe per entry-point service)."
    )
    parser.add_argument("source_dir", help="Extracted webMethods package directory")
    parser.add_argument("--output-dir", default="migration-specs",
                        help="Directory to save recipe JSON files (default: migration-specs/)")
    parser.add_argument("--output", default="",
                        help="Single output file path (overrides --output-dir, generates only first recipe)")
    parser.add_argument("--project", default="",
                        help="Package name (defaults to source_dir name)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--spec", default="",
                        help="Path to enriched migration spec JSON (auto-discovered if omitted)")
    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"ERROR: source_dir not found: {args.source_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[GENERATE] Direct webMethods -> Workato recipe generation")

    # If --output is given, use its parent dir and rename the first recipe
    out_dir = Path(args.output).parent if args.output else Path(args.output_dir)

    paths = generate(
        source_dir=args.source_dir,
        output_dir=str(out_dir),
        project_name=args.project,
        dry_run=args.dry_run,
        model=args.model,
        spec_path=args.spec,
    )

    # If caller expected a single --output path, rename the first recipe to it
    if args.output and paths:
        import shutil
        shutil.move(paths[0], args.output)
        print(f"  Renamed first recipe to: {args.output}")


if __name__ == "__main__":
    main()
