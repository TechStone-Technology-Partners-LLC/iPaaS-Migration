#!/usr/bin/env python3
"""
workato-connection-list.py — List Workato connections and their account_id values.

Usage:
    python workato-connection-list.py
    python workato-connection-list.py --provider oracle
    python workato-connection-list.py --name "GLD"
    python workato-connection-list.py --provider http --name "CheckWriter"

Calls GET /api/connections.
Output: table with columns: ID | Authorized | Provider | Name

The ID values are what you use as `account_id` in a recipe's config array
when wiring connections to steps.

Config array usage example:
    [
      {
        "keyword": "application",
        "provider": "oracle",
        "account_id": 19657520,   ← connection ID from this script
        "skip_validation": false
      }
    ]
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

def _auth_label(conn: dict) -> str:
    authorized = conn.get("authorized", None)
    if authorized is True:
        return "yes"
    if authorized is False:
        return "NO"
    # Some responses use a different key
    if conn.get("authorization_status") == "success":
        return "yes"
    return "?"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="List Workato connections and their account_id values.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--provider", help="Filter by provider name (e.g. oracle, http, salesforce)")
    parser.add_argument("--name",     help="Filter by connection name substring (client-side match)")
    parser.add_argument("--limit",    type=int, default=100, help="Max connections to fetch (default: 100)")
    parser.add_argument("--json",     action="store_true", dest="json_out",
                        help="Output raw JSON instead of table")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- Build query params ---
    params: dict = {}
    if args.provider:
        params["search[provider]"] = args.provider
    params["per_page"] = min(args.limit, 100)

    # --- GET /connections ---
    filter_desc = []
    if args.provider:
        filter_desc.append(f"provider='{args.provider}'")
    if args.name:
        filter_desc.append(f"name contains '{args.name}'")
    filter_str = " AND ".join(filter_desc) if filter_desc else "all"
    print(f"Fetching connections ({filter_str}) …")

    body, err = wc.api_get("/connections", token, params=params)
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    # Normalise response
    items: list = []
    if isinstance(body, dict):
        items = body.get("result", body.get("items", body.get("connections", [])))
    elif isinstance(body, list):
        items = body

    # Client-side name filter
    if args.name:
        name_lower = args.name.lower()
        items = [c for c in items if isinstance(c, dict) and name_lower in c.get("name", "").lower()]

    if not items:
        print()
        print("No connections found matching the search criteria.")
        print()
        return

    # --- JSON output ---
    if args.json_out:
        print(json.dumps(items, indent=2))
        return

    # --- Table output ---
    rows: list[list[str]] = []
    for c in items:
        if not isinstance(c, dict):
            continue
        rows.append([
            str(c.get("id", "")),
            _auth_label(c),
            wc.truncate(c.get("provider", ""), 20),
            wc.truncate(c.get("name", ""), 55),
        ])

    print()
    wc.print_table(rows, ["ID", "Auth", "Provider", "Name"])
    print()
    print(f"  {len(rows)} connection(s) found.")
    print()
    print("  NOTE: Use the ID column as `account_id` in recipe config arrays.")
    print("  Example config entry:")
    print('    {"keyword": "application", "provider": "<provider>",')
    print('     "account_id": <ID>, "skip_validation": false}')
    print()

    # Highlight any unauthorised connections
    unauth = [r for r in rows if r[1] != "yes"]
    if unauth:
        print(f"  WARNING: {len(unauth)} connection(s) are NOT authorized:")
        for r in unauth:
            print(f"    ID {r[0]}  {r[3]}")
        print("  Authorize them in Workato GUI (App Connections page) before use.")
        print()


if __name__ == "__main__":
    main()
