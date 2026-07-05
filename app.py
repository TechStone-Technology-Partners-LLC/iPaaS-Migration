#!/usr/bin/env python3
"""
MigrAlte — AI-Powered Integration Migration
Run: streamlit run app.py
"""

import base64
import io
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
import urllib.error
import zipfile
from pathlib import Path

import streamlit as st

# ─── Constants ─────────────────────────────────────────────────────────────────

AGENT_DIR = Path(__file__).parent.resolve()

PLATFORM_LABELS = {
    "boomi":      "Boomi",
    "mulesoft":   "MuleSoft",
    "workato":    "Workato",
    "celigo":     "Celigo",
    "webmethods": "webMethods.io",
}
SOURCE_PLATFORMS = ["boomi", "mulesoft", "workato", "celigo", "webmethods"]
TARGET_PLATFORMS = ["boomi", "workato", "celigo", "webmethods"]

# MigrAlte brand palette (extracted from architecture diagram)
C = {
    "navy":       "#1A2B4A",
    "blue":       "#1E5FA8",
    "green":      "#2D6A0C",
    "orange":     "#E07820",
    "purple":     "#7B4FAB",
    "teal":       "#0D9A8A",
    "lightblue":  "#4A8FCC",
    "navy_light": "#243454",
    "bg":         "#F4F7FC",
    "card":       "#FFFFFF",
    "muted":      "#6B7A9A",
}

WM_UPLOAD_DIR = "active-development/wm_upload"

# Pipeline steps in execution order — keys match [PHASE] markers in migrate.py output
PIPELINE_STEPS = [
    ("PULL",     "Pull",     "Fetch source files"),
    ("ANALYZE",  "Analyze",  "Parse flows & services"),
    ("ENRICH",   "Enrich",   "AI deep enrichment"),
    ("DOCUMENT", "Document", "Design document"),
    ("GENERATE", "Generate", "Push to target"),
]
_PHASE_KEYS = {s[0] for s in PIPELINE_STEPS}
_PHASE_RE   = re.compile(r'\[([A-Z]+)\]')


# ─── Branding helpers ──────────────────────────────────────────────────────────

def _logo_b64() -> str:
    logo_path = AGENT_DIR / "logos" / "TechStone.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def inject_css():
    logo_b64 = _logo_b64()
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="height:28px; filter:brightness(0) invert(1); opacity:0.9;">' if logo_b64 else ""

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Page base ──────────────────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {C["bg"]} !important;
}}

/* Hide default Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stHeader"] {{ display: none; }}

/* Reduce top padding */
.main .block-container {{
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}}

/* ── Header banner ──────────────────────────────────────────────────────── */
.migralte-header {{
    background: linear-gradient(135deg, {C["navy"]} 0%, {C["navy_light"]} 60%, #2A3F66 100%);
    padding: 1.6rem 2rem 1.4rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 4px 24px rgba(26,43,74,0.18);
}}
.migralte-logo-mark {{
    font-size: 2.6rem;
    font-weight: 900;
    color: white;
    background: linear-gradient(135deg, {C["blue"]} 0%, {C["teal"]} 100%);
    width: 58px; height: 58px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    letter-spacing: -2px;
    box-shadow: 0 2px 12px rgba(30,95,168,0.4);
}}
.migralte-title-group {{ flex: 1; }}
.migralte-title {{
    color: #FFFFFF;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.8px;
    line-height: 1.1;
}}
.migralte-subtitle {{
    color: #7CA4D4;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    margin: 3px 0 0 0;
}}
.migralte-tagline {{
    color: #7CA4D4;
    font-size: 0.82rem;
    text-align: right;
    line-height: 1.5;
}}
.migralte-tagline strong {{ color: #A8C4E8; }}

/* ── Upload zone ────────────────────────────────────────────────────────── */
.upload-mode-label {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {C["muted"]};
    margin-bottom: 0.4rem;
}}
.pkg-ready {{
    background: #E2EFDA;
    color: {C["green"]};
    border: 1px solid #8DC87E;
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 0.4rem;
}}

/* ── Section labels ─────────────────────────────────────────────────────── */
.section-label {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {C["muted"]};
    margin-bottom: 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid {C["bg"]};
}}

/* ── Platform cards ─────────────────────────────────────────────────────── */
.platform-card {{
    background: {C["card"]};
    border-radius: 12px;
    padding: 1.4rem 1.4rem 1rem 1.4rem;
    box-shadow: 0 2px 10px rgba(26,43,74,0.07);
    border: 1px solid rgba(26,43,74,0.07);
    margin-bottom: 1rem;
}}
.card-header-source {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {C["blue"]};
    letter-spacing: 0.5px;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.card-header-target {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {C["teal"]};
    letter-spacing: 0.5px;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.dot-source {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: {C["blue"]};
    display: inline-block;
}}
.dot-target {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: {C["teal"]};
    display: inline-block;
}}

/* ── Options bar ────────────────────────────────────────────────────────── */
.options-bar {{
    background: {C["card"]};
    border-radius: 12px;
    padding: 1rem 1.4rem;
    box-shadow: 0 2px 10px rgba(26,43,74,0.07);
    border: 1px solid rgba(26,43,74,0.07);
    margin-bottom: 1.2rem;
}}

/* ── Run button override ────────────────────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {{
    background: linear-gradient(135deg, {C["navy"]} 0%, {C["blue"]} 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(26,43,74,0.25) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,43,74,0.35) !important;
}}

/* ── Output log ─────────────────────────────────────────────────────────── */
.log-wrap {{
    background: {C["navy"]};
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #A8C4E8;
    line-height: 1.6;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}}

/* ── Status badges ──────────────────────────────────────────────────────── */
.badge-success {{
    background: #E2EFDA;
    color: {C["green"]};
    border: 1px solid #8DC87E;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-size: 0.9rem;
}}
.badge-error {{
    background: #FDDEDE;
    color: #C0392B;
    border: 1px solid #E07070;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-size: 0.9rem;
}}

/* ── Step tracker ───────────────────────────────────────────────────────── */
.step-tracker {{
    display: flex;
    gap: 0.5rem;
    margin: 0.8rem 0 0.5rem 0;
    align-items: stretch;
}}
.step-card {{
    flex: 1;
    border-radius: 10px;
    padding: 0.9rem 0.7rem 0.8rem 0.7rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    min-width: 0;
    transition: all 0.25s ease;
}}
.step-pending {{
    background: #EDF0F7;
    border: 1.5px solid #D1D8E8;
    opacity: 0.55;
}}
.step-active {{
    background: linear-gradient(135deg, {C["blue"]} 0%, {C["teal"]} 100%);
    border: 1.5px solid {C["blue"]};
    box-shadow: 0 4px 18px rgba(30,95,168,0.28);
}}
.step-done {{
    background: #E2EFDA;
    border: 1.5px solid #8DC87E;
}}
.step-icon {{
    font-size: 1.25rem;
    font-weight: 800;
    line-height: 1;
}}
.step-pending .step-icon {{ color: #9AACC8; }}
.step-active  .step-icon {{ color: #FFFFFF; animation: step-pulse 1.5s ease-in-out infinite; }}
.step-done    .step-icon {{ color: #2D6A0C; }}
.step-label {{
    font-size: 0.75rem;
    font-weight: 700;
    text-align: center;
}}
.step-pending .step-label {{ color: #6B7A9A; }}
.step-active  .step-label {{ color: #FFFFFF; }}
.step-done    .step-label {{ color: #2D6A0C; }}
.step-desc {{
    font-size: 0.68rem;
    text-align: center;
    line-height: 1.3;
}}
.step-pending .step-desc {{ color: #9AACC8; }}
.step-active  .step-desc {{ color: rgba(255,255,255,0.82); }}
.step-done    .step-desc {{ color: #5A8C4A; }}
@keyframes step-pulse {{
    0%, 100% {{ opacity: 1;   transform: scale(1); }}
    50%       {{ opacity: 0.7; transform: scale(1.18); }}
}}
.step-detail {{
    background: {C["navy"]};
    border-radius: 8px;
    padding: 0.55rem 1rem;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #A8C4E8;
    margin-top: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}}

/* ── Footer ─────────────────────────────────────────────────────────────── */
.migralte-footer {{
    background: {C["navy"]};
    border-radius: 10px;
    padding: 0.9rem 1.6rem;
    margin-top: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #7CA4D4;
    font-size: 0.82rem;
}}
.footer-tagline {{ font-weight: 500; }}
.footer-tagline strong {{ color: #A8C4E8; }}
</style>

<!-- Header -->
<div class="migralte-header">
    <div class="migralte-logo-mark">M→</div>
    <div class="migralte-title-group">
        <p class="migralte-title">MigrAlte</p>
        <p class="migralte-subtitle">AI-Powered Integration Migration</p>
    </div>
    <div class="migralte-tagline">
        <strong>AI + Automation + Expertise</strong><br>
        Faster, Smarter Migrations
        {"<br><br>" + logo_img if logo_img else ""}
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Step tracker ─────────────────────────────────────────────────────────────

def render_step_tracker(current_phase: str, completed: set, detail: str) -> str:
    """Return HTML for the 5-step progress tracker."""
    html = '<div class="step-tracker">'
    for key, label, desc in PIPELINE_STEPS:
        if key in completed:
            state, icon = "done", "✓"
        elif key == current_phase:
            state, icon = "active", "◉"
        else:
            state, icon = "pending", str([s[0] for s in PIPELINE_STEPS].index(key) + 1)
        html += (
            f'<div class="step-card step-{state}">'
            f'<div class="step-icon">{icon}</div>'
            f'<div class="step-label">{label}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div>'
        )
    html += '</div>'
    if detail:
        safe = detail.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html += f'<div class="step-detail">{safe}</div>'
    return html


def _is_detail_line(line: str) -> bool:
    """True if the line is meaningful progress text (not a phase header or blank)."""
    s = line.strip()
    if not s:
        return False
    if _PHASE_RE.match(s):
        return False
    if s.startswith("$") or s.startswith("  $"):
        return False
    if s in ("---", "..."):
        return False
    return True


# ─── webMethods package helpers ───────────────────────────────────────────────

def _gdrive_file_id(url_or_id: str) -> str | None:
    """Extract Google Drive file ID from a share URL or return the raw ID."""
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url_or_id)
    if m:
        return m.group(1)
    m = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url_or_id)
    if m:
        return m.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{25,}$', url_or_id.strip()):
        return url_or_id.strip()
    return None


def _download_gdrive(file_id: str, zip_dest: Path) -> None:
    """Download a file from Google Drive, handling the large-file confirm redirect."""
    base_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())

    with opener.open(base_url) as resp:
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read()

    # Google sends an HTML confirm page for large files
    if b"confirm=" in body and b"<html" in body:
        m = re.search(rb'confirm=([0-9A-Za-z_-]+)', body)
        if m:
            confirm = m.group(1).decode()
            confirm_url = f"https://drive.google.com/uc?export=download&confirm={confirm}&id={file_id}"
            with opener.open(confirm_url) as resp2:
                body = resp2.read()

    zip_dest.write_bytes(body)


def prepare_wm_package(uploaded_file, drive_url: str, base_dir: Path) -> Path | None:
    """
    Resolve the webMethods package source directory.
    Returns the path to the extracted directory, or None if no source provided.
    Raises on download/extraction errors.
    """
    upload_dir = base_dir / WM_UPLOAD_DIR
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True)

    zip_path = upload_dir / "package.zip"

    if uploaded_file is not None:
        zip_path.write_bytes(uploaded_file.read())
    elif drive_url and drive_url.strip():
        file_id = _gdrive_file_id(drive_url.strip())
        if not file_id:
            raise ValueError(f"Could not extract a Google Drive file ID from: {drive_url}")
        _download_gdrive(file_id, zip_path)
    else:
        return None

    extract_dir = upload_dir / "extracted"
    extract_dir.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    return extract_dir


def target_credential_form(platform: str) -> dict:
    env = {}
    if platform == "boomi":
        env["BOOMI_API_URL"]        = st.text_input("API URL", value="https://api.boomi.com/api/rest/v1", key="tgt_boomi_url")
        env["BOOMI_ACCOUNT_ID"]     = st.text_input("Account ID", key="tgt_boomi_account")
        env["BOOMI_USERNAME"]       = st.text_input("Username (email)", key="tgt_boomi_user")
        env["BOOMI_API_TOKEN"]      = st.text_input("API Token", type="password", key="tgt_boomi_token")
        env["BOOMI_ENVIRONMENT_ID"] = st.text_input("Environment ID", key="tgt_boomi_env")
        env["BOOMI_TARGET_FOLDER"]  = st.text_input("Target Folder ID", key="tgt_boomi_folder")
        env["BOOMI_VERIFY_SSL"]     = "true"
    elif platform == "workato":
        env["WORKATO_API_TOKEN"] = st.text_input("API Token", type="password", key="tgt_wt_token")
        env["WORKATO_EMAIL"]     = st.text_input("Account email", key="tgt_wt_email")
    elif platform == "celigo":
        env["CELIGO_API_TOKEN"] = st.text_input("API Token", type="password", key="tgt_cel_token")
    elif platform == "webmethods":
        env["WMIO_TENANT_URL"] = st.text_input("Tenant URL", placeholder="https://mycompany.int-aws-us.webmethods.io", key="tgt_wmio_url")
        env["WMIO_USERNAME"]   = st.text_input("Username", key="tgt_wmio_user")
        env["WMIO_PASSWORD"]   = st.text_input("Password", type="password", key="tgt_wmio_pass")
    return env


# ─── Migration runner ──────────────────────────────────────────────────────────

def build_migrate_cmd(target: str, source_dir: str, dest_name: str,
                      project: str, dry_run: bool,
                      skip_analyze: bool, skip_enrich: bool,
                      skip_document: bool, md_dir: str) -> list:
    cmd = [
        sys.executable, str(AGENT_DIR / "migrate.py"),
        "--from", "webmethods",
        "--to", target,
        "--source-dir", source_dir,
    ]
    if project:
        cmd += ["--project", project]
    if dest_name:
        cmd += ["--dest-name", dest_name]
    if dry_run:
        cmd.append("--dry-run")
    if skip_analyze:
        cmd.append("--skip-analyze")
    if skip_enrich:
        cmd.append("--skip-enrich")
    if skip_document:
        cmd.append("--skip-document")
    if md_dir and md_dir.strip():
        cmd += ["--md-dir", md_dir.strip()]
    return cmd


def stream_subprocess(cmd: list, env: dict, output_queue: queue.Queue):
    merged_env = {**os.environ, **{k: v for k, v in env.items() if not k.startswith("_") and v}}
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(AGENT_DIR), env=merged_env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        for line in proc.stdout:
            output_queue.put(line)
        proc.wait()
        output_queue.put(None)
        output_queue.put(("__returncode__", proc.returncode))
    except Exception as e:
        output_queue.put(f"ERROR: {e}\n")
        output_queue.put(None)
        output_queue.put(("__returncode__", 1))


# ─── Dotenv loader (for Anthropic key in Generate from Analysis mode) ──────────

def _load_dotenv_into_env():
    env_path = AGENT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ─── Generate recipe from Analysis.md ─────────────────────────────────────────

GENERATION_SYSTEM = """\
You are a Workato integration engineer building recipes via the Workato REST API.
You read webMethods IS package analyses and produce complete, valid Workato recipe JSON objects.
Return ONLY a single JSON object — no markdown fences, no prose.
"""

GENERATION_PROMPT = """\
Read the following webMethods IS package analysis and generate a Workato recipe JSON
for the PRIMARY flow (the main callable/SOAP-triggered flow).
Skip batch or NACHA flat-file flows — those require custom implementation.

ANALYSIS DOCUMENT:
{md_content}

== REQUIRED OUTPUT FORMAT ==
Return a JSON object with exactly these 4 top-level keys:
  "name"        — descriptive recipe name
  "description" — paragraph describing the recipe, external systems, and gaps
  "code"        — trigger JSON object (see format below — NOT a string)
  "config"      — array of connection config entries (NOT a string)

== EXACT WORKATO STEP FORMATS — COPY THESE PATTERNS ==

CALLABLE RECIPE TRIGGER:
{{
  "number": 0, "keyword": "trigger", "provider": "workato", "name": "callable_recipe",
  "as": "callable_recipe", "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "dynamicPickListSelection": {{}}, "toggleCfg": {{}},
  "input": {{
    "http_method": "post",
    "request_url_suffix": "/<endpoint-slug>",
    "response_type": "dynamic",
    "input_fields_raw_schema": "[{{\"name\":\"field1\",\"type\":\"string\",\"optional\":false,\"label\":\"Field 1\"}}]"
  }},
  "block": [ <steps here> ]
}}

EACH LOOP — keyword "each" (NEVER "foreach"):
{{
  "number": 1, "keyword": "each", "as": "item_loop", "title": "For each item",
  "uuid": "any-uuid",
  "input": {{ "source": "[PILL: callable_recipe.items]" }},
  "block": [ <child steps> ]
}}

IF / ELSE — conditions INSIDE input (NEVER at step top level):
{{
  "number": 2, "keyword": "if", "title": "Check condition", "uuid": "any-uuid",
  "input": {{
    "type": "compound", "operand": "and",
    "conditions": [{{"operand": "equals", "lhs": "[PILL: item_loop.type]", "rhs": "Check"}}]
  }},
  "block": [
    {{ <true step> }},
    {{ "number": 4, "keyword": "else", "uuid": "any-uuid", "block": [ <false steps> ] }}
  ]
}}

HTTP POST ACTION — ONLY valid external service call:
{{
  "number": 3, "keyword": "action", "provider": "http", "name": "post",
  "as": "service_alias", "title": "Call ServiceName", "uuid": "any-uuid",
  "dynamicPickListSelection": {{}}, "toggleCfg": {{}},
  "input": {{
    "url": "PLACEHOLDER — obtain from SME: ServiceName",
    "content_type": "application/json",
    "payload": "{{\"field\": \"[PILL: callable_recipe.field]\"}}"
  }}
}}
IMPORTANT: payload must be a JSON-serialized STRING (in quotes), NEVER a raw JSON object.

RESCUE / ERROR HANDLING — rescue is a STANDALONE SIBLING at the end of the parent block (NOT wrapped in monitor):
[
  {{ <step 1 — normal processing> }},
  {{ <step 2 — normal processing> }},
  {{ "number": 8, "keyword": "rescue", "uuid": "any-uuid", "block": [ <catch steps> ] }}
]
CRITICAL: There is NO "monitor" keyword in Workato. "monitor" renders the entire block as ONE blank gray step.
Use only "rescue" as a standalone sibling as shown above — NEVER wrap steps in a "monitor" container.

CONFIG: {{"keyword": "application", "provider": "http", "account_id": null, "skip_validation": true}}

DATA PILLS: write "[PILL: alias.field_name]" — user wires actual pills in GUI after push.

== HARD RULES ==
1. ONLY valid action provider is "http". NEVER use "workato" as an action provider.
   There is NO workato/log_message, workato/set_variables, or any other workato/* action.
   These do NOT exist in Workato and will render as empty blank steps in the canvas.
2. Loop keyword is "each" — NEVER "foreach".
3. IF conditions: always inside input.conditions — never at step top level.
4. HTTP payload: always a JSON-serialized string — never a raw JSON object.
5. Every action step must have "dynamicPickListSelection": {{}} and "toggleCfg": {{}}.
6. Do NOT emit "extended_input_schema" or "extended_output_schema".
7. input_fields_raw_schema: ONLY use type "string", "integer", or "boolean" for fields.
   NEVER type "object" or "array" — Workato silently wipes the trigger schema for these types.
   Declare array/object fields as type "string" with a label note.
8. Every "if" step MUST have an "else" sibling as the LAST item in its block.
9. NEVER use "monitor" keyword — it does not exist in Workato and causes a blank recipe.
   Use "rescue" as a standalone sibling step instead (no monitor wrapper).
"""

def generate_recipe_from_analysis(md_content: str) -> dict:
    """
    Call Claude to generate a Workato recipe JSON from an Analysis.md.
    Returns the parsed recipe dict. Raises on API or parse failure.
    """
    _load_dotenv_into_env()
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed — run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set — add it to .env or set it in the environment"
        )

    client = anthropic.Anthropic(api_key=api_key)
    prompt = GENERATION_PROMPT.format(md_content=md_content)

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=GENERATION_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$",          "", raw, flags=re.MULTILINE)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise RuntimeError(f"Claude returned non-JSON output: {raw[:400]}")


# ─── Workato direct push ──────────────────────────────────────────────────────

def _strip_schema_hints(obj):
    """
    Recursively remove extended_input_schema / extended_output_schema from the
    recipe code tree. These are UI hint fields from ZIP exports that the Workato
    POST API does not accept and will return HTTP 500 on.
    """
    _STRIP = {"extended_input_schema", "extended_output_schema"}
    if isinstance(obj, dict):
        return {k: _strip_schema_hints(v) for k, v in obj.items() if k not in _STRIP}
    if isinstance(obj, list):
        return [_strip_schema_hints(i) for i in obj]
    return obj


def _normalize_workato_config(config: list) -> list:
    """
    Workato ZIP exports encode account_id as {"zip_name": ..., "name": ..., "folder": ""}.
    The REST API POST requires account_id to be a numeric ID or null.
    Replace any non-numeric account_id with null + skip_validation=true so the
    recipe creates cleanly and connections can be wired in the GUI.
    """
    out = []
    for entry in config:
        e = dict(entry)
        acct = e.get("account_id")
        if acct is not None and not isinstance(acct, (int, float)):
            e["account_id"] = None
            e["skip_validation"] = True
        out.append(e)
    return out


def _validate_recipe_code(code: dict) -> list:
    """Return list of human-readable issues that will cause blank steps in Workato."""
    issues = []

    def _walk(node, path=""):
        if isinstance(node, dict):
            kw   = node.get("keyword", "")
            prov = node.get("provider", "")
            name = node.get("name", "")

            if kw == "trigger" and prov == "workato" and name == "callable_recipe":
                inp = node.get("input", {})
                if "input_schema" in inp or "output_schema" in inp:
                    issues.append("Trigger uses wrong input keys ('input_schema'/'output_schema'). "
                                  "Must use 'input_fields_raw_schema'. Re-run migration to fix.")
                if "input_fields_raw_schema" not in inp:
                    issues.append("Trigger missing 'input_fields_raw_schema'. "
                                  "Workato will show 'Select an app and trigger event'.")
                # Check for type:"object" or type:"array" in schema — silently wipes trigger
                raw_schema = inp.get("input_fields_raw_schema", "")
                if isinstance(raw_schema, str) and ('"object"' in raw_schema or '"array"' in raw_schema):
                    issues.append("Trigger input_fields_raw_schema contains type 'object' or 'array'. "
                                  "Workato silently wipes the trigger input for these types — "
                                  "re-run migration to fix (all fields must be string/integer/boolean).")

            if kw == "action" and prov == "workato":
                issues.append(f"Step '{path}' uses provider='workato' action ('{name}'). "
                              "This provider does not exist for actions — will render as a blank step.")

            if kw == "foreach":
                issues.append(f"Step '{path}' uses keyword='foreach'. "
                              "Workato loop keyword is 'each' — 'foreach' is invalid.")

            if kw == "if" and "conditions" in node and "input" not in node:
                issues.append(f"Step '{path}' has IF conditions at the top level. "
                              "Must be inside input.conditions.")

            if kw == "action" and prov == "http":
                payload = node.get("input", {}).get("payload")
                if isinstance(payload, dict):
                    issues.append(f"Step '{path}' HTTP payload is a JSON object. "
                                  "Must be a JSON-serialized string.")

            if kw == "monitor":
                issues.append(f"Step '{path}' uses keyword 'monitor' which does not exist in Workato. "
                              "This renders the entire block as one blank gray step. "
                              "Use 'rescue' as a standalone sibling step instead.")

            for k, v in node.items():
                _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                _walk(item, f"{path}[{i}]")

    _walk(code)
    return issues


def push_recipe_workato(recipe_json: dict, token: str,
                        folder_id: str, name_override: str) -> dict:
    """
    POST a Workato recipe JSON directly to the platform.
    Returns {"id": <int|None>, "error": <str|None>, "warnings": [...]}.
    """
    name = name_override.strip() or recipe_json.get("name", "Untitled Recipe")

    raw_config      = recipe_json.get("config", [])
    clean_config    = _normalize_workato_config(raw_config)
    stripped_conns  = [
        e.get("provider", "?") for e, r in zip(clean_config, raw_config)
        if r.get("account_id") and not isinstance(r.get("account_id"), (int, float))
    ]

    raw_code   = recipe_json.get("code", {})
    clean_code = _strip_schema_hints(raw_code)

    # Pre-push validation — detect known broken patterns before sending to Workato
    val_issues = _validate_recipe_code(raw_code)

    payload = {
        "recipe": {
            "name":   name,
            "code":   json.dumps(clean_code),
            "config": json.dumps(clean_config),
        }
    }
    # Workato API requires a numeric folder ID — skip if it's a name/slug
    fid = folder_id.strip()
    if fid and fid.isdigit():
        payload["recipe"]["folder_id"] = fid

    body = json.dumps(payload).encode()
    req  = urllib.request.Request(
        "https://www.workato.com/api/recipes",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token.strip()}",
            "Content-Type":  "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
        resp = json.loads(raw)
        rid = resp.get("id")
        if rid:
            return {"id": rid, "error": None,
                    "warnings": stripped_conns, "validation": val_issues}
        # 200 but no id — surface full response for diagnosis
        return {"id": None, "error": f"No id in response: {raw.decode(errors='replace')[:600]}",
                "warnings": [], "validation": val_issues}
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        return {"id": None, "error": f"HTTP {e.code}: {err[:800]}",
                "warnings": [], "validation": val_issues}
    except Exception as ex:
        msg = str(ex) or repr(ex)
        return {"id": None, "error": msg, "warnings": [], "validation": val_issues}


# ─── Main UI ───────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="MigrAlte — AI-Powered Migration",
        page_icon="🔀",
        layout="wide",
    )

    inject_css()

    # ── Mode selector ────────────────────────────────────────────────────────
    mode = st.radio(
        "mode",
        ["🔄  Migrate Package", "📝  Generate from Analysis", "📤  Push Recipe JSON"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # ── Generate from Analysis mode (early return) ───────────────────────────
    if mode == "📝  Generate from Analysis":
        st.markdown(
            '<div class="platform-card"><div class="card-header-source">'
            '<span class="dot-source"></span>'
            ' Generate Workato Recipe from Analysis.md</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Upload an existing Analysis.md produced by a previous migration session. "
            "Claude reads it and generates a complete recipe JSON, then pushes it to Workato."
        )

        col_a, col_w = st.columns(2, gap="medium")

        with col_a:
            st.markdown('<div class="section-label">Analysis File</div>', unsafe_allow_html=True)
            analysis_file = st.file_uploader(
                "Upload Analysis.md",
                type=["md", "txt"],
                label_visibility="collapsed",
                key="gen_analysis_file",
            )
            if analysis_file:
                st.markdown(
                    f'<div class="pkg-ready">✓ {analysis_file.name} — ready</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
            gen_folder = st.text_input("Folder ID", key="gen_folder",
                                       placeholder="e.g. 31661117 — leave blank for root")
            gen_name   = st.text_input("Recipe name override", key="gen_name",
                                       placeholder="Leave blank to use name from generated JSON")

        with col_w:
            st.markdown(
                '<div class="card-header-target"><span class="dot-target"></span>'
                ' Target Platform</div>',
                unsafe_allow_html=True,
            )
            tgt_env = target_credential_form("workato")

        st.markdown('</div>', unsafe_allow_html=True)

        gen_col, _ = st.columns([1, 5])
        with gen_col:
            gen_clicked = st.button("✨  Generate & Push", type="primary",
                                    use_container_width=True, key="gen_btn")

        if gen_clicked:
            gen_token = tgt_env.get("WORKATO_API_TOKEN", "")
            if analysis_file is None:
                st.error("Please upload an Analysis.md file.")
            elif not gen_token.strip():
                st.error("Workato API token is required.")
            else:
                md_content = analysis_file.read().decode("utf-8", errors="ignore")

                gen_placeholder = st.empty()
                gen_placeholder.info("🤖 Claude is reading the analysis and generating the recipe…")

                try:
                    recipe_json = generate_recipe_from_analysis(md_content)
                except Exception as exc:
                    gen_placeholder.empty()
                    st.error(f"Generation failed: {exc}")
                    st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
                    return

                gen_placeholder.success(
                    f"✅ Recipe generated: **{recipe_json.get('name', '—')}** "
                    f"({len(recipe_json.get('code', {}).get('block', []))} top-level steps)"
                )

                # Show generated JSON for review
                with st.expander("Review generated recipe JSON before push"):
                    st.code(json.dumps(recipe_json, indent=2), language="json")

                # Download option
                st.download_button(
                    label="⬇  Download recipe JSON",
                    data=json.dumps(recipe_json, indent=2),
                    file_name=f"{recipe_json.get('name', 'recipe').lower().replace(' ', '_')}.recipe.json",
                    mime="application/json",
                )

                with st.spinner("Pushing to Workato…"):
                    result = push_recipe_workato(recipe_json, gen_token, gen_folder, gen_name)

                if result["id"]:
                    st.markdown(
                        f'<div class="badge-success">✅ Pushed — Recipe ID: <b>{result["id"]}</b></div>',
                        unsafe_allow_html=True,
                    )
                    st.info(f"Open in Workato: https://app.workato.com/recipes/{result['id']}")
                    if result.get("warnings"):
                        conns = ", ".join(f"`{c}`" for c in result["warnings"])
                        st.warning(f"Wire connections in GUI: {conns}")
                else:
                    st.markdown(
                        f'<div class="badge-error">❌ Push failed: {result["error"]}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
        return

    # ── Push Recipe JSON mode (early return) ─────────────────────────────────
    if mode == "📤  Push Recipe JSON":
        st.markdown(
            '<div class="platform-card"><div class="card-header-target">'
            '<span class="dot-target"></span> Push Workato Recipe JSON</div>',
            unsafe_allow_html=True,
        )

        col_j, col_w = st.columns(2, gap="medium")

        with col_j:
            st.markdown('<div class="section-label">Recipe File</div>', unsafe_allow_html=True)
            recipe_file = st.file_uploader(
                "Upload recipe JSON",
                type=["json"],
                label_visibility="collapsed",
                key="push_recipe_file",
            )
            if recipe_file:
                try:
                    preview = json.loads(recipe_file.read())
                    recipe_file.seek(0)
                    detected_name = preview.get("name", "—")
                    step_count    = len(preview.get("code", {}).get("block", []))
                    st.markdown(
                        f'<div class="pkg-ready">✓ {recipe_file.name}'
                        f'&nbsp; — &nbsp;<b>{detected_name}</b>'
                        f'&nbsp;({step_count} top-level steps)</div>',
                        unsafe_allow_html=True,
                    )
                except Exception:
                    st.warning("Could not preview JSON — will still attempt push.")

            st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
            push_folder = st.text_input("Folder ID", key="push_folder",
                                        placeholder="e.g. 31661117 — leave blank for root")
            push_name   = st.text_input("Recipe name override", key="push_name",
                                        placeholder="Leave blank to use name from JSON")

        with col_w:
            st.markdown(
                '<div class="card-header-target"><span class="dot-target"></span>'
                ' Target Platform</div>',
                unsafe_allow_html=True,
            )
            tgt_env = target_credential_form("workato")

        st.markdown('</div>', unsafe_allow_html=True)

        push_col, _ = st.columns([1, 5])
        with push_col:
            push_clicked = st.button("▶  Push Recipe", type="primary",
                                     use_container_width=True, key="push_btn")

        if push_clicked:
            push_token = tgt_env.get("WORKATO_API_TOKEN", "")
            if recipe_file is None:
                st.error("Please upload a recipe JSON file.")
            elif not push_token.strip():
                st.error("Workato API token is required.")
            else:
                try:
                    recipe_json = json.loads(recipe_file.read())
                except json.JSONDecodeError as exc:
                    st.error(f"Invalid JSON: {exc}")
                    st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
                    return

                with st.spinner("Pushing recipe to Workato…"):
                    result = push_recipe_workato(
                        recipe_json, push_token, push_folder, push_name
                    )

                if result["id"]:
                    st.markdown(
                        f'<div class="badge-success">✅ Recipe pushed — ID: <b>{result["id"]}</b></div>',
                        unsafe_allow_html=True,
                    )
                    st.info(f"Open in Workato: https://app.workato.com/recipes/{result['id']}")
                    if result.get("warnings"):
                        conns = ", ".join(f"`{c}`" for c in result["warnings"])
                        st.warning(
                            f"Connection(s) not wired (zip-export format — wire in GUI): {conns}"
                        )
                else:
                    st.markdown(
                        f'<div class="badge-error">❌ Push failed: {result["error"]}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
        return

    # ── Source / Target columns ──────────────────────────────────────────────
    col_src, col_tgt = st.columns(2, gap="medium")

    with col_src:
        st.markdown(
            '<div class="platform-card">'
            '<div class="card-header-source"><span class="dot-source"></span>'
            ' Source &nbsp;—&nbsp; webMethods IS Package</div>',
            unsafe_allow_html=True,
        )

        input_mode = st.radio(
            "Package source",
            ["📁  Upload from computer", "☁️  Google Drive"],
            horizontal=True,
            label_visibility="collapsed",
        )

        wm_local_file = None
        wm_drive_url  = ""

        if input_mode == "📁  Upload from computer":
            wm_local_file = st.file_uploader(
                "Upload webMethods package (.zip)",
                type=["zip"],
                label_visibility="visible",
            )
            if wm_local_file:
                sz = wm_local_file.size // 1024
                st.markdown(
                    f'<div class="pkg-ready">✓ {wm_local_file.name} &nbsp;({sz} KB) — ready</div>',
                    unsafe_allow_html=True,
                )
        else:
            wm_drive_url = st.text_input(
                "Google Drive share URL or File ID",
                placeholder="https://drive.google.com/file/d/…",
            )
            if wm_drive_url.strip():
                file_id = _gdrive_file_id(wm_drive_url.strip())
                if file_id:
                    st.markdown(
                        f'<div class="pkg-ready">✓ File ID: {file_id[:16]}… — will download on run</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning("Could not parse a Drive file ID from that URL.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tgt:
        st.markdown('<div class="platform-card"><div class="card-header-target"><span class="dot-target"></span> Target Platform</div>', unsafe_allow_html=True)
        target = st.selectbox("Platform", TARGET_PLATFORMS, format_func=lambda p: PLATFORM_LABELS[p], key="target_platform", label_visibility="collapsed")
        tgt_env = target_credential_form(target)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Options bar ──────────────────────────────────────────────────────────
    st.markdown('<div class="options-bar"><div class="section-label">Migration Options</div>', unsafe_allow_html=True)
    oc1, oc2, oc3 = st.columns([2, 2, 2])
    with oc1:
        project_name = st.text_input("Package / project name ✱", placeholder="e.g. GLDFundingEngine20080714",
                                     help="Used to name the spec file and destination folder. Defaults to the zip filename if blank.")
        dest_name    = st.text_input("Destination folder / project", placeholder="MIG_<project>")
    with oc2:
        md_dir = st.text_input("Markdown dir for doc appendix", placeholder="e.g. WebMethods/MD/")
    with oc3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        dry_run       = st.checkbox("Dry run", help="Generate artifacts without pushing to target")
        skip_analyze  = st.checkbox("Skip analyze", help="Re-use existing spec in migration-specs/")
        skip_enrich   = st.checkbox("Skip enrich", help="Skip AI enrichment (faster, lower quality)")
        skip_document = st.checkbox("Skip document", help="Skip Word design document generation")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Run button ───────────────────────────────────────────────────────────
    run_col, _ = st.columns([1, 4])
    with run_col:
        run_clicked = st.button("▶  Run Migration", type="primary", use_container_width=True)

    # ── Output ───────────────────────────────────────────────────────────────
    if run_clicked:
        # Validate source
        if wm_local_file is None and not wm_drive_url.strip():
            st.error("Please provide a webMethods package — upload a .zip or enter a Google Drive URL.")
            return

        # Prepare package on disk
        with st.spinner("Preparing webMethods package…"):
            try:
                source_dir = prepare_wm_package(wm_local_file, wm_drive_url, AGENT_DIR)
            except Exception as exc:
                st.error(f"Package preparation failed: {exc}")
                return

        if source_dir is None:
            st.error("No package source provided.")
            return

        # Auto-derive project name from zip filename if not specified
        effective_project = project_name.strip() if project_name.strip() else (
            Path(wm_local_file.name).stem if wm_local_file else ""
        )

        st.success(f"Package extracted → `{source_dir.relative_to(AGENT_DIR)}`   |   Project: **{effective_project or 'auto'}**")

        cmd = build_migrate_cmd(
            target, str(source_dir), dest_name, effective_project,
            dry_run, skip_analyze, skip_enrich, skip_document, md_dir,
        )
        combined_env = {**tgt_env}

        st.markdown("---")
        st.markdown('<div class="section-label">Migration Progress</div>', unsafe_allow_html=True)

        step_placeholder   = st.empty()
        status_placeholder = st.empty()
        # Live log — shows last 30 lines of subprocess output as they arrive
        log_placeholder    = st.empty()

        q: queue.Queue = queue.Queue()
        thread = threading.Thread(target=stream_subprocess, args=(cmd, combined_env, q), daemon=True)
        thread.start()

        current_phase:    str  = ""
        completed_phases: set  = set()
        last_detail:      str  = ""
        returncode = None
        all_output_lines: list = []
        _LOG_TAIL = 30   # lines visible in the live window

        step_placeholder.markdown(
            render_step_tracker(current_phase, completed_phases, "Starting..."),
            unsafe_allow_html=True,
        )

        def _render_live_log(lines: list) -> None:
            tail = lines[-_LOG_TAIL:] if len(lines) > _LOG_TAIL else lines
            escaped = "\n".join(
                l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                for l in tail
            )
            log_placeholder.markdown(
                f'<div class="log-wrap">{escaped}</div>',
                unsafe_allow_html=True,
            )

        while True:
            try:
                item = q.get(timeout=0.1)
            except queue.Empty:
                continue

            if item is None:
                break
            if isinstance(item, tuple) and item[0] == "__returncode__":
                returncode = item[1]
                continue

            line = item.rstrip()
            all_output_lines.append(line)

            # Detect phase transitions from [PHASE] markers
            m = _PHASE_RE.search(line)
            if m and m.group(1) in _PHASE_KEYS:
                new_phase = m.group(1)
                if current_phase and current_phase != new_phase:
                    completed_phases.add(current_phase)
                current_phase = new_phase
                last_detail = ""
            elif _is_detail_line(line):
                last_detail = line.strip()

            step_placeholder.markdown(
                render_step_tracker(current_phase, completed_phases, last_detail),
                unsafe_allow_html=True,
            )
            _render_live_log(all_output_lines)

        while not q.empty():
            item = q.get_nowait()
            if isinstance(item, tuple) and item[0] == "__returncode__":
                returncode = item[1]

        # Mark final phase as done
        if current_phase:
            completed_phases.add(current_phase)
        step_placeholder.markdown(
            render_step_tracker("", completed_phases, ""),
            unsafe_allow_html=True,
        )

        if returncode == 0:
            status_placeholder.markdown(
                '<div class="badge-success">✅ Migration completed successfully.</div>',
                unsafe_allow_html=True,
            )
        else:
            status_placeholder.markdown(
                f'<div class="badge-error">❌ Migration failed (exit {returncode}).</div>',
                unsafe_allow_html=True,
            )

        # Replace live log with a static collapsible version
        log_placeholder.empty()
        with st.expander("Full migration log", expanded=(returncode != 0)):
            st.code("\n".join(all_output_lines) if all_output_lines else "(no output)", language="bash")

        # Persist artifacts info so push buttons survive Streamlit rerenders
        import glob as _glob
        project_slug = (effective_project or "migration_project").lower().replace(" ", "_")
        recipe_files = sorted(
            Path(p) for p in _glob.glob(
                str(AGENT_DIR / "migration-specs" / f"{project_slug}_*_workato_recipe.json")
            )
        )
        st.session_state["_artifacts"] = {
            "project_slug":  project_slug,
            "workato_token": tgt_env.get("WORKATO_API_TOKEN", ""),
            "folder":        dest_name.strip() or f"MIG_{project_slug}",
            "recipe_paths":  [str(r) for r in recipe_files],
        }

    # ── Artifacts (rendered outside run_clicked so push buttons work) ─────────
    _arts = st.session_state.get("_artifacts")
    if _arts:
        import glob as _glob
        project_slug = _arts["project_slug"]
        wt_token     = _arts.get("workato_token", "")
        folder       = _arts.get("folder", "")

        # Re-discover recipe files in case new ones appeared
        recipe_files = sorted(
            Path(p) for p in _glob.glob(
                str(AGENT_DIR / "migration-specs" / f"{project_slug}_*_workato_recipe.json")
            )
        )
        spec_path = AGENT_DIR / "migration-specs" / f"{project_slug}.json"
        doc_path  = AGENT_DIR / "migration-specs" / f"{project_slug}_design_document.docx"

        tab_labels = []
        if recipe_files:
            for rf in recipe_files:
                svc = rf.stem.replace(f"{project_slug}_", "").replace("_workato_recipe", "")
                tab_labels.append(f"Recipe: {svc}")
        if spec_path.exists():
            tab_labels.append("Migration Spec")
        if doc_path.exists():
            tab_labels.append("Design Document")

        if tab_labels:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            if recipe_files:
                st.markdown(
                    f'<div class="badge-success">✅ {len(recipe_files)} recipe(s) ready</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            tabs = st.tabs(tab_labels)
            tab_idx = 0

            for rf in recipe_files:
                with tabs[tab_idx]:
                    with open(rf, encoding="utf-8") as f:
                        rjson = json.load(f)
                    rname  = rjson.get("name", rf.stem)
                    rsteps = len(rjson.get("code", {}).get("block", []))
                    folder_label = f"folder ID: `{folder}`" if folder.isdigit() else "folder: root (enter a numeric folder ID to target a specific folder)"
                    st.caption(f"**{rname}** | {rsteps} top-level steps | {folder_label}")
                    st.code(json.dumps(rjson, indent=2), language="json")

                    # Folder ID input — persisted per recipe stem so it survives rerenders
                    fid_key = f"_fid_{rf.stem}"
                    if fid_key not in st.session_state:
                        # Pre-fill if the stored folder is already numeric
                        st.session_state[fid_key] = folder if folder.isdigit() else ""

                    fid_col, dl_col, push_col = st.columns([3, 2, 2])
                    with fid_col:
                        push_folder_id = st.text_input(
                            "Workato folder ID (numeric, required)",
                            key=fid_key,
                            placeholder="e.g. 31661117  —  from the URL: app.workato.com/recipes?fid=...",
                        )

                    with dl_col:
                        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                        st.download_button(
                            label="Download JSON",
                            data=json.dumps(rjson, indent=2),
                            file_name=rf.name,
                            mime="application/json",
                            key=f"dl_{rf.stem}",
                        )
                    with push_col:
                        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                        if st.button("Push to Workato", key=f"push_{rf.stem}",
                                     type="primary", use_container_width=True):
                            # Extract digits from whatever the user pasted
                            # handles "31661117", "?fid=31661117", full URLs, spaces, etc.
                            _fid_digits = re.search(r'\d{5,}', push_folder_id)
                            extracted_fid = _fid_digits.group(0) if _fid_digits else ""
                            if not wt_token.strip():
                                st.error("Workato API token not found — enter it in the Target Platform field and rerun the migration first.")
                            elif not extracted_fid:
                                st.error("Paste the numeric folder ID (or the full Workato URL). Example: 31661117")
                            else:
                                # Pre-push validation — warn if recipe has known broken patterns
                                val_issues = _validate_recipe_code(rjson.get("code", {}))
                                if val_issues:
                                    st.warning(
                                        f"**Recipe format issues detected ({len(val_issues)}) — "
                                        "this recipe will likely show blank steps in Workato.** "
                                        "Re-run the migration to regenerate with the fixed generator. "
                                        "Pushing anyway...\n\n"
                                        + "\n\n".join(f"- {v}" for v in val_issues)
                                    )
                                # Clear previous result before new attempt
                                st.session_state.pop(f"_push_result_{rf.stem}", None)
                                with st.spinner(f"Pushing {rname}..."):
                                    res = push_recipe_workato(rjson, wt_token, extracted_fid, "")
                                if res["id"]:
                                    st.session_state[f"_push_result_{rf.stem}"] = {
                                        "ok": True, "id": res["id"],
                                        "warnings": res.get("warnings", []),
                                        "validation": res.get("validation", []),
                                    }
                                else:
                                    st.session_state[f"_push_result_{rf.stem}"] = {
                                        "ok": False, "error": res["error"],
                                        "validation": res.get("validation", []),
                                    }

                    pr = st.session_state.get(f"_push_result_{rf.stem}")
                    if pr:
                        if pr["ok"]:
                            st.success(f"Pushed — Recipe ID: **{pr['id']}**")
                            st.info(f"https://app.workato.com/recipes/{pr['id']}")
                            if pr.get("warnings"):
                                st.warning("Wire connections in GUI: " + ", ".join(pr["warnings"]))
                            if pr.get("validation"):
                                st.warning(
                                    "**Recipe pushed but may show blank steps** — "
                                    "re-run migration to regenerate:\n\n"
                                    + "\n\n".join(f"- {v}" for v in pr["validation"])
                                )
                        else:
                            st.error(f"Push failed: {pr['error']}")
                tab_idx += 1

            if spec_path.exists():
                with tabs[tab_idx]:
                    with open(spec_path) as f:
                        spec_content = f.read()
                    st.code(spec_content, language="json")
                tab_idx += 1

            if doc_path.exists():
                with tabs[tab_idx]:
                    with open(doc_path, "rb") as f:
                        doc_bytes = f.read()
                    st.download_button(
                        label="Download Design Document (.docx)",
                        data=doc_bytes,
                        file_name=doc_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                    )
                    st.caption(f"Generated: {doc_path.name}  ({len(doc_bytes) // 1024} KB)")

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="display:flex; align-items:center; gap:0.5rem; opacity:0.8;">
        TechStone LLC &nbsp;·&nbsp; MigrAlte
    </span>
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
