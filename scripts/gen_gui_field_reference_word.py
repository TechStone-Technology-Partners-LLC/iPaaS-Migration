#!/usr/bin/env python3
"""
Generates a branded Word (.docx) version of docs/GUI_FIELD_REFERENCE.html --
every field, toggle, and button in the MigrAIte Streamlit app (app.py),
explained mode by mode.

Reuses the exact same TechStone-branded docx building blocks as
scripts/gen_product_doc_word.py (headings, tables, callouts) rather than
duplicating that styling code, so the two documents stay visually consistent.

Usage:
    python scripts/gen_gui_field_reference_word.py
    python scripts/gen_gui_field_reference_word.py --output docs/MyName.docx
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("ERROR: python-docx not installed. Run: pip install python-docx", file=sys.stderr)
    sys.exit(1)

from gen_product_doc_word import (
    Document, NAVY, BLUE, MUTED_GRAY, DARK_GRAY, WARN_BG, WARN_FG,
    add_heading1, add_heading2, add_heading3, add_body, add_table,
)


def add_subhead(doc, text):
    """A light sub-grouping label above a table, e.g. 'Live pull from Boomi' --
    one notch below add_heading3, no top spacing of its own since it always
    sits directly under a platform heading or intro paragraph."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = DARK_GRAY
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    return p


def add_callout(doc, tag, text, fg=None, bg=None):
    """A highlighted note block, matching the HTML reference's .callout style."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    fg = fg or WARN_FG
    bg = bg or WARN_BG
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.left_indent = Inches(0.15)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "%02X%02X%02X" % (bg[0], bg[1], bg[2]))
    pPr.append(shd)

    r = p.add_run(tag.upper() + "\n")
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = fg
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.color.rgb = DARK_GRAY
    return p


SRC_BG, SRC_FG = (0xE8, 0xEF, 0xFA), (0x2B, 0x5F, 0xB8)
TGT_BG, TGT_FG = (0xE4, 0xF3, 0xF0), (0x0E, 0x7C, 0x6B)


def _rgb(t):
    from docx.shared import RGBColor
    return RGBColor(*t)


def build(output_path: str):
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    for section in doc.sections:
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)

    # ─── Title page ─────────────────────────────────────────────────────────
    logo = ROOT / "logos" / "TechStone.png"
    if logo.is_file():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(logo), width=Inches(1.8))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(30)
    run = p.add_run("MigrAIte")
    run.font.size = Pt(30)
    run.font.bold = True
    run.font.color.rgb = NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("GUI Field Reference")
    run.font.size = Pt(15)
    run.font.color.rgb = BLUE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run(
        "What every field, button, and toggle in the MigrAIte Streamlit app does, "
        "grouped by the screen it appears on."
    )
    run.font.size = Pt(10.5)
    run.font.italic = True
    run.font.color.rgb = MUTED_GRAY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    run = p.add_run("Written against the current build of app.py")
    run.font.size = Pt(9)
    run.font.color.rgb = MUTED_GRAY

    doc.add_page_break()

    # ─── Global controls ────────────────────────────────────────────────────
    add_heading1(doc, "Global Controls")
    add_body(doc, "Two controls sit above the three mode tabs and apply no matter which mode you're in.")
    add_table(
        doc,
        ["Control", "Type", "Description"],
        [
            ("Theme", "Dark / Light toggle",
             "Switches the whole app's palette. Dark is the default. Every color in the UI routes "
             "through one shared token set, so this is a full re-theme, not a partial one — "
             "including the platform tiles, inputs, badges, and the terminal log panel (which stays "
             "black in both themes, like a code editor's console)."),
            ("Mode selector", "3-way segmented control",
             "Migrate Package runs the full pull → analyze → enrich → document → "
             "generate pipeline. Generate from Analysis skips straight to recipe generation from an "
             "existing analysis document. Push Recipe JSON skips generation entirely and just pushes "
             "an already-built recipe file. Switching modes resets the fields below it."),
        ],
        col_widths=[1.3, 1.6, 3.4],
    )

    # ─── Mode 1: Migrate Package ────────────────────────────────────────────
    add_heading1(doc, "Mode 1 — Migrate Package")
    add_body(
        doc,
        "The default mode: a full pipeline run from a source platform to a target platform. The "
        "screen is built as two side-by-side cards — Source Platform on the left, Target Platform "
        "on the right — followed by a shared Migration Options bar and a Run button.",
    )

    add_heading2(doc, "Source Platform")
    add_body(
        doc,
        "Pick one of five platforms as tiles (logo + name). The fields that appear below the tiles "
        "change completely depending on which one is selected — each platform has its own intake "
        "flow, shown as sub-sections below.",
    )

    add_heading3(doc, "Boomi")
    add_body(doc, "A second-level toggle chooses between a live pull from the Boomi platform API, or an already-pulled local directory.")
    add_subhead(doc, "Live pull from Boomi")
    add_table(
        doc,
        ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("Boomi folder name or ID", "text", "e.g. MIG_CustomerAPI", "The Boomi folder to pull components from."),
            ("Process name(s) — optional", "text", "(blank = whole folder)",
             "Leave blank to migrate every component in the folder. Otherwise migrates only the named "
             "process(es) plus their actual dependencies (connections, maps, profiles) — not "
             "everything else sitting in the folder. Comma-separate multiple names; % wildcards "
             "allowed (e.g. 'Sync %')."),
            ("API URL", "text", "https://api.boomi.com/api/rest/v1", "Boomi REST API base URL."),
            ("Account ID", "text", "—", "Boomi account ID."),
            ("Username (email)", "text", "—", "Boomi login email."),
            ("API Token", "password", "—",
             "Boomi API token. Session-only — merged into the migration subprocess's environment "
             "for this run and never written to disk."),
        ],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )
    add_subhead(doc, "Local directory (already pulled)")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("Local directory path", "text", "active-development/", "Path to a directory of already-pulled Boomi component XML.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )

    add_heading3(doc, "MuleSoft")
    add_body(doc, "No live pull exists for MuleSoft today — it's local-file-only.")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("MuleSoft project directory", "text", "e.g. samples/mulesoft/customer-api/",
          "Path to a local MuleSoft project folder or export.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )

    add_heading3(doc, "Workato")
    add_body(doc, "A second-level toggle chooses between a live pull from Workato, or a local export directory.")
    add_subhead(doc, "Live pull from Workato")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("Workato folder name or ID", "text", "e.g. WebMethodsMigration", "The Workato folder to pull recipes from."),
            ("API Token", "password", "—", "Workato API token for this pull."),
            ("Account email", "text", "—", "Workato account email."),
        ],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )
    add_subhead(doc, "Local export directory")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("Local export directory", "text", "e.g. exports/workato/", "Path to a previously-exported Workato directory.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )

    add_heading3(doc, "Celigo")
    add_body(doc, "A second-level toggle chooses between a live pull from Celigo, or a local export directory.")
    add_subhead(doc, "Live pull from Celigo")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("Celigo integration name", "text", "e.g. Order Sync", "The Celigo integration to pull."),
            ("API Token", "password", "—", "Celigo API token for this pull."),
        ],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )
    add_subhead(doc, "Local export directory")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("Local export directory", "text", "e.g. exports/celigo/", "Path to a previously-exported Celigo directory.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )

    add_heading3(doc, "webMethods")
    add_body(doc, "A three-way toggle: upload a package zip directly, paste a Google Drive link, or live-pull from webMethods.io.")
    add_subhead(doc, "Upload from computer")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("Upload webMethods package (.zip)", "file upload", ".zip only",
          "Extracted into a fresh, uniquely-named working directory on each run — nothing is overwritten between runs.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )
    add_subhead(doc, "Google Drive")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [("Google Drive share URL or File ID", "text", "https://drive.google.com/file/d/…",
          "A shareable Drive link (or bare file ID) to a package zip. Downloaded server-side when you click Run.")],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )
    add_subhead(doc, "Live pull (webMethods.io)")
    add_table(
        doc, ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("webMethods.io project name", "text", "e.g. GLD Compliance", "The webMethods.io project to pull."),
            ("Tenant URL", "text", "https://mycompany.int-aws-us.webmethods.io", "Your webMethods.io tenant URL."),
            ("Username", "text", "—", "webMethods.io username."),
            ("Password", "password", "—", "webMethods.io password."),
        ],
        col_widths=[1.4, 0.7, 1.5, 2.7],
    )

    add_callout(
        doc, "Note",
        "All source credential fields are session-only. They're merged into the migration "
        "subprocess's environment for that one run and are never written to .env or any file on disk.",
        fg=_rgb(SRC_FG), bg=_rgb(SRC_BG),
    )

    add_heading2(doc, "Target Platform")
    add_body(doc, "Four platforms, same tile pattern as the source side. The credential fields underneath change based on which target is selected.")
    add_table(
        doc,
        ["Field", "Type", "Default", "Description"],
        [
            ("Boomi — API URL", "text", "https://api.boomi.com/api/rest/v1", "Boomi REST API base URL."),
            ("Boomi — Account ID", "text", "—", "Boomi account to push into."),
            ("Boomi — Username (email)", "text", "—", "Boomi login email."),
            ("Boomi — API Token", "password", "—", "Boomi API token with write access."),
            ("Boomi — Environment ID", "text", "—", "Boomi environment to deploy into."),
            ("Boomi — Target Folder ID", "text", "—", "Destination folder ID for generated components."),
            ("Workato — API Token", "password", "—",
             "Workato API token. Needs write/create scope on recipes and folders — a token that only "
             "passes GET /users/me is not sufficient (Workato returns 404, not 401/403, for "
             "missing-scope writes)."),
            ("Workato — Account email", "text", "—", "Workato account email."),
            ("Celigo — API Token", "password", "—", "Celigo API token."),
            ("webMethods — Tenant URL", "text", "https://mycompany.int-aws-us.webmethods.io", "Target webMethods.io tenant."),
            ("webMethods — Username", "text", "—", "webMethods.io username."),
            ("webMethods — Password", "password", "—", "webMethods.io password."),
        ],
        col_widths=[1.8, 0.7, 1.4, 2.4],
    )

    add_heading2(doc, "Migration Options")
    add_body(doc, "A shared options bar below both platform cards, applying to the run regardless of source/target choice.")
    add_table(
        doc,
        ["Field", "Type", "Default", "Description"],
        [
            ("Package / project name ✱", "text", "(derived if blank)",
             "Used to name the spec file and destination folder. Defaults to the zip filename, "
             "directory name, or live-pull folder/integration name if left blank."),
            ("Destination folder / project", "text", "MIG_<project>",
             "The container the migrated asset(s) get pushed into on the target platform."),
            ("Markdown dir for doc appendix", "text", "e.g. WebMethods/MD/",
             "Optional — attaches markdown files from this directory as an appendix to the "
             "generated Word design document."),
            ("Dry run", "checkbox", "off",
             "Generate artifacts without pushing to the target. Does not apply to AIRO builds below."),
            ("Skip analyze", "checkbox", "off",
             "Re-use an existing spec already in migration-specs/ instead of re-analyzing the source."),
            ("Skip enrich", "checkbox", "off",
             "Skip the AI enrichment pass. Faster, but lower-quality output for nested/complex service logic."),
            ("Skip document", "checkbox", "ON by default",
             "Skip Word design-document generation. On by default — that step makes no LLM calls "
             "itself (it's local .docx assembly from the already-generated spec), but it's the phase "
             "you're least likely to need on every run. Uncheck to also get the branded .docx this run."),
            ("Build via AIRO (live-validated)", "checkbox", "off",
             "Only shown when Target is Workato. Resolves and validates every connector/action live "
             "against Workato's real schema via the AIRO MCP recipe builder, instead of the static "
             "generator's blind JSON assembly (which falls back to 'Select an app and action' "
             "placeholders it can't map). Slower and uses LLM tokens. Auth rides on Claude Code's own "
             "login, not the Workato API token field above."),
        ],
        col_widths=[1.6, 0.7, 1.1, 2.9],
    )
    add_callout(
        doc, "AIRO + Dry run",
        "AIRO creates each recipe live in Workato as it builds, regardless of the Dry run checkbox — "
        "Dry run only skips the final push of its steps. It is not a no-side-effects mode when AIRO is enabled.",
        fg=_rgb((0xB8, 0x3B, 0x4B)), bg=_rgb((0xFB, 0xEA, 0xEC)),
    )

    add_heading2(doc, "Run & Progress")
    add_body(
        doc,
        "Clicking Run Migration resolves the source into exactly one of: a prepared local directory, "
        "or a live-pull reference (credentials riding along separately), then launches migrate.py as a "
        "subprocess and streams its output live.",
    )
    add_table(
        doc,
        ["Element", "Description"],
        [
            ("Step tracker",
             "Five pipeline phases shown as connected cards: Pull (fetch source files) → Analyze "
             "(parse flows & services) → Enrich (AI deep enrichment) → Document (design document) "
             "→ Generate (push to target). Each lights up as the subprocess emits its matching "
             "[PHASE] marker, and is marked done once the next phase begins."),
            ("Live log", "A terminal-styled panel showing the last 30 lines of subprocess output, updating as the run progresses."),
            ("Status badge", "“Migration completed successfully” or “Migration failed (exit N)” once the subprocess exits."),
            ("Full migration log", "A collapsible expander with the complete captured output — expanded automatically on failure."),
        ],
        col_widths=[1.5, 4.3],
    )

    add_heading2(doc, "Artifacts & Results")
    add_body(doc, "After a run, whatever files actually got produced appear as tabs — only tabs with real output show up.")
    add_table(
        doc,
        ["Tab", "Appears when", "Contents"],
        [
            ("AIRO Build Summary", "“Build via AIRO” was checked",
             "Build cost, error/success state, and the agent's own summary of what it built per recipe."),
            ("Recipe: <service>", "The static generator produced one or more recipe JSON files",
             "The full recipe JSON, a Workato folder ID field (accepts a bare ID, a ?fid= query string, "
             "or a full URL — digits are extracted automatically), a Download JSON button, and a "
             "Push to Workato button that uses the target credentials entered above."),
            ("Migration Spec", "A spec JSON was generated", "The platform-agnostic migration spec produced by the Analyze phase."),
            ("Design Document", "“Skip document” was unchecked", "The generated TechStone-branded Word design document."),
        ],
        col_widths=[1.4, 1.8, 2.6],
    )

    # ─── Mode 2: Generate from Analysis ─────────────────────────────────────
    add_heading1(doc, "Mode 2 — Generate from Analysis")
    add_body(
        doc,
        "Skips pull/analyze/enrich entirely: upload an Analysis.md already produced by a previous "
        "migration session, and Claude reads it directly to generate a complete Workato recipe JSON, "
        "then pushes it.",
    )
    add_table(
        doc,
        ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("Analysis file", "file upload", ".md or .txt, 200MB max", "The analysis document to generate a recipe from."),
            ("Folder ID", "text", "e.g. 31661117 — leave blank for root", "Workato folder to push the generated recipe into."),
            ("Recipe name override", "text", "(uses generated name)", "Leave blank to use the name Claude assigns in the generated JSON."),
            ("Target — API Token", "password", "—", "Required before generation can run."),
            ("Target — Account email", "text", "—", "Workato account email."),
        ],
        col_widths=[1.5, 0.8, 1.7, 2.3],
    )
    add_body(
        doc,
        "Generate & Push runs generation, shows a success message with the recipe name and step "
        "count, offers a 'Review generated recipe JSON before push' expander and a 'Download recipe "
        "JSON' button, then pushes to Workato and reports the resulting recipe ID and link (or any "
        "connections that still need wiring in the GUI).",
        muted=True,
    )

    # ─── Mode 3: Push Recipe JSON ───────────────────────────────────────────
    add_heading1(doc, "Mode 3 — Push Recipe JSON")
    add_body(doc, "For when you already have a recipe JSON file (from a previous Generate run, or built by hand) and just need to push it.")
    add_table(
        doc,
        ["Field", "Type", "Default / placeholder", "Description"],
        [
            ("Recipe file", "file upload", ".json only",
             "On upload, a preview line shows the detected recipe name and top-level step count (if "
             "the JSON doesn't parse, push is still attempted)."),
            ("Folder ID", "text", "e.g. 31661117 — leave blank for root", "Workato folder to push into."),
            ("Recipe name override", "text", "(uses name from JSON)", "Leave blank to use the recipe's own name field."),
            ("Target — API Token", "password", "—", "Required before push can run."),
            ("Target — Account email", "text", "—", "Workato account email."),
        ],
        col_widths=[1.5, 0.8, 1.7, 2.3],
    )
    add_body(
        doc,
        "Push Recipe pushes the uploaded JSON as-is and reports the resulting recipe ID and link, or "
        "the push error if it failed.",
        muted=True,
    )

    doc.save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate the MigrAIte GUI field reference Word doc.")
    ap.add_argument("--output", default=str(ROOT / "docs" / "GUI_FIELD_REFERENCE.docx"))
    args = ap.parse_args()
    build(args.output)
