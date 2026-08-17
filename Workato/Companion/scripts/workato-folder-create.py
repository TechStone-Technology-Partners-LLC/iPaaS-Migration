#!/usr/bin/env python3
"""
workato-folder-create.py — Create a Workato folder or list existing folders.

Usage:
    # Create a folder
    python workato-folder-create.py --name "MyFolder" --parent-id 12345

    # List root folders
    python workato-folder-create.py --list

    # List folders under a specific parent
    python workato-folder-create.py --list --parent-id 12345

CRITICAL API NOTE:
    The Workato folders API uses FLAT JSON — no wrapper key:
        CORRECT : {"name": "FolderName", "parent_id": 12345}
        WRONG   : {"folder": {"name": "FolderName", ...}}  → HTTP 400

    parent_id must be an integer. The root level folders on Workato have
    parent_id = null / not set. Use --parent-id 0 to mean "root" if the
    API accepts it, or omit --parent-id for top-level folder creation.
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

def _list_folders(token: str, parent_id: int | None) -> None:
    """List folders, optionally filtered by parent_id."""
    params: dict = {}
    if parent_id is not None:
        params["parent_id"] = parent_id

    print("Fetching folders …")
    body, err = wc.api_get("/folders", token, params=params)
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    # Normalise response shape
    items: list = []
    if isinstance(body, dict):
        items = body.get("result", body.get("items", body.get("folders", [])))
    elif isinstance(body, list):
        items = body

    if not items:
        scope = f"under parent_id={parent_id}" if parent_id is not None else "at root level"
        print(f"\nNo folders found {scope}.\n")
        return

    rows: list[list[str]] = []
    for f in items:
        if not isinstance(f, dict):
            continue
        rows.append([
            str(f.get("id", "")),
            str(f.get("parent_id", "")),
            wc.truncate(f.get("name", ""), 50),
        ])

    print()
    wc.print_table(rows, ["ID", "Parent ID", "Name"])
    print()
    print(f"  {len(rows)} folder(s) found.")
    print()


def _create_folder(token: str, name: str, parent_id: int | None, dry_run: bool) -> None:
    """Create a folder via POST /api/folders."""
    # CRITICAL: flat payload — no wrapper key
    payload: dict = {"name": name}
    if parent_id is not None:
        payload["parent_id"] = parent_id

    if dry_run:
        print()
        print("DRY RUN — payload that would be POSTed to POST /api/folders:")
        print("-" * 50)
        print(json.dumps(payload, indent=2))
        print()
        print("(No API call made — remove --dry-run to create the folder.)")
        print()
        return

    print(f"Creating folder '{name}'" + (f" under parent {parent_id}" if parent_id else " at root") + " …")
    body, err = wc.api_post("/folders", payload, token)
    if err:
        print(f"ERROR: {err}")
        print()
        print("Troubleshooting:")
        print("  - Verify --parent-id is a valid folder ID in your Workato account.")
        print("  - The Workato API uses FLAT JSON (no wrapper key). This script handles that.")
        print("  - Try --list to see existing folder IDs.")
        sys.exit(1)

    # Normalise response
    folder = body
    if isinstance(body, dict):
        folder = body.get("folder", body.get("result", body))

    fid  = folder.get("id", "?") if isinstance(folder, dict) else "?"
    fname = folder.get("name", name) if isinstance(folder, dict) else name
    fpid = folder.get("parent_id", parent_id) if isinstance(folder, dict) else parent_id

    print()
    print("Folder created successfully.")
    print(f"  Folder ID   : {fid}")
    print(f"  Name        : {fname}")
    if fpid is not None:
        print(f"  Parent ID   : {fpid}")
    print()
    print(f"  Use folder_id={fid} when creating recipes in this folder.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Workato folder or list existing folders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--name",      help="Folder name to create (required unless --list)")
    parser.add_argument("--parent-id", type=int, help="Parent folder ID (omit for root-level)")
    parser.add_argument("--list",      action="store_true", help="List existing folders instead of creating one")
    parser.add_argument("--dry-run",   action="store_true", help="Print payload but do not call the API")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- Route to list or create ---
    if args.list:
        _list_folders(token, args.parent_id)
    else:
        if not args.name:
            parser.error("--name is required when creating a folder (or use --list to list folders).")
        _create_folder(token, args.name, args.parent_id, args.dry_run)


if __name__ == "__main__":
    main()
