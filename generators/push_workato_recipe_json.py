#!/usr/bin/env python3
"""
Push a Workato recipe JSON file to the platform via REST API.

Usage:
    python generators/push_workato_recipe_json.py <recipe.json> \
        [--folder "MIG_myproject"] [--name "Override Name"]

Required env: WORKATO_API_TOKEN
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


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


def validate_recipe(code: dict) -> list:
    """
    Check a recipe code object for known broken patterns that cause blank steps in Workato.
    Returns a list of warning strings (empty = clean).
    """
    warnings = []

    def walk(node, path=""):
        if isinstance(node, dict):
            kw = node.get("keyword", "")
            prov = node.get("provider", "")
            name = node.get("name", "")

            # Trigger must have input_fields_raw_schema (not input_schema / output_schema)
            if kw == "trigger" and prov == "workato" and name == "callable_recipe":
                inp = node.get("input", {})
                if "input_schema" in inp or "output_schema" in inp:
                    warnings.append(
                        f"[{path}] Trigger uses 'input_schema'/'output_schema' — "
                        "must be 'input_fields_raw_schema'. Workato will render this as unconfigured."
                    )
                if "input_fields_raw_schema" not in inp:
                    warnings.append(
                        f"[{path}] Trigger missing 'input_fields_raw_schema' — "
                        "trigger will show 'Select an app and trigger event'."
                    )
                raw_schema = inp.get("input_fields_raw_schema", "")
                if isinstance(raw_schema, str) and ('"object"' in raw_schema or '"array"' in raw_schema):
                    warnings.append(
                        f"[{path}] Trigger input_fields_raw_schema has type 'object' or 'array' — "
                        "Workato silently wipes the entire trigger input for these types. "
                        "All fields must be type string/integer/boolean."
                    )

            # workato/* action types do not exist
            if kw == "action" and prov == "workato":
                warnings.append(
                    f"[{path}] provider='workato' action (name='{name}') does not exist in Workato — "
                    "will render as a blank empty step. Use provider='http', name='post' instead."
                )

            # foreach is not a valid Workato keyword
            if kw == "foreach":
                warnings.append(
                    f"[{path}] keyword='foreach' is invalid — Workato loop keyword is 'each'."
                )

            # IF conditions at top level (not inside input)
            if kw == "if" and "conditions" in node and "input" not in node:
                warnings.append(
                    f"[{path}] IF step has 'conditions' at top level — "
                    "must be inside 'input': {{\"type\":\"compound\",\"operand\":\"and\",\"conditions\":[...]}}."
                )

            # HTTP action payload must be a string
            if kw == "action" and prov == "http":
                payload = node.get("input", {}).get("payload")
                if isinstance(payload, dict):
                    warnings.append(
                        f"[{path}] HTTP action 'payload' is a JSON object — "
                        "must be a JSON-serialized string. Workato will ignore object-type payloads."
                    )

            # monitor is not a valid Workato keyword
            if kw == "monitor":
                warnings.append(
                    f"[{path}] keyword='monitor' does not exist in Workato — "
                    "this renders the entire block as ONE blank gray step, making the recipe appear empty. "
                    "Use 'rescue' as a standalone sibling step instead (no monitor wrapper)."
                )

            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")

    walk(code)
    return warnings


def _strip_schema_hints(obj):
    """Remove extended_input_schema / extended_output_schema — rejected by Workato POST API."""
    _STRIP = {"extended_input_schema", "extended_output_schema"}
    if isinstance(obj, dict):
        return {k: _strip_schema_hints(v) for k, v in obj.items() if k not in _STRIP}
    if isinstance(obj, list):
        return [_strip_schema_hints(i) for i in obj]
    return obj


def _normalize_config(config: list) -> list:
    """Replace zip-export account_id objects with null."""
    out = []
    for entry in config:
        e = dict(entry)
        acct = e.get("account_id")
        if acct is not None and not isinstance(acct, (int, float)):
            e["account_id"] = None
            e["skip_validation"] = True
        out.append(e)
    return out


def push(recipe_path: str, folder: str = "", name_override: str = "") -> None:
    _load_dotenv()
    token = os.environ.get("WORKATO_API_TOKEN", "").strip()
    if not token:
        print("ERROR: WORKATO_API_TOKEN not set in .env", file=sys.stderr)
        sys.exit(1)

    with open(recipe_path, encoding="utf-8") as f:
        recipe = json.load(f)

    name        = name_override.strip() or recipe.get("name", "Untitled Recipe")
    raw_code    = recipe.get("code", {})
    clean_code  = _strip_schema_hints(raw_code)
    clean_cfg   = _normalize_config(recipe.get("config", []))

    # Pre-push validation — catch known broken patterns before sending to Workato
    issues = validate_recipe(raw_code)
    if issues:
        print(f"  RECIPE VALIDATION WARNINGS ({len(issues)} issues found):", file=sys.stderr)
        for w in issues:
            print(f"    - {w}", file=sys.stderr)
        print(
            "  The recipe will be pushed but may render with blank/empty steps in Workato.\n"
            "  Re-run the migration to regenerate with the fixed generator.",
            file=sys.stderr,
        )

    payload: dict = {
        "recipe": {
            "name":   name,
            "code":   json.dumps(clean_code),
            "config": json.dumps(clean_cfg),
        }
    }
    fid = folder.strip()
    if fid and fid.isdigit():
        payload["recipe"]["folder_id"] = fid

    body = json.dumps(payload).encode()
    req  = urllib.request.Request(
        "https://www.workato.com/api/recipes",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
        recipe_id = resp.get("id")
        if recipe_id:
            print(f"  SUCCESS — Recipe ID: {recipe_id}")
            print(f"  URL: https://app.workato.com/recipes/{recipe_id}")
        else:
            print(f"  WARN: push returned 200 but no id: {resp}")
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        print(f"  HTTP ERROR {e.code}: {err[:800]}", file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(f"  EXCEPTION: {ex}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Push a Workato recipe JSON file to the platform."
    )
    parser.add_argument("recipe_path", help="Path to the recipe JSON file")
    parser.add_argument("--folder", default="", help="Workato folder ID or name")
    parser.add_argument("--name",   default="", help="Override recipe name")
    args = parser.parse_args()

    if not os.path.isfile(args.recipe_path):
        print(f"ERROR: Recipe file not found: {args.recipe_path}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[PUSH] Pushing {Path(args.recipe_path).name} to Workato...")
    push(args.recipe_path, args.folder, args.name)


if __name__ == "__main__":
    main()
