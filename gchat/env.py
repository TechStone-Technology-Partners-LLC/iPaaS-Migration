"""Shared environment loading for the gchat bot.

One .env loader instead of a fifth copy of the pattern duplicated across
scripts/*.py and app.py. Real environment variables always win over .env.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Load REPO_ROOT/.env into os.environ (simple parser, no deps)."""
    env_path = REPO_ROOT / ".env"
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


def get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def get_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "")
    try:
        return float(raw) if raw else default
    except ValueError:
        return default


def get_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "")
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def allowed_users() -> list[str]:
    """Optional comma-separated allowlist of Chat sender emails."""
    raw = get("GCHAT_ALLOWED_USERS")
    return [u.strip().lower() for u in raw.split(",") if u.strip()]
