#!/usr/bin/env python3
"""
workato-recipe-push.py — Update (PUT) an existing Workato recipe.

Usage:
    python workato-recipe-push.py --recipe-id 12345 --code-file updated_code.json
    python workato-recipe-push.py --recipe-id 12345 --name "New Name"
    python workato-recipe-push.py --recipe-id 12345 \\
        --code-file code.json --config-file config.json --dry-run

Workflow:
    1. GET /api/recipes/{id}  — read current state
    2. Merge only the fields you specify (unchanged fields are preserved)
    3. PUT /api/recipes/{id}  — write back the merged state

IMPORTANT:
    - The Workato PUT API is a *full replace*, so this script always reads
      current state first to avoid accidentally deleting existing steps.
    - code and config must be JSON strings in the PUT body; this script
      handles serialisation automatically.
    - Active recipes must be stopped before they can be updated.
      This script will warn you but will NOT stop the recipe automatically.
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

def _load_json_file(path: str, label: str) -> dict | list:
    if not os.path.isfile(path):
        print(f"ERROR: {label} file not found: {path}")
        sys.exit(1)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {label} file is not valid JSON: {exc}")
        sys.exit(1)


def _ensure_json_string(value: object, field_name: str) -> str:
    """
    Workato stores 'code' and 'config' as JSON *strings* in the API response
    sometimes and as objects other times, depending on endpoint version.
    This normalises both cases to a JSON string for the PUT body.
    """
    if isinstance(value, str):
        # Validate it is parseable, then re-serialise to normalise whitespace.
        try:
            parsed = json.loads(value)
            return json.dumps(parsed)
        except json.JSONDecodeError:
            # Return as-is; the platform will reject it if it's truly invalid.
            return value
    elif value is None:
        return json.dumps({} if field_name == "code" else [])
    else:
        return json.dumps(value)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update (PUT) an existing Workato recipe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--recipe-id",   required=True, type=int, help="Recipe ID to update")
    parser.add_argument("--code-file",                            help="Path to JSON file with new recipe code object")
    parser.add_argument("--config-file",                          help="Path to JSON file with new config array")
    parser.add_argument("--name",                                 help="New recipe name (replaces current)")
    parser.add_argument("--description",                          help="New description (replaces current)")
    parser.add_argument("--dry-run",     action="store_true",     help="Print merged payload but do not call PUT")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- Step 1: GET current state ---
    print(f"Fetching current state of recipe {args.recipe_id} …")
    body, err = wc.api_get(f"/recipes/{args.recipe_id}", token)
    if err:
        print(f"ERROR fetching recipe: {err}")
        sys.exit(1)

    # The response may be wrapped in {"recipe": {...}} or flat
    current = body.get("recipe", body) if isinstance(body, dict) else body
    if not isinstance(current, dict):
        print(f"ERROR: Unexpected API response format: {body!r}")
        sys.exit(1)

    current_name   = current.get("name", "")
    current_active = current.get("running", False) or current.get("active", False)

    print(f"  Name    : {current_name}")
    print(f"  Active  : {'YES — recipe is running; stop it in Workato GUI before updating' if current_active else 'no'}")
    print(f"  Folder  : {current.get('folder_id', '?')}")
    print()

    if current_active:
        print("WARNING: This recipe is currently active (running).")
        print("         Workato may reject the PUT. Stop the recipe in the GUI first.")
        print()

    # --- Step 2: Merge changes ---
    merged = dict(current)  # shallow copy of the full current object

    if args.name:
        merged["name"] = args.name

    if args.description is not None:
        merged["description"] = args.description

    if args.code_file:
        new_code = _load_json_file(args.code_file, "--code-file")
        merged["code"] = new_code
    # else keep current code as-is

    if args.config_file:
        new_config = _load_json_file(args.config_file, "--config-file")
        if not isinstance(new_config, list):
            print("ERROR: --config-file must contain a JSON array.")
            sys.exit(1)
        merged["config"] = new_config
    # else keep current config as-is

    # Normalise code and config to JSON strings for the PUT body
    merged["code"]   = _ensure_json_string(merged.get("code"),   "code")
    merged["config"] = _ensure_json_string(merged.get("config"), "config")

    # Remove read-only fields that the API rejects on PUT
    for ro in ("id", "user_id", "created_at", "updated_at", "last_run_at",
               "running", "job_succeeded_count", "job_failed_count",
               "copy_count", "trigger_application", "action_applications",
               "applications", "api_key", "stop_cause"):
        merged.pop(ro, None)

    payload = {"recipe": merged}

    # --- Dry run ---
    if args.dry_run:
        print("DRY RUN — merged payload that would be PUT to /api/recipes/{id}:")
        print("-" * 60)
        # Pretty-print with code/config expanded for readability
        display = dict(payload)
        display["recipe"] = dict(merged)
        for field in ("code", "config"):
            val = display["recipe"].get(field)
            if isinstance(val, str):
                try:
                    display["recipe"][field] = json.loads(val)
                except json.JSONDecodeError:
                    pass
        print(json.dumps(display, indent=2))
        print()
        print("(No API call made — remove --dry-run to push the update.)")
        print()
        return

    # --- Step 3: PUT ---
    print(f"Pushing update to recipe {args.recipe_id} …")
    put_body, put_err = wc.api_put(f"/recipes/{args.recipe_id}", payload, token)

    if put_err:
        print(f"ERROR: {put_err}")
        sys.exit(1)

    updated = put_body.get("recipe", put_body) if isinstance(put_body, dict) else put_body
    rid  = updated.get("id", args.recipe_id) if isinstance(updated, dict) else args.recipe_id
    name = updated.get("name", merged.get("name", "?")) if isinstance(updated, dict) else merged.get("name", "?")

    print()
    print("Recipe updated successfully.")
    print(f"  Recipe ID   : {rid}")
    print(f"  Name        : {name}")
    print(f"  URL         : https://www.workato.com/recipes/{rid}")
    print()


if __name__ == "__main__":
    main()
