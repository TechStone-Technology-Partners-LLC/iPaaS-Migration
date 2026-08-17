#!/usr/bin/env python3
"""
workato-env-check.py — Check Workato environment setup and connectivity.

Usage:
    python workato-env-check.py

Checks:
  - WORKATO_API_TOKEN is set (from .env or environment)
  - WORKATO_BASE_URL override (optional)
  - Connectivity: GET /users/me
"""

import os
import sys

# ---------------------------------------------------------------------------
# Bootstrap: find workato-common on the path
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

# Import as module (Python requires valid identifiers; load via importlib)
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("workato_common", os.path.join(_SCRIPTS_DIR, "workato-common.py"))
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
wc = _mod   # alias


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_var(name: str, value: str, default: str | None = None) -> None:
    """Print a single env-var row."""
    col = name.ljust(22)
    if value:
        masked = "..." + value[-4:] if len(value) >= 4 else "****"
        print(f"  {col}  SET     (ends in {masked})")
    else:
        if default:
            print(f"  {col}  UNSET   (using default: {default})")
        else:
            print(f"  {col}  UNSET")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("Workato Environment Check")
    print("=" * 43)
    print()

    # Locate .env upward from the scripts dir (typically finds project root .env)
    env_path = wc.find_env_file(_SCRIPTS_DIR)

    if env_path:
        print(f"  .env file found : {env_path}")
    else:
        print("  .env file       : NOT FOUND (will rely on shell environment)")
    print()

    # --- Resolve token ---
    token = wc.resolve_token(_SCRIPTS_DIR)

    # --- Resolve optional base URL override ---
    base_url_override: str = ""
    if env_path:
        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("WORKATO_BASE_URL="):
                        base_url_override = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    if not base_url_override:
        base_url_override = os.environ.get("WORKATO_BASE_URL", "")

    base_url = base_url_override or wc.BASE_URL

    # --- Print variable status table ---
    print("  Variable               Status")
    print("  " + "-" * 50)
    _check_var("WORKATO_API_TOKEN", token)
    if base_url_override:
        _check_var("WORKATO_BASE_URL", base_url_override)
    else:
        print(f"  {'WORKATO_BASE_URL'.ljust(22)}  UNSET   (using default: {wc.BASE_URL})")

    print()

    # --- Gate on token ---
    if not token:
        print("  ERROR: WORKATO_API_TOKEN is not set.")
        print()
        print("  Fix options:")
        print("    1. Add  WORKATO_API_TOKEN=<token>  to your project .env file.")
        print("    2. Export the variable in your shell:  export WORKATO_API_TOKEN=<token>")
        print()
        sys.exit(1)

    # --- Connectivity test ---
    print("  Connectivity test: GET /users/me")
    body, err = wc.api_get("/users/me", token, base_url)

    if err:
        print(f"  FAILED — {err}")
        print()
        print("  Troubleshooting:")
        print("    - Verify your WORKATO_API_TOKEN is valid (Settings → API Tokens in Workato).")
        print("    - Check network / VPN access to www.workato.com.")
        print("    - If SSL errors occur, check corporate proxy (Zscaler, Netskope, Umbrella).")
        print()
        sys.exit(1)

    # Parse response
    email = body.get("email", "<unknown>")
    acct_id = body.get("id", "<unknown>")
    name  = body.get("name", "")
    plan  = body.get("plan_name", "")

    print(f"  OK — account   : {email}")
    if name:
        print(f"         name    : {name}")
    print(f"         id      : {acct_id}")
    if plan:
        print(f"         plan    : {plan}")

    print()
    print("  Environment is configured correctly.")
    print()


if __name__ == "__main__":
    main()
