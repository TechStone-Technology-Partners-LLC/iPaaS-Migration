#!/usr/bin/env python3
"""
Migration Orchestrator -- end-to-end pipeline for any A -> B integration migration.

Real-world usage:
    python migrate.py --from boomi --boomi-folder "MIG_CustomerAPI" --to workato
    python migrate.py --from boomi --boomi-folder "My Integrations" --to workato --project my-proj
    python migrate.py --from mulesoft --source-dir samples/mulesoft/customer-api/ --to workato

Pipeline:
    1. PULL     -- fetch source components (Boomi folder -> local XML, or existing files)
    2. ANALYZE  -- run the right analyzer -> migration-specs/<project>.json
    3. ENRICH   -- AI enrichment pass (deep logic for webMethods; generic for others)
    4. DOCUMENT -- generate migration design document -> migration-specs/<project>_design_document.docx
    5. GENERATE -- run the right generator -> target platform artifacts

No spec file needed as input -- the spec is produced automatically.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Windows cp1252 default encoding breaks on non-ASCII output -- this script
# prints Boomi component/process names verbatim, which can contain anything.
# Reconfigure stdout/stderr to UTF-8 so that content never crashes a print.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ─── Skill path detection ─────────────────────────────────────────────────────

def find_skill_path():
    """
    Locate the boomi-integration skill directory.
    Priority: BOOMI_SKILL_PATH env var > .env file > common install locations.
    """
    # 1. Environment variable
    p = os.environ.get("BOOMI_SKILL_PATH")
    if p and os.path.isdir(p):
        return p

    # 2. .env file
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("BOOMI_SKILL_PATH="):
                    p = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if os.path.isdir(p):
                        return p

    # 3. Common install locations
    candidates = [
        os.path.expanduser("~/.claude/plugins/cache/boomi-companion/bc-integration/*/skills/boomi-integration"),
        os.path.expanduser("~/.claude/plugins/cache/boomi-companion/*/skills/boomi-integration"),
    ]
    for pattern in candidates:
        matches = glob.glob(pattern)
        if matches:
            # Pick the most recent version
            return sorted(matches)[-1]

    return None


# ─── Shell script runner ──────────────────────────────────────────────────────

def run_script(script_path, args, cwd=None):
    """
    Run a bash script and return (stdout, returncode).
    Streams output live and also captures it.
    """
    cmd = ["bash", script_path] + args
    print(f"  $ bash {os.path.basename(script_path)} {' '.join(args)}")
    result = subprocess.run(cmd, cwd=cwd or os.getcwd(), capture_output=False, text=True)
    return result.returncode


def run_python(script_path, args, cwd=None):
    """Run a Python script."""
    cmd = [sys.executable, script_path] + args
    print(f"  $ python {os.path.basename(script_path)} {' '.join(args)}")
    result = subprocess.run(cmd, cwd=cwd or os.getcwd(), text=True)
    return result.returncode


# ─── Boomi pull phase ─────────────────────────────────────────────────────────

def get_latest_inventory(cwd):
    """Find the most recently written component_search_*.json file."""
    pattern = os.path.join(cwd, "active-development", "inventories", "component_search_*.json")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


# Component-type subdirectories analyze_boomi.py indexes under active-development/.
# Kept separate from inventories/ (search-result history, harmless to keep),
# .sync-state/ (push/pull diff state, untouched here), and wm_upload/ (unrelated).
BOOMI_COMPONENT_DIRS = (
    "process", "connector-settings", "connector-action", "transform.map",
    "profile.json", "profile.xml", "profile.flatfile", "profile.db", "profile.edi",
)


def clear_boomi_component_dirs(cwd):
    """
    Remove previously-pulled component files from active-development/ before a
    fresh live pull. Without this, analyze_boomi.py indexes EVERY component
    ever pulled from ANY Boomi folder in ANY prior run -- not just this run's
    folder -- silently mixing unrelated migrations into one spec.
    """
    base = os.path.join(cwd, "active-development")
    cleared = 0
    for name in BOOMI_COMPONENT_DIRS:
        d = os.path.join(base, name)
        if os.path.isdir(d):
            # Clear the directory's contents rather than rmtree-ing the
            # directory itself. On OneDrive-backed folders, the sync agent
            # can hold a handle on a just-emptied directory for a while
            # (longer with more files to index), so the final rmdir can keep
            # failing with WinError 5 well past a short retry window. Content
            # removal never touches that directory's own handle.
            for entry in os.scandir(d):
                for attempt in range(5):
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            shutil.rmtree(entry.path)
                        else:
                            os.remove(entry.path)
                        break
                    except PermissionError:
                        if attempt == 4:
                            raise
                        time.sleep(0.5)
            cleared += 1
    if cleared:
        print(f"  Cleared {cleared} stale component director{'y' if cleared == 1 else 'ies'} "
              f"from a previous pull")


def _run_boomi_search(search_script, filters, cwd):
    """Run boomi-component-search.sh with the given filter args, return its records list."""
    rc = run_script(search_script, filters, cwd=cwd)
    if rc != 0:
        print(f"ERROR: Component search failed (exit {rc})", file=sys.stderr)
        sys.exit(1)
    inventory_file = get_latest_inventory(cwd)
    if not inventory_file:
        print("ERROR: Search completed but no inventory file found.", file=sys.stderr)
        sys.exit(1)
    with open(inventory_file, encoding="utf-8") as f:
        return json.load(f).get("records", [])


def _component_id(rec):
    """
    Extract a component id from a search record. --folder/--name results are
    flat ({"componentId": ...}); --related-to results are wrapper objects
    ({"references": [{"componentId": ...}], "relation": "references"|"referenced-by"})
    -- same search script, two different record shapes.
    """
    rid = rec.get("componentId") or rec.get("id")
    if rid:
        return rid
    for ref in rec.get("references") or []:
        rid = ref.get("componentId")
        if rid:
            return rid
    return None


def pull_boomi_folder(folder_name, skill_path, cwd, process_names=None):
    """
    1. Search the Boomi folder for components.
       - No process_names: every component in the folder (processes + all
         dependency types) -- the original "migrate everything" behavior.
       - process_names given: search by name within the folder for ONLY
         those specific process(es), then pull each match's actual
         dependency closure via --related-to, instead of the whole folder.
         This is what makes "migrate just this one process" actually mean
         that process and what it needs, not everything sitting next to it.
    2. Pull every resulting component to local active-development/.
    Returns a list of pulled component IDs.
    """
    scripts = os.path.join(skill_path, "scripts")
    search_script = os.path.join(scripts, "boomi-component-search.sh")
    pull_script = os.path.join(scripts, "boomi-component-pull.sh")

    if not os.path.isfile(search_script):
        print(f"ERROR: Search script not found at {search_script}", file=sys.stderr)
        sys.exit(1)

    records_by_id = {}

    if process_names:
        print(f"\n[PULL] Searching Boomi folder '{folder_name}' for process(es): "
              f"{', '.join(process_names)}...")
        matched_processes = []
        for name in process_names:
            found = _run_boomi_search(
                search_script, ["--folder", folder_name, "--name", name, "--type", "process"], cwd
            )
            if not found:
                print(f"  WARNING: No process matching '{name}' found in folder '{folder_name}'")
            for rec in found:
                matched_processes.append(rec)
                rid = _component_id(rec)
                if rid:
                    records_by_id[rid] = rec

        if not matched_processes:
            print(f"WARNING: No components found in folder '{folder_name}' matching {process_names}")
            return []

        print(f"  Matched {len(matched_processes)} process(es); fetching dependencies...")
        for proc in matched_processes:
            proc_id = _component_id(proc)
            proc_name = proc.get("name", "unknown")
            if not proc_id:
                continue
            related = _run_boomi_search(search_script, ["--related-to", proc_id], cwd)
            # Only pull what this process DEPENDS ON ("references"), not things
            # that happen to call into it ("referenced-by") -- those aren't
            # needed to analyze/rebuild this process on its own.
            deps = [r for r in related if r.get("relation") == "references"]
            print(f"    {proc_name}: {len(deps)} dependenc{'y' if len(deps) == 1 else 'ies'} "
                  f"({len(related) - len(deps)} referenced-by skipped)")
            for rec in deps:
                rid = _component_id(rec)
                if rid:
                    # --related-to records don't carry name/type -- the pull
                    # step fetches real metadata from Boomi regardless.
                    records_by_id.setdefault(rid, {"componentId": rid, "name": "(dependency)", "type": "unknown"})
    else:
        print(f"\n[PULL] Searching Boomi folder '{folder_name}' for all components...")
        # Pull ALL component types in the folder (processes + their dependencies)
        all_types = "process,connector-settings,connector-action,transform.map,profile.json,profile.xml,profile.flatfile,profile.db,profile.edi"
        found = _run_boomi_search(search_script, ["--folder", folder_name, "--type", all_types], cwd)
        for rec in found:
            rid = _component_id(rec)
            if rid:
                records_by_id[rid] = rec

    records = list(records_by_id.values())
    if not records:
        print(f"WARNING: No components found in folder '{folder_name}'")
        return []

    print(f"  {len(records)} component(s) to pull")
    clear_boomi_component_dirs(cwd)

    # Pull each component
    pulled = []
    for rec in records:
        comp_id = _component_id(rec)
        comp_name = rec.get("name", "unknown")
        comp_type = rec.get("type", "unknown")
        if not comp_id:
            continue
        print(f"  Pulling {comp_type}: {comp_name} ({comp_id})")
        rc = run_script(pull_script, ["--component-id", comp_id], cwd=cwd)
        if rc != 0:
            print(f"    WARNING: Pull failed for {comp_name} -- continuing", file=sys.stderr)
        else:
            pulled.append(comp_id)

    print(f"  Pulled {len(pulled)}/{len(records)} components")
    return pulled


# ─── Analyze phase ────────────────────────────────────────────────────────────

# Each analyzer entry: script path + how to build its CLI args.
# "positional" means source_dir is a positional arg (analyze_boomi, analyze_mulesoft).
# "source-dir" means it uses --source-dir <dir> flag (workato, celigo, webmethods).
ANALYZERS = {
    "boomi":       {"script": "analyzers/analyze_boomi.py",      "arg_style": "positional"},
    "mulesoft":    {"script": "analyzers/analyze_mulesoft.py",   "arg_style": "positional"},
    "workato":     {"script": "analyzers/analyze_workato.py",    "arg_style": "source-dir"},
    "celigo":      {"script": "analyzers/analyze_celigo.py",     "arg_style": "source-dir"},
    "webmethods":  {"script": "analyzers/analyze_webmethods.py", "arg_style": "source-dir"},
}


# Live-pull flag each analyzer accepts as an alternative to --source-dir.
# Credentials for the pull itself come from the environment (WORKATO_API_TOKEN/
# EMAIL, CELIGO_API_TOKEN, WMIO_TENANT_URL/USERNAME/PASSWORD) -- this only tells
# the analyzer *what* to pull, not how to authenticate.
LIVE_PULL_ANALYZER_FLAG = {
    "workato": "--folder",
    "celigo": "--integration",
    "webmethods": "--wmio-project",
}


def run_analyze(source_system, source_dir, project_name, cwd, live_pull_value=None):
    """Run the appropriate analyzer and return the spec file path."""
    entry = ANALYZERS.get(source_system)
    if not entry:
        print(f"ERROR: No analyzer for source system '{source_system}'. "
              f"Available: {', '.join(ANALYZERS)}", file=sys.stderr)
        sys.exit(1)

    analyzer_path = os.path.join(cwd, entry["script"])
    if not os.path.isfile(analyzer_path):
        print(f"ERROR: Analyzer not found: {analyzer_path}", file=sys.stderr)
        sys.exit(1)

    spec_path = os.path.join(cwd, "migration-specs", f"{project_name}.json")

    live_flag = LIVE_PULL_ANALYZER_FLAG.get(source_system)
    if live_pull_value and live_flag:
        # e.g. analyze_workato.py --folder <name-or-id> --project <name> --output <path>
        analyzer_args = [live_flag, live_pull_value, "--project", project_name, "--output", spec_path]
    elif entry["arg_style"] == "positional":
        # analyze_boomi.py <source_dir> --project <name> --output <path>
        analyzer_args = [source_dir, "--project", project_name, "--output", spec_path]
    else:
        # analyze_workato.py --source-dir <dir> --project <name> --output <path>
        analyzer_args = ["--source-dir", source_dir, "--project", project_name, "--output", spec_path]

    print(f"\n[ANALYZE] Running {os.path.basename(analyzer_path)}...")
    rc = run_python(analyzer_path, analyzer_args, cwd=cwd)
    if rc != 0:
        print(f"ERROR: Analyzer failed (exit {rc})", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(spec_path):
        print(f"ERROR: Spec file not created at {spec_path}", file=sys.stderr)
        sys.exit(1)

    print(f"  Spec: {spec_path}")
    return spec_path


# ─── Enrich phase ────────────────────────────────────────────────────────────

def run_enrich(source_system, spec_path, source_dir, cwd, live_pull_value=None):
    """
    AI enrichment pass.
    - webmethods IS package (local flow.xml): deep call-chain analysis via enrich_webmethods.py
    - webmethods.io live pull (no local flow.xml) and all other sources:
      requires_review step enrichment via enrich_spec.py
    """
    is_wmio_live_pull = source_system == "webmethods" and live_pull_value
    if source_system == "webmethods" and not is_wmio_live_pull:
        enricher = os.path.join(cwd, "enrichers", "enrich_webmethods.py")
        if not os.path.isfile(enricher):
            print(f"WARNING: enrich_webmethods.py not found — skipping ENRICH", file=sys.stderr)
            return
        enrich_args = [spec_path, "--source-dir", source_dir]
    else:
        enricher = os.path.join(cwd, "enrichers", "enrich_spec.py")
        if not os.path.isfile(enricher):
            print(f"WARNING: enrich_spec.py not found — skipping ENRICH", file=sys.stderr)
            return
        enrich_args = [spec_path]

    print(f"\n[ENRICH] Running {os.path.basename(enricher)}...")
    rc = run_python(enricher, enrich_args, cwd=cwd)
    if rc != 0:
        print(f"WARNING: Enrichment failed (exit {rc}) -- continuing", file=sys.stderr)


# ─── Document phase ───────────────────────────────────────────────────────────

def run_document(target_system, spec_path, project_name, cwd, md_dir=None):
    """Generate a Word design document from the migration spec."""
    generator_path = os.path.join(cwd, "generators", "generate_word_doc.py")
    if not os.path.isfile(generator_path):
        print(f"WARNING: generate_word_doc.py not found at {generator_path} -- skipping DOCUMENT phase",
              file=sys.stderr)
        return

    out_path = os.path.join(cwd, "migration-specs", f"{project_name}_design_document.docx")
    doc_args = [spec_path, "--output", out_path, "--target", target_system]
    if md_dir and os.path.isdir(md_dir):
        doc_args += ["--md-dir", md_dir]

    print(f"\n[DOCUMENT] Generating design document...")
    rc = run_python(generator_path, doc_args, cwd=cwd)
    if rc != 0:
        print(f"WARNING: Document generation failed (exit {rc}) -- continuing", file=sys.stderr)
    else:
        print(f"  Output: migration-specs/{project_name}_design_document.docx")
    return out_path


# ─── Generate phase ───────────────────────────────────────────────────────────

# Each generator entry: script path + the target-specific flag name for the
# "folder/project/integration" concept, and whether --dry-run is supported.
GENERATORS = {
    "workato":    {"script": "generators/generate_workato.py",    "dest_flag": "--folder"},
    "celigo":     {"script": "generators/generate_celigo.py",     "dest_flag": "--integration"},
    "webmethods": {"script": "generators/generate_webmethods.py", "dest_flag": "--project"},
    "boomi":      {"script": "generators/generate_boomi.py",      "dest_flag": "--project"},
    "mulesoft":   {"script": None},   # Future: generate_mulesoft.py
}


def resolve_or_create_workato_folder(folder_name_or_id: str) -> str | None:
    """
    push_workato_recipe_json.py only sets folder_id on the push payload when
    given a purely numeric string -- a typed folder NAME (e.g. the UI's
    default "MIG_<project>") silently gets dropped, and the recipe lands
    wherever Workato defaults new recipes to instead of the intended folder.
    This mirrors generate_workato_airo.py's resolve_or_create_folder(): look
    up the name via the plain REST API, create it if missing, and return a
    guaranteed-real numeric ID. Returns None on any failure (missing token,
    network error, etc.) -- callers should fall back to pushing without a
    folder_id rather than failing the whole run over this.
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
        print(f"  NOTE: could not resolve/create Workato folder '{folder_name_or_id}' ({e}) "
              f"-- pushing without a folder_id; recipes will land in Workato's default location.",
              file=sys.stderr)
        return None


def run_generate(target_system, spec_path, dest_name, dry_run, cwd, use_airo=False):
    """Run the appropriate generator."""
    if use_airo:
        if target_system != "workato":
            print(f"ERROR: --use-airo only supports --to workato today (got '{target_system}')", file=sys.stderr)
            sys.exit(1)
        generator_path = os.path.join(cwd, "generators", "generate_workato_airo.py")
        if not os.path.isfile(generator_path):
            print(f"ERROR: Generator not found: {generator_path}", file=sys.stderr)
            sys.exit(1)
        gen_args = [spec_path, "--folder", dest_name]
        if dry_run:
            gen_args.append("--dry-run")
        print(f"\n[GENERATE] Building via the live AIRO recipe builder "
              f"(slower than the static generator -- each step is validated against Workato live)...")
        rc = run_python(generator_path, gen_args, cwd=cwd)
        if rc != 0:
            print(f"ERROR: AIRO generator failed (exit {rc})", file=sys.stderr)
            sys.exit(1)
        return

    entry = GENERATORS.get(target_system, {})
    generator = entry.get("script")

    if generator is None:
        available = [k for k, v in GENERATORS.items() if v.get("script")]
        print(f"ERROR: No generator yet for target '{target_system}'. "
              f"Available targets: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    generator_path = os.path.join(cwd, generator)
    if not os.path.isfile(generator_path):
        print(f"ERROR: Generator not found: {generator_path}", file=sys.stderr)
        sys.exit(1)

    dest_flag = entry.get("dest_flag", "--folder")
    gen_args = [spec_path, dest_flag, dest_name]
    if dry_run:
        gen_args.append("--dry-run")

    print(f"\n[GENERATE] Running {os.path.basename(generator_path)}...")
    rc = run_python(generator_path, gen_args, cwd=cwd)
    if rc != 0:
        print(f"ERROR: Generator failed (exit {rc})", file=sys.stderr)
        sys.exit(1)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="End-to-end integration migration: pull from source -> analyze -> generate for target.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported platforms: boomi, mulesoft, workato, celigo, webmethods

Examples:
  # Boomi folder -> Workato (live pull + push)
  python migrate.py --from boomi --boomi-folder "MIG_CustomerAPI" --to workato

  # Boomi folder -> Celigo
  python migrate.py --from boomi --boomi-folder "My Integrations" --to celigo

  # Boomi folder -> webMethods.io
  python migrate.py --from boomi --boomi-folder "My Folder" --to webmethods

  # MuleSoft project -> Workato
  python migrate.py --from mulesoft --source-dir samples/mulesoft/customer-api/ --to workato

  # Celigo exported JSON -> Workato
  python migrate.py --from celigo --source-dir path/to/celigo-exports/ --to workato

  # Workato folder -> Boomi (live pull, needs WORKATO_API_TOKEN/EMAIL in .env)
  python migrate.py --from workato --workato-folder "My Folder" --to boomi

  # Celigo integration -> Workato (live pull, needs CELIGO_API_TOKEN in .env)
  python migrate.py --from celigo --celigo-integration "My Integration" --to workato

  # webMethods.io project -> Boomi (live pull, needs WMIO_TENANT_URL/USERNAME/PASSWORD in .env)
  python migrate.py --from webmethods --wmio-project "My Project" --to boomi

  # webMethods.io export -> Celigo
  python migrate.py --from webmethods --source-dir path/to/wmio-exports/ --to celigo

  # Dry run -- generate without pushing to target
  python migrate.py --from boomi --boomi-folder "My Folder" --to workato --dry-run

  # Skip pull and analyze (use existing spec)
  python migrate.py --from boomi --to workato --project my-proj --skip-pull --skip-analyze

  # Skip document generation (useful for automated CI pipelines)
  python migrate.py --from mulesoft --source-dir exports/ --to workato --skip-document

  # Include Markdown analysis files as appendix in design document
  python migrate.py --from webmethods --source-dir exports/ --to boomi --md-dir WebMethods/MD/

  # Build via the live AIRO recipe builder instead of the static generator --
  # avoids placeholder connector/action steps, at the cost of LLM tokens + time
  python migrate.py --from boomi --boomi-folder "My Folder" --to workato --use-airo
""",
    )
    PLATFORMS = ["boomi", "mulesoft", "workato", "celigo", "webmethods"]
    parser.add_argument("--from", dest="source", required=True,
                        choices=PLATFORMS,
                        help="Source integration platform")
    parser.add_argument("--to", dest="target", required=True,
                        choices=PLATFORMS,
                        help="Target integration platform")

    # Source options -- exactly one way of pointing at the source is allowed.
    # --boomi-folder, --workato-folder, --celigo-integration and --wmio-project
    # each trigger a LIVE pull from that platform's API (credentials from env/.env);
    # --source-dir points at files that are already local (an export, an upload, a
    # cloned project) and skips the pull step entirely.
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--boomi-folder",
                              help="Boomi folder name or ID to pull processes from (for --from boomi)")
    source_group.add_argument("--workato-folder",
                              help="Workato folder name or ID to pull recipes from -- live pull (for --from workato)")
    source_group.add_argument("--celigo-integration",
                              help="Celigo integration name to pull flows from -- live pull (for --from celigo)")
    source_group.add_argument("--wmio-project",
                              help="webMethods.io project name to pull workflows from -- live pull (for --from webmethods)")
    source_group.add_argument("--source-dir",
                              help="Local directory of source files (skips the pull step)")

    parser.add_argument("--boomi-process", default=None,
                        help="Comma-separated process name(s) or LIKE pattern(s) (%% wildcards) to migrate "
                             "from --boomi-folder, instead of every component in the folder. Pulls each "
                             "matched process plus its actual dependency closure (via --related-to), not "
                             "the whole folder. Only meaningful together with --boomi-folder.")
    parser.add_argument("--project", default=None,
                        help="Project name for spec and output file naming (default: folder or dir name)")
    parser.add_argument("--dest-name", default=None,
                        help="Name for the destination folder/project/integration on the target platform "
                             "(default: MIG_<project>)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate artifacts without pushing to the target platform")
    parser.add_argument("--skip-pull", action="store_true",
                        help="Skip the pull step (use already-downloaded active-development/ files)")
    parser.add_argument("--skip-analyze", action="store_true",
                        help="Skip the analyze step (use an existing spec in migration-specs/)")
    parser.add_argument("--skip-enrich", action="store_true",
                        help="Skip the AI enrichment step")
    parser.add_argument("--skip-document", action="store_true",
                        help="Skip the document generation step")
    parser.add_argument("--skip-generate", action="store_true",
                        help="Stop after PULL/ANALYZE/ENRICH/DOCUMENT -- do not run GENERATE. Produces the "
                             "migration spec (and design doc) for review without touching the target platform "
                             "at all. Most useful with --use-airo, which otherwise builds and pushes recipes "
                             "live with no offline preview step; re-run the generator directly on the "
                             "produced spec once you're ready to build.")
    parser.add_argument("--md-dir", default=None,
                        help="Directory of .md analysis files to append as appendix in the design document")
    parser.add_argument("--use-airo", action="store_true",
                        help="Build Workato recipes via the live AIRO MCP recipe builder instead of the "
                             "static JSON generator (--to workato only). Each connector/action is resolved "
                             "and validated live against Workato's real schema instead of guessed -- no "
                             "'Select an app and action' placeholders where a live equivalent exists. Slower "
                             "and uses LLM tokens; auth rides on Claude Code's own OAuth, not WORKATO_API_TOKEN.")
    args = parser.parse_args()

    cwd = os.getcwd()

    # ── Validate source args ───────────────────────────────────────────────
    # Live-pull flag for each source platform that supports one today. MuleSoft
    # has no live pull anywhere in the codebase -- it is local-file-only, period.
    LIVE_PULL_FLAG = {
        "boomi":      args.boomi_folder,
        "workato":    args.workato_folder,
        "celigo":     args.celigo_integration,
        "webmethods": args.wmio_project,
    }
    live_pull_value = LIVE_PULL_FLAG.get(args.source)

    if args.source == "boomi" and not args.boomi_folder and not args.source_dir and not args.skip_pull:
        print("ERROR: --from boomi requires either --boomi-folder or --source-dir", file=sys.stderr)
        sys.exit(1)

    file_based_sources = ("mulesoft", "workato", "celigo", "webmethods")
    if (args.source in file_based_sources and not args.source_dir and not live_pull_value
            and not args.skip_pull and not args.skip_analyze):
        live_flag_hint = {
            "workato": "--workato-folder <name-or-id>",
            "celigo": "--celigo-integration <name>",
            "webmethods": "--wmio-project <name> (webMethods.io only -- IS packages must use --source-dir)",
            "mulesoft": None,
        }.get(args.source)
        msg = f"ERROR: --from {args.source} requires --source-dir <path-to-exported-files>"
        if live_flag_hint:
            msg += f" or {live_flag_hint}"
        print(msg, file=sys.stderr)
        sys.exit(1)

    # ── Determine project name ─────────────────────────────────────────────
    project_name = args.project
    if not project_name:
        # A specific --boomi-process name makes a more useful default than the
        # whole folder name when only migrating one process out of it.
        name_source = args.boomi_process or args.boomi_folder or live_pull_value or args.source_dir
        if name_source:
            project_name = re.sub(r"[^\w-]", "_", Path(str(name_source).rstrip("/\\")).name).strip("_")
        else:
            project_name = "migration_project"
    project_name = project_name.lower().replace(" ", "_")

    dest_name = args.dest_name or f"MIG_{project_name}"

    print(f"Migration Agent")
    print(f"  Source  : {args.source}")
    print(f"  Target  : {args.target}")
    print(f"  Project : {project_name}")
    print(f"  Dest    : {dest_name}")
    print(f"  Dry run : {args.dry_run}")

    # ── PHASE 1: PULL ──────────────────────────────────────────────────────
    source_dir = args.source_dir or os.path.join(cwd, "active-development")

    if args.source == "boomi" and args.boomi_folder and not args.skip_pull:
        skill_path = find_skill_path()
        if not skill_path:
            print(
                "ERROR: Could not find boomi-integration skill. "
                "Set BOOMI_SKILL_PATH in .env to the skill directory path.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"  Skill   : {skill_path}")

        process_names = (
            [n.strip() for n in args.boomi_process.split(",") if n.strip()]
            if args.boomi_process else None
        )
        pulled = pull_boomi_folder(args.boomi_folder, skill_path, cwd, process_names=process_names)
        if not pulled:
            print(
                f"ERROR: Pulled 0 components from Boomi folder '{args.boomi_folder}'"
                + (f" matching process(es) {process_names}" if process_names else "") + ". "
                f"Refusing to fall through to ANALYZE against whatever files already happen "
                f"to be sitting in active-development/ -- that would silently analyze stale "
                f"data from an unrelated prior run instead of failing loudly. Check the folder "
                f"name/ID, confirm it contains components of the searched types, and that the "
                f"authenticated Boomi account can see it.",
                file=sys.stderr,
            )
            sys.exit(1)
        source_dir = os.path.join(cwd, "active-development")

    elif args.skip_pull:
        print("\n[PULL] Skipped (--skip-pull)")

    # ── PHASE 2: ANALYZE ───────────────────────────────────────────────────
    spec_path = os.path.join(cwd, "migration-specs", f"{project_name}.json")

    if not args.skip_analyze:
        spec_path = run_analyze(args.source, source_dir, project_name, cwd, live_pull_value=live_pull_value)
    else:
        if not os.path.isfile(spec_path):
            print(f"ERROR: --skip-analyze set but spec not found at {spec_path}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[ANALYZE] Skipped -- using existing spec: {spec_path}")

    # ── PHASE 3: ENRICH ───────────────────────────────────────────────────
    if not args.skip_enrich:
        run_enrich(args.source, spec_path, source_dir, cwd, live_pull_value=live_pull_value)
    else:
        print("\n[ENRICH] Skipped (--skip-enrich)")

    # ── PHASE 4: DOCUMENT ─────────────────────────────────────────────────
    if not args.skip_document:
        run_document(args.target, spec_path, project_name, cwd, md_dir=args.md_dir)
    else:
        print("\n[DOCUMENT] Skipped (--skip-document)")

    # ── PHASE 5: GENERATE ─────────────────────────────────────────────────
    if args.skip_generate:
        # Stop here, before the target platform is ever touched -- the spec
        # (and design doc) are the approval artifact. This is the real
        # offline-review point for --use-airo in particular: AIRO itself has
        # no staged/dry-run mode (it validates live, against the real recipe,
        # as it builds), so the only place a genuine "build but don't push
        # yet" checkpoint can exist is before GENERATE is ever invoked.
        print(f"\n{'=' * 50}")
        print(f"Spec ready for review: {args.source} -> {args.target} (GENERATE not run)")
        print(f"  Project : {project_name}")
        print(f"  Spec    : migration-specs/{project_name}.json")
        doc_file = os.path.join(cwd, "migration-specs", f"{project_name}_design_document.docx")
        if os.path.isfile(doc_file):
            print(f"  Document: migration-specs/{project_name}_design_document.docx")
        print(f"  When ready, generate for real with e.g.:")
        if args.use_airo:
            print(f"    python generators/generate_workato_airo.py migration-specs/{project_name}.json --folder \"{dest_name}\"")
        else:
            print(f"    python migrate.py --from {args.source} --to {args.target} --skip-analyze --skip-enrich --project {project_name} --dest-name \"{dest_name}\"")
        return

    # --use-airo always wins, for every source: it replaces whichever
    # generator would otherwise run (the static JSON generator, or the
    # webMethods direct-AI path below) with a live AIRO-validated build.
    if args.use_airo:
        run_generate(args.target, spec_path, dest_name, args.dry_run, cwd, use_airo=True)
    # webMethods -> Workato: use direct AI generator (flow.xml -> recipe JSON).
    # Generates one recipe per independent entry-point service in the ns/ tree.
    # Only applies to a local IS package (real flow.xml files on disk) -- a live
    # --wmio-project pull is cloud JSON, not flow.xml, so it goes through the
    # normal spec-driven generator instead.
    elif (args.source == "webmethods" and args.target == "workato"
            and not args.wmio_project and os.path.isdir(source_dir)):
        direct_gen = os.path.join(cwd, "generators", "generate_workato_from_wm.py")
        recipe_dir = os.path.join(cwd, "migration-specs")
        gen_args = [source_dir, "--output-dir", recipe_dir, "--project", project_name,
                    "--spec", spec_path]
        if args.dry_run:
            gen_args.append("--dry-run")
        print(f"\n[GENERATE] webMethods->Workato direct AI generation (one recipe per entry point)...")
        rc = run_python(direct_gen, gen_args, cwd=cwd)
        if rc != 0:
            print(f"WARNING: Direct generator failed (exit {rc})", file=sys.stderr)
            print("  (tip: ensure ANTHROPIC_API_KEY is set in .env)", file=sys.stderr)
            # Do NOT fall back to spec-based — it produces empty recipes.
            # Exit so the UI shows the real error rather than silently succeeding.
            sys.exit(rc)
        elif not args.dry_run:
            # Push each generated recipe JSON file
            push_script = os.path.join(cwd, "generators", "push_workato_recipe_json.py")
            recipe_files = sorted(glob.glob(
                os.path.join(recipe_dir, f"{project_name.lower()}_*_workato_recipe.json")
            ))
            if recipe_files and os.path.isfile(push_script):
                # dest_name is a NAME ("MIG_<project>" by default), but
                # push_workato_recipe_json.py only sets folder_id when given
                # purely numeric digits -- resolve/create the real folder ID
                # up front so all recipes actually land in the intended
                # folder instead of silently falling back to Workato's
                # default location.
                resolved_folder = resolve_or_create_workato_folder(dest_name) or dest_name
                print(f"\n  Pushing {len(recipe_files)} recipe(s) to Workato folder '{dest_name}' (id: {resolved_folder})...")
                for i, rfile in enumerate(recipe_files):
                    # No --name override: use the name Claude generated for the
                    # recipe JSON itself (a descriptive name based on what the
                    # recipe does), not a mechanical MIG_WM_<service> tag.
                    run_python(push_script, [rfile, "--folder", resolved_folder], cwd=cwd)
                    if i < len(recipe_files) - 1:
                        time.sleep(2)  # avoid bursting Workato's API with back-to-back POSTs
            else:
                print(f"\n  Recipe JSON(s) saved to: {recipe_dir}")
                print(f"  Push via: MigrAlte UI -> Push Recipe JSON mode")
    else:
        run_generate(args.target, spec_path, dest_name, args.dry_run, cwd)

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'=' * 50}")
    print(f"Migration complete: {args.source} -> {args.target}")
    print(f"  Project  : {project_name}")
    print(f"  Spec     : migration-specs/{project_name}.json")
    doc_file = os.path.join(cwd, "migration-specs", f"{project_name}_design_document.docx")
    if os.path.isfile(doc_file):
        print(f"  Document : migration-specs/{project_name}_design_document.docx")
    output_spec = spec_path.replace(".json", f"_{args.target}_output.json")
    if os.path.isfile(output_spec):
        print(f"  Output   : {os.path.relpath(output_spec)}")


if __name__ == "__main__":
    main()
