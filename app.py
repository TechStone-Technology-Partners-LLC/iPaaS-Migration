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
import uuid
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image

# ─── Constants ─────────────────────────────────────────────────────────────────

AGENT_DIR = Path(__file__).parent.resolve()

PLATFORM_LABELS = {
    "boomi":      "Boomi",
    "mulesoft":   "MuleSoft",
    "workato":    "Workato",
    "celigo":     "Celigo",
    "webmethods": "webMethods",
}
SOURCE_PLATFORMS = ["boomi", "mulesoft", "workato", "celigo", "webmethods"]
TARGET_PLATFORMS = ["boomi", "workato", "celigo", "webmethods"]

# DEMO MODE -- set back to False after the Workato demo. Hides every other
# target platform tile so the Target picker shows Workato only; nothing else
# about target handling changes (TARGET_PLATFORMS itself is untouched, so
# this is a one-line revert).
DEMO_WORKATO_ONLY_TARGET = True

# Since the target is pinned to Workato above, a Workato source would mean a
# Workato-to-Workato migration, which isn't a real scenario -- hide it from
# the Source picker too while the target demo restriction is on.
# SOURCE_PLATFORMS itself is untouched, so this is also a one-line revert.
DEMO_HIDE_WORKATO_SOURCE = True

# CLI flag migrate.py expects for a LIVE pull from each source platform.
# MuleSoft has no live pull — it's local-file-only, so it's absent here.
LIVE_FLAG_BY_SOURCE = {
    "boomi":      "--boomi-folder",
    "workato":    "--workato-folder",
    "celigo":     "--celigo-integration",
    "webmethods": "--wmio-project",
}

# MigrAIte design tokens — Vercel/Linear-inspired, built on TechStone's actual
# brand blue (#0023F8, sampled directly from logos/TechStone.png — not a
# guess). Dark is the primary/default palette; light mirrors the same
# structure so every CSS rule below (which only ever reads var(--token), not
# these dicts directly) re-themes automatically when inject_css() picks one.
C_DARK = {
    # Lightened ~6% toward white from the original near-black #0A0A0C scale --
    # that read as too dark/oppressive as a page background. Small absolute
    # RGB values mean even this modest a blend is clearly visible without
    # turning it into a grey theme.
    "bg":          "#19191B",
    "surface":     "#212124",
    "surface2":    "#2A2A2D",
    "border":      "#343438",
    "border_hi":   "#46464B",
    "ink":         "#F2F2F3",
    "ink_soft":    "#A3A3AB",
    "ink_faint":   "#6E6E76",
    "brand":       "#0023F8",   # true logo blue — solid fills only
    "accent":      "#5B74FF",   # brightened for AA text/icon contrast on dark
    "accent_tint": "rgba(91,116,255,0.12)",
    "good":        "#3ECF8E",
    "good_tint":   "rgba(62,207,142,0.12)",
    "warn":        "#F2B84B",
    "warn_tint":   "rgba(242,184,75,0.12)",
    # Brightened from #F2495C -- dropped below AA (3.52:1) against its own
    # tint once the surrounding surface2 got lighter above.
    "bad":         "#F6808D",
    "bad_tint":    "rgba(246,128,141,0.12)",
    # Wordmark colors sampled directly from logos/migrAIte.png (#1A3C37 /
    # #23B09D on white) -- those exact values would be near-invisible text-
    # on-dark-background, so lightened/brightened here for AA contrast on
    # the dark bg, same convention as `accent` above.
    "wordmark":        "#BFC8C7",
    "wordmark_accent": "#5AC4B6",
    # legacy aliases some older f-strings below still reference
    "navy":        "#0A0A0C",
    "blue":        "#5B74FF",
    "green":       "#3ECF8E",
    "teal":        "#5B74FF",
    "muted":       "#A3A3AB",
    "card":        "#131316",
}

C_LIGHT = {
    "bg":          "#FFFFFF",
    "surface":     "#F7F7F8",
    "surface2":    "#F0F0F2",
    "border":      "#E3E3E7",
    "border_hi":   "#CDCDD3",
    "ink":         "#17171A",
    "ink_soft":    "#52525B",
    "ink_faint":   "#86868F",
    "brand":       "#0023F8",   # same true logo blue in both themes
    "accent":      "#0023F8",   # solid brand blue reads better on white than the dark-mode-brightened tint
    "accent_tint": "rgba(0,35,248,0.08)",
    # Darkened from the original #1E8E5A/#9C6A08/#C62F45 -- those read fine
    # as text on plain white, but every actual use is as text ON TOP OF
    # their own *_tint background (status pills, done-step cards), which is
    # a much lower-contrast pairing (a pale wash of the same hue, not solid
    # white) and was failing AA there (as low as 3.42:1) even though it
    # looked fine on its own. Tint rgb values below match these new bases.
    "good":        "#187248",
    "good_tint":   "rgba(24,114,72,0.10)",
    "warn":        "#8C5F07",
    "warn_tint":   "rgba(140,95,7,0.10)",
    "bad":         "#B22A3E",
    "bad_tint":    "rgba(178,42,62,0.10)",
    # Exact colors from logos/migrAIte.png (#1A3C37 / #23B09D) -- the accent
    # is nudged slightly darker (#23B09D -> #1C8D7E) for the same reason as
    # good/warn/bad above: 2.7:1 against white is too low for permanent UI
    # text, even at this large/bold size.
    "wordmark":        "#1A3C37",
    "wordmark_accent": "#1C8D7E",
    "navy":        "#FFFFFF",
    "blue":        "#0023F8",
    "green":       "#187248",
    "teal":        "#0023F8",
    "muted":       "#52525B",
    "card":        "#F7F7F8",
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


def _logo_mark_b64() -> str:
    """
    Just the icon glyph (blue/grey pinwheel), cropped from the real logo —
    the full lockup's wordmark is solid black and unreadable on a dark page.
    Falls back to the full logo if the cropped asset isn't there.
    """
    mark_path = AGENT_DIR / "logos" / "TechStone_mark.png"
    if mark_path.exists():
        with open(mark_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return _logo_b64()


def _file_b64(*path_parts: str) -> str:
    p = AGENT_DIR.joinpath(*path_parts)
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def _flow_tile() -> tuple:
    """
    Build the repeating tile for the flowing migration arrow out of the real
    MigrAIte mark (logos/MigrAIte_mark.png) -- the three overlapping diamonds
    already read as a rightward chevron on their own, which is exactly why
    that mark was cropped from logos/migrAIte.png in the first place.

    The mark's own content fills almost its entire canvas edge-to-edge (no
    built-in margin), unlike the old hand-drawn SVG chevron whose viewBox had
    whitespace baked in -- tiling it as-is via background-repeat would merge
    repeats into one continuous smear instead of a train of distinct arrows.
    So this crops to the real diamond content, then pastes it onto a wider
    transparent canvas (content + a trailing gap 1.3x the content's own
    width) before base64-encoding. The gap is sized relative to the content
    rather than a fixed pixel value so it stays proportionate if the source
    mark ever changes -- widened from an initial 0.4x after the first pass
    packed too many repeats across a typical card width to read as distinct
    marks rather than a dense strip.

    Returns (base64_png, width, height) of the resulting tile -- the real
    aspect ratio, not a hand-guessed one, so callers can derive exact
    background-size / keyframe-distance CSS values that line up cleanly on
    each repeat instead of risking a visible seam. ("", 0, 0) if the asset is
    missing -- background-image then simply renders as a blank animated
    strip, a decorative texture rather than a hard dependency.
    """
    p = AGENT_DIR / "logos" / "MigrAIte_mark.png"
    if not p.exists():
        return "", 0, 0
    mark = Image.open(p).convert("RGBA")
    content = mark.crop(mark.getbbox())
    gap = round(content.width * 1.3)
    tile = Image.new("RGBA", (content.width + gap, content.height), (0, 0, 0, 0))
    tile.paste(content, (0, 0), content)
    buf = io.BytesIO()
    tile.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode(), tile.width, tile.height


def inject_css(theme: str = "dark"):
    C = C_LIGHT if theme == "light" else C_DARK
    suffix = "light" if theme == "light" else "dark"

    # Flowing migration arrow tile (the MigrAIte diamond mark, repeated) --
    # sized off the tile's own real aspect ratio so the background-size and
    # the keyframe travel distance line up exactly on every repeat.
    flow_tile_b64, flow_tile_w, flow_tile_h = _flow_tile()
    flow_aspect = (flow_tile_w / flow_tile_h) if flow_tile_h else 4.32
    flow_line_h = 26
    flow_line_w = round(flow_line_h * flow_aspect)
    flow_px_per_sec = 29  # same travel speed the old SVG chevron used
    flow_line_duration = round(flow_line_w / flow_px_per_sec, 2)

    # TechStone mark -- sits beside the "by TechStone" attribution, not the
    # product name (it's the parent company's mark, not MigrAIte's own). Its
    # own colors (brand blue + neutral grey) read fine on either background,
    # so it's the one asset that doesn't need a per-theme variant.
    techstone_b64 = _logo_mark_b64()
    techstone_img = (
        f'<img src="data:image/png;base64,{techstone_b64}" class="techstone-mark-img">'
        if techstone_b64 else ""
    )
    # KeyStone (AI vertical this product is built under) -- small icon next
    # to the "A KeyStone AI Solution" subtitle under the MigrAIte wordmark.
    # Unlike TechStone's mark, KeyStone's asset is near-white on dark / dark
    # teal on light, so it genuinely needs the matching per-theme file.
    keystone_b64 = _file_b64("logos", f"KeyStone_mark_{suffix}.png")
    keystone_img = (
        f'<img src="data:image/png;base64,{keystone_b64}" class="keystone-mark-img">'
        if keystone_b64 else ""
    )
    # MigrAIte's own mark -- cropped from the real logo provided and background-
    # removed (it's colored diamonds with no legitimate white content, so this
    # was a safe distance-based alpha removal, unlike Celigo's white-on-black
    # wordmark earlier). Falls back to the dashed placeholder box if the file
    # is ever missing, same convention as every other logo asset in this file.
    migraite_mark_b64 = _file_b64("logos", "MigrAIte_mark.png")
    migraite_mark_img = (
        f'<img src="data:image/png;base64,{migraite_mark_b64}" class="migraite-mark-img">'
        if migraite_mark_b64
        else '<div class="brand-placeholder-mark" title="MigrAIte logo placeholder"></div>'
    )
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Baloo+2:wght@600;700&display=swap');

/* ── Design tokens ──────────────────────────────────────────────────────── */
:root {{
    --bg:          {C["bg"]};
    --surface:     {C["surface"]};
    --surface-2:   {C["surface2"]};
    --border:      {C["border"]};
    --border-hi:   {C["border_hi"]};
    --ink:         {C["ink"]};
    --ink-soft:    {C["ink_soft"]};
    --ink-faint:   {C["ink_faint"]};
    --brand:       {C["brand"]};
    --accent:      {C["accent"]};
    --accent-tint: {C["accent_tint"]};
    --good:        {C["good"]};
    --good-tint:   {C["good_tint"]};
    --warn:        {C["warn"]};
    --warn-tint:   {C["warn_tint"]};
    --bad:         {C["bad"]};
    --bad-tint:    {C["bad_tint"]};
    --wordmark:        {C["wordmark"]};
    --wordmark-accent: {C["wordmark_accent"]};
    --radius:      8px;
    --radius-lg:   12px;
}}

/* ── Page base ──────────────────────────────────────────────────────────── */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--ink) !important;
}}
p, span, label, div {{ color: var(--ink); }}
::selection {{ background: var(--accent-tint); color: var(--ink); }}

/* Hide default Streamlit chrome */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stHeader"] {{ display: none; }}
[data-testid="stDecoration"] {{ display: none; }}

/* Streamlit reserves ~96px of top padding on its real block-container
   (data-testid="stMainBlockContainer" in this version -- ".main
   .block-container" below doesn't match it, which is why this rule alone
   never actually closed the gap left by hiding stHeader) for its native
   header bar. We hide that header entirely above, so this padding is now
   just a dead zone and needs its own override. */
[data-testid="stMainBlockContainer"],
.main .block-container {{
    padding-top: 1.25rem !important;
    padding-bottom: 6rem !important;
    max-width: min(1600px, 92vw) !important;
}}

[data-testid="stVerticalBlock"] {{ gap: 1.05rem; }}

/* ── Top bar ────────────────────────────────────────────────────────────────
   Brand hierarchy, left to right: MigrAIte (the product -- placeholder mark,
   no dedicated logo yet) > "A KeyStone AI Solution" (the AI vertical it's
   built under) > "by TechStone" with TechStone's own mark (the parent
   company, right-aligned attribution). */
.topbar {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding-bottom: 1.1rem;
    margin-bottom: 1.6rem;
    border-bottom: 1px solid var(--border);
}}
.topbar-left {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
}}
.brand-placeholder-mark {{
    width: 44px; height: 44px; flex-shrink: 0;
    border: 1.5px dashed var(--border-hi);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: var(--surface);
}}
.brand-placeholder-mark::before {{
    content: "";
    width: 15px; height: 15px;
    border-radius: 4px;
    background: var(--accent);
    opacity: 0.55;
}}
.migraite-mark-img {{
    height: 44px;
    width: auto;
    flex-shrink: 0;
}}
.topbar-title-group {{
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    line-height: 1.1;
}}
.topbar-title {{
    font-family: 'Baloo 2', 'Inter', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: var(--wordmark);
    letter-spacing: -0.3px;
    margin: 0;
    line-height: 1.1 !important;
}}
.topbar-title-accent {{ color: var(--wordmark-accent); }}
.topbar-subtitle {{
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.68rem;
    color: var(--ink-faint);
    letter-spacing: 0.1px;
}}
.keystone-mark-img {{ height: 11px; width: auto; flex-shrink: 0; opacity: 0.9; }}
.topbar-spacer {{ flex: 1; }}
.topbar-by {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.72rem;
    color: var(--ink-faint);
    text-align: right;
}}
.techstone-mark-img {{ height: 20px; width: auto; flex-shrink: 0; }}
.topbar-by b {{ color: var(--ink-soft); font-weight: 600; }}

/* ── Segmented control (mode selector + radio sub-choices) ─────────────── */
div[role="radiogroup"] {{
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 3px;
    width: fit-content;
}}
div[role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 6px !important;
    padding: 0.38rem 0.9rem !important;
    margin: 0 !important;
    transition: all 0.15s ease;
    cursor: pointer;
}}
div[role="radiogroup"] label:has(input:checked) {{
    background: var(--surface-2) !important;
    box-shadow: inset 0 0 0 1px var(--border-hi);
}}
div[role="radiogroup"] label > div:first-child {{ display: none; }}
div[role="radiogroup"] label p {{
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: var(--ink-soft) !important;
    white-space: nowrap !important;
}}
div[role="radiogroup"] label:has(input:checked) p {{
    color: var(--ink) !important;
    font-weight: 600 !important;
}}

/* ── Section labels ─────────────────────────────────────────────────────── */
.section-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 0.7rem;
}}

/* ── Bordered section cards ─────────────────────────────────────────────────
   st.container(border=True) applies its border/padding directly onto
   [data-testid="stVerticalBlock"] in this Streamlit version, rather than a
   separate wrapper element -- but that testid matches EVERY vertical block
   on the page (bordered or not), so a bare selector would wreck plain
   layout blocks everywhere. Scoped instead via :has() to just the blocks
   that start with one of this app's own card-header markers, each of which
   only ever appears as the first element inside one of the four real
   bordered containers (source/target platform cards, Migration Options,
   Migration Progress) -- see render_platform_card_header() and the
   .boxed-section-label usages in main(). */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-header-source),
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-header-target),
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .boxed-section-label) {{
    background: var(--surface) !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
    padding: 1.3rem 1.3rem 1rem 1.3rem !important;
    margin-top: 0.5rem;
    margin-bottom: 1.3rem;
}}
.card-header-source, .card-header-target {{
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--ink-soft);
    letter-spacing: 0.2px;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.55rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 0.68rem;
}}
.dot-source, .dot-target {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
    box-shadow: 0 0 0 3px var(--accent-tint);
}}
.card-header-logo {{
    height: 15px;
    width: auto;
    max-width: 60px;
    object-fit: contain;
    flex-shrink: 0;
}}

/* ── Platform picker tiles (icon-tile replacement for a plain selectbox) ── */
.platform-tile-logo {{
    width: 100%;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.4rem;
}}
.platform-tile-logo img {{
    /* Fixed px, not a % of the tile -- source has 5 tiles per row and target
       has 4, so at 80%-of-tile the exact same logo rendered noticeably
       larger on the (wider) target tiles. A fixed cap makes every logo the
       same size regardless of how many columns its row is divided into. */
    max-height: 28px;
    max-width: 92px;
    object-fit: contain;
}}
.platform-tile-logo-placeholder {{
    border: 1.5px dashed var(--border-hi);
    border-radius: 6px;
    background: var(--surface);
}}
/* The platform-picker's name label wraps (e.g. "webMethods") when the source
   row's 5 tiles make each column narrower than the target row's 4 -- same
   class of bug as the earlier Dark/Light toggle wrap. Scoped to just these
   buttons: Streamlit wraps the logo div and the button each in their own
   stElementContainer, so the real sibling relationship is one level up. */
[data-testid="stElementContainer"]:has(.platform-tile-logo)
    ~ [data-testid="stElementContainer"] [data-testid="stButton"] button p {{
    white-space: nowrap !important;
    font-size: 0.82rem !important;
}}

/* ── Inputs: text, selectbox ────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {{
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--ink) !important;
    font-size: 0.88rem !important;
}}
/* The actual bordered input box is this wrapper (input + password-reveal
   button both sit inside it) -- styling only the <input> leaves a white strip
   showing through wherever the button sits, since the input doesn't cover
   the full width of its root. */
[data-testid="stTextInputRootElement"] {{
    background: var(--surface-2) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}}
/* BaseWeb's own inner wrapper (input + reveal button) also hardcodes a
   white background independently of the root element above -- it has to
   be overridden separately or a sliver of white shows through next to
   the password-reveal button. */
[data-baseweb="base-input"] {{
    background: var(--surface-2) !important;
}}
[data-testid="stTextInputRootElement"]:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-tint) !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: var(--ink-faint) !important; }}
[data-testid="stTextInput"] input:focus,
div[data-baseweb="select"]:focus-within > div {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-tint) !important;
}}
[data-testid="stWidgetLabel"] p {{
    color: var(--ink-soft) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}
div[data-baseweb="popover"] li {{ background: var(--surface-2) !important; color: var(--ink) !important; }}
div[data-baseweb="popover"] li:hover {{ background: var(--border) !important; }}

/* ── Checkboxes ─────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] input {{ accent-color: var(--accent); }}
[data-testid="stCheckbox"] p {{ color: var(--ink-soft) !important; font-size: 0.85rem !important; }}

/* ── Password-reveal + inline help-tooltip icon buttons ─────────────────────
   Streamlit's own emotion-generated classes on this button out-specificity
   a plain attribute selector even with !important, so reset everything first. */
button[aria-label="Show password text"],
button[aria-label="Hide password text"] {{
    all: unset !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 0.6rem !important;
    color: var(--ink-faint) !important;
}}
button[aria-label="Show password text"] svg,
button[aria-label="Hide password text"] svg {{ fill: currentColor !important; }}
button[aria-label="Show password text"]:hover,
button[aria-label="Hide password text"]:hover {{ color: var(--ink) !important; }}
button[aria-label^="Help for"] {{ color: var(--ink-faint) !important; }}
button[aria-label^="Help for"]:hover {{ color: var(--accent) !important; }}
div[data-baseweb="tooltip"] {{
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--ink) !important;
}}
/* The outer [data-baseweb="tooltip"] positioning wrapper above renders
   correctly dark, but the actual visible card is an unlabeled CHILD div one
   level in (no data-testid/data-baseweb hook of its own) that independently
   hardcodes a near-white background -- without this, every tooltip popup
   looks like a blank/washed-out box since its text (ink-colored, set via the
   rule above) becomes nearly invisible against that light fill. */
div[data-baseweb="tooltip"] > div {{
    background: var(--surface-2) !important;
    border-radius: var(--radius) !important;
}}

/* ── Buttons ────────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {{
    border-radius: var(--radius) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
    background: var(--surface-2) !important;
    color: var(--ink) !important;
}}
[data-testid="stButton"] > button:hover {{
    border-color: var(--border-hi) !important;
    background: var(--border) !important;
}}
[data-testid="stButton"] > button[kind="primary"] {{
    background: var(--brand) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--brand) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
}}
/* The color above NEVER actually reached the visible text: Streamlit wraps
   every button's label in its own inner <p>, and the global `p, span,
   label, div {{ color: var(--ink) }}` rule (way above) matches that <p>
   directly -- a child's own directly-matched rule always wins over a
   parent's inherited color, !important or not, since !important only
   settles conflicts between rules that both apply to the SAME element, not
   inheritance. Net effect: every "primary" button (platform-tile selection,
   Run Migration, Generate & Push via AIRO, ...) was rendering var(--ink)
   text on the solid brand-blue fill -- invisible-looking near-black-on-blue
   in light mode specifically, since var(--ink) only happens to be
   near-white (and so look fine by accident) in dark mode. Fixing it
   requires re-asserting white with equal-or-greater specificity directly on
   the actual inner element, not just the <button>. */
[data-testid="stButton"] > button[kind="primary"] p,
[data-testid="stButton"] > button[kind="primary"] span,
[data-testid="stButton"] > button[kind="primary"] div {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{
    filter: brightness(1.12);
    box-shadow: 0 2px 10px var(--accent-tint) !important;
}}
[data-testid="stDownloadButton"] > button {{
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface-2) !important;
    color: var(--ink) !important;
    font-weight: 500 !important;
}}

/* ── File uploader ──────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {{
    background: var(--surface) !important;
    border: 1px dashed var(--border-hi) !important;
    border-radius: var(--radius-lg) !important;
}}
[data-testid="stFileUploader"] section:hover {{ border-color: var(--accent) !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {{ color: var(--ink-faint) !important; }}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {{
    all: unset !important;
    cursor: pointer !important;
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--ink) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.9rem !important;
    display: inline-flex !important;
    align-items: center !important;
}}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover {{
    border-color: var(--border-hi) !important;
}}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] * {{ color: inherit !important; }}

/* ── Alerts (success / error / warning / info) ─────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    border-left: 3px solid var(--ink-faint) !important;
}}
[data-testid="stAlert"] p {{ color: var(--ink) !important; font-size: 0.86rem !important; }}
div[data-testid="stAlertContentSuccess"] {{ color: var(--good) !important; }}
div[data-testid="stAlertContentError"]   {{ color: var(--bad) !important; }}
div[data-testid="stAlertContentWarning"] {{ color: var(--warn) !important; }}
div[data-testid="stAlertContentInfo"]    {{ color: var(--accent) !important; }}
[data-testid="stAlert"]:has(div[data-testid="stAlertContentSuccess"]) {{ border-left-color: var(--good) !important; background: var(--good-tint) !important; }}
[data-testid="stAlert"]:has(div[data-testid="stAlertContentError"])   {{ border-left-color: var(--bad) !important;  background: var(--bad-tint) !important; }}
[data-testid="stAlert"]:has(div[data-testid="stAlertContentWarning"]) {{ border-left-color: var(--warn) !important; background: var(--warn-tint) !important; }}
[data-testid="stAlert"]:has(div[data-testid="stAlertContentInfo"])    {{ border-left-color: var(--accent) !important; background: var(--accent-tint) !important; }}

/* ── Expander ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
}}
[data-testid="stExpander"] summary {{ color: var(--ink-soft) !important; font-size: 0.85rem !important; }}

/* ── Tabs (artifacts section) ───────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 1.4rem;
    border-bottom: 1px solid var(--border);
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--ink-faint) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0 0 0.6rem 0 !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{ color: var(--ink) !important; font-weight: 600 !important; }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background-color: var(--accent) !important; height: 2px !important; }}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{ display: none !important; }}

/* ── Code blocks ────────────────────────────────────────────────────────── */
[data-testid="stCodeBlock"] pre {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
}}
code, pre, [data-testid="stCodeBlock"] * {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ── Captions ───────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {{ color: var(--ink-faint) !important; font-size: 0.82rem !important; }}

/* ── Spinner ────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] p {{ color: var(--ink-soft) !important; }}

/* ── Status pills (pkg-ready, badges) ───────────────────────────────────── */
.pkg-ready, .badge-success, .badge-error {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid transparent;
}}
.pkg-ready::before, .badge-success::before, .badge-error::before {{
    content: ""; width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
}}
.pkg-ready {{
    background: var(--good-tint); color: var(--good); border-color: rgba(62,207,142,0.25);
}}
.pkg-ready::before {{ background: var(--good); }}
.badge-success {{
    background: var(--good-tint); color: var(--good); border-color: rgba(62,207,142,0.25);
    font-size: 0.86rem; padding: 0.55rem 1.1rem;
}}
.badge-success::before {{ background: var(--good); }}
.badge-error {{
    background: var(--bad-tint); color: var(--bad); border-color: rgba(242,73,92,0.25);
    font-size: 0.86rem; padding: 0.55rem 1.1rem;
}}
.badge-error::before {{ background: var(--bad); }}

/* ── Output log (terminal panel) ────────────────────────────────────────── */
/* This panel is deliberately a fixed-black terminal in BOTH themes (same
   convention as a code editor's integrated console) -- its own colors are
   literal, not theme tokens, since var(--ink-soft)/var(--border-hi) flip to
   dark greys in light mode and would be unreadable against this always-black
   background. */
.log-wrap {{
    background: #000000;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2.2rem 1.3rem 1.3rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #B7B7BE;
    line-height: 1.65;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
    position: relative;
}}
.log-wrap::before {{
    content: "● ● ●";
    position: absolute;
    top: 0.8rem; left: 1.1rem;
    font-size: 0.6rem;
    letter-spacing: 3px;
    color: #4A4A4F;
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Flowing migration arrow (source -> target, shown while a run is live) ── */
.flow-track {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin: 0.2rem 0 1.2rem;
}}
.flow-endpoint {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--ink-soft);
    white-space: nowrap;
    flex-shrink: 0;
}}
.flow-endpoint img {{ height: 18px; width: auto; }}
.flow-line {{
    flex: 1;
    height: {flow_line_h}px;
    background-image: url("data:image/png;base64,{flow_tile_b64}");
    background-repeat: repeat-x;
    background-position: center left;
    background-size: {flow_line_w}px {flow_line_h}px;
    animation: flow-move {flow_line_duration}s linear infinite;
}}
@keyframes flow-move {{
    from {{ background-position: 0 center; }}
    to   {{ background-position: {flow_line_w}px center; }}
}}

/* ── Fixed action bar ───────────────────────────────────────────────────────
   Different source platforms show wildly different field counts (MuleSoft:
   1 field; Boomi live-pull: 6+), which used to push the primary button up
   and down the page as the user just browsed platform options -- a
   professional tool's primary action doesn't relocate itself depending on
   unrelated form state. position:sticky was tried first but only engages
   once the page is scrolled far enough for the element to reach the
   viewport edge -- with no scrolling (just switching platforms) it still
   sits in normal flow and visibly jumps, confirmed live. position:fixed
   actually decouples it from document flow entirely, so it's genuinely
   anchored to the same screen position regardless of scroll or content
   height. Same :has()-scoping trick as the bordered section cards above
   (no separate wrapper element exists to target directly, so an invisible
   marker that's always the first child identifies which stVerticalBlock to
   pin) -- padding-bottom on the block-container (below) reserves room so
   this fixed bar never covers the last field(s) of the form above it.

   The bar itself spans the full viewport width (so its background/border
   reads as real app chrome, not a box floating mid-page), but the button
   inside it must still line up under the form above -- a first attempt
   used a hardcoded calc(50vw - 600px) offset assuming a fixed 1200px
   content width, which only matched by coincidence at one viewport size
   and was visibly misaligned at others (confirmed live: ~120px off at a
   2533px-wide window). Fixed by giving the INNER row the exact same
   max-width + auto-centering as the page's own content area instead of
   guessing an offset, so the two can never drift apart regardless of
   viewport width. */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .sticky-action-marker) {{
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg);
    border-top: 1px solid var(--border);
    box-shadow: 0 -4px 16px rgba(0,0,0,0.25);
    z-index: 999;
}}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .sticky-action-marker)
    > [data-testid="stElementContainer"]:has(.sticky-action-marker) ~ [data-testid="stLayoutWrapper"] {{
    /* Streamlit's own stMainBlockContainer carries a built-in 80px left/right
       padding we never overrode (only touched top/bottom/max-width earlier) --
       position:fixed drops out of that ancestor's box model entirely, so this
       replica has to restate the same 80px itself or it silently drifts from
       the real content's left edge (confirmed live: exactly 80px off at every
       viewport width tested, not a proportional error). */
    max-width: min(1600px, 92vw);
    margin: 0 auto;
    padding: 1rem 80px 1.2rem;
    box-sizing: border-box;
}}

/* ── Migration lock (blocks clicks during a run, changes nothing visually) ──
   pointer-events is inherited, so setting it on the single top-level page
   container (stMainBlockContainer) disables click/hover on every descendant
   in one place -- no opacity change, no graying, nothing hidden, just
   un-clickable. Deliberately NOT styled to look "disabled": the point is to
   keep the whole form legible for walking someone through the UI live while
   a migration runs, not to visually lock it down. The cursor change is the
   only hint anything is different. */
[data-testid="stMainBlockContainer"]:has(.migration-lock-marker) {{
    pointer-events: none;
    cursor: not-allowed;
}}

/* ── Step tracker (pipeline) ────────────────────────────────────────────── */
.step-tracker {{
    display: flex;
    gap: 0;
    margin: 0.9rem 0 0.6rem 0;
    align-items: stretch;
}}
.step-card {{
    flex: 1;
    border-radius: var(--radius);
    padding: 0.85rem 0.6rem 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    min-width: 0;
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    transition: all 0.2s ease;
}}
.step-card + .step-card {{ margin-left: 10px; }}
.step-card + .step-card::before {{
    content: "";
    position: absolute;
    left: -10px; top: 50%; width: 10px; height: 1px;
    background: var(--border);
}}
.step-pending {{ opacity: 0.55; }}
.step-active  {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-tint); }}
.step-done    {{ border-color: rgba(62,207,142,0.3); background: var(--good-tint); }}
.step-icon {{
    width: 20px; height: 20px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem;
    font-weight: 700;
    line-height: 1;
    background: var(--surface-2);
    color: var(--ink-faint);
}}
.step-active .step-icon {{
    background: var(--accent); color: #fff; animation: step-pulse 1.4s ease-in-out infinite;
}}
.step-done .step-icon {{ background: var(--good); color: #06150F; }}
.step-label {{ font-size: 0.74rem; font-weight: 600; text-align: center; color: var(--ink-soft); }}
.step-active .step-label {{ color: var(--ink); }}
.step-done .step-label {{ color: var(--good); }}
.step-desc {{ font-size: 0.66rem; text-align: center; line-height: 1.3; color: var(--ink-faint); }}
@keyframes step-pulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 var(--accent-tint); }}
    50%       {{ box-shadow: 0 0 0 5px var(--accent-tint); }}
}}
.step-detail {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.5rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: var(--ink-soft);
    margin-top: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}}

/* ── Footer ─────────────────────────────────────────────────────────────── */
.migralte-footer {{
    border-top: 1px solid var(--border);
    padding: 1.1rem 0 0;
    margin-top: 2.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--ink-faint);
    font-size: 0.78rem;
}}
.footer-tagline strong {{ color: var(--ink-soft); font-weight: 600; }}
</style>

<div class="topbar">
    <div class="topbar-left">
        {migraite_mark_img}
        <div class="topbar-title-group">
            <p class="topbar-title">migr<span class="topbar-title-accent">AI</span>te</p>
            <span class="topbar-subtitle">{keystone_img} A KeyStone AI Solution</span>
        </div>
    </div>
    <div class="topbar-spacer"></div>
    <div class="topbar-by">{techstone_img}<span>by <b>TechStone</b></span></div>
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


def _cleanup_old_wm_uploads(upload_root: Path, keep: Path) -> None:
    """Best-effort removal of previous wm_upload run directories. Never raises:
    this repo lives under OneDrive, whose sync client can transiently hold a
    lock on files/folders it's still scanning or uploading from a prior run --
    a stuck leftover just gets skipped and retried on a future call instead of
    blocking the current upload."""
    for child in upload_root.iterdir():
        if child == keep or not child.is_dir():
            continue
        shutil.rmtree(child, ignore_errors=True)


def prepare_wm_package(uploaded_file, drive_url: str, base_dir: Path) -> Path | None:
    """
    Resolve the webMethods package source directory.
    Returns the path to the extracted directory, or None if no source provided.
    Raises on download/extraction errors.

    Each call extracts into a fresh, uniquely-named subdirectory instead of
    clearing and reusing one fixed path -- reusing a fixed path required an
    rmtree before every extract, which intermittently failed with "WinError 5
    Access is denied" on a prior run's files because OneDrive (this repo's
    working directory is under OneDrive\\Desktop) can still be syncing them.
    """
    upload_root = base_dir / WM_UPLOAD_DIR
    upload_root.mkdir(parents=True, exist_ok=True)

    run_dir = upload_root / uuid.uuid4().hex[:12]
    run_dir.mkdir()

    zip_path = run_dir / "package.zip"

    if uploaded_file is not None:
        zip_path.write_bytes(uploaded_file.read())
    elif drive_url and drive_url.strip():
        file_id = _gdrive_file_id(drive_url.strip())
        if not file_id:
            raise ValueError(f"Could not extract a Google Drive file ID from: {drive_url}")
        _download_gdrive(file_id, zip_path)
    else:
        return None

    extract_dir = run_dir / "extracted"
    extract_dir.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    _cleanup_old_wm_uploads(upload_root, keep=run_dir)

    return extract_dir


def render_platform_card_header(kind: str, state_key: str, options: list, label: str) -> None:
    """
    Renders the header row (logo + name) for a platform card -- must be
    called as the first thing inside an already-open st.container(border=True)
    so the rest of the card's widgets land below it as real children of the
    same bordered box. Echoes whatever is currently selected in `state_key`:
    once you pick a platform, the header swaps its generic dot for that
    platform's actual logo and the label becomes
    "<Source/Target> Platform -- <Name>". Falls back to the generic dot when
    no logo file exists yet for the selected platform.

    Earlier versions of this also tinted the card's own border with a color
    sampled from the logo, done by opening a raw HTML <div class="platform-card">
    and relying on a later st.markdown('</div>') to close it -- that never
    actually worked: Streamlit renders each st.markdown() call as its own
    self-contained DOM fragment, so the "closing" div was an orphaned sibling,
    not a real parent wrapping the widgets in between (confirmed by inspecting
    the live DOM -- the div's innerHTML ended right after the header, despite
    looking like a bordered card around everything in screenshots). A real
    st.container(border=True) at the call site replaces that broken pattern
    with Streamlit's own genuine bordered container; the per-selection border
    tint is dropped since there's no supported way to pass a custom color to
    st.container() itself.
    """
    selected = st.session_state.get(state_key, options[0])
    logo_b64 = _file_b64("logos", "connectors", f"{selected}.png")
    icon_html = (
        f'<img src="data:image/png;base64,{logo_b64}" class="card-header-logo">'
        if logo_b64 else f'<span class="dot-{kind}"></span>'
    )
    st.markdown(
        f'<div class="card-header-{kind}">{icon_html} {label} Platform — {PLATFORM_LABELS[selected]}</div>',
        unsafe_allow_html=True,
    )


def render_flow_track(source_key: str, target_key: str) -> str:
    """
    A flowing-dashes arrow between the source and target platform badges --
    shown in the Migration Progress section while a run is actually in
    flight, as a visual confirmation of "data is moving from here to there".
    The motion is a plain CSS background-position keyframe animation (see
    .flow-line in inject_css), not JS -- same approach as every other
    animated element in this app (the active step tracker's pulse, etc).
    """
    src_logo = _file_b64("logos", "connectors", f"{source_key}.png")
    tgt_logo = _file_b64("logos", "connectors", f"{target_key}.png")
    src_icon = f'<img src="data:image/png;base64,{src_logo}">' if src_logo else ""
    tgt_icon = f'<img src="data:image/png;base64,{tgt_logo}">' if tgt_logo else ""
    return (
        '<div class="flow-track">'
        f'<div class="flow-endpoint">{src_icon} {PLATFORM_LABELS[source_key]}</div>'
        '<div class="flow-line"></div>'
        f'<div class="flow-endpoint">{tgt_icon} {PLATFORM_LABELS[target_key]}</div>'
        '</div>'
    )


def platform_picker(options: list, state_key: str) -> str:
    """
    Icon-tile platform picker -- replaces a plain st.selectbox so each option
    can show the connector's real logo alongside its name. Neither
    st.selectbox nor st.radio can embed an image inside their own rendered
    option label (both render as plain text, same limitation already hit
    styling the tooltip/input internals elsewhere in this file), so this
    lays the logo and the button out as separate elements in the same
    column instead. Looks for a real asset at
    logos/connectors/<platform-key>.png; until one exists for a given
    platform, shows a plain neutral placeholder (not a guessed brand color --
    a wrong color read as more wrong than no color at all) in the exact same
    slot, so dropping the real file in later needs no code change, same
    pattern as logos/TechStone_mark.png / logos/KeyStone_mark_dark.png.
    Selection persists via session_state; the active tile is shown with a
    primary (brand-blue) button so no extra CSS hook is needed to mark
    "currently selected" -- Streamlit's own button `type` already does it
    natively.
    """
    if state_key not in st.session_state:
        st.session_state[state_key] = options[0]
    cols = st.columns(len(options))
    for col, key in zip(cols, options):
        with col:
            logo_b64 = _file_b64("logos", "connectors", f"{key}.png")
            if logo_b64:
                st.markdown(
                    f'<div class="platform-tile-logo">'
                    f'<img src="data:image/png;base64,{logo_b64}"></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="platform-tile-logo platform-tile-logo-placeholder"></div>',
                    unsafe_allow_html=True,
                )
            is_selected = st.session_state[state_key] == key
            if st.button(
                PLATFORM_LABELS[key], key=f"{state_key}_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                # A plain state update isn't enough: within THIS SAME script
                # pass, buttons rendered earlier in the loop already computed
                # their own `type=` from the OLD session_state value, so they'd
                # stay visually stale for one run. Force the next rerun so
                # every tile's highlight reflects the new selection immediately.
                st.session_state[state_key] = key
                st.rerun()
    return st.session_state[state_key]


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


def source_credential_form(platform: str) -> dict:
    """
    Credential fields for a LIVE pull from the given source platform. These are
    session-only: merged into the migrate.py subprocess's environment for this
    run (see stream_subprocess) and never written to .env or disk. Platforms
    with no live-pull path (MuleSoft) return an empty dict — nothing to collect.
    """
    env = {}
    if platform == "boomi":
        env["BOOMI_API_URL"]    = st.text_input("API URL", value="https://api.boomi.com/api/rest/v1", key="src_boomi_url")
        env["BOOMI_ACCOUNT_ID"] = st.text_input("Account ID", key="src_boomi_account")
        env["BOOMI_USERNAME"]   = st.text_input("Username (email)", key="src_boomi_user")
        env["BOOMI_API_TOKEN"]  = st.text_input("API Token", type="password", key="src_boomi_token")
        env["BOOMI_VERIFY_SSL"] = "true"
    elif platform == "workato":
        env["WORKATO_API_TOKEN"] = st.text_input("API Token", type="password", key="src_wt_token")
        env["WORKATO_EMAIL"]     = st.text_input("Account email", key="src_wt_email")
    elif platform == "celigo":
        env["CELIGO_API_TOKEN"] = st.text_input("API Token", type="password", key="src_cel_token")
    elif platform == "webmethods":
        env["WMIO_TENANT_URL"] = st.text_input("Tenant URL", placeholder="https://mycompany.int-aws-us.webmethods.io", key="src_wmio_url")
        env["WMIO_USERNAME"]   = st.text_input("Username", key="src_wmio_user")
        env["WMIO_PASSWORD"]   = st.text_input("Password", type="password", key="src_wmio_pass")
    return env


# ─── Migration runner ──────────────────────────────────────────────────────────

def build_migrate_cmd(source: str, target: str, source_dir: str, live_ref: str,
                      dest_name: str, project: str, dry_run: bool,
                      skip_analyze: bool, skip_enrich: bool,
                      skip_document: bool, md_dir: str, use_airo: bool = False,
                      boomi_process: str = "", skip_generate: bool = False) -> list:
    cmd = [
        sys.executable, str(AGENT_DIR / "migrate.py"),
        "--from", source,
        "--to", target,
    ]
    if live_ref:
        # Live pull from the source platform's API — e.g. --boomi-folder,
        # --workato-folder, --celigo-integration, --wmio-project.
        cmd += [LIVE_FLAG_BY_SOURCE.get(source, "--source-dir"), live_ref]
        if source == "boomi" and boomi_process.strip():
            cmd += ["--boomi-process", boomi_process.strip()]
    elif source_dir:
        cmd += ["--source-dir", source_dir]
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
    if use_airo:
        cmd.append("--use-airo")
    if skip_generate:
        # Stop before GENERATE/AIRO is ever invoked -- the real offline
        # review point, since AIRO itself has no staged/dry-run mode (see
        # generate_workato_airo.py's module docstring). Used when Dry run +
        # Build via AIRO are both checked: produce the spec for approval,
        # then a separate "Generate & Push" action runs the AIRO build for
        # real once the user confirms.
        cmd.append("--skip-generate")
    return cmd


def _escape_log_html(lines: list, tail_n: int = 30) -> str:
    """HTML-escape the last `tail_n` lines of subprocess output for display
    inside a <div class="log-wrap">. Shared by every live-log view in this
    app (the main migration run, and the AIRO approval-gate build below)."""
    tail = lines[-tail_n:] if len(lines) > tail_n else lines
    return "\n".join(
        l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for l in tail
    )


def stream_subprocess(cmd: list, env: dict, output_queue: queue.Queue):
    merged_env = {**os.environ, **{k: v for k, v in env.items() if not k.startswith("_") and v}}
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(AGENT_DIR), env=merged_env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
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


# ─── Locked migration runner ───────────────────────────────────────────────────

def _run_locked_migration():
    """
    Runs the actual blocking migrate.py subprocess and renders its live
    progress -- called only while st.session_state["_migration_running"] is
    True, AFTER the full page (theme toggle, mode selector, platform
    pickers, options, Run Migration button) has already rendered normally
    above it. The form stays fully visible and readable -- useful for
    walking someone through the UI while a run is live -- but a CSS rule
    keyed off the ".migration-lock-marker" div main() inserts at the very
    top makes the whole page body pointer-events:none for as long as this
    flag is set, so nothing on it can actually be clicked.

    That protects against a real bug: any widget interaction during a
    blocking script run makes Streamlit cancel that run outright (its
    cooperative-cancellation model checks for a pending rerun at every
    delta-producing call, e.g. each st.markdown() in the polling loop
    below) -- which is exactly what "losing the session mid-migration" was.
    `disabled=True` per-widget doesn't scale to "every widget on the page,"
    and still wouldn't help mid-run anyway -- a widget's rendered appearance
    is fixed the moment it's called, and this function blocks for minutes
    inside one call, so nothing rendered earlier in the same run could be
    told to look different now regardless. One page-level CSS rule, applied
    before any of it renders, sidesteps both problems at once. See also the
    AIRO approval button's "_airo_gen_running" flag for the same underlying
    risk, addressed on a smaller scale (that one button only).

    Reads the parameters the "Run Migration" click captured into
    st.session_state["_pending_run"] (the click itself only does cheap
    validation/resolution, then stashes params and reruns -- see main() --
    rather than starting this blocking work inline, since at that point the
    lock marker hasn't been drawn yet for THIS run; the rerun it triggers is
    what gets a script execution where the marker renders first).
    """
    pending = st.session_state.get("_pending_run") or {}
    cmd            = pending["cmd"]
    combined_env   = pending["combined_env"]
    source         = pending["source"]
    target         = pending["target"]
    effective_project   = pending["effective_project"]
    dest_name          = pending["dest_name"]
    tgt_env            = pending["tgt_env"]
    airo_approval_gate = pending["airo_approval_gate"]

    progress_card = st.container(border=True)
    progress_card.__enter__()
    st.markdown('<div class="section-label boxed-section-label">Migration Progress</div>', unsafe_allow_html=True)
    st.markdown(render_flow_track(source, target), unsafe_allow_html=True)

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
        log_placeholder.markdown(
            f'<div class="log-wrap">{_escape_log_html(lines, _LOG_TAIL)}</div>',
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
            '<div class="badge-success">Migration completed successfully.</div>',
            unsafe_allow_html=True,
        )
    else:
        status_placeholder.markdown(
            f'<div class="badge-error">Migration failed (exit {returncode}).</div>',
            unsafe_allow_html=True,
        )

    # Replace live log with a static collapsible version
    log_placeholder.empty()
    with st.expander("Full migration log", expanded=(returncode != 0)):
        st.code("\n".join(all_output_lines) if all_output_lines else "(no output)", language="bash")

    progress_card.__exit__(None, None, None)

    # Persist artifacts info so push buttons survive Streamlit rerenders
    import glob as _glob
    project_slug = (effective_project or "migration_project").lower().replace(" ", "_")
    recipe_files = sorted(
        Path(p) for p in _glob.glob(
            str(AGENT_DIR / "migration-specs" / f"{project_slug}_*_workato_recipe.json")
        )
    )
    airo_output_path = AGENT_DIR / "migration-specs" / f"{project_slug}_workato_airo_output.json"
    st.session_state["_artifacts"] = {
        "project_slug":  project_slug,
        "workato_token": tgt_env.get("WORKATO_API_TOKEN", ""),
        "folder":        dest_name.strip() or f"MIG_{project_slug}",
        "recipe_paths":  [str(r) for r in recipe_files],
        "airo_output":   str(airo_output_path) if airo_output_path.exists() else "",
        # True when this run stopped at --skip-generate (Dry run + Build
        # via AIRO both checked) -- the spec is ready but AIRO hasn't
        # been invoked yet, pending the user's explicit approval below.
        "awaiting_airo_approval": airo_approval_gate and returncode == 0,
    }

    # Unlock the page and land back on the normal interactive view, which
    # will now show the results (tabs, approval gate, etc.) via _artifacts.
    st.session_state["_migration_running"] = False
    st.session_state.pop("_pending_run", None)
    st.rerun()


# ─── Main UI ───────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="MigrAlte — AI-Powered Migration",
        page_icon="🔀",
        layout="wide",
    )

    # While a migration is actively running, the whole page still renders
    # normally -- platform pickers, options, theme toggle, all of it stays
    # visible and fully readable (useful for walking someone through the UI
    # while a run is live) -- but none of it can be CLICKED. A click on any
    # widget during a blocking script run makes Streamlit cancel that run
    # outright (its cooperative-cancellation model checks for a pending
    # rerun at every delta-producing call, e.g. each st.markdown() in the
    # polling loop below), which is exactly what "losing the session
    # mid-migration" was. `disabled=True` only protects one widget at a
    # time and has to be threaded through every single call site; this
    # marker + the matching CSS rule (search .migration-lock-marker)
    # disables pointer-events on the ENTIRE page body in one place instead,
    # so nothing anywhere can register a click while this is present --
    # without hiding or graying out a single thing.
    is_migration_running = st.session_state.get("_migration_running", False)
    if is_migration_running:
        st.markdown('<div class="migration-lock-marker"></div>', unsafe_allow_html=True)

    # Theme must be resolved before inject_css() builds the stylesheet. This
    # renders as its own slim row above the branded header rather than trying
    # to splice a live widget into the topbar's static HTML below -- a
    # markdown-injected <div> never actually wraps separately-rendered
    # widgets in Streamlit's DOM (confirmed by inspecting the live DOM; see
    # render_platform_card_header()'s docstring for the full story and the
    # st.container(border=True) fix used for the bordered sections), so
    # keeping the toggle as its own real sibling element is the robust path.
    _theme_spacer, _theme_toggle_col = st.columns([10, 2])
    with _theme_toggle_col:
        theme_label = st.radio(
            "Theme", ["Dark", "Light"], horizontal=True,
            label_visibility="collapsed", key="theme_radio",
        )
    theme = "light" if theme_label == "Light" else "dark"

    inject_css(theme)

    # ── Mode selector ────────────────────────────────────────────────────────
    mode = st.radio(
        "mode",
        ["Migrate Package", "Generate from Analysis", "Push Recipe JSON"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # ── Generate from Analysis mode (early return) ───────────────────────────
    if mode == "Generate from Analysis":
        gen_card = st.container(border=True)
        gen_card.__enter__()
        st.markdown(
            '<div class="card-header-source">'
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
                    f'<div class="pkg-ready">{analysis_file.name} — ready</div>',
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

        gen_card.__exit__(None, None, None)

        gen_bar = st.container()
        gen_bar.__enter__()
        st.markdown('<div class="sticky-action-marker"></div>', unsafe_allow_html=True)
        gen_col, _ = st.columns([1, 5])
        with gen_col:
            gen_clicked = st.button("Generate & Push", type="primary",
                                    use_container_width=True, key="gen_btn")
        gen_bar.__exit__(None, None, None)

        if gen_clicked:
            gen_token = tgt_env.get("WORKATO_API_TOKEN", "")
            if analysis_file is None:
                st.error("Please upload an Analysis.md file.")
            elif not gen_token.strip():
                st.error("Workato API token is required.")
            else:
                md_content = analysis_file.read().decode("utf-8", errors="ignore")

                gen_placeholder = st.empty()
                gen_placeholder.info("Claude is reading the analysis and generating the recipe…")

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
                    f"Recipe generated: **{recipe_json.get('name', '—')}** "
                    f"({len(recipe_json.get('code', {}).get('block', []))} top-level steps)"
                )

                # Show generated JSON for review
                with st.expander("Review generated recipe JSON before push"):
                    st.code(json.dumps(recipe_json, indent=2), language="json")

                # Download option
                st.download_button(
                    label="Download recipe JSON",
                    data=json.dumps(recipe_json, indent=2),
                    file_name=f"{recipe_json.get('name', 'recipe').lower().replace(' ', '_')}.recipe.json",
                    mime="application/json",
                )

                with st.spinner("Pushing to Workato…"):
                    result = push_recipe_workato(recipe_json, gen_token, gen_folder, gen_name)

                if result["id"]:
                    st.markdown(
                        f'<div class="badge-success">Pushed — Recipe ID: <b>{result["id"]}</b></div>',
                        unsafe_allow_html=True,
                    )
                    st.info(f"Open in Workato: https://app.workato.com/recipes/{result['id']}")
                    if result.get("warnings"):
                        conns = ", ".join(f"`{c}`" for c in result["warnings"])
                        st.warning(f"Wire connections in GUI: {conns}")
                else:
                    st.markdown(
                        f'<div class="badge-error">Push failed: {result["error"]}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
        return

    # ── Push Recipe JSON mode (early return) ─────────────────────────────────
    if mode == "Push Recipe JSON":
        push_card = st.container(border=True)
        push_card.__enter__()
        st.markdown(
            '<div class="card-header-target">'
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
                        f'<div class="pkg-ready">{recipe_file.name}'
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

        push_card.__exit__(None, None, None)

        push_bar = st.container()
        push_bar.__enter__()
        st.markdown('<div class="sticky-action-marker"></div>', unsafe_allow_html=True)
        push_col, _ = st.columns([1, 5])
        with push_col:
            push_clicked = st.button("Push Recipe", type="primary",
                                     use_container_width=True, key="push_btn")
        push_bar.__exit__(None, None, None)

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
                        f'<div class="badge-success">Recipe pushed — ID: <b>{result["id"]}</b></div>',
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
                        f'<div class="badge-error">Push failed: {result["error"]}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("""
<div class="migralte-footer">
    <span class="footer-tagline"><strong>AI + Automation + Expertise</strong> = Faster, Smarter Migrations</span>
    <span style="opacity:0.8;">TechStone LLC &nbsp;·&nbsp; MigrAlte</span>
</div>""", unsafe_allow_html=True)
        return

    # ── Source / Target columns ──────────────────────────────────────────────
    # Middle column is kept purely for the gap it gives between the two cards
    # (the static-looking compact arrow that used to live here was removed --
    # at 46px wide it barely showed any motion; the full-width flowing arrow
    # in Migration Progress below is the one that actually reads as moving).
    col_src, _, col_tgt = st.columns([5, 0.6, 5], gap="small")

    with col_src:
        src_card = st.container(border=True)
        src_card.__enter__()
        source_platforms_shown = (
            [p for p in SOURCE_PLATFORMS if p != "workato"]
            if DEMO_HIDE_WORKATO_SOURCE else SOURCE_PLATFORMS
        )
        # Same staleness guard as the target picker: a prior session may have
        # left "workato" selected as source before this flag was turned on.
        if st.session_state.get("source_platform_sel") not in source_platforms_shown:
            st.session_state["source_platform_sel"] = source_platforms_shown[0]
        render_platform_card_header("source", "source_platform_sel", source_platforms_shown, "Source")
        source = platform_picker(source_platforms_shown, "source_platform_sel")

        # Populated selectively below depending on `source` and which radio
        # option is picked; run_clicked resolves exactly one of these per run.
        wm_local_file, wm_drive_url = None, ""
        src_local_dir_input, src_live_ref = "", ""
        src_boomi_process = ""
        src_env: dict = {}
        source_mode = "dir"   # "dir" | "upload" | "gdrive" | one of LIVE_FLAG_BY_SOURCE's keys

        if source == "webmethods":
            wm_modes = ["Upload from computer", "Google Drive", "Live pull (webMethods.io)"]
            input_mode = st.radio("Package source", wm_modes, horizontal=True, label_visibility="collapsed")

            if input_mode == wm_modes[0]:
                source_mode = "upload"
                wm_local_file = st.file_uploader("Upload webMethods package (.zip)", type=["zip"])
                if wm_local_file:
                    sz = wm_local_file.size // 1024
                    st.markdown(f'<div class="pkg-ready">{wm_local_file.name} &nbsp;({sz} KB) — ready</div>', unsafe_allow_html=True)
            elif input_mode == wm_modes[1]:
                source_mode = "gdrive"
                wm_drive_url = st.text_input("Google Drive share URL or File ID", placeholder="https://drive.google.com/file/d/…")
                if wm_drive_url.strip():
                    file_id = _gdrive_file_id(wm_drive_url.strip())
                    if file_id:
                        st.markdown(f'<div class="pkg-ready">File ID: {file_id[:16]}… — will download on run</div>', unsafe_allow_html=True)
                    else:
                        st.warning("Could not parse a Drive file ID from that URL.")
            else:
                source_mode = "webmethods"  # matches LIVE_FLAG_BY_SOURCE key -> --wmio-project
                src_live_ref = st.text_input("webMethods.io project name", placeholder="e.g. GLD Compliance", key="src_wmio_ref")
                src_env = source_credential_form("webmethods")

        elif source == "boomi":
            boomi_modes = ["Live pull from Boomi", "Local directory (already pulled)"]
            input_mode = st.radio("Boomi source", boomi_modes, horizontal=True, label_visibility="collapsed")
            if input_mode == boomi_modes[0]:
                source_mode = "boomi"  # -> --boomi-folder
                src_live_ref = st.text_input("Boomi folder name or ID", placeholder="e.g. MIG_CustomerAPI", key="src_boomi_ref")
                src_boomi_process = st.text_input(
                    "Process name(s) — optional", placeholder="e.g. Integration Troubleshooting - Associate",
                    help="Leave blank to migrate every component in the folder. Otherwise migrates only the "
                         "named process(es) plus their actual dependencies (connections, maps, profiles) — "
                         "not everything else sitting in the folder. Comma-separate multiple names; "
                         "% wildcards allowed (e.g. 'Sync %').",
                    key="src_boomi_process",
                )
                src_env = source_credential_form("boomi")
            else:
                source_mode = "dir"
                src_local_dir_input = st.text_input("Local directory path", placeholder="active-development/", key="src_boomi_dir")

        elif source == "mulesoft":
            source_mode = "dir"
            src_local_dir_input = st.text_input(
                "MuleSoft project directory", placeholder="e.g. samples/mulesoft/customer-api/",
                help="MuleSoft has no live pull today — point at a local project folder or export.",
                key="src_mulesoft_dir",
            )

        elif source == "workato":
            wt_modes = ["Live pull from Workato", "Local export directory"]
            input_mode = st.radio("Workato source", wt_modes, horizontal=True, label_visibility="collapsed")
            if input_mode == wt_modes[0]:
                source_mode = "workato"  # -> --workato-folder
                src_live_ref = st.text_input("Workato folder name or ID", placeholder="e.g. WebMethodsMigration", key="src_wt_ref")
                src_env = source_credential_form("workato")
            else:
                source_mode = "dir"
                src_local_dir_input = st.text_input("Local export directory", placeholder="e.g. exports/workato/", key="src_wt_dir")

        elif source == "celigo":
            cel_modes = ["Live pull from Celigo", "Local export directory"]
            input_mode = st.radio("Celigo source", cel_modes, horizontal=True, label_visibility="collapsed")
            if input_mode == cel_modes[0]:
                source_mode = "celigo"  # -> --celigo-integration
                src_live_ref = st.text_input("Celigo integration name", placeholder="e.g. Order Sync", key="src_cel_ref")
                src_env = source_credential_form("celigo")
            else:
                source_mode = "dir"
                src_local_dir_input = st.text_input("Local export directory", placeholder="e.g. exports/celigo/", key="src_cel_dir")

        src_card.__exit__(None, None, None)

    with col_tgt:
        tgt_card = st.container(border=True)
        tgt_card.__enter__()
        target_platforms_shown = ["workato"] if DEMO_WORKATO_ONLY_TARGET else TARGET_PLATFORMS
        # A prior session (before demo mode was turned on) may have left a
        # now-hidden platform selected -- platform_picker just returns
        # whatever's in session_state, so without this it would silently keep
        # targeting "boomi" behind the scenes while only showing a Workato
        # tile. Reset it to the only visible option so what's displayed and
        # what's actually targeted can't disagree.
        if st.session_state.get("target_platform_sel") not in target_platforms_shown:
            st.session_state["target_platform_sel"] = target_platforms_shown[0]
        render_platform_card_header("target", "target_platform_sel", target_platforms_shown, "Target")
        target = platform_picker(target_platforms_shown, "target_platform_sel")
        tgt_env = target_credential_form(target)
        tgt_card.__exit__(None, None, None)

    # ── Options bar ──────────────────────────────────────────────────────────
    options_card = st.container(border=True)
    options_card.__enter__()
    st.markdown('<div class="section-label boxed-section-label">Migration Options</div>', unsafe_allow_html=True)
    oc1, oc2, oc3 = st.columns([2, 2, 2])
    with oc1:
        project_name = st.text_input("Package / project name ✱", placeholder="e.g. GLDFundingEngine20080714",
                                     help="Used to name the spec file and destination folder. Defaults to the "
                                          "zip filename, directory name, or live-pull folder/integration name if blank.")
        dest_name    = st.text_input("Destination folder / project", placeholder="MIG_<project>")
    with oc2:
        md_dir = st.text_input("Markdown dir for doc appendix", placeholder="e.g. WebMethods/MD/")
    with oc3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        dry_run       = st.checkbox("Dry run", help="Generate artifacts without pushing to target")
        skip_analyze  = st.checkbox("Skip analyze", help="Re-use existing spec in migration-specs/")
        skip_enrich   = st.checkbox("Skip enrich", help="Skip AI enrichment (faster, lower quality)")
        skip_document = st.checkbox(
            "Skip document", value=True,
            help="Skip Word design document generation. On by default — generate_word_doc.py makes "
                 "no LLM calls itself (it's local .docx assembly from the already-generated spec), but "
                 "it's the one phase you're least likely to need on every run. Uncheck to also get the "
                 "branded .docx this run.",
        )
        use_airo = False
        if target == "workato":
            use_airo = st.checkbox(
                "Build via AIRO",
                help="Resolve and validate every connector/action live against Workato's real schema "
                     "via the AIRO MCP recipe builder, instead of the static generator's blind JSON "
                     "assembly (which falls back to 'Select an app and action' placeholders it can't "
                     "map). Slower and uses LLM tokens. Auth rides on Claude Code's own login, not "
                     "WORKATO_API_TOKEN. Note: once a build starts, AIRO always creates and fully "
                     "pushes each recipe live -- it can't pause mid-build for approval. With Dry run "
                     "also checked, this app stops the pipeline one phase earlier instead: it produces "
                     "the spec for you to review, then AIRO only runs once you click the approval "
                     "button that appears below.",
            )
            if use_airo and dry_run:
                st.caption(
                    "ℹ️ **Dry run will stop right after the spec is generated** — "
                    "Analyze/Enrich/Document run as usual, then the pipeline stops "
                    "before AIRO is ever invoked. You'll get an **approve-to-build** "
                    "button once the spec is ready to review."
                )
    options_card.__exit__(None, None, None)

    # ── Run button ───────────────────────────────────────────────────────────
    run_bar = st.container()
    run_bar.__enter__()
    st.markdown('<div class="sticky-action-marker"></div>', unsafe_allow_html=True)
    run_col, _ = st.columns([1, 4])
    with run_col:
        run_clicked = st.button(
            "Migration running…" if is_migration_running else "Run Migration",
            type="primary", use_container_width=True, disabled=is_migration_running,
        )
    run_bar.__exit__(None, None, None)

    # ── Output ───────────────────────────────────────────────────────────────
    if run_clicked and not is_migration_running:
        # Resolve the source into exactly one of: a local directory, or a
        # live-pull reference name/ID (credentials ride along in src_env).
        source_dir = None
        live_ref   = ""

        if source_mode == "upload":
            if wm_local_file is None:
                st.error("Please upload a webMethods package .zip.")
                return
            with st.spinner("Preparing webMethods package…"):
                try:
                    source_dir = prepare_wm_package(wm_local_file, "", AGENT_DIR)
                except Exception as exc:
                    st.error(f"Package preparation failed: {exc}")
                    return
            effective_project = project_name.strip() or Path(wm_local_file.name).stem
            st.success(f"Package extracted → `{source_dir.relative_to(AGENT_DIR)}`   |   Project: **{effective_project}**")

        elif source_mode == "gdrive":
            if not wm_drive_url.strip():
                st.error("Please enter a Google Drive URL.")
                return
            with st.spinner("Downloading from Google Drive…"):
                try:
                    source_dir = prepare_wm_package(None, wm_drive_url, AGENT_DIR)
                except Exception as exc:
                    st.error(f"Package preparation failed: {exc}")
                    return
            effective_project = project_name.strip() or "wm_package"
            st.success(f"Package extracted → `{source_dir.relative_to(AGENT_DIR)}`   |   Project: **{effective_project}**")

        elif source_mode == "dir":
            if not src_local_dir_input.strip():
                st.error(f"Please provide a local directory for the {PLATFORM_LABELS[source]} source.")
                return
            candidate = Path(src_local_dir_input.strip())
            if not candidate.is_dir():
                st.error(f"Directory not found: {candidate}")
                return
            source_dir = candidate
            effective_project = project_name.strip() or source_dir.name
            st.success(f"Using local directory → `{source_dir}`   |   Project: **{effective_project}**")

        else:
            # source_mode is a LIVE_FLAG_BY_SOURCE key: boomi / workato / celigo / webmethods
            if not src_live_ref.strip():
                st.error(f"Please provide the {PLATFORM_LABELS[source]} name/ID to pull from.")
                return
            live_ref = src_live_ref.strip()
            effective_project = project_name.strip() or re.sub(r"[^\w-]", "_", live_ref).strip("_").lower()
            process_note = f"   |   Process(es): **{src_boomi_process.strip()}**" if (source == "boomi" and src_boomi_process.strip()) else ""
            st.success(f"Will live-pull from {PLATFORM_LABELS[source]}: **{live_ref}**{process_note}   |   Project: **{effective_project}**")

        # Dry run + Build via AIRO together means "stop before GENERATE and
        # let me approve first" -- AIRO can't offer that itself (it always
        # builds and pushes live, in one session -- see the checkbox's own
        # help text), so the only real place to honor Dry run for this combo
        # is to stop the whole migrate.py pipeline before AIRO is ever
        # invoked, not inside it.
        airo_approval_gate = use_airo and dry_run
        if airo_approval_gate:
            # This run is guaranteed NOT to produce a fresh AIRO output file
            # (GENERATE is skipped entirely) -- but a stale one from an
            # earlier run under the same project name may already be sitting
            # on disk and would otherwise be mistaken for a current result,
            # hiding the approval button below (which only shows when no
            # AIRO output exists yet). Same staleness class CLAUDE.md already
            # documents being fixed once for the pull phase's
            # active-development/ directory -- clear it here too.
            _stale_slug = (effective_project or "migration_project").lower().replace(" ", "_")
            _stale_airo = AGENT_DIR / "migration-specs" / f"{_stale_slug}_workato_airo_output.json"
            if _stale_airo.exists():
                _stale_airo.unlink()
        cmd = build_migrate_cmd(
            source, target, str(source_dir) if source_dir else "", live_ref,
            dest_name, effective_project, dry_run, skip_analyze, skip_enrich, skip_document, md_dir,
            use_airo=use_airo, boomi_process=src_boomi_process,
            skip_generate=airo_approval_gate,
        )
        combined_env = {**src_env, **tgt_env}

        # Don't start the blocking work inline -- by this point the theme
        # toggle, mode selector, and the rest of this form have ALREADY
        # rendered earlier in this same script run, without the lock marker
        # (is_migration_running was still False when they were drawn). Stash
        # what the locked run needs and rerun instead; the NEXT execution
        # starts with the flag already True, so the lock marker renders
        # before anything else this time, and _run_locked_migration() below
        # does the actual work with the whole page already click-proof.
        st.session_state["_pending_run"] = {
            "cmd": cmd, "combined_env": combined_env,
            "source": source, "target": target,
            "effective_project": effective_project, "dest_name": dest_name,
            "tgt_env": tgt_env, "airo_approval_gate": airo_approval_gate,
        }
        st.session_state["_migration_running"] = True
        st.rerun()

    if is_migration_running:
        _run_locked_migration()

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
        airo_path = AGENT_DIR / "migration-specs" / f"{project_slug}_workato_airo_output.json"
        has_airo  = airo_path.exists()

        # ── AIRO approval gate ──────────────────────────────────────────────
        # Set when Dry run + Build via AIRO were both checked: migrate.py
        # stopped right after producing the spec (--skip-generate), before
        # AIRO was ever invoked. Review the spec/doc tabs below, then this
        # button runs generate_workato_airo.py for real -- this IS the
        # approve-then-push step AIRO itself can't offer (it always builds
        # and pushes live in one session once started).
        if _arts.get("awaiting_airo_approval") and not has_airo:
            st.markdown("---")
            approval_card = st.container(border=True)
            with approval_card:
                st.markdown(
                    '<div class="section-label boxed-section-label">Step 5 — Generate: awaiting approval</div>',
                    unsafe_allow_html=True,
                )
                # Guards against a double-click triggering two live AIRO builds
                # (and two pushed recipes), cleared in `finally` below so a
                # crash can't leave it stuck forever. Streamlit only draws a
                # widget's appearance (incl. disabled=) once, at the moment
                # st.button() is called -- flipping this flag AFTER that point
                # in the SAME script run never updates how the button already
                # on screen looks. So the click only sets the flag and
                # reruns; the actual build runs on the NEXT script execution,
                # which starts with the flag already True -- the button
                # renders disabled from the very first line of that run,
                # instead of staying clickable-looking the whole time it's
                # supposedly building.
                running_key = f"_airo_gen_running_{project_slug}"
                is_running = st.session_state.get(running_key, False)

                if not is_running:
                    st.write(
                        "The migration spec is ready for review below — nothing has touched Workato yet. "
                        "Approve to build and push the recipe live via AIRO."
                    )
                    if st.button("Generate & Push via AIRO", type="primary", key="approve_airo_generate"):
                        st.session_state[running_key] = True
                        st.rerun()
                else:
                    st.button("Generate & Push via AIRO", type="primary", disabled=True, key="approve_airo_generate_running")
                    st.info("Starting the AIRO build now — this talks to the live Workato platform and "
                            "can take a few minutes. Don't close this tab.")
                    gen_rc = None
                    try:
                        gen_cmd = [
                            sys.executable, str(AGENT_DIR / "generators" / "generate_workato_airo.py"),
                            str(spec_path), "--folder", folder,
                        ]
                        gen_q: queue.Queue = queue.Queue()
                        gen_thread = threading.Thread(
                            target=stream_subprocess,
                            args=(gen_cmd, {"WORKATO_API_TOKEN": wt_token}, gen_q),
                            daemon=True,
                        )
                        gen_thread.start()

                        # st.code (not a markdown-rendered HTML div) -- AIRO's
                        # log includes the agent's own free-form text, which
                        # can contain backticks/asterisks; a markdown-parsed
                        # view mangles those into stray inline-code pills and
                        # doubly-escaped entities. st.code treats it as
                        # literal text, guaranteed not to mis-render.
                        gen_log_placeholder = st.empty()
                        gen_lines: list = []
                        with st.spinner("Building via AIRO — this creates and pushes the recipe live in Workato..."):
                            while True:
                                try:
                                    item = gen_q.get(timeout=0.1)
                                except queue.Empty:
                                    continue
                                if item is None:
                                    break
                                if isinstance(item, tuple) and item[0] == "__returncode__":
                                    gen_rc = item[1]
                                    continue
                                gen_lines.append(item.rstrip())
                                tail = gen_lines[-30:]
                                gen_log_placeholder.code("\n".join(tail), language="bash")
                            while not gen_q.empty():
                                item = gen_q.get_nowait()
                                if isinstance(item, tuple) and item[0] == "__returncode__":
                                    gen_rc = item[1]

                        gen_log_placeholder.empty()
                        with st.expander("AIRO build log", expanded=(gen_rc != 0)):
                            st.code("\n".join(gen_lines) if gen_lines else "(no output)", language="bash")
                    except Exception as exc:
                        st.error(f"AIRO build crashed before finishing: {exc}")
                        st.exception(exc)
                    finally:
                        st.session_state[running_key] = False

                    if gen_rc == 0:
                        # Rerun only on success, to land cleanly on the fresh
                        # "AIRO Build Summary" tab. On failure, don't rerun --
                        # an immediate rerun would wipe the error/log below
                        # before the user has a chance to read them.
                        st.session_state["_artifacts"]["awaiting_airo_approval"] = False
                        st.rerun()
                    elif gen_rc is not None:
                        st.error(f"AIRO build failed (exit {gen_rc}) — see log above.")

        tab_labels = []
        if has_airo:
            tab_labels.append("AIRO Build Summary")
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
                    f'<div class="badge-success">{len(recipe_files)} recipe(s) ready</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            tabs = st.tabs(tab_labels)
            tab_idx = 0

            if has_airo:
                with tabs[tab_idx]:
                    with open(airo_path, encoding="utf-8") as f:
                        airo_result = json.load(f)
                    cost = airo_result.get("cost_usd", 0.0)
                    is_err = airo_result.get("is_error", False)
                    if is_err:
                        st.error(f"AIRO build session ended in an error state (cost so far: ${cost:.2f})")
                    else:
                        st.success(f"AIRO build complete — cost: ${cost:.2f}")
                    # AIRO always pushes now (see generate_workato_airo.py's module
                    # docstring for why an earlier "skip push" dry-run mode was
                    # removed -- it left builds unflushed instead of reviewable).
                    # Whether a recipe is actually live or just a draft is the
                    # platform's own call, parsed from the agent's required
                    # "Status: PLATFORM|DRAFT" lines -- surface that plainly,
                    # since a draft needs one manual click in Workato itself
                    # that nothing in this app can do on the user's behalf.
                    if airo_result.get("has_draft"):
                        st.warning(
                            "⚠️ One or more recipes above were saved as a **draft**, not published live. "
                            "Open the recipe link below and click **Save** in the Workato Recipe Editor "
                            "to publish it — there's no button here that can do that step for you."
                        )
                    elif airo_result.get("recipe_statuses"):
                        st.caption(
                            "✓ All recipes saved live on the Workato platform — each one is created "
                            "**Stopped**, though, so nothing runs yet. Open a recipe link above and "
                            "click **Start** in Workato when you're ready to activate it."
                        )
                    st.caption(f"Folder: {airo_result.get('folder', '(unknown)')}  |  "
                               f"Spec: {Path(airo_result.get('spec', '')).name}")
                    st.markdown(airo_result.get("summary") or "_(agent produced no summary text — see the full migration log above)_")
                tab_idx += 1

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
