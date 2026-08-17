"""
workato-common.py — Shared utilities for Workato Companion scripts.

Import pattern (from a sibling script):
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import workato_common as wc   # Note: import uses underscore, file uses hyphen
"""

import json
import os
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://www.workato.com/api"


# ---------------------------------------------------------------------------
# .env helpers
# ---------------------------------------------------------------------------

def find_env_file(start_dir: str) -> str | None:
    """
    Walk upward from *start_dir* looking for a .env file.
    Returns the absolute path of the first .env found, or None.
    """
    current = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(current, ".env")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:          # filesystem root reached
            return None
        current = parent


def load_env(project_root: str) -> str:
    """
    Read WORKATO_API_TOKEN from *project_root*/.env.
    Falls back to the environment variable if the file is absent or the key
    is not found in it.

    Returns the token string (may be empty string if nowhere found).
    """
    tok: str | None = None
    env_path = os.path.join(project_root, ".env")

    # If the caller passed a directory that doesn't contain .env directly,
    # walk upward to find one.
    if not os.path.isfile(env_path):
        found = find_env_file(project_root)
        if found:
            env_path = found

    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("WORKATO_API_TOKEN="):
                    tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    except Exception:
        pass

    return tok or os.environ.get("WORKATO_API_TOKEN", "")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def get_headers(token: str) -> dict[str, str]:
    """Return standard auth + content-type headers."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }


def _request(
    method: str,
    path: str,
    body_dict: dict | None,
    token: str,
    base_url: str = BASE_URL,
) -> tuple[dict | list | None, str | None]:
    """
    Low-level HTTP helper.

    Returns (parsed_body, error_string).
    On success  error_string is None.
    On failure  parsed_body is None and error_string describes what went wrong.
    """
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    headers = get_headers(token)

    data: bytes | None = None
    if body_dict is not None:
        data = json.dumps(body_dict).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            if raw.strip():
                return json.loads(raw), None
            return {}, None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        excerpt = raw[:400] if len(raw) > 400 else raw
        return None, f"HTTP {exc.code} {exc.reason}: {excerpt}"
    except urllib.error.URLError as exc:
        return None, f"Network error: {exc.reason}"
    except json.JSONDecodeError as exc:
        return None, f"JSON decode error: {exc}"


def api_get(
    path: str,
    token: str,
    base_url: str = BASE_URL,
    params: dict | None = None,
) -> tuple[dict | list | None, str | None]:
    """
    GET *base_url*/*path* with optional query *params*.
    Returns (body_dict, error).
    """
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        path = f"{path}?{query}"
    return _request("GET", path, None, token, base_url)


def api_post(
    path: str,
    body_dict: dict,
    token: str,
    base_url: str = BASE_URL,
) -> tuple[dict | list | None, str | None]:
    """POST *body_dict* to *base_url*/*path*. Returns (body_dict, error)."""
    return _request("POST", path, body_dict, token, base_url)


def api_put(
    path: str,
    body_dict: dict,
    token: str,
    base_url: str = BASE_URL,
) -> tuple[dict | list | None, str | None]:
    """PUT *body_dict* to *base_url*/*path*. Returns (body_dict, error)."""
    return _request("PUT", path, body_dict, token, base_url)


def api_delete(
    path: str,
    token: str,
    base_url: str = BASE_URL,
) -> tuple[dict | list | None, str | None]:
    """DELETE *base_url*/*path*. Returns (body_dict, error)."""
    return _request("DELETE", path, None, token, base_url)


# ---------------------------------------------------------------------------
# Formatting utilities
# ---------------------------------------------------------------------------

def truncate(text: str, width: int) -> str:
    """Truncate *text* to *width* characters, appending '…' if cut."""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= width:
        return text
    return text[: width - 1] + "…"


def print_table(rows: list[list[str]], headers: list[str]) -> None:
    """
    Print a plain-text table.  *rows* is a list of string lists; *headers*
    defines column names and implicitly the number of columns.
    """
    all_rows = [headers] + [[str(c) for c in r] for r in rows]
    col_widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]

    sep = "  ".join("-" * w for w in col_widths)
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))

    print(header_line)
    print(sep)
    for row in all_rows[1:]:
        print("  ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))


# ---------------------------------------------------------------------------
# Token resolution helper (used by every companion script)
# ---------------------------------------------------------------------------

def resolve_token(project_root: str | None = None) -> str:
    """
    Resolve the API token, searching upward from *project_root* (or the
    directory containing this file if not specified).
    """
    root = project_root or os.path.dirname(os.path.abspath(__file__))
    return load_env(root)
