#!/usr/bin/env python3
"""
workato-recipe-create.py — Create a new Workato recipe via the API.

Usage:
    python workato-recipe-create.py --name "My Recipe" --folder-id 12345
    python workato-recipe-create.py --name "My Recipe" --folder-id 12345 \\
        --code-file recipe_code.json --config-file recipe_config.json \\
        --description "Does X and Y" --dry-run

Notes:
    - --code-file   : JSON file containing the recipe code object (trigger + steps).
                      If omitted, a minimal passthrough (no-op) recipe is used.
    - --config-file : JSON file containing the config array (connection wiring).
    - The Workato API requires code and config as JSON *strings*, not objects.
      This script handles that serialisation automatically.
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
# Minimal passthrough recipe code (used when --code-file is omitted)
# ---------------------------------------------------------------------------
_PASSTHROUGH_CODE = {
    "number": 1,
    "provider": "clock",
    "name": "scheduled_event",
    "as": "trigger",
    "title": None,
    "description": None,
    "keyword": "trigger",
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "interval": "1",
        "start_at": ""
    },
    "block": [],
    "uuid": "00000000-0000-0000-0000-000000000001",
    "comment": "Minimal passthrough — replace with your recipe logic"
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json_file(path: str, label: str) -> dict | list:
    """Load and parse a JSON file; exit with a clear error on failure."""
    if not os.path.isfile(path):
        print(f"ERROR: {label} file not found: {path}")
        sys.exit(1)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {label} file is not valid JSON: {exc}")
        sys.exit(1)


def _build_payload(
    name: str,
    folder_id: int,
    description: str,
    code_obj: dict | list,
    config_obj: list | None,
) -> dict:
    """
    Build the POST /api/recipes payload.
    Both 'code' and 'config' must be JSON *strings* inside the recipe object.
    """
    recipe: dict = {
        "name": name,
        "folder_id": str(folder_id),
        "code": json.dumps(code_obj),
    }
    if description:
        recipe["description"] = description
    if config_obj is not None:
        recipe["config"] = json.dumps(config_obj)
    return {"recipe": recipe}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a new Workato recipe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--name",        required=True,       help="Recipe name")
    parser.add_argument("--folder-id",   required=True, type=int, help="Target folder ID (integer)")
    parser.add_argument("--code-file",                        help="Path to JSON file with recipe code object")
    parser.add_argument("--config-file",                      help="Path to JSON file with config array")
    parser.add_argument("--description", default="",          help="Recipe description")
    parser.add_argument("--dry-run",     action="store_true", help="Print payload but do not call the API")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- Load code ---
    if args.code_file:
        code_obj = _load_json_file(args.code_file, "--code-file")
    else:
        code_obj = _PASSTHROUGH_CODE
        print("INFO: --code-file not provided; using minimal passthrough recipe code.")

    # --- Load config ---
    config_obj = None
    if args.config_file:
        config_obj = _load_json_file(args.config_file, "--config-file")
        if not isinstance(config_obj, list):
            print("ERROR: --config-file must contain a JSON array, not an object.")
            sys.exit(1)

    # --- Build payload ---
    payload = _build_payload(
        name=args.name,
        folder_id=args.folder_id,
        description=args.description,
        code_obj=code_obj,
        config_obj=config_obj,
    )

    # --- Dry run ---
    if args.dry_run:
        print()
        print("DRY RUN — payload that would be POSTed to POST /api/recipes:")
        print("-" * 60)

        # Pretty-print the outer structure; expand the code/config strings back
        # for readability.
        display = dict(payload)
        display["recipe"] = dict(payload["recipe"])
        if "code" in display["recipe"]:
            display["recipe"]["code"] = json.loads(display["recipe"]["code"])
        if "config" in display["recipe"]:
            display["recipe"]["config"] = json.loads(display["recipe"]["config"])
        print(json.dumps(display, indent=2))
        print()
        print("(No API call made — remove --dry-run to create the recipe.)")
        print()
        return

    # --- POST ---
    print(f"Creating recipe '{args.name}' in folder {args.folder_id} …")
    body, err = wc.api_post("/recipes", payload, token)

    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    recipe = body.get("recipe", body)  # API may return {"recipe": {...}} or flat
    rid  = recipe.get("id", body.get("id", "?"))
    name = recipe.get("name", args.name)

    print()
    print("Recipe created successfully.")
    print(f"  Recipe ID   : {rid}")
    print(f"  Name        : {name}")
    print(f"  Folder ID   : {args.folder_id}")
    print(f"  URL         : https://www.workato.com/recipes/{rid}")
    print()


if __name__ == "__main__":
    main()
