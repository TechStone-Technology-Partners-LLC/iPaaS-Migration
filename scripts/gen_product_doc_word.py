#!/usr/bin/env python3
"""
Generates a branded Word (.docx) version of docs/PRODUCT_DOCUMENTATION.md.

Standalone (not spec-driven, unlike generators/generate_word_doc.py) — this
is a one-off content -> docx renderer for the MigrAIte product documentation
itself, using the same TechStone brand palette/conventions.

Usage:
    python scripts/gen_product_doc_word.py
    python scripts/gen_product_doc_word.py --output docs/MyName.docx
"""

import argparse
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("ERROR: python-docx not installed. Run: pip install python-docx", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# ─── Brand palette (matches generators/generate_word_doc.py) ──────────────────
NAVY       = RGBColor(0x1F, 0x4E, 0x79)
BLUE       = RGBColor(0x2E, 0x74, 0xB5)
TEAL       = RGBColor(0x00, 0x70, 0xC0)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY  = RGBColor(0x40, 0x40, 0x40)
MUTED_GRAY = RGBColor(0x6B, 0x6B, 0x6B)
ALT_ROW    = RGBColor(0xF2, 0xF7, 0xFD)
ACCENT_BG  = RGBColor(0xDD, 0xEB, 0xF7)
GOOD_BG    = RGBColor(0xE2, 0xEF, 0xDA)
GOOD_FG    = RGBColor(0x2D, 0x6A, 0x0C)
WARN_BG    = RGBColor(0xFF, 0xF2, 0xCC)
WARN_FG    = RGBColor(0xB0, 0x66, 0x0A)
OFF_BG     = RGBColor(0xEF, 0xF2, 0xF7)
OFF_FG     = RGBColor(0x6B, 0x7A, 0x9A)

PHASE_COLORS = [
    RGBColor(0x1E, 0x5F, 0xA8),  # pull
    RGBColor(0x0C, 0x8A, 0x7C),  # analyze
    RGBColor(0x7B, 0x4F, 0xAB),  # enrich
    RGBColor(0xC9, 0x70, 0x0E),  # document
    RGBColor(0x2D, 0x6A, 0x0C),  # generate
]


def shade_cell(cell, rgb: RGBColor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "%02X%02X%02X" % (rgb[0], rgb[1], rgb[2]))
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_border_color(cell, rgb: RGBColor):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")
        el.set(qn("w:color"), "%02X%02X%02X" % (rgb[0], rgb[1], rgb[2]))
        borders.append(el)
    tcPr.append(borders)


def add_heading1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single")
    top.set(qn("w:sz"), "6")
    top.set(qn("w:space"), "6")
    top.set(qn("w:color"), "1F4E79")
    pBdr.append(top)
    pPr.append(pBdr)
    run = p.add_run(text)
    run.font.size = Pt(17)
    run.font.bold = True
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"
    return p


def add_heading2(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = BLUE
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    return p


def add_heading3(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = TEAL
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    return p


def add_body(doc, text, italic=False, muted=False, bold_lead=None):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead + " ")
        r.font.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = DARK_GRAY
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.italic = italic
    run.font.color.rgb = MUTED_GRAY if muted else DARK_GRAY
    p.paragraph_format.space_after = Pt(6)
    return p


def add_bullets(doc, items, ordered=False):
    style = "List Number" if ordered else "List Bullet"
    for item in items:
        p = doc.add_paragraph(style=style)
        if isinstance(item, tuple):
            lead, rest = item
            r = p.add_run(lead + " ")
            r.font.bold = True
            r.font.size = Pt(10.5)
            r.font.color.rgb = DARK_GRAY
            run = p.add_run(rest)
        else:
            run = p.add_run(item)
        run.font.size = Pt(10.5)
        run.font.color.rgb = DARK_GRAY
        p.paragraph_format.space_after = Pt(3)


def add_code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.left_indent = Inches(0.15)
    shade_cell_p(p)
    for i, line in enumerate(text.strip("\n").split("\n")):
        if i:
            p.add_run().add_break()
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        run.font.color.rgb = DARK_GRAY
    return p


def shade_cell_p(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F5F5F5")
    pPr.append(shd)


def add_table(doc, headers, rows, col_widths=None, cell_badges=None):
    """cell_badges: optional dict {(row_idx, col_idx): (bg, fg)} for status pills."""
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(9.5)
        shade_cell(hdr[i], NAVY)
    for r_i, row in enumerate(rows):
        cells = t.add_row().cells
        for c_i, val in enumerate(row):
            cells[c_i].text = ""
            p = cells[c_i].paragraphs[0]
            run = p.add_run(val)
            run.font.size = Pt(9.5)
            badge = (cell_badges or {}).get((r_i, c_i))
            if badge:
                bg, fg = badge
                run.font.color.rgb = fg
                run.font.bold = True
                shade_cell(cells[c_i], bg)
            else:
                run.font.color.rgb = DARK_GRAY
            if r_i % 2 == 1 and not badge:
                shade_cell(cells[c_i], ALT_ROW)
    if col_widths:
        for row in t.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    return t


def add_overview_diagram(doc):
    """The sources -> spec -> targets summary diagram, rendered once by
    scripts/gen_product_diagram.py and reused identically in the .md and the
    HTML artifact — embedded here as an actual picture, not a table mockup."""
    image_path = ROOT / "docs" / "assets" / "migraite_diagram.png"
    if not image_path.is_file():
        add_body(doc, "[Diagram missing — run: python scripts/gen_product_diagram.py]", italic=True, muted=True)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Inches(6.2))
    p.paragraph_format.space_after = Pt(4)

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(
        "Every source funnels into the same neutral spec; every target is generated from it. "
        "A sixth source works with all four targets on day one — no new translator pairs to write."
    )
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = MUTED_GRAY
    cap.paragraph_format.space_after = Pt(14)


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
    run = p.add_run("Product Documentation")
    run.font.size = Pt(15)
    run.font.color.rgb = BLUE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("AI-powered integration migration agent — built by TechStone LLC\non top of the Boomi Companion (bc-integration) skill")
    run.font.size = Pt(10.5)
    run.font.italic = True
    run.font.color.rgb = MUTED_GRAY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    run = p.add_run("Reflects the codebase as of 2026-09-15")
    run.font.size = Pt(9)
    run.font.color.rgb = MUTED_GRAY

    doc.add_page_break()

    # ─── 1. Overview ────────────────────────────────────────────────────────
    add_heading1(doc, "1. Executive Overview")

    add_heading2(doc, "1.1 The problem")
    add_body(doc, "Every iPaaS migration is normally a manual re-implementation project: an integrator reads the old flow, mentally reverse-engineers its intent, and rebuilds it by hand in the new tool. That process is slow, inconsistent between integrators, and loses tribal knowledge that was never written down.")

    add_heading2(doc, "1.2 What MigrAIte does")
    add_body(doc, "MigrAIte automates the reverse-engineering and re-implementation steps around a platform-agnostic intermediate representation (the migration spec). A flow is first parsed out of its source platform into that neutral JSON representation, independent of any target, and only then translated into the target platform's native format — the same \"compiler front-end / back-end\" split used in real compilers.")

    add_heading2(doc, "1.3 How it works, at a glance")
    add_overview_diagram(doc)

    add_heading2(doc, "1.4 Supported platforms")
    platform_rows = [
        ("Source (pull + analyze)", "Boomi", "Production"),
        ("", "MuleSoft", "Built — pre-production"),
        ("", "Workato", "Production"),
        ("", "Celigo", "Built — pre-production"),
        ("", "webMethods.io / webMethods IS", "Production"),
        ("", "Oracle SOA Suite / EBS", "Analyzer only, not CLI-wired"),
        ("Target (generate + push)", "Boomi", "Production"),
        ("", "Workato", "Production"),
        ("", "Celigo", "Built — pre-production"),
        ("", "webMethods.io", "Built — pre-production"),
        ("", "MuleSoft", "Source-only"),
        ("Roadmap", "SAP · Azure Logic Apps", "Planned"),
    ]
    STATUS_BADGE = {
        "Production": (GOOD_BG, GOOD_FG),
        "Built — pre-production": (WARN_BG, WARN_FG),
        "Analyzer only, not CLI-wired": (WARN_BG, WARN_FG),
        "Source-only": (OFF_BG, OFF_FG),
        "Planned": (OFF_BG, OFF_FG),
    }
    badges = {}
    rows = []
    for i, (role, platform, status) in enumerate(platform_rows):
        rows.append((role, platform, status))
        bg_fg = STATUS_BADGE.get(status)
        if bg_fg:
            badges[(i, 2)] = bg_fg
    add_table(doc, ["Role", "Platform", "Status"], rows, col_widths=[1.8, 2.6, 2.0], cell_badges=badges)

    add_heading2(doc, "1.5 How a migration is delivered")
    add_table(
        doc,
        ["Surface", "Who uses it", "What it's for"],
        [
            ("migrate.py CLI", "Engineers, CI pipelines", "Scriptable, reproducible, flag-driven migrations"),
            ("MigrAIte (Streamlit app)", "Non-technical stakeholders, demos", "Drag-and-drop a package zip or Drive link; watch the pipeline run live"),
            ("Google Chat bot", "Teams collaborating async in Chat", "Kick off and monitor a migration from a Chat thread"),
        ],
        col_widths=[1.8, 2.4, 2.2],
    )

    add_heading2(doc, "1.6 What comes out the other end")
    add_bullets(doc, [
        "The migrated artifacts themselves — pushed live to the target platform (or written to disk with --dry-run).",
        "A platform-agnostic migration spec (migration-specs/<project>.json) — a durable, diffable record of what the source flow did.",
        "A branded Word design document (migration-specs/<project>_design_document.docx) for stakeholders.",
        "A gap/fidelity report — anything that can't be mapped 1:1 is flagged explicitly, never silently guessed at.",
    ])

    # ─── 2. Quickstart ──────────────────────────────────────────────────────
    add_heading1(doc, "2. Quickstart")
    add_body(doc, "No credentials required — this walks through a dry run against a bundled sample project.")

    add_heading3(doc, "1. Install dependencies")
    add_code(doc, "pip install -r requirements.txt")

    add_heading3(doc, "2. Copy the environment template")
    add_body(doc, "Only needed once you move past dry-run.")
    add_code(doc, "cp .env.example .env")

    add_heading3(doc, "3. Run a dry-run migration against a bundled sample")
    add_code(doc, "python migrate.py --from mulesoft --source-dir samples/mulesoft/customer-api/ --to workato --dry-run")

    add_heading3(doc, "4. What you'll see")
    add_body(doc, "One [PHASE]-tagged block per stage as it runs:")
    add_code(doc, """[PULL] Source files already on disk - skipping pull.
[ANALYZE] Parsing samples/mulesoft/customer-api/ ...
[ANALYZE] Wrote migration-specs/customer-api.json (3 flows, 1 gap)
[ENRICH] Generic enrichment pass ...
[DOCUMENT] Wrote migration-specs/customer-api_design_document.docx
[GENERATE] Dry run - Workato recipe JSON printed below, not pushed.""")

    add_heading3(doc, "5. Inspect the output, then go live")
    add_body(doc, "Open migration-specs/customer-api.json (the spec — see §7) and migration-specs/customer-api_design_document.docx (the stakeholder summary). Once WORKATO_API_TOKEN / WORKATO_EMAIL are in .env, drop --dry-run to push for real.")

    # ─── 3. Core Concepts ───────────────────────────────────────────────────
    add_heading1(doc, "3. Core Concepts")
    add_body(doc, "The vocabulary this document uses precisely:")
    add_table(
        doc,
        ["Term", "Meaning"],
        [
            ("Migration spec", "The platform-agnostic JSON file every analyzer produces and every generator consumes. Has no target-specific concepts in it."),
            ("Analyzer", "A phase-2 script that parses one source platform's native format into a migration spec."),
            ("Enricher", "A phase-3 script that runs an LLM pass over the spec to resolve logic a static parser can't."),
            ("Generator", "A phase-4/5 script that compiles a spec into one target platform's native format and pushes it live."),
            ("Phase", "One of the five pipeline stages. Every run executes all five unless an operator explicitly skips one."),
            ("Integration / flow", "One migratable unit inside a spec's integrations[] array."),
            ("Gap", "An entry in gaps[]: something that couldn't be mapped with full confidence — never silently guessed at."),
            ("Fidelity score", "An informal measure of how much of a source flow's behavior survived the round trip."),
            ("Session continuity", "The convention that a project's spec and progress notes persist across sessions."),
        ],
        col_widths=[1.7, 4.7],
    )

    # ─── 4. Pipeline ────────────────────────────────────────────────────────
    add_heading1(doc, "4. The Five-Phase Pipeline")
    add_body(doc, "Every migration — run through migrate.py, the Streamlit app, or the Chat bot — goes through the same five phases. No phase is ever skipped implicitly; skipping is only ever an explicit flag chosen by the operator.")

    add_table(
        doc,
        ["#", "Phase", "What happens", "Skip flag"],
        [
            ("1", "PULL", "If the source is a live platform, fetch components to local disk. MuleSoft/webMethods projects are usually already on disk.", "--skip-pull"),
            ("2", "ANALYZE", "Run the analyzer matching --from. Parses the platform's native format into migration-specs/<project>.json.", "--skip-analyze"),
            ("3", "ENRICH", "An LLM (Claude) pass that expands logic a static parser can't fully resolve. webMethods gets a dedicated deep pass.", "--skip-enrich"),
            ("4", "DOCUMENT", "Generates a TechStone-branded Word design document for non-technical reviewers.", "--skip-document"),
            ("5", "GENERATE", "Run the generator matching --to. Translates the spec into the target format and pushes it live unless --dry-run.", "not skippable"),
        ],
        col_widths=[0.35, 0.95, 3.9, 1.2],
    )

    add_heading2(doc, "4.1 Why the spec is the center of gravity, not either platform")
    add_body(doc, "Why this matters: because the spec is neutral, it's reusable. A webMethods package analyzed once has been generated into Workato six separate times across different sessions in this project's history — none of which required re-running the analyzer against webMethods again. The expensive, fragile part happens once; regenerating into a different shape, or a different target platform entirely, is cheap.", italic=True)

    # ─── 5. Architecture ────────────────────────────────────────────────────
    add_heading1(doc, "5. Architecture & Repository Layout")
    add_code(doc, """iPaaS-Migration/
  migrate.py                 - single-command CLI, orchestrates all 5 phases
  app.py                     - "MigrAIte" Streamlit UI (branded, drag-and-drop)
  analyzers/                 - phase 2, one file per SOURCE platform
    analyze_boomi.py
    analyze_mulesoft.py
    analyze_workato.py
    analyze_celigo.py
    analyze_webmethods.py
    analyze_oracle_soa.py     - standalone, not yet CLI-wired
  enrichers/                 - phase 3, AI enrichment
    enrich_spec.py            - generic pass
    enrich_webmethods.py      - deep webMethods-specific pass
  generators/                - phases 4 & 5, one file per TARGET (+ Word doc)
    generate_boomi.py
    generate_workato.py
    generate_workato_from_wm.py
    generate_celigo.py
    generate_webmethods.py
    generate_word_doc.py
  migration-specs/           - canonical specs, Word docs, progress notes
  active-development/        - staged source artifacts (gitignored)
  Workato/Companion/         - workato-integration skill + RecipeComponents
  WebMethods/                - webMethods analysis output + mapping Excel files
  gchat/                     - Google Chat bot surface (Claude Agent SDK + Pub/Sub)
  logos/                     - TechStone branding assets""")

    add_heading2(doc, "5.1 Built on Boomi Companion")
    add_body(doc, "This workspace is Boomi-oriented first: all Boomi-side platform operations go through the boomi-integration skill's shell scripts, never hand-rolled curl. A custom curl against the Boomi API is treated as a stop-and-discuss event, not a thing to just do.")

    add_heading2(doc, "5.2 Tech stack")
    add_table(
        doc,
        ["Concern", "Technology"],
        [
            ("Core pipeline", "Python 3, requests, python-dotenv"),
            ("AI enrichment", "Anthropic API (anthropic SDK)"),
            ("Streamlit UI", "streamlit"),
            ("Design docs", "openpyxl (Excel mapping sheets), Word generation via python-docx"),
            ("Boomi platform ops", "Bash scripts from the boomi-integration skill"),
            ("Google Chat bot", "claude-agent-sdk, google-cloud-pubsub, google-api-python-client"),
        ],
        col_widths=[1.8, 4.6],
    )

    # ─── 6. Usage ───────────────────────────────────────────────────────────
    add_heading1(doc, "6. Using MigrAIte")
    add_heading2(doc, "6.1 Single-command CLI (migrate.py)")
    add_code(doc, "python migrate.py --from <source> --to <target> [options]")

    add_table(
        doc,
        ["Flag", "Type / default", "Purpose"],
        [
            ("--from / --to", "choice, required", "Source / target platform — MuleSoft is source-only"),
            ("--boomi-folder", "string", "Pull live from this Boomi folder (exclusive with --source-dir)"),
            ("--source-dir", "path", "Use local files already on disk instead of pulling"),
            ("--project", "string, default = dir name", "Name used for the spec file and output naming"),
            ("--dest-name", "string, default = MIG_<project>", "Target-side folder/project name"),
            ("--dry-run", "flag, default false", "Generate target artifacts without pushing them live"),
            ("--skip-pull / -analyze / -enrich / -document", "flag, default false", "Skip an individual phase"),
            ("--md-dir", "path", "Attach a directory of .md analysis files as a Word doc appendix"),
        ],
        col_widths=[2.2, 1.9, 2.5],
    )

    add_code(doc, """# Boomi folder -> Workato, full pipeline, live push
python migrate.py --from boomi --boomi-folder "MIG_CustomerAPI" --to workato

# webMethods package -> Workato, with AI enrichment + Word doc
python migrate.py --from webmethods --source-dir active-development/wm_upload/extracted \\
  --to workato --project mypackage

# Dry run - inspect generated JSON without touching the target platform
python migrate.py --from boomi --boomi-folder "My Folder" --to workato --dry-run

# Resume a session - skip pull + analyze, reuse an existing spec
python migrate.py --from boomi --to workato --project my-proj --skip-pull --skip-analyze""")

    add_heading2(doc, "6.2 Running one phase at a time")
    add_body(doc, "Useful when iterating on a single phase without re-running the whole pipeline.")
    add_code(doc, """# Analyze only
python analyzers/analyze_webmethods.py <source-dir> --project <name>

# Enrich only
python enrichers/enrich_webmethods.py migration-specs/<proj>.json --source-dir <dir>

# Generate only
python generators/generate_workato.py migration-specs/my-project.json --dry-run""")

    add_heading2(doc, "6.3 MigrAIte (Streamlit app)")
    add_body(doc, "python -m streamlit run app.py — a branded, non-technical front end for the same pipeline. Upload a source package as a zip (or paste a Google Drive share link), pick source and target, toggle dry-run / skip-analyze / skip-enrich / skip-document, and watch the five phases run live.")

    add_heading2(doc, "6.4 Google Chat bot")
    add_body(doc, "python -m gchat.bot runs a Pub/Sub pull loop — Google never calls this machine; events are pulled, and replies go out as HTTPS calls to the Chat API. Current constraint: one active migration globally at a time — a demo-stage limit, not an architectural one.")

    # ─── 7. Migration spec reference ────────────────────────────────────────
    add_heading1(doc, "7. The Migration Spec — Schema Reference")
    add_body(doc, "Every analyzer emits, and every generator consumes, a spec with the same shape (schema_version: \"1.0\"). The fields below are pulled directly from a real spec produced by analyze_workato.py — not an aspirational sketch.")

    add_heading2(doc, "7.1 Top-level fields")
    add_table(
        doc,
        ["Field", "Type", "Description"],
        [
            ("schema_version", "string", 'Spec format version (currently "1.0")'),
            ("source_system", "string", 'Platform analyzed from, e.g. "workato", "boomi"'),
            ("project_name", "string", "Matches the --project value at analyze time"),
            ("summary", "object", "Roll-up counts — flows, connections, gaps found, complexity"),
            ("connections", "array", "Reusable connections referenced by the flows"),
            ("integrations", "array", "One entry per migratable flow (trigger, steps, error handling)"),
            ("gaps", "array", "Everything that couldn't be mapped with full confidence"),
            ("migration_notes", "array", "Free-text operator notes carried through from analysis"),
        ],
        col_widths=[1.6, 0.9, 3.9],
    )

    add_heading2(doc, "7.2 Each gaps[] entry")
    add_table(
        doc,
        ["Field", "Description"],
        [
            ("source_ref", 'Traceable pointer back into the source, e.g. "AIMigrationTest5:step-1"'),
            ("behavioral_difference", "What's not guaranteed to carry over 1:1"),
            ("suggested_resolution", "A concrete next action — often a specific skill script to run"),
            ("severity", '"low" / "medium" / "high"'),
            ("decision_required / auto_resolved", "Whether a human must choose, and whether enrichment closed it automatically"),
        ],
        col_widths=[2.0, 4.4],
    )

    add_heading2(doc, "7.3 Real example (trimmed)")
    add_code(doc, """{
  "schema_version": "1.0",
  "source_system": "workato",
  "project_name": "aimigrationtest5",
  "summary": { "total_flows": 1, "gaps_found": 2, "overall_complexity": "medium" },
  "integrations": [{
    "name": "AIMigrationTest5",
    "flow_type": "scheduled",
    "trigger": { "type": "scheduler", "workato_provider": "clock",
                 "schedule": { "time_unit": "days", "trigger_every": "1" } },
    "steps": [{
      "type": "connector_action", "sequence": 1, "requires_review": true,
      "severity": "medium",
      "behavioral_difference": "Workato connector action - verify Boomi has equivalent native connector before using REST.",
      "suggested_resolution": "Run boomi-component-search.sh; if none found, use REST with custom auth."
    }],
    "error_handling": { "has_error_handler": false, "strategies": [] }
  }]
}""")
    add_body(doc, 'This is the actual spec behind the "AIMigrationTest5" migration referenced in §12 — a connector step the Workato API didn’t expose enough metadata about, flagged rather than guessed at, with an explicit next action.')

    add_heading2(doc, "7.4 Naming convention")
    add_code(doc, """MIG_<SourceSystem>_<FlowName>_<ComponentType>

MIG_MS_GetCustomers_Process
MIG_MS_PostgreSQL_Connection
MIG_MS_CustomerResponse_JSON_Profile""")
    add_body(doc, "Boomi-side folder structure: ClaudeCode/MIG_<ProjectName>/")

    add_heading2(doc, "7.5 Session continuity")
    add_bullets(doc, [
        "Check migration-specs/ for an existing spec before starting — don't re-analyze if one already exists and source files haven't changed.",
        "Resume from wherever the last session left off.",
        "After each generation session, record done/pending/blocked flows in migration-specs/<project>_progress.md.",
    ])

    # ─── 8. Guardrails ──────────────────────────────────────────────────────
    add_heading1(doc, "8. Operating Rules & Guardrails")
    add_body(doc, "Hard constraints on how MigrAIte touches a live Boomi account — not suggestions.")
    add_bullets(doc, [
        "Never hand-roll curl against the Boomi API. All Boomi operations go through the boomi-integration skill's .sh scripts; needing custom curl is a stop-and-discuss moment.",
        "Auth errors halt, they don't retry. A Boomi auth failure stops the session for a human — repeated bad-credential calls risk an account lockout.",
        "Connector discovery before generation. The account's live native connectors are checked before designing a Boomi-target integration; generic REST is the fallback, never the default.",
        "Credentials stay out of the conversation where possible. Production credentials are pulled pre-encrypted from the platform GUI rather than typed into component XML by hand.",
        ".env is never read directly. Shell scripts load it internally via source .env, keeping secrets out of the agent's context window.",
        "Component IDs are account-scoped. A fresh account means first-time pushes use boomi-component-create.sh, not -push.sh.",
    ], ordered=True)

    # ─── 9. Security ────────────────────────────────────────────────────────
    add_heading1(doc, "9. Security & Credential Handling")
    add_body(doc, "Two categories of secret: platform API credentials (Boomi, Workato, Anthropic) and the source/target systems' own connection credentials referenced inside generated components.")
    add_body(doc, "Platform API credentials live in .env and are never read by the agent directly — every CLI script loads them internally via source .env inside its own subprocess.", bold_lead="")
    add_body(doc, "Connection credentials inside migrated components follow a strict preference order:")
    add_bullets(doc, [
        "Pull from platform (preferred). Production credentials are configured once in the GUI, then the pre-encrypted value is pulled down — the plaintext secret never enters the conversation.",
        "User-provided (acceptable). A credential shared directly in conversation can be used, with a reminder of option 1 if it looks like a production secret.",
        "Never recited back. Credentials are avoided in plans, summaries, or overviews, since those can be visible during screen sharing.",
    ], ordered=True)
    add_body(doc, "Account portability: a migration spec is reusable across Boomi accounts, but pushed component IDs are not — a fresh account's first push uses boomi-component-create.sh, which mints new IDs.")

    # ─── 10. Troubleshooting ────────────────────────────────────────────────
    add_heading1(doc, "10. Troubleshooting & FAQ")
    faqs = [
        ("I got a Boomi auth error mid-run — why did it just stop?",
         "By design. Repeated bad-credential calls risk an account lockout, so an auth failure halts the session for a human rather than retrying automatically. Run boomi-env-check.sh, then boomi-folder-create.sh --test-connection."),
        ("curl failed with exit code 35 (SSL handshake failure).",
         "Almost always corporate SSL-inspection middleware (Zscaler, Netskope, Cisco Umbrella) or a VPN intercepting the TLS handshake — check that before troubleshooting further."),
        ('I got "ComponentId invalid" when pushing to Boomi.',
         "No sync state exists for that component yet — usually the first push on a new account. Use boomi-component-create.sh, not -push.sh."),
        ("I'm resuming a migration on a different Boomi account.",
         "Component/folder IDs from the old account don't exist on the new one. Re-run credential setup and connector discovery, but don't re-analyze — the spec is account-agnostic and can go straight to generate."),
        ("A parallel branch ran sequentially after migrating to Boomi.",
         "Known, flagged gap: BPEL <flow> (true parallel execution) maps to a Boomi Branch shape, which executes its paths sequentially — recorded in gaps[], not silently dropped."),
    ]
    for q, a in faqs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run("Q: " + q)
        run.font.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = NAVY
        add_body(doc, a, muted=True)

    # ─── 11. Environment ────────────────────────────────────────────────────
    add_heading1(doc, "11. Required Environment / Credentials")
    add_body(doc, "Set in .env (never read directly by the agent — loaded internally by the CLI scripts). See .env.example for the full annotated list.")
    add_table(
        doc,
        ["Platform", "Key variables"],
        [
            ("Boomi", "Configured during Boomi Companion setup"),
            ("Workato", "WORKATO_API_TOKEN, WORKATO_EMAIL"),
            ("Anthropic (LLM enrichment)", "ANTHROPIC_API_KEY"),
        ],
        col_widths=[2.2, 4.2],
    )
    add_body(doc, "Credential health checks: bash <skill-path>/scripts/boomi-env-check.sh and bash <skill-path>/scripts/boomi-folder-create.sh --test-connection.")

    # ─── 12. Track record ───────────────────────────────────────────────────
    add_heading1(doc, "12. Track Record")
    add_body(doc, "MigrAIte has moved real flows across every supported direction, including production webMethods IS packages for a banking client (payment routing, compliance checks against Oracle) into both Workato and Boomi, a Workato-authored Salesforce-to-NetSuite sync into Boomi, and a full Oracle SOA Suite/BPEL sample suite into Boomi at an 80% automated-fidelity score. Every run leaves behind its spec, its design document, and an explicit list of what still needs a human — nothing is migrated by silent guesswork.")

    # ─── 13. Roadmap ────────────────────────────────────────────────────────
    add_heading1(doc, "13. Roadmap")
    add_body(doc, "To be defined.", italic=True, muted=True)

    doc.save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate the MigrAIte product documentation Word doc.")
    ap.add_argument("--output", default=str(ROOT / "docs" / "PRODUCT_DOCUMENTATION.docx"))
    args = ap.parse_args()
    build(args.output)
