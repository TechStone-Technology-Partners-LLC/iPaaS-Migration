#!/usr/bin/env python3
"""
workato-recipe-search.py — List and search Workato recipes.

Usage:
    python workato-recipe-search.py
    python workato-recipe-search.py --name "funding"
    python workato-recipe-search.py --folder-id 31661117
    python workato-recipe-search.py --active
    python workato-recipe-search.py --name "GLD" --folder-id 31661117 --limit 50

Calls GET /api/recipes with the provided query parameters.
Output: table with columns: ID | Active | Folder ID | Last Updated | Name
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Bootstrap workato-common
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("workato_common", os.path.join(_SCRIPTS_DIR, "workato-common.py"))
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
wc = _mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_date(val: str | None) -> str:
    """Trim ISO timestamps to YYYY-MM-DD HH:MM for table display."""
    if not val:
        return ""
    # Format: 2026-06-20T14:33:22.000Z → 2026-06-20 14:33
    try:
        return val[:16].replace("T", " ")
    except Exception:
        return val


def _active_label(recipe: dict) -> str:
    if recipe.get("running") or recipe.get("active"):
        return "yes"
    return "no"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="List and search Workato recipes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--name",      help="Filter by name substring (case-insensitive on server)")
    parser.add_argument("--folder-id", type=int, help="Filter to recipes in this folder ID")
    parser.add_argument("--active",    action="store_true", help="Show only active (running) recipes")
    parser.add_argument("--limit",     type=int, default=25, help="Maximum recipes to return (default: 25)")
    parser.add_argument("--page",      type=int, default=1,  help="Page number for pagination (default: 1)")
    parser.add_argument("--json",      action="store_true",  dest="json_out",
                        help="Output raw JSON instead of table")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- Build query params ---
    params: dict = {}
    if args.name:
        params["search[name]"] = args.name
    if args.folder_id:
        params["search[folder_id]"] = args.folder_id
    if args.active:
        params["search[active]"] = "true"
    params["per_page"] = min(args.limit, 100)
    params["page"]     = args.page

    # --- GET /recipes ---
    print(f"Searching recipes (limit={args.limit}) …")
    body, err = wc.api_get("/recipes", token, params=params)
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    # Workato returns {"result": [...]} or {"items": [...]} depending on version
    items: list = []
    if isinstance(body, dict):
        items = body.get("result", body.get("items", body.get("recipes", [])))
    elif isinstance(body, list):
        items = body

    if not items:
        print()
        print("No recipes found matching the search criteria.")
        print()
        return

    # --- JSON output mode ---
    if args.json_out:
        print(json.dumps(items, indent=2))
        return

    # --- Table output ---
    rows: list[list[str]] = []
    for r in items:
        if not isinstance(r, dict):
            continue
        rows.append([
            str(r.get("id", "")),
            _active_label(r),
            str(r.get("folder_id", "")),
            _format_date(r.get("updated_at")),
            wc.truncate(r.get("name", ""), 55),
        ])

    headers = ["ID", "Active", "Folder ID", "Last Updated", "Name"]

    print()
    wc.print_table(rows, headers)
    print()
    print(f"  {len(rows)} recipe(s) returned.")

    if len(items) == params["per_page"]:
        print(f"  (There may be more results — use --page {args.page + 1} or increase --limit)")
    print()


if __name__ == "__main__":
    main()
