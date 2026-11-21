#!/usr/bin/env python3
"""Build the v3 front page for news-image-20261121 (offline, PIL only).

Fixes exactly one defect of v2 (see VERIFY-REPORT.md / coordinator note):
in v2 the colour-block banners were painted ON TOP of the scenes (the
card banner covered the top 15 px of a 36 px scene strip = 42% of the
artwork), and the scene functions drew with absolute coordinates meant
for a 326x110 hero frame, so inside a 243x36 card frame elements spilled
out of the frame and over neighbouring cards. The DATE CHECK box was
also 36 px tall while its text needed three 11 px-pitch lines from
dy+4, so the last line touched / crossed the bottom border.

v3 changes ONLY the construction, never the content:
  * every scene is drawn on its own tile of exactly the frame size
    (Image.new + its own ImageDraw), then pasted onto the page --
    clipping is guaranteed by construction, nothing can spill out;
  * the stack is strictly vertical: banner -> scene -> text, the
    banner never overlaps the scene;
  * card scenes are 60 px tall (was a 36 px strip) so the artwork
    reads; the vertical layout is re-budgeted to fit 1024x1024;
  * the DATE CHECK box is sized AFTER wrapping: box height =
    lines * pitch + top/bottom padding, so the text sits inside it
    with clearance from the border.
All 42 stories, headlines, decks, sources, briefs, numbers strip,
regions, map pins/dots and the DATE CHECK wording are identical to v2.

Run:  python3 build_v3.py            (writes entry-v3.png beside this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry-v3.png")

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (200, 16, 46)
RED_DARK = (160, 10, 34)
NAVY = (11, 37, 69)
NAVY_DARK = (7, 24, 48)
TEAL = (14, 124, 123)
GREEN = (46, 140, 66)
GOLD = (232, 163, 23)
PURPLE = (106, 76, 147)
TAN = (217, 196, 143)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIFB = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIFI = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANSB = lambda s: font("DejaVuSans-Bold.ttf", s)


def fit_text(draw, text, fname, size, max_w):
    """Largest font of the given family (down to 10) that fits max_w."""
    while size > 10:
        f = font(fname, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(fname, 10)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fname, size, max_w, max_lines, min_size):
    """Shrink the font (down to min_size) until the text wraps to at
    most max_lines; returns (font, lines). Text is never cut: if it
    still needs more lines at min_size the caller keeps max_lines
    lines, exactly as v2 did."""
    while size > min_size:
        f = font(fname, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font(fname, min_size)
    return f, wrap(draw, text, f, max_w)


def banner(d, x, y, w, h, text, size=20, fill=RED):
    """Giant colour-block banner with white capital text. Drawn on the
    page ABOVE the scene tile, never on top of it."""
    d.rectangle([x, y, x + w, y + h], fill=fill)
    f = fit_text(d, text, "DejaVuSans-Bold.ttf", size, w - 12)
    d.text((x + 7, y + (h - f.size) // 2 - 1), text, font=f, fill=WHITE)


def chip(d, x, y, text, size=11):
    """Small black tag with white text, drawn INSIDE a scene tile;
    returns its width."""
    f = SANSB(size)
    w = int(d.textlength(text, font=f)) + 12
    d.rectangle([x, y, x + w, y + size + 7], fill=BLACK)
    d.text((x + 6, y + 3), text, font=f, fill=WHITE)
    return w


def new_tile(w, h, bg):
    """A fresh tile of exactly the frame size, with its own draw
    context. Everything drawn here is clipped to the tile by
    construction."""
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


# ---------------------------------------------------------------- scenes
# Every scene draws on its own tile in LOCAL coordinates (origin 0,0,
# all positions as fractions of the tile width/height, radii as
# fractions of the tile height so circles stay circular). Nothing can
# leave the tile. Dark scenes always carry one big glowing element so
# they read at 300 px.

def scene_cop31(w, h):
    img, d = new_tile(w, h, (9, 61, 79))
    d.rectangle([0, int(0.78 * h), w, h], fill=(6, 38, 50))
    # pavilion roofline FIRST, so the clock and thermometer drawn after
    # it sit on top of it instead of being buried under it (v2 drew the
    # roofline last and it swallowed the clock whole)
    d.polygon([(0, h), (0.21 * w, 0.55 * h), (0.46 * w, h)],
              fill=(4, 26, 36))
    d.polygon([(0.46 * w, h), (0.70 * w, 0.50 * h), (w, h)],
              fill=(4, 26, 36))
    # glowing sun / heat disc, top right, fully inside
    cx, cy = 0.85 * w, 0.44 * h
    for rr, col in ((0.40, (232, 120, 42)), (0.32, (244, 160, 40)),
                    (0.24, (255, 205, 60))):
        r = rr * h
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # globe, left, raised clear of the bottom-left chip
    gx, gy = 0.16 * w, 0.42 * h
    d.ellipse([gx - 0.31 * h, gy - 0.31 * h, gx + 0.31 * h, gy + 0.31 * h],
              fill=(255, 220, 120))
    d.ellipse([gx - 0.27 * h, gy - 0.27 * h, gx + 0.27 * h, gy + 0.27 * h],
              fill=(38, 140, 210))
    d.ellipse([gx - 0.14 * h, gy - 0.18 * h, gx + 0.02 * h, gy - 0.02 * h],
              fill=(46, 160, 90))
    d.ellipse([gx - 0.03 * h, gy + 0.04 * h, gx + 0.15 * h, gy + 0.20 * h],
              fill=(46, 160, 90))
    # thermometer, centre, fully inside
    tx = 0.50 * w
    d.rounded_rectangle([tx, 0.16 * h, tx + 0.05 * w, 0.72 * h], 8,
                        fill=WHITE)
    d.ellipse([tx - 0.02 * w, 0.62 * h, tx + 0.07 * w, 0.86 * h], fill=RED)
    d.rectangle([tx + 0.015 * w, 0.24 * h, tx + 0.035 * w, 0.70 * h],
                fill=RED)
    # clock, bottom centre-right
    kx, ky, kr = 0.68 * w, 0.76 * h, 0.20 * h
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=WHITE,
              outline=INK, width=2)
    d.line([kx, ky, kx, ky - 0.13 * h], fill=INK, width=2)
    d.line([kx, ky, kx + 0.10 * h, ky + 0.04 * h], fill=INK, width=2)
    return img


def scene_riyadh(w, h):
    img, d = new_tile(w, h, (8, 14, 44))
    # stars
    for sx, sy in ((0.09, 0.16), (0.28, 0.09), (0.46, 0.22), (0.64, 0.11),
                   (0.83, 0.18), (0.18, 0.40), (0.55, 0.36), (0.92, 0.44)):
        d.ellipse([sx * w - 2, sy * h - 2, sx * w + 2, sy * h + 2],
                  fill=(255, 240, 180))
    # skyline, buildings as fractions of the tile width
    base = h
    for bx, bw, bh in ((0, 0.10, 0.42), (0.115, 0.08, 0.60),
                       (0.21, 0.12, 0.34), (0.345, 0.09, 0.68),
                       (0.45, 0.11, 0.46), (0.575, 0.09, 0.78),
                       (0.68, 0.10, 0.40), (0.79, 0.09, 0.56),
                       (0.89, 0.11, 0.36)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = base - bh * h
        d.rectangle([x0, y0, x1, base], fill=(2, 4, 14))
        wy = y0 + 0.08 * h
        while wy < base - 0.06 * h:
            wx = x0 + 0.015 * w
            while wx < x1 - 0.015 * w:
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 90))
                wx += 0.035 * w
            wy += 0.11 * h
    # glowing missile trails, endpoints kept inside the tile
    for (x0, y0, x1, y1) in ((0.12, 0.08, 0.46, 0.72),
                             (0.55, 0.04, 0.77, 0.64),
                             (0.80, 0.09, 0.92, 0.52)):
        d.line([x0 * w, y0 * h, x1 * w, y1 * h], fill=(255, 190, 60),
               width=4)
        d.line([x0 * w, y0 * h, x1 * w, y1 * h], fill=WHITE, width=2)
    # interception starbursts at the trail ends
    for cx, cy, r in ((0.46, 0.72, 0.16), (0.77, 0.64, 0.14),
                      (0.92, 0.52, 0.11)):
        for rr, col in ((r + 0.08, (255, 170, 40)),
                        (r, (255, 230, 120)), (r / 2, WHITE)):
            rr *= h
            d.ellipse([cx * w - rr, cy * h - rr, cx * w + rr, cy * h + rr],
                      fill=col)
    return img


def scene_peru(w, h):
    img, d = new_tile(w, h, (232, 114, 42))
    d.rectangle([0, h // 2, w, h], fill=(196, 138, 74))
    # sun glow, top right
    sx, sy = 0.83 * w, 0.30 * h
    d.ellipse([sx - 0.28 * h, sy - 0.28 * h, sx + 0.28 * h, sy + 0.28 * h],
              fill=(255, 236, 150))
    d.ellipse([sx - 0.18 * h, sy - 0.18 * h, sx + 0.18 * h, sy + 0.18 * h],
              fill=(255, 250, 210))
    # mountains
    d.polygon([(0, h), (0.28 * w, 0.31 * h), (0.58 * w, h)],
              fill=(96, 62, 32))
    d.polygon([(0.43 * w, h), (0.77 * w, 0.20 * h), (w, h)],
              fill=(70, 44, 22))
    d.polygon([(0.23 * w, 0.42 * h), (0.28 * w, 0.31 * h),
               (0.33 * w, 0.42 * h), (0.30 * w, 0.47 * h),
               (0.25 * w, 0.47 * h)], fill=WHITE)
    # house, bottom right on the mountainside, clear of the chip
    hx, hy = 0.62 * w, 0.62 * h
    d.rectangle([hx, hy, hx + 0.14 * w, hy + 0.24 * h], fill=WHITE)
    d.polygon([(hx - 0.01 * w, hy), (hx + 0.07 * w, hy - 0.16 * h),
               (hx + 0.15 * w, hy)], fill=RED_DARK)
    d.rectangle([hx + 0.055 * w, hy + 0.11 * h, hx + 0.085 * w,
                 hy + 0.24 * h], fill=(90, 50, 20))
    # big red seismograph across the lower middle, inside the tile
    pts = [(0.02, 0.55), (0.18, 0.55), (0.25, 0.30), (0.31, 0.72),
           (0.36, 0.24), (0.43, 0.68), (0.49, 0.40), (0.55, 0.55),
           (0.98, 0.55)]
    pts = [(fx * w, fy * h) for fx, fy in pts]
    d.line(pts, fill=RED, width=5)
    d.line(pts, fill=WHITE, width=1)
    # ground crack, bottom right
    d.line([(0.62 * w, 0.92 * h), (0.71 * w, 0.78 * h),
            (0.81 * w, 0.90 * h)], fill=(60, 36, 16), width=3)
    return img

def scene_kryvyi(w, h):
    img, d = new_tile(w, h, (18, 14, 26))
    base = h
    for bx, bw, bh in ((0, 0.18, 0.44), (0.21, 0.15, 0.57),
                       (0.38, 0.19, 0.37), (0.59, 0.17, 0.50),
                       (0.78, 0.21, 0.40)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = base - bh * h
        d.rectangle([x0, y0, x1, base], fill=(5, 4, 10))
        wy = y0 + 0.10 * h
        while wy < base - 0.07 * h:
            d.rectangle([x0 + 0.025 * w, wy, x0 + 0.05 * w, wy + 0.07 * h],
                        fill=(255, 214, 90))
            wy += 0.17 * h
    # fire glow, big layered flame, centre
    fx = 0.50 * w
    d.polygon([(fx - 0.14 * w, h), (fx - 0.04 * w, 0.30 * h),
               (fx + 0.02 * w, 0.55 * h), (fx + 0.07 * w, 0.26 * h),
               (fx + 0.14 * w, h)], fill=(255, 110, 20))
    d.polygon([(fx - 0.08 * w, h), (fx - 0.02 * w, 0.45 * h),
               (fx + 0.03 * w, 0.62 * h), (fx + 0.07 * w, 0.42 * h),
               (fx + 0.08 * w, h)], fill=(255, 200, 60))
    d.polygon([(fx - 0.035 * w, h), (fx, 0.62 * h), (fx + 0.035 * w, h)],
              fill=(255, 240, 140))
    # smoke, top
    for sx, sy, r in ((0.29, 0.28, 0.18), (0.45, 0.28, 0.18),
                      (0.66, 0.30, 0.16)):
        d.ellipse([sx * w - r * h, sy * h - r * h, sx * w + r * h,
                   sy * h + r * h], fill=(120, 118, 130))
    # ambulance cross glow, top right
    ax, ay = 0.88 * w, 0.22 * h
    d.ellipse([ax - 0.20 * h, ay - 0.20 * h, ax + 0.20 * h, ay + 0.20 * h],
              fill=WHITE)
    d.rectangle([ax - 0.05 * h, ay - 0.13 * h, ax + 0.05 * h, ay + 0.13 * h],
                fill=RED)
    d.rectangle([ax - 0.13 * h, ay - 0.05 * h, ax + 0.13 * h, ay + 0.05 * h],
                fill=RED)
    return img


def scene_davao(w, h):
    img, d = new_tile(w, h, (47, 155, 232))
    d.ellipse([0.03 * w, 0.10 * h, 0.25 * w, 0.37 * h], fill=WHITE)
    d.ellipse([0.70 * w, 0.20 * h, 0.94 * w, 0.43 * h], fill=WHITE)
    # runway
    d.rectangle([0, 0.80 * h, w, h], fill=(70, 70, 78))
    d.line([0.04 * w, 0.90 * h, 0.96 * w, 0.90 * h], fill=WHITE, width=2)
    # plane
    px, py = 0.16 * w, 0.20 * h
    d.polygon([(px, py + 0.20 * h), (px + 0.62 * w, py + 0.20 * h),
               (px + 0.69 * w, py + 0.30 * h),
               (px + 0.62 * w, py + 0.37 * h), (px, py + 0.37 * h)],
              fill=WHITE)
    d.polygon([(px + 0.40 * w, py + 0.20 * h), (px + 0.48 * w, py - 0.03 * h),
               (px + 0.53 * w, py + 0.20 * h)], fill=(200, 16, 46))
    d.polygon([(px + 0.62 * w, py + 0.20 * h), (px + 0.69 * w, py + 0.03 * h),
               (px + 0.71 * w, py + 0.20 * h)], fill=(200, 16, 46))
    d.polygon([(px + 0.25 * w, py + 0.37 * h), (px + 0.35 * w, py + 0.57 * h),
               (px + 0.40 * w, py + 0.37 * h)], fill=(220, 225, 235))
    # evacuation slide to the runway
    d.polygon([(px + 0.62 * w, py + 0.37 * h), (px + 0.72 * w, py + 0.37 * h),
               (px + 0.81 * w, 0.80 * h), (px + 0.76 * w, 0.80 * h)],
              fill=(255, 150, 30))
    return img


def scene_bitcoin(w, h):
    img, d = new_tile(w, h, (13, 27, 62))
    # gold coin, left
    cx, cy, r = 0.14 * w, 0.5 * h, 0.30 * h
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3],
              fill=(255, 214, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    # "B" drawn as a letter: the U+20BF glyph is missing (tofu) in this
    # DejaVu build, so the v2 coin showed an empty rectangle
    d.text((cx - 8, cy - 12), "B", font=SANSB(22), fill=WHITE)
    # falling chart, inside the tile
    pts = [(0.26, 0.13), (0.41, 0.23), (0.53, 0.17), (0.66, 0.40),
           (0.78, 0.50), (0.92, 0.83)]
    pts = [(fx * w, fy * h) for fx, fy in pts]
    d.line(pts, fill=(255, 70, 70), width=4)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE)
    # the drop, fully inside the tile (was cut off at the right edge in v2)
    d.text((0.58 * w, 0.78 * h), "-3.9%", font=SANSB(12),
           fill=(255, 90, 90))
    return img


def scene_rahul(w, h):
    img, d = new_tile(w, h, (46, 158, 79))
    d.rectangle([0.12 * w, 0.10 * h, 0.88 * w, 0.90 * h],
                fill=(196, 164, 110))
    # stumps, right
    sx = 0.79 * w
    for i in range(3):
        d.rectangle([sx + i * 0.03 * w, 0.17 * h, sx + i * 0.03 * w + 4,
                     0.43 * h], fill=(255, 220, 120))
    d.rectangle([sx - 0.01 * w, 0.13 * h, sx + 0.09 * w, 0.18 * h],
                fill=(255, 220, 120))
    # bat
    d.line([0.25 * w, 0.90 * h, 0.45 * w, 0.20 * h], fill=(150, 100, 50),
           width=9)
    d.line([0.45 * w, 0.20 * h, 0.50 * w, 0.07 * h], fill=(120, 80, 40),
           width=5)
    # ball
    d.ellipse([0.53 * w, 0.43 * h, 0.58 * w, 0.63 * h], fill=RED)
    d.ellipse([0.545 * w, 0.48 * h, 0.565 * w, 0.58 * h], fill=WHITE)
    # crease line
    d.line([0.16 * w, 0.90 * h, 0.84 * w, 0.90 * h], fill=WHITE, width=2)
    return img


def scene_icj(w, h):
    img, d = new_tile(w, h, (27, 42, 94))
    for i in range(5):
        cx = 0.11 * w + i * 0.18 * w
        d.rectangle([cx, 0.10 * h, cx + 0.05 * w, 0.90 * h],
                    fill=(230, 228, 220))
    d.rectangle([0.04 * w, 0.07 * h, 0.96 * w, 0.17 * h],
                fill=(230, 228, 220))
    # gold scales, centred between the middle columns
    cx, cy = 0.56 * w, 0.55 * h
    d.line([cx, cy - 0.20 * h, cx, cy + 0.20 * h], fill=GOLD, width=3)
    d.line([cx - 0.08 * w, cy - 0.17 * h, cx + 0.08 * w, cy - 0.17 * h],
           fill=GOLD, width=3)
    d.line([cx - 0.08 * w, cy - 0.17 * h, cx - 0.11 * w, cy + 0.03 * h],
           fill=GOLD, width=2)
    d.line([cx + 0.08 * w, cy - 0.17 * h, cx + 0.11 * w, cy + 0.03 * h],
           fill=GOLD, width=2)
    d.ellipse([cx - 0.14 * w, cy, cx - 0.08 * w, cy + 0.13 * h], fill=GOLD)
    d.ellipse([cx + 0.08 * w, cy, cx + 0.14 * w, cy + 0.13 * h], fill=GOLD)
    d.ellipse([cx - 0.02 * w, cy + 0.17 * h, cx + 0.02 * w, cy + 0.25 * h],
              fill=GOLD)
    return img


def scene_kyiv(w, h):
    img, d = new_tile(w, h, (35, 35, 58))
    base = h
    for bx, bw, bh in ((0, 0.16, 0.40), (0.19, 0.13, 0.57),
                       (0.35, 0.18, 0.33), (0.55, 0.15, 0.50),
                       (0.73, 0.17, 0.37), (0.91, 0.09, 0.47)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = base - bh * h
        d.rectangle([x0, y0, x1, base], fill=(10, 10, 20))
        wy = y0 + 0.08 * h
        while wy < base - 0.07 * h:
            d.rectangle([x0 + 0.02 * w, wy, x0 + 0.04 * w, wy + 0.07 * h],
                        fill=(255, 214, 90))
            wy += 0.15 * h
    # red NO bubble, top centre, fully inside
    cx, cy, r = 0.5 * w, 0.30 * h, 0.26 * h
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx - 8, cy - 8), "NO", font=SANSB(11), fill=WHITE)
    return img


def scene_ukeu(w, h):
    img, d = new_tile(w, h, (63, 158, 77))
    # EU circle of stars, left
    cx, cy, r = 0.18 * w, 0.5 * h, 0.30 * h
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 51, 153))
    for k in range(8):
        import math
        a = math.pi * 2 * k / 8 - math.pi / 2
        sx, sy = cx + 0.18 * h * math.cos(a), cy + 0.18 * h * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # wheat stalks, right
    for wx in (0.50 * w, 0.62 * w, 0.74 * w, 0.86 * w):
        d.line([wx, 0.93 * h, wx, 0.20 * h], fill=(255, 220, 90), width=3)
        wy = 0.20 * h
        while wy < 0.50 * h:
            d.ellipse([wx - 0.03 * w, wy, wx - 0.004 * w, wy + 0.10 * h],
                      fill=(255, 205, 60))
            d.ellipse([wx + 0.004 * w, wy, wx + 0.03 * w, wy + 0.10 * h],
                      fill=(255, 205, 60))
            wy += 0.10 * h
    # union jack hint
    d.rectangle([0.35 * w, 0.13 * h, 0.43 * w, 0.40 * h],
                fill=(200, 16, 46))
    d.line([0.35 * w, 0.13 * h, 0.43 * w, 0.40 * h], fill=WHITE, width=2)
    d.line([0.43 * w, 0.13 * h, 0.35 * w, 0.40 * h], fill=WHITE, width=2)
    return img


def scene_oil(w, h):
    img, d = new_tile(w, h, (24, 90, 140))
    # red sun, top right
    sx, sy = 0.86 * w, 0.27 * h
    d.ellipse([sx - 0.23 * h, sy - 0.23 * h, sx + 0.23 * h, sy + 0.23 * h],
              fill=(220, 60, 40))
    # tanker
    d.polygon([(0.08 * w, 0.37 * h), (0.62 * w, 0.37 * h),
               (0.70 * w, 0.53 * h), (0.12 * w, 0.53 * h)],
              fill=(30, 30, 36))
    d.rectangle([0.49 * w, 0.17 * h, 0.60 * w, 0.37 * h], fill=WHITE)
    d.rectangle([0.16 * w, 0.43 * h, 0.66 * w, 0.57 * h],
                fill=(180, 20, 30))
    d.rectangle([0, 0.83 * h, w, h], fill=(16, 60, 100))
    # barrels, bottom right
    for bx in (0.77 * w, 0.86 * w):
        d.rounded_rectangle([bx, 0.57 * h, bx + 0.07 * w, 0.83 * h], 3,
                            fill=(20, 20, 24))
        d.rectangle([bx, 0.65 * h, bx + 0.07 * w, 0.68 * h], fill=GOLD)
    return img


def scene_nsw(w, h):
    img, d = new_tile(w, h, (28, 28, 34))
    # lamp glow, top right
    lx, ly = 0.86 * w, 0.30 * h
    d.ellipse([lx - 0.25 * h, ly - 0.25 * h, lx + 0.25 * h, ly + 0.25 * h],
              fill=(255, 220, 120))
    d.ellipse([lx - 0.15 * h, ly - 0.15 * h, lx + 0.15 * h, ly + 0.15 * h],
              fill=WHITE)
    # excavator
    d.rectangle([0.07 * w, 0.30 * h, 0.29 * w, 0.53 * h],
                fill=(255, 190, 30))
    d.rectangle([0.31 * w, 0.20 * h, 0.40 * w, 0.53 * h],
                fill=(255, 190, 30))
    d.line([0.40 * w, 0.33 * h, 0.54 * w, 0.57 * h], fill=(255, 190, 30),
           width=6)
    d.polygon([(0.53 * w, 0.50 * h), (0.60 * w, 0.50 * h),
               (0.58 * w, 0.67 * h), (0.52 * w, 0.67 * h)],
              fill=(180, 180, 190))
    # coal chunks, bottom
    for cx, cy, r in ((0.16, 0.67, 0.13), (0.26, 0.70, 0.11),
                      (0.70, 0.67, 0.14), (0.81, 0.70, 0.11),
                      (0.89, 0.67, 0.10)):
        d.polygon([(cx * w - r * h, cy * h + r * h), (cx * w, cy * h - r * h),
                   (cx * w + r * h, cy * h + r * h)], fill=(8, 8, 10),
                  outline=(90, 90, 100))
    return img


def scene_kenya(w, h):
    img, d = new_tile(w, h, (138, 90, 43))
    d.polygon([(0, h), (0.45 * w, 0.17 * h), (w, h)], fill=(110, 66, 28))
    # teal crystals, top
    for cx, cy, s in ((0.33, 0.37, 0.15), (0.49, 0.27, 0.18),
                      (0.66, 0.40, 0.13)):
        d.polygon([(cx * w, cy * h - s * h), (cx * w + s * h, cy * h + s * h),
                   (cx * w - s * h, cy * h + s * h)], fill=(20, 180, 180),
                  outline=WHITE)
    # pickaxe, left
    d.line([0.16 * w, 0.23 * h, 0.27 * w, 0.63 * h], fill=(120, 82, 40),
           width=5)
    d.arc([0.21 * w, 0.13 * h, 0.35 * w, 0.50 * h], 200, 340,
          fill=(200, 200, 210), width=4)
    # sun, top right
    sx, sy = 0.90 * w, 0.23 * h
    d.ellipse([sx - 0.18 * h, sy - 0.18 * h, sx + 0.18 * h, sy + 0.18 * h],
              fill=(255, 220, 120))
    return img


def scene_sa(w, h):
    img, d = new_tile(w, h, (58, 43, 77))
    base = h
    for bx, bw, bh in ((0, 0.19, 0.33), (0.21, 0.17, 0.47),
                       (0.40, 0.20, 0.30), (0.63, 0.18, 0.43),
                       (0.83, 0.17, 0.33)):
        d.rectangle([bx * w, base - bh * h, (bx + bw) * w, base],
                    fill=(24, 16, 34))
    # candle with big flame, centre
    cx = 0.5 * w
    d.rectangle([cx - 0.025 * w, 0.30 * h, cx + 0.025 * w, 0.87 * h],
                fill=(240, 235, 220))
    d.ellipse([cx - 0.065 * w, 0.03 * h, cx + 0.065 * w, 0.30 * h],
              fill=(255, 190, 60))
    d.ellipse([cx - 0.035 * w, 0.08 * h, cx + 0.035 * w, 0.28 * h],
              fill=(255, 240, 160))
    d.line([cx, 0.28 * h, cx, 0.32 * h], fill=INK, width=2)
    return img


def scene_busts(w, h):
    img, d = new_tile(w, h, (16, 32, 68))
    # siren glows, top corners
    d.ellipse([0.07 * w, 0.10 * h, 0.23 * w, 0.43 * h], fill=(255, 60, 60))
    d.ellipse([0.77 * w, 0.10 * h, 0.93 * w, 0.43 * h], fill=(60, 120, 255))
    # handcuffs
    for cx in (0.35 * w, 0.65 * w):
        d.ellipse([cx - 0.28 * h, 0.50 * h - 0.28 * h, cx + 0.28 * h,
                   0.50 * h + 0.28 * h], outline=GOLD, width=5)
    d.line([0.43 * w, 0.42 * h, 0.57 * w, 0.42 * h], fill=GOLD, width=5)
    d.ellipse([0.48 * w, 0.38 * h, 0.52 * w, 0.50 * h], fill=GOLD)
    return img


SCENES = {
    "cop31": scene_cop31, "riyadh": scene_riyadh, "peru": scene_peru,
    "kryvyi": scene_kryvyi, "davao": scene_davao, "bitcoin": scene_bitcoin,
    "rahul": scene_rahul, "icj": scene_icj, "kyiv": scene_kyiv,
    "ukeu": scene_ukeu, "oil": scene_oil, "nsw": scene_nsw,
    "kenya": scene_kenya, "sa": scene_sa, "busts": scene_busts,
}

# ---------------------------------------------------------------- data
# (banner, loc line, headline, deck, source, scene, region)
# IDENTICAL to v2 -- see the audit script; do not edit wording here.
HEROES = [
    ("COP31: OVERTIME", "1  ANTALYA, TÜRKIYE · CLIMATE",
     "Climate summit runs into Saturday with no deal",
     "COP31 missed its Friday close; a draft with no fossil fuels split "
     "nearly 200 countries.",
     "— AP", "cop31", "Global"),
    ("SAUDI: MISSILES", "2  RIYADH · WAR",
     "Three Houthi missiles shot down over Riyadh",
     "The coalition says it destroyed three ballistic missiles fired at "
     "the capital before dawn.",
     "— Reuters", "riyadh", "Middle East"),
    ("PERU: QUAKE 6.7", "3  JUNÍN, PERU · EARTHQUAKE",
     "Magnitude 6.7 earthquake shakes central Peru",
     "The deep quake near Junín was felt in Lima and along the coast. "
     "No deaths or damage reported.",
     "— USGS, IGP", "peru", "Americas"),
]

CARDS = [
    ("KRYVYI RIH: DOUBLE-TAP", "4  KRYVYI RIH · WAR",
     "Russian strikes kill 2 in Kryvyi Rih",
     "A boy of 7 and a paramedic of 20 died; at least 47 hurt as drones "
     "hit rescuers.",
     "— Kyiv Independent", "kryvyi", "Europe"),
    ("DAVAO: 146 SAFE", "5  DAVAO · AVIATION",
     "Jet lands safely after engine fire alert",
     "Air Niugini 767 diverts to Davao; all 137 passengers and 9 crew "
     "walk off.",
     "— AP", "davao", "Asia"),
    ("BITCOIN: $58,983", "6  WORLD · MARKETS",
     "Bitcoin trades below $59,000 on Saturday",
     "Down about 4% in 24 hours, its lowest since September 2024.",
     "— CoinGecko", "bitcoin", "Global"),
    ("RAHUL: 124*", "7  WELLINGTON · CRICKET",
     "Rahul hits a century against New Zealand",
     "India 344 for 2 at tea, replying to 368, on day three.",
     "— AFP", "rahul", "Oceania"),
    ("THE HAGUE: ICJ REJECTED", "8  THE HAGUE · LAW",
     "Myanmar and China reject ICJ genocide ruling",
     "Verdict “unjust”, they say; Türkiye and the Swiss hail it.",
     "— AFP", "icj", "Europe"),
    ("KYIV: NO NEW YALTA", "9  KYIV · DIPLOMACY",
     "Kyiv: Shenzhen was no “new Yalta”",
     "Sybiha answers Putin's summit; Zelenskyy calls the bid to redraw "
     "the world a failure.",
     "— Reuters", "kyiv", "Europe"),
    ("UK–EU: 2 DEALS", "10  LONDON · BRUSSELS",
     "UK and EU strike farm and youth deals",
     "Agriculture and youth mobility agreed in London and Brussels.",
     "— Reuters", "ukeu", "Europe"),
    ("TOKYO: 8M BARRELS", "11  TOKYO · ENERGY",
     "Tokyo to buy 8m barrels of Saudi oil",
     "Refilling reserves; deal agreed.",
     "— Reuters", "oil", "Asia"),
    ("NSW: COALMINE LAW", "12  SYDNEY · ENERGY",
     "NSW passes Mount Pleasant coalmine law",
     "Mine may lift output 32% to 16.5m tonnes a year until 2032.",
     "— Guardian", "nsw", "Oceania"),
    ("KENYA: $60BN MINERALS", "13  MRIMA HILL · MINING",
     "US group wins huge Kenya mining deal",
     "Mrima Hill deposits put at over $60bn, beating Chinese rivals.",
     "— BBC", "kenya", "Africa"),
    ("SOUTH AFRICA: 60 A DAY", "14  SOUTH AFRICA · CRIME",
     "South Africa murders fall, still 60 a day",
     "Rate down, toll still 60 daily.",
     "— Reuters", "sa", "Africa"),
    ("US SWOOP: 2 GANGS", "15  WASHINGTON · CRIME",
     "US busts Italian syndicate, biker gang",
     "Canada and Australia raids in a global swoop.",
     "— Reuters", "busts", "Americas"),
]

BRIEFS = [
    (16, "China warns off Mt Fuji climbers", "Asia"),
    (17, "Somalia: no land for two wars", "Africa"),
    (18, "UK penalises settlement builders", "Europe"),
    (19, "Türkiye welcomes ICJ verdict", "Europe"),
    (20, "Swiss hail ICJ ruling", "Europe"),
    (21, "Hodeidah turned into arms hub", "Middle East"),
    (22, "Iran rejects US arms claims", "Middle East"),
    (23, "Modi: dialogue and trust at SCO", "Asia"),
    (24, "Russia ships fuel to Brazil", "Americas"),
    (25, "German minister regrets remark", "Europe"),
    (26, "Israel envoy: ready to join strikes", "Middle East"),
    (27, "US panel faults India voter rolls", "Americas"),
    (28, "Türkiye: end Cyprus “hostage”", "Europe"),
    (29, "Ethics Day marked in 70 nations", "Global"),
    (30, "Zverev can stretch No. 1 lead", "Global"),
    (31, "Sinner out; Djokovic fails to qualify", "Global"),
    (32, "Odisha stays on orange alert", "Asia"),
    (33, "France seeks UN meeting on Kyiv", "Europe"),
    (34, "Kushner: Trump wants Europe near", "Americas"),
    (35, "Island states press $120bn target", "Global"),
    (36, "Nigeria states back local police", "Africa"),
    (37, "Kenya Senate summons ministers", "Africa"),
    (38, "Bayelsa boat crash: 4 dead, 24 saved", "Africa"),
    (39, "Dozens missing off Senegal coast", "Africa"),
    (40, "Australia Senate rushes Defence Bill", "Oceania"),
    (41, "Alcaraz meets Shelton in Turin semi", "Europe"),
    (42, "Hyundai unveils 2027 Elantra in LA", "Americas"),
]

NUMBERS = [
    ("Day 13", "of a COP31 summit planned to close on day 12"),
    ("3", "missiles shot down over Riyadh"),
    ("6.7", "magnitude of the quake in Junín, Peru"),
    ("146", "people safe after a jet's emergency landing"),
    ("$58,983", "bitcoin early Saturday, down 3.9% in a day"),
    ("124*", "K L Rahul's score at tea in Wellington"),
]

REGIONS = [
    ("Americas", 6, (200, 16, 46)),
    ("Europe", 10, (0, 90, 160)),
    ("Middle East", 4, (232, 163, 23)),
    ("Asia", 6, (120, 90, 160)),
    ("Africa", 7, (46, 140, 66)),
    ("Oceania", 3, (14, 124, 123)),
    ("Global", 6, (90, 90, 90)),
]

DATE_CHECK = (
    "DATE CHECK — Left out on purpose (first reported earlier): Kyiv barrage, "
    "110+ missiles / 400+ drones, at least 9 killed — 20 Nov · Houthi strikes "
    "on Sana'a; Saudi downs a missile and 5 drones — 20 Nov · PIF Tower hit, "
    "Riyadh — 19 Nov · ICJ Myanmar ruling handed down — 19 Nov · Shenzhen "
    "trilateral — 19 Nov · Cyclone Akvan landfall — 20 Nov. The Peru quake "
    "struck 19:09 local Fri 20 Nov = 00:09 UTC Sat 21 Nov, counted as 21 Nov "
    "by UTC dating."
)

# pin positions on the map, as fractions of the map box
PINS = {
    1: (0.585, 0.295), 2: (0.630, 0.363), 3: (0.289, 0.561),
    4: (0.593, 0.234), 5: (0.849, 0.461), 6: (0.080, 0.850),
    7: (0.940, 0.729), 8: (0.512, 0.211), 9: (0.585, 0.220),
    10: (0.500, 0.240), 11: (0.888, 0.302), 12: (0.919, 0.688),
    13: (0.609, 0.524), 14: (0.578, 0.644), 15: (0.286, 0.283),
}
DOTS = {
    16: (0.890, 0.300), 17: (0.660, 0.470), 18: (0.490, 0.210),
    19: (0.580, 0.270), 20: (0.530, 0.220), 21: (0.620, 0.380),
    22: (0.660, 0.330), 23: (0.780, 0.350), 24: (0.330, 0.600),
    25: (0.540, 0.210), 26: (0.600, 0.350), 27: (0.280, 0.300),
    28: (0.590, 0.290), 29: (0.120, 0.850), 30: (0.160, 0.850),
    31: (0.200, 0.850), 32: (0.800, 0.380), 33: (0.500, 0.220),
    34: (0.270, 0.320), 35: (0.900, 0.650), 36: (0.530, 0.440),
    37: (0.620, 0.510), 38: (0.520, 0.460), 39: (0.470, 0.420),
    40: (0.930, 0.700), 41: (0.540, 0.230), 42: (0.220, 0.300),
}

CONTINENTS = [
    [(0.02, 0.12), (0.10, 0.05), (0.20, 0.08), (0.24, 0.16), (0.20, 0.26),
     (0.14, 0.30), (0.06, 0.24)],
    [(0.24, 0.42), (0.30, 0.40), (0.34, 0.50), (0.30, 0.66), (0.26, 0.58)],
    [(0.46, 0.10), (0.52, 0.06), (0.56, 0.12), (0.54, 0.20), (0.48, 0.20)],
    [(0.46, 0.30), (0.54, 0.28), (0.58, 0.36), (0.56, 0.52), (0.50, 0.56),
     (0.46, 0.44)],
    [(0.56, 0.06), (0.78, 0.04), (0.92, 0.12), (0.88, 0.26), (0.74, 0.30),
     (0.62, 0.24), (0.56, 0.16)],
    [(0.84, 0.62), (0.92, 0.60), (0.94, 0.68), (0.86, 0.70)],
]


def draw_map(w, h):
    """The navy map as its own tile, like the scenes."""
    img, d = new_tile(w, h, NAVY_DARK)
    for poly in CONTINENTS:
        pts = [(fx * w, fy * h) for fx, fy in poly]
        d.polygon(pts, fill=TAN, outline=(180, 155, 100))
    for num, (fx, fy) in PINS.items():
        px, py = fx * w, fy * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=1)
        f = SANSB(10)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 6), t, font=f,
               fill=WHITE)
    for num, (fx, fy) in DOTS.items():
        px, py = fx * w, fy * h
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 220, 230),
                  outline=WHITE, width=1)
    return img


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 14
    right = W - mx

    # ---- kicker
    d.text((mx, 4), "THE WORLD IN ONE DAY", font=SANSB(13), fill=RED)
    rt = "42 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((right - d.textlength(rt, font=SANSB(11)), 6), rt,
           font=SANSB(11), fill=INK)
    d.line([mx, 22, right, 22], fill=RED, width=2)

    # ---- masthead + deck
    title = "Saturday 21 November 2026"
    f = SERIFB(54)
    d.text(((W - d.textlength(title, font=f)) / 2, 24), title, font=f,
           fill=INK)
    deck = ("Climate summit runs past its deadline · Three missiles shot "
            "down over Riyadh · Strong quake shakes Peru")
    fd = SERIFI(15)
    d.text(((W - d.textlength(deck, font=fd)) / 2, 82), deck, font=fd,
           fill=INK)

    # ---- numbers strip (68 px tall: labels end well above the rule)
    y0, y1 = 102, 170
    d.line([mx, y0, right, y0], fill=INK, width=2)
    d.line([mx, y1, right, y1], fill=INK, width=2)
    cw = (right - mx) / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = mx + i * cw
        fn = fit_text(d, num, "DejaVuSerif-Bold.ttf", 40, cw - 16)
        d.text((cx + 8, y0 + 2), num, font=fn, fill=INK)
        fl = SANS(11)
        for j, line in enumerate(wrap(d, label, fl, cw - 16)):
            d.text((cx + 8, y0 + 42 + j * 12), line, font=fl, fill=GREY)
        if i:
            d.line([cx, y0 + 4, cx, y1 - 4], fill=RED, width=2)

    # ---- region bar
    y0, y1 = 174, 187
    total = sum(c for _, c, _ in REGIONS)
    cx = mx
    for name, count, col in REGIONS:
        seg = (right - mx) * count / total
        d.rectangle([cx, y0, cx + seg - 1, y1], fill=col)
        f = SANSB(10)
        t = f"{name.upper()} {count}"
        tw = d.textlength(t, font=f)
        if tw < seg - 6:
            d.text((cx + (seg - tw) / 2, y0 + 2), t, font=f, fill=WHITE)
        cx += seg

    # ---- heroes: banner -> scene tile -> loc -> headline -> deck
    # (strictly vertical; the banner never overlaps the scene)
    hy = 191
    hw = 326
    gap = 9
    hero_chips = ["NO DEAL · DAY 13", "3 SHOT DOWN", "00:09 UTC · 108 KM DEEP"]
    hero_scene_h = 77
    for i, (banner_txt, loc, head, deck_txt, src, scene, _reg) in enumerate(HEROES):
        x = mx + i * (hw + gap)
        banner(d, x, hy, hw, 24, banner_txt, size=20)
        tile = SCENES[scene](hw, hero_scene_h)
        # chip sits INSIDE the tile, bottom left, drawn on the tile itself
        td = ImageDraw.Draw(tile)
        chip(td, 6, hero_scene_h - 22, hero_chips[i])
        img.paste(tile, (x, hy + 24))
        yy = hy + 24 + hero_scene_h + 3
        d.text((x, yy), loc, font=SANSB(11), fill=RED)
        fh = SERIFB(21)
        lines = wrap(d, head, fh, hw)
        yy += 16
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 24
        fd2, lines = fit_lines(d, deck_txt + "  " + src,
                               "DejaVuSans.ttf", 12, hw, 2, 10)
        yy += 2
        for line in lines[:2]:
            d.text((x, yy), line, font=fd2, fill=(40, 40, 40))
            yy += 14

    # ---- cards header
    cy = 390
    d.text((mx, cy), "MORE FROM SATURDAY", font=SANSB(12), fill=RED)
    rt = "STORIES 4–15"
    d.text((right - d.textlength(rt, font=SANSB(12)), cy), rt,
           font=SANSB(12), fill=INK)
    d.line([mx, cy + 17, right, cy + 17], fill=INK, width=2)

    # ---- cards: 4 cols x 3 rows, banner -> 60px scene tile -> text
    cw2 = 243
    gap2 = 8
    card_scene_h = 60
    top = 411
    for i, (banner_txt, loc, head, deck_txt, src, scene, _reg) in enumerate(CARDS):
        row, col = divmod(i, 4)
        x = mx + col * (cw2 + gap2)
        y = top + row * (137 + 6)
        banner(d, x, y, cw2, 14, banner_txt, size=12)
        tile = SCENES[scene](cw2, card_scene_h)
        img.paste(tile, (x, y + 14))
        yy = y + 14 + card_scene_h + 2
        d.text((x, yy), loc, font=SANSB(9), fill=RED)
        fh, lines = fit_lines(d, head, "DejaVuSerif-Bold.ttf", 13, cw2, 2, 11)
        yy += 13
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 14
        fd2, lines = fit_lines(d, deck_txt + " " + src,
                               "DejaVuSans.ttf", 10, cw2, 2, 9)
        yy += 1
        for line in lines[:2]:
            d.text((x, yy), line, font=fd2, fill=(40, 40, 40))
            yy += 11

    # ---- bottom: map + briefs
    by = 839
    d.text((mx, by), "WHERE IT HAPPENED", font=SANSB(12), fill=INK)
    bx = 360
    d.text((bx, by), "ALSO ON SATURDAY 21 NOVEMBER 2026 — 27 MORE STORIES",
           font=SANSB(12), fill=INK)
    d.line([mx, by + 17, right, by + 17], fill=INK, width=2)
    img.paste(draw_map(338, 88), (mx, by + 21))
    d.text((mx, by + 114),
           "Pins 1–15 are the lead stories and cards; dots 16–42 are the briefs.",
           font=SANS(9), fill=GREY)
    # briefs in 3 columns x 9 rows
    colw = (right - bx) / 3
    fb = SANS(10)
    for i, (num, text, _reg) in enumerate(BRIEFS):
        col, row = divmod(i, 9)
        x = bx + col * colw
        y = by + 21 + row * 11
        d.text((x, y), f"{num}  {text}", font=fb, fill=INK)

    # ---- DATE CHECK: measure the wrap FIRST, then size the box so the
    # text fits inside it with padding on all sides
    dc_font = SANS(11)
    dc_lines = wrap(d, DATE_CHECK, dc_font, right - mx - 16)
    dc_pitch, dc_pad = 12, 5
    dc_h = len(dc_lines) * dc_pitch + 2 * dc_pad
    dy = 962
    assert dy + dc_h <= 1010, f"DATE CHECK box overflows: {dy + dc_h}"
    d.rectangle([mx, dy, right, dy + dc_h], outline=RED, width=2)
    yy = dy + dc_pad
    for line in dc_lines:
        d.text((mx + 8, yy), line, font=dc_font, fill=INK)
        yy += dc_pitch

    # ---- footer
    foot = ("Every story here happened, or was first reported, on Saturday "
            "21 November 2026. Officials' counts and claims are attributed.")
    d.text((mx, 1012), foot, font=SANS(9), fill=GREY)
    rt = "Sources named beside each story · original drawings"
    d.text((right - d.textlength(rt, font=SANS(9)), 1012), rt,
           font=SANS(9), fill=GREY)

    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {size} bytes ({size / 1024:.1f} KiB)")


if __name__ == "__main__":
    build()
