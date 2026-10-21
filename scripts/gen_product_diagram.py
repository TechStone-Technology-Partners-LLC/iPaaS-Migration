#!/usr/bin/env python3
"""
Renders the "5 sources -> 1 migration spec -> 4 targets" summary diagram
as a single PNG, reused identically across:
  - docs/PRODUCT_DOCUMENTATION.md   (as an image, not mermaid syntax)
  - docs/PRODUCT_DOCUMENTATION.docx (embedded picture, via gen_product_doc_word.py)
  - the published HTML artifact      (as a base64 data URI)

One rendered asset, three deliverables, identical everywhere it appears —
no dependency on a viewer's mermaid support or inline-SVG CSS var() handling.

Usage:
    python scripts/gen_product_diagram.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "migraite_diagram.png"
FONTS = Path("C:/Windows/Fonts")

SCALE = 3  # supersample for crisp anti-aliased edges, then downscale
W, H = 1600, 700

# ─── Brand palette (light theme, baked in — a raster export can't be theme-aware) ──
WHITE       = (255, 255, 255)
SURFACE_2   = (234, 240, 250)
BORDER      = (185, 198, 222)
BORDER_SOFT = (217, 226, 242)
TEXT        = (22, 35, 63)
TEXT_MUTED  = (91, 107, 140)
ACCENT      = (30, 95, 168)
ACCENT_TINT = (228, 238, 251)
ACCENT_STRONG = (18, 63, 110)

PHASE_COLORS = [
    (30, 95, 168),    # pull
    (12, 138, 124),   # analyze
    (123, 79, 171),   # enrich
    (201, 112, 14),   # document
    (45, 106, 12),    # generate
]


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * SCALE)


F_LABEL   = font("consola.ttf", 15)
F_PILL    = font("calibrib.ttf", 20)
F_EYEBROW = font("consola.ttf", 15)
F_SUBTITLE = font("calibrib.ttf", 21)
F_CAPTION = font("consola.ttf", 15)
F_TAGLINE = font("calibrii.ttf", 17)
F_FOOT    = font("calibrii.ttf", 15)


def s(v):
    return v * SCALE


def text_center(draw, cx, y, txt, fnt, fill, tracking=0):
    if tracking:
        txt = (" " * 0).join(txt)  # no-op placeholder; tracking applied via spaced draw below
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), txt, font=fnt, fill=fill)


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=s(radius), fill=fill, outline=outline, width=s(width))


def cubic_bezier(p0, p1, p2, p3, steps=48):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((s(x), s(y)))
    return pts


def connector(draw, start, end, color=BORDER, width=2):
    mid_x = (start[0] + end[0]) / 2
    p0, p1, p2, p3 = start, (mid_x, start[1]), (mid_x, end[1]), end
    pts = cubic_bezier(p0, p1, p2, p3)
    draw.line(pts, fill=color, width=s(width), joint="curve")


def build():
    canvas = Image.new("RGB", (s(W), s(H)), WHITE)
    d = ImageDraw.Draw(canvas)

    # ── layout ──────────────────────────────────────────────────────────────
    sources = ["Boomi", "MuleSoft", "Workato", "Celigo", "webMethods"]
    targets = ["Boomi", "Workato", "Celigo", "webMethods.io"]

    src_x, src_w = 60, 400
    tgt_x, tgt_w = 1140, 400
    pill_h = 78
    pill_gap = 26

    src_ys = [110 + i * (pill_h + pill_gap) for i in range(len(sources))]
    tgt_total = len(targets) * pill_h + (len(targets) - 1) * pill_gap
    tgt_start = (H - tgt_total) / 2
    tgt_ys = [tgt_start + i * (pill_h + pill_gap) for i in range(len(targets))]

    spec_x, spec_w = 620, 360
    spec_y, spec_h = 100, 500

    # ── containers ───────────────────────────────────────────────────────────
    rounded_rect(d, (s(src_x - 10), s(src_ys[0] - 40), s(src_x + src_w + 10), s(src_ys[-1] + pill_h + 30)),
                 radius=16, fill=SURFACE_2, outline=BORDER_SOFT, width=2)
    rounded_rect(d, (s(tgt_x - 10), s(tgt_ys[0] - 40), s(tgt_x + tgt_w + 10), s(tgt_ys[-1] + pill_h + 30)),
                 radius=16, fill=SURFACE_2, outline=BORDER_SOFT, width=2)

    text_center(d, s(src_x + src_w / 2), s(src_ys[0] - 34), "SOURCES", F_LABEL, TEXT_MUTED)
    text_center(d, s(tgt_x + tgt_w / 2), s(tgt_ys[0] - 34), "TARGETS", F_LABEL, TEXT_MUTED)

    # ── connectors (drawn before pills so pill fills sit on top of line ends) ─
    fan_in_ys = [160, 255, 350, 445, 540][: len(sources)]
    fan_out_ys = [200, 313, 427, 540][: len(targets)]
    for i, y0 in enumerate(src_ys):
        start = (src_x + src_w, y0 + pill_h / 2)
        end = (spec_x, fan_in_ys[i])
        connector(d, start, end)
    for j, y0 in enumerate(tgt_ys):
        start = (spec_x + spec_w, fan_out_ys[j])
        end = (tgt_x, y0 + pill_h / 2)
        connector(d, start, end)

    # ── spec node ────────────────────────────────────────────────────────────
    rounded_rect(d, (s(spec_x), s(spec_y), s(spec_x + spec_w), s(spec_y + spec_h)),
                 radius=22, fill=ACCENT_TINT, outline=ACCENT, width=2)
    cx = spec_x + spec_w / 2
    text_center(d, s(cx), s(170), "MIGRATION SPEC", F_EYEBROW, ACCENT_STRONG)
    text_center(d, s(cx), s(212), "Platform-agnostic JSON", F_SUBTITLE, TEXT)

    dot_y = 320
    dot_xs = [cx - 100, cx - 50, cx, cx + 50, cx + 100]
    d.line([(s(dot_xs[0] - 8), s(dot_y)), (s(dot_xs[-1] + 8), s(dot_y))], fill=BORDER, width=s(3))
    for x, color in zip(dot_xs, PHASE_COLORS):
        r = 10
        d.ellipse((s(x - r), s(dot_y - r), s(x + r), s(dot_y + r)), fill=color)
    text_center(d, s(cx), s(360), "5-PHASE PIPELINE", F_CAPTION, TEXT_MUTED)
    text_center(d, s(cx), s(430), "Target-neutral by design", F_TAGLINE, TEXT_MUTED)

    # ── pills ────────────────────────────────────────────────────────────────
    for name, y0 in zip(sources, src_ys):
        rounded_rect(d, (s(src_x), s(y0), s(src_x + src_w), s(y0 + pill_h)),
                     radius=10, fill=WHITE, outline=BORDER_SOFT, width=2)
        text_center(d, s(src_x + src_w / 2), s(y0 + pill_h / 2 - 13), name, F_PILL, TEXT)

    for name, y0 in zip(targets, tgt_ys):
        rounded_rect(d, (s(tgt_x), s(y0), s(tgt_x + tgt_w), s(y0 + pill_h)),
                     radius=10, fill=WHITE, outline=BORDER_SOFT, width=2)
        text_center(d, s(tgt_x + tgt_w / 2), s(y0 + pill_h / 2 - 13), name, F_PILL, TEXT)

    # ── caption ──────────────────────────────────────────────────────────────
    caption = "Every source funnels into the same neutral spec; every target is generated from it — no new translator pairs to write."
    text_center(d, s(W / 2), s(H - 34), caption, F_FOOT, TEXT_MUTED)

    canvas = canvas.resize((W * 2, H * 2), Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, optimize=True)
    print(f"Wrote {OUT} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    build()
