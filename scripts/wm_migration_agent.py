#!/usr/bin/env python3
"""
WebmethodsToBoomi_Migration Agent
=====================================
Phase 1 (this script): Analyze a webMethods IS package and produce:
  - WebMethods/Analysis/<PackageName>_Analysis.md   (detailed component breakdown)
  - WebMethods/MD/PackageAnalysis.md                (Boomi migration reference)

Usage:
  python scripts/wm_migration_agent.py
  python scripts/wm_migration_agent.py --package GLDComplianceAdapterServices
  python scripts/wm_migration_agent.py --package MyPackage --source-dir ./my-wm-exports/
"""

import os
import sys
import argparse
import textwrap
from pathlib import Path

# ── Workspace roots ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE   = SCRIPT_DIR.parent          # iPaaS-Migration root
WM_DIR      = WORKSPACE / "WebMethods"
ANALYSIS_DIR = WM_DIR / "Analysis"
MD_DIR       = WM_DIR / "MD"

# ── Boomi folder target ───────────────────────────────────────────────────────
BOOMI_FOLDER_ID = "Rjo4NjIxNDk3"   # MIG_gld_compliance — update if migrating to new folder

# ── Search paths for the package directory ───────────────────────────────────
SEARCH_ROOTS = [
    WORKSPACE / "iPaas Migration" / "WebMethods" / "GLDProject",
    WORKSPACE / "WebMethods",
    WORKSPACE,
]


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_env():
    """Load .env from workspace root into os.environ (simple parser, no deps)."""
    env_path = WORKSPACE / ".env"
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


def find_package_dir(package_name: str, hint: Path | None = None) -> Path | None:
    """Search common locations for the webMethods package directory."""
    candidates = []
    if hint:
        candidates.append(hint)
        candidates.append(hint / package_name)

    for root in SEARCH_ROOTS:
        candidates.append(root / package_name)
        if root.exists():
            for child in root.iterdir():
                if child.is_dir() and child.name == package_name:
                    candidates.append(child)

    for c in candidates:
        if c.is_dir():
            return c
    return None


def collect_files(package_dir: Path) -> dict[str, str]:
    """
    Recursively collect all readable webMethods source files.
    Returns {relative_path: content_string}.
    Skips binary/large files gracefully.
    """
    WM_EXTENSIONS = {".ndf", ".idf", ".xml", ".v3", ".rel", ".bak", ".properties", ".txt", ".md"}
    MAX_FILE_BYTES = 256 * 1024  # 256 KB per file

    collected = {}
    for fpath in sorted(package_dir.rglob("*")):
        if not fpath.is_file():
            continue
        if fpath.suffix.lower() not in WM_EXTENSIONS:
            continue
        rel = str(fpath.relative_to(package_dir))
        if fpath.stat().st_size > MAX_FILE_BYTES:
            collected[rel] = f"[File too large to include: {fpath.stat().st_size} bytes]"
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            collected[rel] = content
        except Exception as e:
            collected[rel] = f"[Could not read: {e}]"

    return collected


def format_files_block(files: dict[str, str]) -> str:
    """Format collected files as a block for the LLM prompt."""
    parts = []
    for rel, content in files.items():
        parts.append(f"=== FILE: {rel} ===\n{content}")
    return "\n\n".join(parts) if parts else "[No source files found]"


# ─────────────────────────────────────────────────────────────────────────────
# Analysis prompt builders
# ─────────────────────────────────────────────────────────────────────────────

ANALYSIS_SYSTEM_PROMPT = textwrap.dedent("""
    You are a senior integration architect specializing in webMethods Integration Server (IS) migrations
    to Boomi. You understand:
    - webMethods IS package structure: manifest.v3, node.idf (namespace), node.ndf (service / connection)
    - JDBC Adapter service format: stored procedure calls, SELECT queries, pipeline IN/OUT fields
    - Flow service format: flow.xml defining sequence, branching, mapping, and sub-service invocations
    - How webMethods types (String, Long, Object, Record) map to Boomi DatabaseV2 and JSON profile types

    When analyzing package files you produce COMPLETE, DETAILED documentation with:
    - Every service name, its DB operation type, all input parameters with types, all output parameters
    - All connection alias details (JDBC URL, schema, driver class)
    - All flow logic constructs (TRY/CATCH, loops, decisions, MAP steps) with their webMethods type
    - All field-level mappings from pipeline-in to pipeline-out

    Format your output as well-structured Markdown with tables wherever data is tabular.
""").strip()


def build_analysis_prompt(package_name: str, files_block: str) -> str:
    return textwrap.dedent(f"""
        Analyze the following webMethods IS package: **{package_name}**

        ## Your task
        Produce a comprehensive Component Analysis document in Markdown format covering:

        1. **Package Overview** — platform, publisher, build date, adapter type, connection alias, DB host/schema
        2. **Service Inventory** — table of all services: name, DB operation (SP/SELECT/INSERT/UPDATE), SQL object
        3. **Detailed Service Definitions** — for EACH service:
           - Purpose
           - DB action (Stored Procedure / SELECT / etc.) and SQL object name
           - Pipeline In table: field name, Java type, DB type, notes
           - Pipeline Out table: field name, Java type, notes
           - Any transformations or business rules
        4. **Flow Services** (if present) — describe the orchestration logic, sequence, branching, mapping steps
        5. **Connections** — adapter alias, JDBC URL, driver, schema, credentials (redact passwords)
        6. **Data Documents / IS Document Types** — if any IData schemas are defined
        7. **Migration Notes** — any gaps, ambiguities, or items needing DBA/architect clarification

        ## Source files

        {files_block}
    """).strip()


def build_package_analysis_prompt(package_name: str, component_analysis: str) -> str:
    return textwrap.dedent(f"""
        You are building a Boomi migration reference document for the webMethods package: **{package_name}**

        Using the Component Analysis below, produce a **PackageAnalysis.md** — the authoritative
        reference for creating every Boomi component. Use the following GLD Compliance example as
        a template for the format and level of detail required.

        ## Output format (follow this structure exactly)
        ```
        # PackageAnalysis — <PackageName> → Boomi Migration Reference

        ## 1. Source Package Summary
        ## 2. Boomi Component Plan           (table: #, component name, type, notes)
        ## 3. Boomi Connection Component     (XML snippet + security note)
        ## 4. Boomi Operation Components     (one section per service/operation)
        ## 5. Process Design                 (flow logic ASCII diagram + DDP table)
        ## 6. Map Shape Field Mappings       (if any Map steps found)
        ## 7. Database Table Definitions     (inferred from adapter metadata)
        ## 8. Stored Procedures Summary      (table)
        ## 9. Migration Gaps                 (table: gap, impact, resolution)
        ## 10. Files Referenced
        ```

        ## Rules
        - Be EXHAUSTIVE: include every field, every parameter, every table column found in the source
        - For stored procedures: list all IN and OUT parameters with DB types and webMethods field names
        - For SELECT queries: include the full SQL and output profile as JSON
        - For flow services: include the ASCII flow diagram showing shape types and their purpose
        - Never invent data — if a detail is unknown, mark it `[UNKNOWN — verify with DBA]`
        - Naming convention for Boomi components: MIG_WM_<PKGPREFIX>_<ComponentName>_<Type>

        ## Component Analysis (source material)
        {component_analysis}
    """).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Claude API calls
# ─────────────────────────────────────────────────────────────────────────────

def call_claude(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-6") -> str:
    """Call the Anthropic Messages API and return the text content."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: 'anthropic' package not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check your .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ─────────────────────────────────────────────────────────────────────────────
# Output writers
# ─────────────────────────────────────────────────────────────────────────────

def write_analysis(package_name: str, content: str) -> Path:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    out = ANALYSIS_DIR / f"{package_name}_Analysis.md"
    out.write_text(content, encoding="utf-8")
    return out


def write_package_analysis(content: str) -> Path:
    MD_DIR.mkdir(parents=True, exist_ok=True)
    out = MD_DIR / "PackageAnalysis.md"
    out.write_text(content, encoding="utf-8")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Main agent entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def main():
    load_env()

    parser = argparse.ArgumentParser(
        description="WebmethodsToBoomi_Migration Agent — Phase 1: Package Analysis"
    )
    parser.add_argument("--package",    "-p", help="webMethods package name")
    parser.add_argument("--source-dir", "-s", help="Path to the package directory (overrides auto-search)")
    parser.add_argument("--model",            help="Claude model ID", default="claude-sonnet-4-6")
    args = parser.parse_args()

    print("=" * 60)
    print("  WebmethodsToBoomi_Migration Agent  — Phase 1")
    print("=" * 60)

    # ── Step 1: Get package name ─────────────────────────────────
    package_name = args.package
    if not package_name:
        package_name = input("\nEnter the name of the webMethods package to migrate: ").strip()
    if not package_name:
        print("ERROR: Package name is required.")
        sys.exit(1)
    print(f"\nPackage: {package_name}")

    # ── Step 2: Locate source files ──────────────────────────────
    source_dir = Path(args.source_dir) if args.source_dir else find_package_dir(package_name)

    if source_dir and source_dir.exists():
        print(f"Source directory: {source_dir}")
        files = collect_files(source_dir)
        print(f"Found {len(files)} source file(s): {', '.join(files.keys())}")
    else:
        print(f"WARNING: Package directory '{package_name}' not found under known search paths.")
        print("Search paths checked:")
        for root in SEARCH_ROOTS:
            print(f"  {root}")
        manual = input(
            "\nEnter the full path to the package directory, or press Enter to proceed "
            "with analysis from context only: "
        ).strip()
        if manual and Path(manual).is_dir():
            source_dir = Path(manual)
            files = collect_files(source_dir)
            print(f"Found {len(files)} source file(s).")
        else:
            files = {}
            print("Proceeding with analysis from package name and naming conventions only.")

    # ── Step 3: Component Analysis (Phase 1a) ────────────────────
    print(f"\n[1/3] Running component analysis via Claude ({args.model})...")
    files_block = format_files_block(files)
    analysis_prompt = build_analysis_prompt(package_name, files_block)
    component_analysis = call_claude(ANALYSIS_SYSTEM_PROMPT, analysis_prompt, model=args.model)

    analysis_path = write_analysis(package_name, component_analysis)
    print(f"      Written: {analysis_path.relative_to(WORKSPACE)}")

    # ── Step 4: PackageAnalysis.md (Phase 1b) ────────────────────
    print(f"\n[2/3] Synthesizing PackageAnalysis.md via Claude ({args.model})...")
    pkg_analysis_prompt = build_package_analysis_prompt(package_name, component_analysis)
    package_analysis_content = call_claude(ANALYSIS_SYSTEM_PROMPT, pkg_analysis_prompt, model=args.model)

    pkg_analysis_path = write_package_analysis(package_analysis_content)
    print(f"      Written: {pkg_analysis_path.relative_to(WORKSPACE)}")

    # ── Step 5: Summary ──────────────────────────────────────────
    print(f"\n[3/3] Phase 1 complete.\n")
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Package analyzed : {package_name}")
    print(f"  Source files read: {len(files)}")
    print(f"  Analysis doc     : WebMethods/Analysis/{package_name}_Analysis.md")
    print(f"  PackageAnalysis  : WebMethods/MD/PackageAnalysis.md")
    print()
    print("  NEXT STEPS (await user instruction before proceeding):")
    print("  Step 8  — Create Map component from Boomi Map Test Skill Excel")
    print("  Step 9  — Apply Agent Bridge component mapping Excel to process structure")
    print("  Step 10 — Generate Boomi.md reference from PackageAnalysis.md + Excel files")
    print("  Step 13 — Generate and push all Boomi components")
    print()
    print("  Stopping — waiting for next instructions.")
    print("=" * 60)

    # Brief preview of what was found (safe for Windows cp1252 console)
    if package_analysis_content:
        preview_lines = package_analysis_content.split("\n")[:15]
        print("\n--- PackageAnalysis.md preview (first 15 lines) ---")
        for line in preview_lines:
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))
        print("...\n")


if __name__ == "__main__":
    main()
