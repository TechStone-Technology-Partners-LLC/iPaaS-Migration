#!/usr/bin/env python3
"""
workato-recipe-pull.py — Download a Workato recipe's full JSON.

Usage:
    python workato-recipe-pull.py --recipe-id 12345
    python workato-recipe-pull.py --recipe-id 12345 --output my_recipe.json

If --output is provided the full recipe JSON is written to that file.
Otherwise the recipe details are printed to stdout and the recipe code
(parsed from its JSON string) is pretty-printed.
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

def _parse_json_field(value: object) -> object:
    """
    The Workato API returns 'code' and 'config' as JSON *strings* in some
    contexts. Parse and return the object; if already a dict/list return
    as-is; if None return None.
    """
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value   # return raw string; caller will handle
    return value


def _count_steps(code: dict | list | None) -> int:
    """Recursively count action/trigger blocks in the recipe code."""
    if code is None:
        return 0
    if isinstance(code, list):
        return sum(_count_steps(item) for item in code)
    if isinstance(code, dict):
        count = 1 if code.get("keyword") in ("trigger", "action", "if", "each", "try") else 0
        block = code.get("block") or []
        return count + sum(_count_steps(item) for item in block)
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a Workato recipe's full JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--recipe-id", required=True, type=int, help="Recipe ID to pull")
    parser.add_argument("--output",                              help="Write full recipe JSON to this file path")
    parser.add_argument("--code-only", action="store_true",      help="Print/save only the recipe code object (not the full envelope)")
    args = parser.parse_args()

    # --- Token ---
    token = wc.resolve_token(_SCRIPTS_DIR)
    if not token:
        print("ERROR: WORKATO_API_TOKEN is not set. Run workato-env-check.py for help.")
        sys.exit(1)

    # --- GET recipe ---
    print(f"Fetching recipe {args.recipe_id} …")
    body, err = wc.api_get(f"/recipes/{args.recipe_id}", token)
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    # Normalise wrapper
    recipe = body.get("recipe", body) if isinstance(body, dict) else body
    if not isinstance(recipe, dict):
        print(f"ERROR: Unexpected API response: {body!r}")
        sys.exit(1)

    # Parse code and config from JSON strings to objects
    code_raw   = recipe.get("code")
    config_raw = recipe.get("config")
    code_obj   = _parse_json_field(code_raw)
    config_obj = _parse_json_field(config_raw)

    # Build the output object with expanded (non-string) code/config
    output_recipe = dict(recipe)
    output_recipe["code"]   = code_obj
    output_recipe["config"] = config_obj

    # --- Metadata summary ---
    name      = recipe.get("name", "")
    rid       = recipe.get("id", args.recipe_id)
    folder_id = recipe.get("folder_id", "?")
    active    = recipe.get("running", False) or recipe.get("active", False)
    updated   = recipe.get("updated_at", "")
    step_count = _count_steps(code_obj)

    print()
    print(f"  Name        : {name}")
    print(f"  ID          : {rid}")
    print(f"  Folder ID   : {folder_id}")
    print(f"  Active      : {'yes' if active else 'no'}")
    if updated:
        print(f"  Last updated: {updated}")
    print(f"  Steps found : ~{step_count}")
    print()

    # --- Output ---
    to_write = output_recipe["code"] if args.code_only else output_recipe

    if args.output:
        out_path = os.path.abspath(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(to_write, f, indent=2)
        label = "Code" if args.code_only else "Full recipe"
        print(f"  {label} JSON written to: {out_path}")
    else:
        label = "Recipe code" if args.code_only else "Full recipe JSON"
        print(f"  {label}:")
        print("-" * 60)
        print(json.dumps(to_write, indent=2))

    print()


if __name__ == "__main__":
    main()
