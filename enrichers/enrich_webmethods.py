#!/usr/bin/env python3
"""
webMethods IS Deep Enrichment (Phase 2.5 — webMethods source only)

The static analyzer sees service invocations like
  INVOKE GLDFundingEngine.MainFlows:processFundingRequest
as a single connector_action black box.

This enricher reads all flow.xml files from the extracted package, builds
a complete service dependency chain, and calls Claude AI to produce a fully
expanded migration spec — with loops, branches, external calls, mappings,
and error handling all resolved.

Usage:
    python enrichers/enrich_webmethods.py migration-specs/proj.json --source-dir active-development/wm_upload/extracted
    python enrichers/enrich_webmethods.py migration-specs/proj.json --source-dir ... --dry-run

No API key required — rides on Claude Code's own login via claude_agent_sdk,
same mechanism as generate_workato_airo.py and gchat/. See ClaudeAgentSession
below for why ANTHROPIC_API_KEY is actively stripped rather than just unused.
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        TextBlock,
    )
except ImportError:
    print("ERROR: claude_agent_sdk not installed. Run: pip install claude-agent-sdk", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Windows cp1252 default encoding breaks on non-ASCII output (e.g. → arrows,
# or unicode in source-system labels/text this script prints verbatim).
# Reconfigure stdout/stderr to UTF-8 if the current codec can't handle it.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ─── Environment / Claude Agent SDK session ────────────────────────────────────

def _load_dotenv():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class ClaudeAgentSession:
    """
    Reusable one-shot Q&A session over the Claude Agent SDK. Kept connected
    across the whole enrichment call (there's normally just one big prompt
    per run here, unlike enrich_spec.py's per-step loop) rather than
    reconnecting. No filesystem/project context or MCP tools -- the prompt
    is fully self-contained.
    """

    def __init__(self, system_prompt: str, model: str | None = None):
        self._options = ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            system_prompt=system_prompt,
            model=model,
        )
        self._client: ClaudeSDKClient | None = None

    async def connect(self) -> None:
        # If ANTHROPIC_API_KEY is set (e.g. for some other script's benefit),
        # the spawned Claude Code CLI subprocess inherits the full parent
        # environment and will prefer that key over this machine's own OAuth
        # login -- silently switching which account gets billed, and failing
        # outright if that key's account has no credit. Strip it so this
        # always rides on OAuth.
        os.environ.pop("ANTHROPIC_API_KEY", None)
        self._client = ClaudeSDKClient(options=self._options)
        await self._client.connect()

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def ask(self, prompt: str) -> str:
        assert self._client is not None
        await self._client.query(prompt)
        parts: list[str] = []
        async for message in self._client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
        return "".join(parts)


# ─── Flow XML discovery ────────────────────────────────────────────────────────

def find_ns_root(source_dir: Path) -> Path:
    """
    Locate the `ns/` namespace root inside a webMethods IS package directory.
    Handles three common extraction layouts:
      1. extracted/ns/...            (zip root = package root)
      2. extracted/PackageName/ns/.. (zip has a top-level package folder)
      3. extracted/...               (no ns/ present — search from source_dir)
    """
    # Level 0: ns/ directly under source_dir
    direct = source_dir / "ns"
    if direct.is_dir():
        return direct

    # Level 1: ns/ under one subdirectory (e.g. extracted/GLDFundingEngine20080714/ns/)
    for child in sorted(source_dir.iterdir()):
        if child.is_dir() and (child / "ns").is_dir():
            return child / "ns"

    # Fallback: search anywhere — rglob finds all flow.xml regardless
    return source_dir


def collect_flow_xmls(source_dir: Path, max_bytes_each: int = 12_000) -> dict:
    """
    Walk the ns/ namespace tree and return {service_path: xml_content}.
    service_path mirrors the ns/ tree: "Namespace/SubNS/ServiceName".
    """
    search_root = find_ns_root(source_dir)
    print(f"  Scanning for flow.xml files under: {search_root}")

    flows = {}
    for xml_path in sorted(search_root.rglob("flow.xml")):
        try:
            content = xml_path.read_text(encoding="utf-8", errors="ignore")
            if len(content) > max_bytes_each:
                content = content[:max_bytes_each] + "\n<!-- [TRUNCATED] -->"
            rel = xml_path.parent.relative_to(search_root)
            service_key = str(rel).replace("\\", "/")
            flows[service_key] = content
        except Exception:
            pass

    if flows:
        print(f"  Found {len(flows)} flow.xml file(s):")
        for k in sorted(flows.keys()):
            print(f"    {k}")

    return flows


def find_entry_points(flows: dict, package_name: str) -> list:
    """
    Identify entry-point services — services not invoked by any other service
    in this package, or whose path contains the package name.
    """
    all_invoked = set()
    for content in flows.values():
        for m in re.finditer(r'service=["\']([^"\']+)["\']', content):
            svc = m.group(1).replace(":", "/").replace(".", "/")
            all_invoked.add(svc.lower())

    entry = []
    for key in flows:
        normalized = key.lower().replace("\\", "/")
        if normalized not in all_invoked:
            entry.append(key)
        elif package_name.lower() in normalized:
            entry.append(key)

    return list(dict.fromkeys(entry))  # dedupe, preserve order


def resolve_service_chain(service_key: str, flows: dict,
                          visited: set = None, depth: int = 0) -> dict:
    """
    Recursively collect a service and all local services it invokes.
    Returns {service_key: xml_content}.
    """
    if visited is None:
        visited = set()
    if service_key in visited or depth > 6:
        return {}
    visited.add(service_key)

    result = {}
    content = flows.get(service_key)
    if not content:
        return result
    result[service_key] = content

    for m in re.finditer(r'service=["\']([^"\']+)["\']', content):
        svc = m.group(1)
        # Convert package.Namespace:service → Namespace/service path
        normalized = svc.replace(":", "/").replace(".", "/")
        # Find matching key (case-insensitive prefix match)
        for k in flows:
            if k.lower().endswith(normalized.lower()) or k.lower() == normalized.lower():
                result.update(resolve_service_chain(k, flows, visited, depth + 1))

    return result


# ─── Claude prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert integration migration engineer specialising in webMethods IS (Integration Server).
You read webMethods flow.xml files and produce structured migration spec JSON.
Return ONLY valid JSON — no markdown fences, no prose outside the JSON object.
"""

def build_enrichment_prompt(package_name: str, service_chain: dict,
                             current_spec: dict) -> str:
    # Format the XML payloads
    xml_block = ""
    for svc_key, xml in service_chain.items():
        xml_block += f"\n\n### Service: {svc_key}\n```xml\n{xml}\n```"

    current_flows_summary = []
    for intg in current_spec.get("integrations", []):
        current_flows_summary.append({
            "name": intg.get("name"),
            "trigger": intg.get("trigger", {}).get("type"),
            "step_count": len(intg.get("steps", [])),
        })

    return f"""Analyze the following webMethods IS flow.xml files for package "{package_name}".

CURRENT STATIC ANALYSIS (incomplete — service invocations not expanded):
{json.dumps(current_flows_summary, indent=2)}

FLOW XML FILES:
{xml_block}

Produce an enriched `integrations` array for the migration spec. Each integration object must have:
{{
  "name": "descriptive service name",
  "flow_type": "primary",
  "trigger": {{
    "type": "http_listener | soap_listener | scheduled | callable | manual",
    "label": "trigger description",
    "note": "any config notes"
  }},
  "steps": [
    {{
      "sequence": 1,
      "type": "foreach | branch | try_catch | connector_action | transform | set_property | decision | stop",
      "label": "human-readable step label",
      "complexity": "low | medium | high",
      "requires_review": false,
      "details": {{}}   // type-specific: loop_variable, branch_conditions, service_name, mapping_fields, etc.
    }}
  ],
  "error_handling": {{
    "has_error_handler": true,
    "strategy": "catch and log | retry | rethrow"
  }},
  "connections_used": ["ServiceName1", "ServiceName2"],
  "migration_notes": "key implementation notes for the target platform"
}}

Rules:
- LOOP/SEQUENCE with array attribute → type "foreach", include loop_variable and source_array in details
- BRANCH/SWITCH → type "branch", include branch_conditions list in details
- INVOKE of external service (not in this package) → type "connector_action", include service_name and params
- MAP → type "transform", include mapping_fields array
- TRY/CATCH/FINALLY → type "try_catch"
- EXIT failure=true → type "stop"
- Expand ALL nested service invocations — do not leave INVOKE to local services as a black box
- Use the actual service logic to write precise labels and notes

Return a JSON object: {{ "integrations": [ ... ] }}
"""


# ─── Claude call ──────────────────────────────────────────────────────────────

async def call_claude(session: "ClaudeAgentSession", prompt: str) -> dict:
    raw = (await session.ask(prompt)).strip()
    # Strip markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    print(f"  WARNING: Could not parse Claude JSON response — returning raw text", file=sys.stderr)
    return {}


# ─── Main enrichment ──────────────────────────────────────────────────────────

async def enrich(spec_path: str, source_dir: str, dry_run: bool = False,
           model: str | None = None) -> None:

    spec_path = Path(spec_path)
    source_dir = Path(source_dir)

    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    package_name = spec.get("project_name", spec_path.stem)
    print(f"  Package : {package_name}")
    print(f"  Source  : {source_dir}")

    # Discover all flow.xml files
    flows = collect_flow_xmls(source_dir)
    if not flows:
        print(f"  WARNING: No flow.xml files found in {source_dir}", file=sys.stderr)
        return

    print(f"  Found {len(flows)} flow.xml file(s) in package")

    # Find entry points and build service chains
    entries = find_entry_points(flows, package_name)
    if not entries:
        entries = list(flows.keys())[:5]
        print(f"  No clear entry points — using top-level services")
    else:
        print(f"  Entry points: {', '.join(entries[:5])}")

    # Collect the full service chain (entry + all transitively invoked local services)
    service_chain = {}
    for ep in entries:
        service_chain.update(resolve_service_chain(ep, flows))

    # Cap to avoid exceeding context limits
    MAX_CHAIN = 20
    if len(service_chain) > MAX_CHAIN:
        # Prioritise entries and largest files
        prioritised = {k: v for k, v in service_chain.items() if k in entries}
        rest = sorted(
            ((k, v) for k, v in service_chain.items() if k not in entries),
            key=lambda kv: len(kv[1]), reverse=True
        )
        for k, v in rest[:MAX_CHAIN - len(prioritised)]:
            prioritised[k] = v
        service_chain = prioritised
        print(f"  Service chain capped at {len(service_chain)} services")

    total_xml_bytes = sum(len(v) for v in service_chain.values())
    print(f"  Total XML to analyse: {total_xml_bytes // 1024} KB across {len(service_chain)} services")

    if dry_run:
        print("\n[DRY RUN] Would send to Claude:")
        for k in service_chain:
            print(f"  {k}")
        print(f"\n  Model: {model}")
        return

    # Call Claude
    prompt = build_enrichment_prompt(package_name, service_chain, spec)

    print(f"\n  Calling Claude ({model or 'default'}) for deep flow analysis…")
    session = ClaudeAgentSession(SYSTEM_PROMPT, model=model)
    await session.connect()
    try:
        result = await call_claude(session, prompt)
    finally:
        await session.disconnect()

    enriched_integrations = result.get("integrations")
    if not enriched_integrations:
        print("  WARNING: Claude returned no integrations — keeping original spec", file=sys.stderr)
        return

    # Merge back into spec
    original_count = len(spec.get("integrations", []))
    spec["integrations"] = enriched_integrations
    spec["summary"]["total_flows"] = len(enriched_integrations)
    spec["summary"]["primary_flows"] = len([i for i in enriched_integrations
                                            if i.get("flow_type") == "primary"])
    spec["summary"]["gaps_found"] = sum(
        1 for intg in enriched_integrations
        for step in intg.get("steps", [])
        if step.get("requires_review")
    )
    spec["enrichment_metadata"] = {
        "enricher": "enrich_webmethods",
        "model": model,
        "services_analysed": len(service_chain),
        "flows_before": original_count,
        "flows_after": len(enriched_integrations),
    }

    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    print(f"  Enriched: {original_count} -> {len(enriched_integrations)} flows")
    print(f"  Spec updated: {spec_path}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Deep AI enrichment for webMethods IS packages."
    )
    parser.add_argument("spec_path", help="Path to migration-specs/*.json")
    parser.add_argument("--source-dir", required=True,
                        help="Directory of extracted webMethods package")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be sent to Claude without calling the API")
    parser.add_argument("--model", default=None,
                        help="Claude model override (default: whatever Claude Code is configured to use)")
    args = parser.parse_args()

    if not os.path.isfile(args.spec_path):
        print(f"ERROR: Spec file not found: {args.spec_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.source_dir):
        print(f"ERROR: Source dir not found: {args.source_dir}", file=sys.stderr)
        sys.exit(1)

    _load_dotenv()
    print(f"\n[ENRICH] Deep webMethods analysis…")
    asyncio.run(enrich(args.spec_path, args.source_dir, dry_run=args.dry_run, model=args.model))


if __name__ == "__main__":
    main()
