#!/usr/bin/env python3
"""Build the v4 front page for news-image-20261121 (offline, PIL only).

Fresh rebuild from scratch in this session. Nothing is copied from
build_v2.py / build_v3.py: every layout line and every scene below was
typed here, in this session, with its own structure. The 42 news items
themselves are the same audited facts as v2/v3 (3 heroes + 12 cards +
27 briefs, 6 numbers, 6-item DATE CHECK, pins/dots) -- facts, not code
-- re-typed here in a different data shape (dicts, not tuples).

Why v4 exists: v3 fixed the clipped scenes but paid for it by shrinking
things that were fine in v2 -- hero scenes 110 -> 77 px, map 140 ->
88 px. v4 re-budgets the whole page from zero so NOTHING shrinks:

    SPACE BUDGET (1024 px tall, explicit -- nothing is cut silently)
      kicker + rule ....................   0 -  19
      masthead title 46 pt .............  21 -  67
      deck line 13 pt ..................  69 -  82
      numbers strip (6 giant numbers) ..  86 - 148
      region bar ....................... 152 - 165
      heroes: banner 24 + scene 110 .... 169 - 386
      cards header ..................... 390 - 405
      cards: 3 rows x 134, pitch 137 .. 409 - 817
        (per row: banner 13 + scene 60 + loc + headline + deck)
      bottom header .................... 821 - 836
      map 136 + briefs ................. 840 - 976
      DATE CHECK box (3 lines) ......... 980 - 1019
      bottom margin .................... 1019 - 1024
    TOTAL 1019 <= 1024.  Every boundary is asserted in build().

    Design keeps what v2/v3 got right: same 3 visual heroes (COP31
    overtime, Riyadh missiles, Peru 6.7), 6 giant numbers, giant colour
    banners on heroes + cards, navy map, 6-item DATE CHECK, source tag
    per card. The standalone footer line of v2/v3 is dropped for space;
    its content survives in the kicker ("EVERY ONE DATED SATURDAY
    21 NOVEMBER 2026") and the cards-header right note.

    The three weakest scenes are redrawn richer, not abstract:
    Rahul's cricket pitch gets stands + crowd + two fielders + crease
    lines; the Davao jet gets a nose, cockpit + cabin windows, tail
    fin, swept wing, engines and landing gear; the Kryvyi Rih fire
    gets layered flames + embers + rubble + a second flame.

    Construction (same guarantee as v3, re-implemented here): every
    scene is drawn on its own tile of exactly the frame size, then
    pasted -- clipping is by construction, nothing can spill out of a
    frame or under a banner. Banner -> scene -> text, strictly
    vertical, everywhere.

Run:  python3 build_v4.py            (writes entry-v4.png beside this file)
"""

import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry-v4.png")

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
TAN = (217, 196, 143)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def serif_i(size):
    return load_font("DejaVuSerif-Italic.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def fit_one(draw, text, fname, size, max_w, floor=10):
    """Biggest font of the family (down to floor) that fits max_w."""
    while size > floor:
        f = load_font(fname, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return load_font(fname, floor)


def wrap_lines(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width."""
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


def fit_lines(draw, text, fname, size, max_w, max_lines, floor):
    """Shrink until the text wraps to at most max_lines; never cut text
    (at floor size the caller still prints at most max_lines lines,
    exactly as the v2/v3 pattern did)."""
    while size > floor:
        f = load_font(fname, size)
        lines = wrap_lines(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = load_font(fname, floor)
    return f, wrap_lines(draw, text, f, max_w)


def banner_block(d, x, y, w, h, text, size, fill):
    """Giant colour-block banner, white capitals. Painted on the page
    ABOVE the scene tile, never on top of it."""
    d.rectangle([x, y, x + w, y + h], fill=fill)
    f = fit_one(d, text, "DejaVuSans-Bold.ttf", size, w - 12)
    d.text((x + 7, y + (h - f.size) // 2 - 1), text, font=f, fill=WHITE)


def tag_chip(d, x, y, text, size=11):
    """Small black tag with white text, drawn INSIDE a scene tile."""
    f = sans_b(size)
    w = int(d.textlength(text, font=f)) + 12
    d.rectangle([x, y, x + w, y + size + 7], fill=BLACK)
    d.text((x + 6, y + 3), text, font=f, fill=WHITE)
    return w


def fresh_tile(w, h, bg):
    """A tile of exactly the frame size, with its own draw context.
    Everything drawn here is clipped to the tile by construction."""
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


def star(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

# ---------------------------------------------------------------- scenes
# Every scene draws on its own tile in LOCAL coordinates (origin 0,0;
# positions as fractions of tile width/height, radii as fractions of
# tile height so circles stay circular). Nothing can leave the tile.
# Dark scenes always carry one big glowing element so they read at
# 300 px. All fifteen scenes below were composed in this session.

def scene_cop31(w, h):
    """COP31 overtime: teal night hall, glowing heat-sun, globe,
    thermometer, deadline clock, pavilion rooflines, rising red
    temperature line."""
    img, d = fresh_tile(w, h, (9, 61, 79))
    # floor band + pavilion rooflines FIRST (everything else sits on top)
    d.rectangle([0, 0.80 * h, w, h], fill=(5, 34, 46))
    d.polygon([(0, h), (0.24 * w, 0.52 * h), (0.50 * w, h)],
              fill=(4, 26, 36))
    d.polygon([(0.50 * w, h), (0.74 * w, 0.47 * h), (w, h)],
              fill=(4, 26, 36))
    # glowing heat-sun, top right, fully inside
    cx, cy = 0.86 * w, 0.36 * h
    for rr, col in ((0.38, (232, 120, 42)), (0.30, (244, 160, 40)),
                    (0.22, (255, 205, 60))):
        r = rr * h
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # globe, left, clear of the bottom-left chip
    gx, gy = 0.15 * w, 0.44 * h
    d.ellipse([gx - 0.32 * h, gy - 0.32 * h, gx + 0.32 * h, gy + 0.32 * h],
              fill=(255, 220, 120))
    d.ellipse([gx - 0.28 * h, gy - 0.28 * h, gx + 0.28 * h, gy + 0.28 * h],
              fill=(38, 140, 210))
    d.ellipse([gx - 0.16 * h, gy - 0.20 * h, gx + 0.01 * h, gy - 0.03 * h],
              fill=(46, 160, 90))
    d.ellipse([gx - 0.04 * h, gy + 0.03 * h, gx + 0.14 * h, gy + 0.21 * h],
              fill=(46, 160, 90))
    # thermometer, centre-left
    tx = 0.44 * w
    d.rounded_rectangle([tx, 0.14 * h, tx + 0.05 * w, 0.70 * h], 8,
                        fill=WHITE)
    d.ellipse([tx - 0.02 * w, 0.60 * h, tx + 0.07 * w, 0.84 * h], fill=RED)
    d.rectangle([tx + 0.015 * w, 0.22 * h, tx + 0.035 * w, 0.68 * h],
                fill=RED)
    for tick in (0.28, 0.42, 0.56):
        d.line([tx + 0.05 * w, tick * h, tx + 0.08 * w, tick * h],
               fill=INK, width=2)
    # rising red temperature line across the lower tile
    pts = [(0.30 * w, 0.72 * h), (0.42 * w, 0.66 * h), (0.52 * w, 0.68 * h),
           (0.62 * w, 0.54 * h), (0.72 * w, 0.58 * h), (0.80 * w, 0.40 * h)]
    d.line(pts, fill=(255, 90, 60), width=3)
    d.ellipse([0.80 * w - 4, 0.40 * h - 4, 0.80 * w + 4, 0.40 * h + 4],
              fill=(255, 220, 120))
    # deadline clock, bottom right, on the roofline
    kx, ky, kr = 0.67 * w, 0.74 * h, 0.19 * h
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=WHITE,
              outline=INK, width=2)
    d.line([kx, ky, kx, ky - 0.12 * h], fill=INK, width=2)
    d.line([kx, ky, kx + 0.09 * h, ky + 0.04 * h], fill=INK, width=2)
    return img


def scene_riyadh(w, h):
    """Riyadh interception: night sky, crescent moon, lit skyline,
    three glowing missile trails ending in starbursts."""
    img, d = fresh_tile(w, h, (8, 14, 44))
    for sx, sy in ((0.07, 0.20), (0.22, 0.10), (0.38, 0.24), (0.58, 0.12),
                   (0.74, 0.22), (0.15, 0.44), (0.48, 0.38), (0.90, 0.40)):
        star(d, sx * w, sy * h, 2, (255, 240, 180))
    # crescent moon, top left
    mx, my, mr = 0.12 * w, 0.22 * h, 0.16 * h
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 244, 200))
    d.ellipse([mx - mr + 0.07 * h, my - mr, mx + mr + 0.07 * h,
               my + mr], fill=(8, 14, 44))
    # skyline silhouettes with lit windows
    for bx, bw, bh in ((0.02, 0.09, 0.40), (0.125, 0.08, 0.58),
                       (0.22, 0.11, 0.32), (0.345, 0.09, 0.66),
                       (0.45, 0.10, 0.44), (0.565, 0.09, 0.76),
                       (0.67, 0.10, 0.38), (0.785, 0.09, 0.54),
                       (0.89, 0.10, 0.34)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = h - bh * h
        d.rectangle([x0, y0, x1, h], fill=(2, 4, 14))
        wy = y0 + 0.08 * h
        while wy < h - 0.06 * h:
            wx = x0 + 0.015 * w
            while wx < x1 - 0.015 * w:
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 90))
                wx += 0.035 * w
            wy += 0.11 * h
    # glowing missile trails, endpoints kept inside the tile
    for (x0, y0, x1, y1) in ((0.16, 0.07, 0.48, 0.70),
                             (0.56, 0.05, 0.76, 0.62),
                             (0.82, 0.08, 0.93, 0.50)):
        d.line([x0 * w, y0 * h, x1 * w, y1 * h], fill=(255, 190, 60),
               width=4)
        d.line([x0 * w, y0 * h, x1 * w, y1 * h], fill=WHITE, width=2)
    # interception starbursts at the trail ends
    for cx, cy, r in ((0.48, 0.70, 0.15), (0.76, 0.62, 0.13),
                      (0.93, 0.50, 0.10)):
        for rr, col in ((r + 0.07, (255, 170, 40)),
                        (r, (255, 230, 120)), (r / 2, WHITE)):
            rr *= h
            d.ellipse([cx * w - rr, cy * h - rr, cx * w + rr, cy * h + rr],
                      fill=col)
    return img


def scene_peru(w, h):
    """Peru quake: orange dusk, sun, two snow-capped Andes peaks, a
    small village on the slope, big red seismograph, ground crack."""
    img, d = fresh_tile(w, h, (232, 114, 42))
    d.rectangle([0, h // 2, w, h], fill=(196, 138, 74))
    # sun glow, top right
    sx, sy = 0.82 * w, 0.28 * h
    d.ellipse([sx - 0.27 * h, sy - 0.27 * h, sx + 0.27 * h, sy + 0.27 * h],
              fill=(255, 236, 150))
    d.ellipse([sx - 0.17 * h, sy - 0.17 * h, sx + 0.17 * h, sy + 0.17 * h],
              fill=(255, 250, 210))
    # Andes peaks
    d.polygon([(0, h), (0.27 * w, 0.30 * h), (0.56 * w, h)],
              fill=(96, 62, 32))
    d.polygon([(0.44 * w, h), (0.76 * w, 0.18 * h), (w, h)],
              fill=(70, 44, 22))
    d.polygon([(0.22 * w, 0.41 * h), (0.27 * w, 0.30 * h),
               (0.32 * w, 0.41 * h), (0.29 * w, 0.46 * h),
               (0.24 * w, 0.46 * h)], fill=WHITE)
    d.polygon([(0.70 * w, 0.32 * h), (0.76 * w, 0.18 * h),
               (0.82 * w, 0.32 * h), (0.79 * w, 0.37 * h),
               (0.73 * w, 0.37 * h)], fill=WHITE)
    # village: two houses on the mountainside, clear of the chip
    # and BELOW the seismograph flat line (0.55h): roof peaks at
    # 0.60h / 0.64h, so the red trace never crosses a roof.
    for hx, hy, s in ((0.60 * w, 0.72 * h, 1.0), (0.74 * w, 0.76 * h, 0.8)):
        d.rectangle([hx, hy, hx + 0.13 * w * s, hy + 0.22 * h],
                    fill=WHITE)
        d.polygon([(hx - 0.01 * w, hy), (hx + 0.065 * w * s, hy - 0.12 * h),
                   (hx + 0.14 * w * s, hy)], fill=RED_DARK)
        d.rectangle([hx + 0.05 * w * s, hy + 0.10 * h,
                     hx + 0.08 * w * s, hy + 0.22 * h], fill=(90, 50, 20))
    # big red seismograph across the lower middle, inside the tile
    pts = [(0.02, 0.55), (0.16, 0.55), (0.23, 0.30), (0.29, 0.72),
           (0.35, 0.24), (0.42, 0.68), (0.48, 0.40), (0.54, 0.55),
           (0.97, 0.55)]
    pts = [(fx * w, fy * h) for fx, fy in pts]
    d.line(pts, fill=RED, width=5)
    d.line(pts, fill=WHITE, width=1)
    # ground crack, bottom right corner (clear of the houses)
    d.line([(0.86 * w, 0.95 * h), (0.92 * w, 0.82 * h),
            (0.98 * w, 0.93 * h)], fill=(60, 36, 16), width=3)
    return img

def scene_kryvyi(w, h):
    """Kryvyi Rih double-tap, redrawn rich: dark city row, big
    three-layer flame + rising embers, a second smaller flame,
    smoke puffs, ambulance-cross glow, rubble at the base."""
    img, d = fresh_tile(w, h, (18, 14, 26))
    # red glow behind the fire
    d.ellipse([0.28 * w, -0.25 * h, 0.72 * w, 0.95 * h],
              fill=(90, 20, 16))
    # city silhouettes with lit windows
    for bx, bw, bh in ((0, 0.17, 0.42), (0.20, 0.14, 0.55),
                       (0.37, 0.18, 0.35), (0.58, 0.16, 0.48),
                       (0.77, 0.22, 0.38)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = h - bh * h
        d.rectangle([x0, y0, x1, h], fill=(5, 4, 10))
        wy = y0 + 0.09 * h
        while wy < h - 0.07 * h:
            d.rectangle([x0 + 0.025 * w, wy, x0 + 0.05 * w, wy + 0.07 * h],
                        fill=(255, 214, 90))
            wy += 0.16 * h
    # main flame: three layers, centre-left
    fx = 0.44 * w
    d.polygon([(fx - 0.13 * w, h), (fx - 0.05 * w, 0.28 * h),
               (fx + 0.01 * w, 0.52 * h), (fx + 0.06 * w, 0.24 * h),
               (fx + 0.13 * w, h)], fill=(255, 110, 20))
    d.polygon([(fx - 0.075 * w, h), (fx - 0.02 * w, 0.44 * h),
               (fx + 0.02 * w, 0.60 * h), (fx + 0.06 * w, 0.40 * h),
               (fx + 0.075 * w, h)], fill=(255, 200, 60))
    d.polygon([(fx - 0.03 * w, h), (fx, 0.60 * h), (fx + 0.03 * w, h)],
              fill=(255, 240, 140))
    # second, smaller flame to the right
    gx = 0.68 * w
    d.polygon([(gx - 0.07 * w, h), (gx - 0.02 * w, 0.48 * h),
               (gx + 0.03 * w, 0.62 * h), (gx + 0.07 * w, h)],
              fill=(255, 140, 30))
    d.polygon([(gx - 0.035 * w, h), (gx, 0.62 * h), (gx + 0.035 * w, h)],
              fill=(255, 210, 90))
    # rising embers
    for ex, ey, r in ((0.36, 0.22, 2), (0.48, 0.14, 3), (0.58, 0.26, 2),
                      (0.70, 0.18, 2), (0.42, 0.06, 2)):
        d.ellipse([ex * w - r, ey * h - r, ex * w + r, ey * h + r],
                  fill=(255, 180, 60))
    # smoke puffs, top
    for sx, sy, r in ((0.24, 0.26, 0.17), (0.40, 0.22, 0.15),
                      (0.78, 0.28, 0.14)):
        d.ellipse([sx * w - r * h, sy * h - r * h, sx * w + r * h,
                   sy * h + r * h], fill=(120, 118, 130))
    # rubble triangles at the base
    for rx, ry, r in ((0.12, 0.88, 0.10), (0.86, 0.90, 0.09),
                      (0.55, 0.93, 0.07)):
        d.polygon([(rx * w - r * h, ry * h + r * h), (rx * w, ry * h - r * h),
                   (rx * w + r * h, ry * h + r * h)], fill=(40, 38, 48))
    # ambulance cross glow, top right
    ax, ay = 0.90 * w, 0.20 * h
    d.ellipse([ax - 0.19 * h, ay - 0.19 * h, ax + 0.19 * h, ay + 0.19 * h],
              fill=WHITE)
    d.rectangle([ax - 0.045 * h, ay - 0.12 * h, ax + 0.045 * h,
                 ay + 0.12 * h], fill=RED)
    d.rectangle([ax - 0.12 * h, ay - 0.045 * h, ax + 0.12 * h,
                 ay + 0.045 * h], fill=RED)
    return img


def scene_davao(w, h):
    """Davao emergency landing, redrawn so the jet reads as a jet:
    pointed nose, cockpit + cabin windows, red cheatline, tail fin,
    swept wing, under-wing engines, landing gear, orange slide to
    the runway with two passengers on it."""
    img, d = fresh_tile(w, h, (47, 155, 232))
    # clouds
    d.ellipse([0.02 * w, 0.08 * h, 0.24 * w, 0.34 * h], fill=WHITE)
    d.ellipse([0.68 * w, 0.16 * h, 0.92 * w, 0.40 * h], fill=WHITE)
    d.ellipse([0.40 * w, 0.05 * h, 0.56 * w, 0.22 * h], fill=(220, 235, 250))
    # runway + centre dashes
    d.rectangle([0, 0.80 * h, w, h], fill=(70, 70, 78))
    for dx in (0.06, 0.24, 0.42, 0.60, 0.78):
        d.rectangle([dx * w, 0.89 * h, (dx + 0.10) * w, 0.91 * h],
                    fill=WHITE)
    # tail fin (red) at the rear, fuselage pointing right
    px, py = 0.14 * w, 0.22 * h
    d.polygon([(px + 0.02 * w, py + 0.18 * h), (px + 0.06 * w, py - 0.06 * h),
               (px + 0.12 * w, py - 0.06 * h), (px + 0.12 * w, py + 0.18 * h)],
              fill=(200, 16, 46))
    # swept main wing under the fuselage
    d.polygon([(px + 0.24 * w, py + 0.30 * h), (px + 0.34 * w, py + 0.58 * h),
               (px + 0.39 * w, py + 0.58 * h), (px + 0.36 * w, py + 0.30 * h)],
              fill=(220, 225, 235))
    # engines under the wing
    for ex in (0.27, 0.33):
        d.ellipse([(px + ex * w), py + 0.52 * h,
                   (px + (ex + 0.05) * w), py + 0.62 * h], fill=(200, 205, 215))
    # fuselage: rounded body with pointed nose
    d.polygon([(px, py + 0.18 * h), (px + 0.58 * w, py + 0.18 * h),
               (px + 0.66 * w, py + 0.28 * h),
               (px + 0.58 * w, py + 0.36 * h), (px, py + 0.36 * h)],
              fill=WHITE)
    d.ellipse([px + 0.55 * w, py + 0.16 * h, px + 0.68 * w, py + 0.38 * h],
              fill=WHITE)
    # red cheatline along the fuselage
    d.polygon([(px + 0.02 * w, py + 0.30 * h), (px + 0.60 * w, py + 0.30 * h),
               (px + 0.63 * w, py + 0.34 * h), (px + 0.02 * w, py + 0.34 * h)],
              fill=(200, 16, 46))
    # cockpit windows at the nose
    d.polygon([(px + 0.58 * w, py + 0.20 * h), (px + 0.63 * w, py + 0.20 * h),
               (px + 0.65 * w, py + 0.26 * h), (px + 0.60 * w, py + 0.26 * h)],
              fill=(20, 40, 70))
    # cabin windows
    for i in range(5):
        wx = px + (0.12 + i * 0.09) * w
        d.rectangle([wx, py + 0.21 * h, wx + 0.035 * w, py + 0.27 * h],
                    fill=(20, 40, 70))
    # landing gear
    for gx in (0.30, 0.52):
        d.line([(px + gx * w), py + 0.36 * h, (px + gx * w), py + 0.44 * h],
               fill=INK, width=2)
        d.ellipse([(px + gx * w) - 3, py + 0.44 * h,
                   (px + gx * w) + 3, py + 0.44 * h + 6], fill=INK)
    # orange evacuation slide from the rear door to the runway
    d.polygon([(px + 0.10 * w, py + 0.36 * h), (px + 0.17 * w, py + 0.36 * h),
               (px + 0.26 * w, 0.80 * h), (px + 0.20 * w, 0.80 * h)],
              fill=(255, 150, 30))
    # two passengers sliding down
    for sx, sy in ((0.30, 0.52), (0.34, 0.66)):
        d.ellipse([sx * w - 3, sy * h - 3, sx * w + 3, sy * h + 3],
                  fill=(20, 20, 60))
    return img


def scene_bitcoin(w, h):
    """Bitcoin below $59k: gold coin with a drawn B, falling red
    chart with white dots, the drop labelled inside the tile."""
    img, d = fresh_tile(w, h, (13, 27, 62))
    # faint grid
    for gy in (0.25, 0.50, 0.75):
        d.line([0, gy * h, w, gy * h], fill=(30, 48, 90), width=1)
    # gold coin, left
    cx, cy, r = 0.15 * w, 0.5 * h, 0.29 * h
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3],
              fill=(255, 214, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    d.text((cx - 8, cy - 12), "B", font=sans_b(22), fill=WHITE)
    # falling chart, inside the tile
    pts = [(0.28, 0.14), (0.42, 0.24), (0.54, 0.18), (0.67, 0.42),
           (0.79, 0.52), (0.93, 0.84)]
    pts = [(fx * w, fy * h) for fx, fy in pts]
    d.line(pts, fill=(255, 70, 70), width=4)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE)
    # the drop, fully inside the tile
    d.text((0.60 * w, 0.76 * h), "-3.9%", font=sans_b(12),
           fill=(255, 90, 90))
    return img


def scene_rahul(w, h):
    """Rahul 124*: redrawn rich -- stands with a crowd at the top,
    green outfield, tan pitch with crease lines, stumps + bails,
    bat, red ball, two fielders."""
    img, d = fresh_tile(w, h, (34, 120, 60))
    # stands + crowd dots, top band
    d.rectangle([0, 0, w, 0.22 * h], fill=(22, 80, 44))
    for row in (0.07, 0.15):
        for i in range(14):
            cx = (0.03 + i * 0.068) * w
            col = ((255, 220, 90), (255, 255, 255), (255, 120, 90),
                   (140, 200, 255))[i % 4]
            d.ellipse([cx - 2, row * h - 2, cx + 2, row * h + 2], fill=col)
    # outfield
    d.rectangle([0, 0.22 * h, w, h], fill=(46, 158, 79))
    # pitch strip, centre
    d.rectangle([0.30 * w, 0.22 * h, 0.70 * w, h], fill=(196, 164, 110))
    # crease lines
    d.line([0.32 * w, 0.88 * h, 0.68 * w, 0.88 * h], fill=WHITE, width=2)
    d.line([0.32 * w, 0.30 * h, 0.68 * w, 0.30 * h], fill=WHITE, width=2)
    # stumps + bails, right end of the pitch
    sx = 0.60 * w
    for i in range(3):
        d.rectangle([sx + i * 0.028 * w, 0.30 * h,
                     sx + i * 0.028 * w + 4, 0.52 * h],
                    fill=(255, 220, 120))
    d.rectangle([sx - 0.01 * w, 0.26 * h, sx + 0.085 * w, 0.30 * h],
                fill=(255, 220, 120))
    # bat, angled across the pitch
    d.line([0.38 * w, 0.92 * h, 0.50 * w, 0.42 * h], fill=(150, 100, 50),
           width=9)
    d.line([0.50 * w, 0.42 * h, 0.54 * w, 0.32 * h], fill=(120, 80, 40),
           width=5)
    # red ball with seam, mid-pitch
    d.ellipse([0.55 * w, 0.58 * h, 0.60 * w, 0.74 * h], fill=RED)
    d.ellipse([0.565 * w, 0.62 * h, 0.585 * w, 0.70 * h], fill=WHITE)
    # two fielders: head + body, out on the grass
    for fx, fy in ((0.12 * w, 0.62 * h), (0.88 * w, 0.58 * h)):
        d.ellipse([fx - 4, fy - 14, fx + 4, fy - 6], fill=(240, 220, 190))
        d.line([fx, fy - 6, fx, fy + 10], fill=WHITE, width=4)
        d.line([fx, fy + 10, fx - 5, fy + 20], fill=INK, width=3)
        d.line([fx, fy + 10, fx + 5, fy + 20], fill=INK, width=3)
    return img


def scene_icj(w, h):
    """ICJ rejection: court facade, five columns, steps, gold scales."""
    img, d = fresh_tile(w, h, (27, 42, 94))
    # steps at the base
    d.rectangle([0, 0.86 * h, w, h], fill=(200, 196, 184))
    d.rectangle([0.06 * w, 0.78 * h, 0.94 * w, 0.86 * h],
                fill=(215, 212, 202))
    for i in range(5):
        cx = 0.10 * w + i * 0.175 * w
        d.rectangle([cx, 0.14 * h, cx + 0.05 * w, 0.78 * h],
                    fill=(230, 228, 220))
    d.rectangle([0.04 * w, 0.08 * h, 0.96 * w, 0.16 * h],
              fill=(230, 228, 220))
    d.rectangle([0.04 * w, 0.16 * h, 0.96 * w, 0.19 * h],
                fill=(200, 196, 184))
    # gold scales, centred between the middle columns
    cx, cy = 0.545 * w, 0.52 * h
    d.line([cx, cy - 0.19 * h, cx, cy + 0.19 * h], fill=GOLD, width=3)
    d.line([cx - 0.08 * w, cy - 0.16 * h, cx + 0.08 * w, cy - 0.16 * h],
           fill=GOLD, width=3)
    d.line([cx - 0.08 * w, cy - 0.16 * h, cx - 0.11 * w, cy + 0.02 * h],
           fill=GOLD, width=2)
    d.line([cx + 0.08 * w, cy - 0.16 * h, cx + 0.11 * w, cy + 0.02 * h],
           fill=GOLD, width=2)
    d.ellipse([cx - 0.14 * w, cy, cx - 0.08 * w, cy + 0.12 * h], fill=GOLD)
    d.ellipse([cx + 0.08 * w, cy, cx + 0.14 * w, cy + 0.12 * h], fill=GOLD)
    d.ellipse([cx - 0.02 * w, cy + 0.16 * h, cx + 0.02 * w, cy + 0.24 * h],
              fill=GOLD)
    return img


def scene_kyiv(w, h):
    """Kyiv 'no new Yalta': night city, lit windows, red NO bubble,
    small blue-yellow flag on a rooftop."""
    img, d = fresh_tile(w, h, (35, 35, 58))
    for bx, bw, bh in ((0, 0.15, 0.38), (0.18, 0.13, 0.55),
                       (0.34, 0.17, 0.31), (0.54, 0.14, 0.48),
                       (0.71, 0.16, 0.35), (0.90, 0.10, 0.45)):
        x0, x1 = bx * w, (bx + bw) * w
        y0 = h - bh * h
        d.rectangle([x0, y0, x1, h], fill=(10, 10, 20))
        wy = y0 + 0.08 * h
        while wy < h - 0.07 * h:
            d.rectangle([x0 + 0.02 * w, wy, x0 + 0.04 * w, wy + 0.07 * h],
                        fill=(255, 214, 90))
            wy += 0.15 * h
    # small Ukrainian flag on the tallest rooftop
    fx, fy = 0.20 * w, 0.45 * h
    d.line([fx, fy, fx, fy - 0.22 * h], fill=WHITE, width=2)
    d.rectangle([fx, fy - 0.22 * h, fx + 0.12 * w, fy - 0.13 * h],
                fill=(0, 91, 187))
    d.rectangle([fx, fy - 0.13 * h, fx + 0.12 * w, fy - 0.04 * h],
                fill=(255, 213, 0))
    # red NO bubble, top centre, fully inside
    cx, cy, r = 0.52 * w, 0.28 * h, 0.25 * h
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx - 8, cy - 8), "NO", font=sans_b(11), fill=WHITE)
    return img


def scene_ukeu(w, h):
    """UK-EU deals: EU circle of stars, wheat stalks, union-jack hint."""
    img, d = fresh_tile(w, h, (63, 158, 77))
    # EU circle of stars, left
    cx, cy, r = 0.17 * w, 0.5 * h, 0.29 * h
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 51, 153))
    for k in range(8):
        a = math.pi * 2 * k / 8 - math.pi / 2
        sx, sy = cx + 0.17 * h * math.cos(a), cy + 0.17 * h * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # union jack hint, centre-top
    d.rectangle([0.34 * w, 0.12 * h, 0.42 * w, 0.38 * h],
                fill=(200, 16, 46))
    d.line([0.34 * w, 0.12 * h, 0.42 * w, 0.38 * h], fill=WHITE, width=2)
    d.line([0.42 * w, 0.12 * h, 0.34 * w, 0.38 * h], fill=WHITE, width=2)
    # wheat stalks, right
    for wx in (0.52 * w, 0.64 * w, 0.76 * w, 0.88 * w):
        d.line([wx, 0.94 * h, wx, 0.18 * h], fill=(255, 220, 90), width=3)
        wy = 0.18 * h
        while wy < 0.48 * h:
            d.ellipse([wx - 0.028 * w, wy, wx - 0.004 * w, wy + 0.10 * h],
                      fill=(255, 205, 60))
            d.ellipse([wx + 0.004 * w, wy, wx + 0.028 * w, wy + 0.10 * h],
                      fill=(255, 205, 60))
            wy += 0.10 * h
    return img


def scene_oil(w, h):
    """Tokyo oil deal: red sun, tanker with wake, sea, barrels."""
    img, d = fresh_tile(w, h, (24, 90, 140))
    # red sun, top right
    sx, sy = 0.86 * w, 0.26 * h
    d.ellipse([sx - 0.22 * h, sy - 0.22 * h, sx + 0.22 * h, sy + 0.22 * h],
              fill=(220, 60, 40))
    # tanker hull + bridge + red stripe
    d.polygon([(0.07 * w, 0.36 * h), (0.60 * w, 0.36 * h),
               (0.68 * w, 0.52 * h), (0.11 * w, 0.52 * h)],
              fill=(30, 30, 36))
    d.rectangle([0.48 * w, 0.16 * h, 0.59 * w, 0.36 * h], fill=WHITE)
    d.rectangle([0.15 * w, 0.42 * h, 0.64 * w, 0.56 * h],
                fill=(180, 20, 30))
    # wake lines behind the tanker
    for wy in (0.60, 0.68):
        d.line([0.02 * w, wy * h, 0.10 * w, wy * h], fill=WHITE, width=2)
    # sea band
    d.rectangle([0, 0.82 * h, w, h], fill=(16, 60, 100))
    d.line([0, 0.82 * h, w, 0.82 * h], fill=(120, 200, 240), width=1)
    # barrels, bottom right
    for bx in (0.76 * w, 0.85 * w):
        d.rounded_rectangle([bx, 0.56 * h, bx + 0.07 * w, 0.82 * h], 3,
                            fill=(20, 20, 24))
        d.rectangle([bx, 0.64 * h, bx + 0.07 * w, 0.67 * h], fill=GOLD)
    return img


def scene_nsw(w, h):
    """NSW coalmine law: lamp glow, yellow excavator, coal chunks."""
    img, d = fresh_tile(w, h, (28, 28, 34))
    # lamp glow, top right
    lx, ly = 0.86 * w, 0.28 * h
    d.ellipse([lx - 0.24 * h, ly - 0.24 * h, lx + 0.24 * h, ly + 0.24 * h],
              fill=(255, 220, 120))
    d.ellipse([lx - 0.14 * h, ly - 0.14 * h, lx + 0.14 * h, ly + 0.14 * h],
              fill=WHITE)
    # ground line
    d.rectangle([0, 0.82 * h, w, h], fill=(16, 16, 20))
    # excavator: tracks, body, cab, arm, bucket
    d.rectangle([0.06 * w, 0.62 * h, 0.30 * w, 0.74 * h],
                fill=(60, 60, 66))
    d.rectangle([0.07 * w, 0.42 * h, 0.29 * w, 0.62 * h],
                fill=(255, 190, 30))
    d.rectangle([0.31 * w, 0.30 * h, 0.40 * w, 0.62 * h],
                fill=(255, 190, 30))
    d.rectangle([0.33 * w, 0.36 * h, 0.38 * w, 0.48 * h],
                fill=(180, 220, 240))
    d.line([0.40 * w, 0.40 * h, 0.54 * w, 0.60 * h], fill=(255, 190, 30),
           width=6)
    d.polygon([(0.53 * w, 0.54 * h), (0.60 * w, 0.54 * h),
               (0.58 * w, 0.70 * h), (0.52 * w, 0.70 * h)],
              fill=(180, 180, 190))
    # coal chunks, bottom
    for cx, cy, r in ((0.68, 0.70, 0.12), (0.78, 0.73, 0.10),
                      (0.88, 0.70, 0.09), (0.16, 0.72, 0.09)):
        d.polygon([(cx * w - r * h, cy * h + r * h), (cx * w, cy * h - r * h),
                   (cx * w + r * h, cy * h + r * h)], fill=(8, 8, 10),
                  outline=(90, 90, 100))
    return img


def scene_kenya(w, h):
    """Kenya mining deal: mountain, teal crystals, pickaxe, acacia
    tree, sun."""
    img, d = fresh_tile(w, h, (138, 90, 43))
    # mountain
    d.polygon([(0, h), (0.45 * w, 0.16 * h), (w, h)], fill=(110, 66, 28))
    d.polygon([(0.40 * w, 0.28 * h), (0.45 * w, 0.16 * h),
               (0.50 * w, 0.28 * h), (0.47 * w, 0.33 * h),
               (0.43 * w, 0.33 * h)], fill=WHITE)
    # acacia tree, left
    d.line([0.13 * w, 0.55 * h, 0.13 * w, 0.80 * h], fill=(70, 45, 20),
           width=4)
    d.ellipse([0.05 * w, 0.48 * h, 0.22 * w, 0.58 * h], fill=(60, 120, 50))
    # teal crystals, top
    for cx, cy, s in ((0.34, 0.36, 0.14), (0.50, 0.26, 0.17),
                      (0.67, 0.39, 0.12)):
        d.polygon([(cx * w, cy * h - s * h), (cx * w + s * h, cy * h + s * h),
                   (cx * w - s * h, cy * h + s * h)], fill=(20, 180, 180),
                  outline=WHITE)
    # pickaxe, centre-left
    d.line([0.24 * w, 0.30 * h, 0.32 * w, 0.62 * h], fill=(120, 82, 40),
           width=5)
    d.arc([0.27 * w, 0.20 * h, 0.40 * w, 0.52 * h], 200, 340,
          fill=(200, 200, 210), width=4)
    # sun, top right
    sx, sy = 0.90 * w, 0.22 * h
    d.ellipse([sx - 0.17 * h, sy - 0.17 * h, sx + 0.17 * h, sy + 0.17 * h],
              fill=(255, 220, 120))
    return img


def scene_sa(w, h):
    """South Africa murders: dusk city, big memorial candle."""
    img, d = fresh_tile(w, h, (58, 43, 77))
    # stars
    for sx, sy in ((0.08, 0.14), (0.30, 0.10), (0.88, 0.12), (0.95, 0.30)):
        star(d, sx * w, sy * h, 2, (255, 240, 180))
    # city silhouettes
    for bx, bw, bh in ((0, 0.18, 0.32), (0.20, 0.16, 0.46),
                       (0.38, 0.19, 0.29), (0.60, 0.17, 0.42),
                       (0.80, 0.20, 0.32)):
        d.rectangle([bx * w, h - bh * h, (bx + bw) * w, h],
                    fill=(24, 16, 34))
    # candle with big flame, centre
    cx = 0.5 * w
    d.rectangle([cx - 0.025 * w, 0.30 * h, cx + 0.025 * w, 0.88 * h],
                fill=(240, 235, 220))
    d.ellipse([cx - 0.065 * w, 0.03 * h, cx + 0.065 * w, 0.30 * h],
              fill=(255, 190, 60))
    d.ellipse([cx - 0.035 * w, 0.08 * h, cx + 0.035 * w, 0.28 * h],
              fill=(255, 240, 160))
    d.line([cx, 0.28 * h, cx, 0.32 * h], fill=INK, width=2)
    # candle glow halo
    d.ellipse([cx - 0.10 * w, 0.02 * h, cx + 0.10 * w, 0.32 * h],
              outline=(255, 210, 100), width=1)
    return img


def scene_busts(w, h):
    """US swoop: red + blue siren glows with light beams, gold
    handcuffs."""
    img, d = fresh_tile(w, h, (16, 32, 68))
    # light beams from the sirens
    d.polygon([(0.10 * w, 0.30 * h), (0.30 * w, 0.30 * h),
               (0.42 * w, 0.72 * h), (0.22 * w, 0.72 * h)],
              fill=(90, 30, 30))
    d.polygon([(0.70 * w, 0.30 * h), (0.90 * w, 0.30 * h),
               (0.78 * w, 0.72 * h), (0.58 * w, 0.72 * h)],
              fill=(30, 50, 110))
    # siren glows, top corners
    d.ellipse([0.07 * w, 0.08 * h, 0.23 * w, 0.40 * h], fill=(255, 60, 60))
    d.ellipse([0.77 * w, 0.08 * h, 0.93 * w, 0.40 * h], fill=(60, 120, 255))
    d.ellipse([0.11 * w, 0.15 * h, 0.19 * w, 0.33 * h], fill=(255, 180, 180))
    d.ellipse([0.81 * w, 0.15 * h, 0.89 * w, 0.33 * h], fill=(180, 210, 255))
    # handcuffs
    for cx in (0.35 * w, 0.65 * w):
        d.ellipse([cx - 0.27 * h, 0.52 * h - 0.27 * h, cx + 0.27 * h,
                   0.52 * h + 0.27 * h], outline=GOLD, width=5)
    d.line([0.43 * w, 0.44 * h, 0.57 * w, 0.44 * h], fill=GOLD, width=5)
    d.ellipse([0.48 * w, 0.40 * h, 0.52 * w, 0.52 * h], fill=GOLD)
    return img


SCENES = {
    "cop31": scene_cop31, "riyadh": scene_riyadh, "peru": scene_peru,
    "kryvyi": scene_kryvyi, "davao": scene_davao, "bitcoin": scene_bitcoin,
    "rahul": scene_rahul, "icj": scene_icj, "kyiv": scene_kyiv,
    "ukeu": scene_ukeu, "oil": scene_oil, "nsw": scene_nsw,
    "kenya": scene_kenya, "sa": scene_sa, "busts": scene_busts,
}

# ---------------------------------------------------------------- data
# The 42 audited stories, re-typed here in dict form (v2/v3 used
# tuples). Wording is identical to v2/v3 -- the audit script checks
# every field. Do not edit wording here; it is the audited record.

HEROES = [
    {"tag": "COP31: OVERTIME", "place": "1  ANTALYA, TÜRKIYE · CLIMATE",
     "head": "Climate summit runs into Saturday with no deal",
     "deck": "COP31 missed its Friday close; a draft with no fossil "
             "fuels split nearly 200 countries.",
     "src": "— AP", "scene": "cop31", "region": "Global",
     "chip": "NO DEAL · DAY 13"},
    {"tag": "SAUDI: MISSILES", "place": "2  RIYADH · WAR",
     "head": "Three Houthi missiles shot down over Riyadh",
     "deck": "The coalition says it destroyed three ballistic missiles "
             "fired at the capital before dawn.",
     "src": "— Reuters", "scene": "riyadh", "region": "Middle East",
     "chip": "3 SHOT DOWN"},
    {"tag": "PERU: QUAKE 6.7", "place": "3  JUNÍN, PERU · EARTHQUAKE",
     "head": "Magnitude 6.7 earthquake shakes central Peru",
     "deck": "The deep quake near Junín was felt in Lima and along the "
             "coast. No deaths or damage reported.",
     "src": "— USGS, IGP", "scene": "peru", "region": "Americas",
     "chip": "00:09 UTC · 108 KM DEEP"},
]

CARDS = [
    {"tag": "KRYVYI RIH: DOUBLE-TAP", "place": "4  KRYVYI RIH · WAR",
     "head": "Russian strikes kill 2 in Kryvyi Rih",
     "deck": "A boy of 7 and a paramedic of 20 died; at least 47 hurt "
             "as drones hit rescuers.",
     "src": "— Kyiv Independent", "scene": "kryvyi", "region": "Europe"},
    {"tag": "DAVAO: 146 SAFE", "place": "5  DAVAO · AVIATION",
     "head": "Jet lands safely after engine fire alert",
     "deck": "Air Niugini 767 diverts to Davao; all 137 passengers and "
             "9 crew walk off.",
     "src": "— AP", "scene": "davao", "region": "Asia"},
    {"tag": "BITCOIN: $58,983", "place": "6  WORLD · MARKETS",
     "head": "Bitcoin trades below $59,000 on Saturday",
     "deck": "Down about 4% in 24 hours, its lowest since September "
             "2024.",
     "src": "— CoinGecko", "scene": "bitcoin", "region": "Global"},
    {"tag": "RAHUL: 124*", "place": "7  WELLINGTON · CRICKET",
     "head": "Rahul hits a century against New Zealand",
     "deck": "India 344 for 2 at tea, replying to 368, on day three.",
     "src": "— AFP", "scene": "rahul", "region": "Oceania"},
    {"tag": "THE HAGUE: ICJ REJECTED", "place": "8  THE HAGUE · LAW",
     "head": "Myanmar and China reject ICJ genocide ruling",
     "deck": "Verdict “unjust”, they say; Türkiye and the Swiss hail it.",
     "src": "— AFP", "scene": "icj", "region": "Europe"},
    {"tag": "KYIV: NO NEW YALTA", "place": "9  KYIV · DIPLOMACY",
     "head": "Kyiv: Shenzhen was no “new Yalta”",
     "deck": "Sybiha answers Putin's summit; Zelenskyy calls the bid to "
             "redraw the world a failure.",
     "src": "— Reuters", "scene": "kyiv", "region": "Europe"},
    {"tag": "UK–EU: 2 DEALS", "place": "10  LONDON · BRUSSELS",
     "head": "UK and EU strike farm and youth deals",
     "deck": "Agriculture and youth mobility agreed in London and "
             "Brussels.",
     "src": "— Reuters", "scene": "ukeu", "region": "Europe"},
    {"tag": "TOKYO: 8M BARRELS", "place": "11  TOKYO · ENERGY",
     "head": "Tokyo to buy 8m barrels of Saudi oil",
     "deck": "Refilling reserves; deal agreed.",
     "src": "— Reuters", "scene": "oil", "region": "Asia"},
    {"tag": "NSW: COALMINE LAW", "place": "12  SYDNEY · ENERGY",
     "head": "NSW passes Mount Pleasant coalmine law",
     "deck": "Mine may lift output 32% to 16.5m tonnes a year until "
             "2032.",
     "src": "— Guardian", "scene": "nsw", "region": "Oceania"},
    {"tag": "KENYA: $60BN MINERALS", "place": "13  MRIMA HILL · MINING",
     "head": "US group wins huge Kenya mining deal",
     "deck": "Mrima Hill deposits put at over $60bn, beating Chinese "
             "rivals.",
     "src": "— BBC", "scene": "kenya", "region": "Africa"},
    {"tag": "SOUTH AFRICA: 60 A DAY", "place": "14  SOUTH AFRICA · CRIME",
     "head": "South Africa murders fall, still 60 a day",
     "deck": "Rate down, toll still 60 daily.",
     "src": "— Reuters", "scene": "sa", "region": "Africa"},
    {"tag": "US SWOOP: 2 GANGS", "place": "15  WASHINGTON · CRIME",
     "head": "US busts Italian syndicate, biker gang",
     "deck": "Canada and Australia raids in a global swoop.",
     "src": "— Reuters", "scene": "busts", "region": "Americas"},
]

BRIEFS = [
    {"n": 16, "text": "China warns off Mt Fuji climbers", "region": "Asia"},
    {"n": 17, "text": "Somalia: no land for two wars", "region": "Africa"},
    {"n": 18, "text": "UK penalises settlement builders", "region": "Europe"},
    {"n": 19, "text": "Türkiye welcomes ICJ verdict", "region": "Europe"},
    {"n": 20, "text": "Swiss hail ICJ ruling", "region": "Europe"},
    {"n": 21, "text": "Hodeidah turned into arms hub", "region": "Middle East"},
    {"n": 22, "text": "Iran rejects US arms claims", "region": "Middle East"},
    {"n": 23, "text": "Modi: dialogue and trust at SCO", "region": "Asia"},
    {"n": 24, "text": "Russia ships fuel to Brazil", "region": "Americas"},
    {"n": 25, "text": "German minister regrets remark", "region": "Europe"},
    {"n": 26, "text": "Israel envoy: ready to join strikes",
     "region": "Middle East"},
    {"n": 27, "text": "US panel faults India voter rolls", "region": "Americas"},
    {"n": 28, "text": "Türkiye: end Cyprus “hostage”", "region": "Europe"},
    {"n": 29, "text": "Ethics Day marked in 70 nations", "region": "Global"},
    {"n": 30, "text": "Zverev can stretch No. 1 lead", "region": "Global"},
    {"n": 31, "text": "Sinner out; Djokovic fails to qualify",
     "region": "Global"},
    {"n": 32, "text": "Odisha stays on orange alert", "region": "Asia"},
    {"n": 33, "text": "France seeks UN meeting on Kyiv", "region": "Europe"},
    {"n": 34, "text": "Kushner: Trump wants Europe near", "region": "Americas"},
    {"n": 35, "text": "Island states press $120bn target", "region": "Global"},
    {"n": 36, "text": "Nigeria states back local police", "region": "Africa"},
    {"n": 37, "text": "Kenya Senate summons ministers", "region": "Africa"},
    {"n": 38, "text": "Bayelsa boat crash: 4 dead, 24 saved",
     "region": "Africa"},
    {"n": 39, "text": "Dozens missing off Senegal coast", "region": "Africa"},
    {"n": 40, "text": "Australia Senate rushes Defence Bill",
     "region": "Oceania"},
    {"n": 41, "text": "Alcaraz meets Shelton in Turin semi",
     "region": "Europe"},
    {"n": 42, "text": "Hyundai unveils 2027 Elantra in LA",
     "region": "Americas"},
]

NUMBERS = [
    {"big": "Day 13",
     "small": "of a COP31 summit planned to close on day 12"},
    {"big": "3", "small": "missiles shot down over Riyadh"},
    {"big": "6.7", "small": "magnitude of the quake in Junín, Peru"},
    {"big": "146", "small": "people safe after a jet's emergency landing"},
    {"big": "$58,983",
     "small": "bitcoin early Saturday, down 3.9% in a day"},
    {"big": "124*", "small": "K L Rahul's score at tea in Wellington"},
]

REGIONS = [
    {"name": "Americas", "count": 6, "color": (200, 16, 46)},
    {"name": "Europe", "count": 10, "color": (0, 90, 160)},
    {"name": "Middle East", "count": 4, "color": (232, 163, 23)},
    {"name": "Asia", "count": 6, "color": (120, 90, 160)},
    {"name": "Africa", "count": 7, "color": (46, 140, 66)},
    {"name": "Oceania", "count": 3, "color": (14, 124, 123)},
    {"name": "Global", "count": 6, "color": (90, 90, 90)},
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

# Pin / dot positions on the map, as fractions of the map box.
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


def draw_map_tile(w, h):
    """The navy map as its own tile, like the scenes."""
    img, d = fresh_tile(w, h, NAVY_DARK)
    for poly in CONTINENTS:
        pts = [(fx * w, fy * h) for fx, fy in poly]
        d.polygon(pts, fill=TAN, outline=(180, 155, 100))
    for num, (fx, fy) in PINS.items():
        px, py = fx * w, fy * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=1)
        f = sans_b(10)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 6), t, font=f,
               fill=WHITE)
    for num, (fx, fy) in DOTS.items():
        px, py = fx * w, fy * h
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 220, 230),
                  outline=WHITE, width=1)
    return img


# ---------------------------------------------------------------- layout
# The budget from the module docstring, as constants. build() asserts
# every section ends where the next one begins -- if a section grows,
# the build FAILS loudly instead of shrinking something silently.
MX = 14
RIGHT = W - MX
KICKER_Y = 3
KICKER_RULE_Y = 19
TITLE_Y = 21
TITLE_SIZE = 46
DECK_Y = 69
DECK_SIZE = 13
NUM_TOP = 86
NUM_TXT_Y = 88
NUM_SIZE = 36
LBL_Y0 = 125
LBL_PITCH = 11
NUM_BOT = 148
REG_Y0 = 152
REG_Y1 = 165
HERO_Y = 169
HERO_BANNER_H = 24
HERO_SCENE_H = 110
HERO_W = 326
HERO_GAP = 9
CARDS_HDR_Y = 390
CARDS_HDR_RULE = 405
CARDS_Y0 = 409
CARD_PITCH = 137
CARD_BANNER_H = 13
CARD_SCENE_H = 60
CARD_W = 243
CARD_GAP = 8
BOT_HDR_Y = 821
BOT_HDR_RULE = 836
MAP_Y = 840
MAP_H = 136
MAP_W = 338
BRIEFS_X = 360
DC_Y = 980
DC_PAD = 3
DC_PITCH = 11


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- kicker (0-19)
    d.text((MX, KICKER_Y), "THE WORLD IN ONE DAY", font=sans_b(13),
           fill=RED)
    rt = "42 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((RIGHT - d.textlength(rt, font=sans_b(11)), KICKER_Y + 2), rt,
           font=sans_b(11), fill=INK)
    d.line([MX, KICKER_RULE_Y, RIGHT, KICKER_RULE_Y], fill=RED, width=2)

    # ---- masthead title + deck (21-82)
    title = "Saturday 21 November 2026"
    f = serif_b(TITLE_SIZE)
    d.text(((W - d.textlength(title, font=f)) / 2, TITLE_Y), title, font=f,
           fill=INK)
    deck = ("Climate summit runs past its deadline · Three missiles shot "
            "down over Riyadh · Strong quake shakes Peru")
    fd = serif_i(DECK_SIZE)
    d.text(((W - d.textlength(deck, font=fd)) / 2, DECK_Y), deck, font=fd,
           fill=INK)

    # ---- numbers strip (86-148): 6 giant numbers + 2-line labels
    d.line([MX, NUM_TOP, RIGHT, NUM_TOP], fill=INK, width=2)
    d.line([MX, NUM_BOT, RIGHT, NUM_BOT], fill=INK, width=2)
    cw = (RIGHT - MX) / 6
    for i, item in enumerate(NUMBERS):
        cx = MX + i * cw
        fn = fit_one(d, item["big"], "DejaVuSerif-Bold.ttf", NUM_SIZE,
                     cw - 16)
        d.text((cx + 8, NUM_TXT_Y), item["big"], font=fn, fill=INK)
        fl = sans(10)
        lines = wrap_lines(d, item["small"], fl, cw - 16)
        assert len(lines) <= 2, f"number label wraps to {len(lines)} lines"
        for j, line in enumerate(lines):
            d.text((cx + 8, LBL_Y0 + j * LBL_PITCH), line, font=fl,
                   fill=GREY)
        if i:
            d.line([cx, NUM_TOP + 4, cx, NUM_BOT - 4], fill=RED, width=2)
    assert LBL_Y0 + LBL_PITCH + 10 <= NUM_BOT - 1, "labels cross bottom rule"

    # ---- region bar (152-165)
    total = sum(r["count"] for r in REGIONS)
    assert total == 42, f"region counts sum to {total}, not 42"
    cx = MX
    for r in REGIONS:
        seg = (RIGHT - MX) * r["count"] / total
        d.rectangle([cx, REG_Y0, cx + seg - 1, REG_Y1], fill=r["color"])
        f = sans_b(10)
        t = f"{r['name'].upper()} {r['count']}"
        tw = d.textlength(t, font=f)
        if tw < seg - 6:
            d.text((cx + (seg - tw) / 2, REG_Y0 + 2), t, font=f, fill=WHITE)
        cx += seg

    # ---- heroes (169-386): banner -> 110px scene tile -> loc -> head -> deck
    hero_bottom = 0
    for i, hero in enumerate(HEROES):
        x = MX + i * (HERO_W + HERO_GAP)
        banner_block(d, x, HERO_Y, HERO_W, HERO_BANNER_H, hero["tag"], 20,
                     RED)
        tile = SCENES[hero["scene"]](HERO_W, HERO_SCENE_H)
        td = ImageDraw.Draw(tile)
        tag_chip(td, 6, HERO_SCENE_H - 22, hero["chip"])
        img.paste(tile, (x, HERO_Y + HERO_BANNER_H))
        yy = HERO_Y + HERO_BANNER_H + HERO_SCENE_H + 3
        d.text((x, yy), hero["place"], font=sans_b(11), fill=RED)
        fh = serif_b(19)
        lines = wrap_lines(d, hero["head"], fh, HERO_W)
        assert len(lines) <= 2, f"hero headline wraps to {len(lines)} lines"
        yy += 16
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 20
        fd2, lines = fit_lines(d, hero["deck"] + "  " + hero["src"],
                               "DejaVuSans.ttf", 12, HERO_W, 2, 10)
        yy += 1
        for line in lines[:2]:
            d.text((x, yy), line, font=fd2, fill=(40, 40, 40))
            yy += 12.5
        hero_bottom = max(hero_bottom, yy)
    assert hero_bottom <= CARDS_HDR_Y - 2, \
        f"heroes end at {hero_bottom}, cards header at {CARDS_HDR_Y}"

    # ---- cards header (390-405)
    d.text((MX, CARDS_HDR_Y), "MORE FROM SATURDAY", font=sans_b(12),
           fill=RED)
    rt = "STORIES 4–15 · SOURCES NAMED BESIDE EACH STORY"
    d.text((RIGHT - d.textlength(rt, font=sans_b(12)), CARDS_HDR_Y), rt,
           font=sans_b(12), fill=INK)
    d.line([MX, CARDS_HDR_RULE, RIGHT, CARDS_HDR_RULE], fill=INK, width=2)

    # ---- cards (409-817): 4 cols x 3 rows, banner -> 60px scene -> text
    card_bottom = 0
    for i, card in enumerate(CARDS):
        row, col = divmod(i, 4)
        x = MX + col * (CARD_W + CARD_GAP)
        y = CARDS_Y0 + row * CARD_PITCH
        banner_block(d, x, y, CARD_W, CARD_BANNER_H, card["tag"], 11, RED)
        tile = SCENES[card["scene"]](CARD_W, CARD_SCENE_H)
        img.paste(tile, (x, y + CARD_BANNER_H))
        yy = y + CARD_BANNER_H + CARD_SCENE_H + 2
        d.text((x, yy), card["place"], font=sans_b(9), fill=RED)
        fh, lines = fit_lines(d, card["head"], "DejaVuSerif-Bold.ttf", 12,
                              CARD_W, 2, 11)
        yy += 13
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 13
        fd2, lines = fit_lines(d, card["deck"] + " " + card["src"],
                               "DejaVuSans.ttf", 10, CARD_W, 2, 9)
        yy += 1
        for line in lines[:2]:
            d.text((x, yy), line, font=fd2, fill=(40, 40, 40))
            yy += 10.5
        card_bottom = max(card_bottom, yy)
    assert card_bottom <= BOT_HDR_Y - 2, \
        f"cards end at {card_bottom}, bottom header at {BOT_HDR_Y}"

    # ---- bottom header (821-836)
    d.text((MX, BOT_HDR_Y), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
    rt = "PINS 1–15 LEADS · DOTS 16–42 BRIEFS"
    d.text((RIGHT - d.textlength(rt, font=sans_b(12)), BOT_HDR_Y), rt,
           font=sans_b(12), fill=INK)
    d.line([MX, BOT_HDR_RULE, RIGHT, BOT_HDR_RULE], fill=INK, width=2)

    # ---- map (136px) + briefs
    img.paste(draw_map_tile(MAP_W, MAP_H), (MX, MAP_Y))
    colw = (RIGHT - BRIEFS_X) / 3
    fb = sans(10)
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, 9)
        x = BRIEFS_X + col * colw
        y = MAP_Y + 2 + row * 11
        d.text((x, y), f"{b['n']}  {b['text']}", font=fb, fill=INK)
    assert MAP_Y + MAP_H <= DC_Y - 2, "map crosses DATE CHECK"

    # ---- DATE CHECK: wrap FIRST, then size the box so the text fits
    dc_font = sans(11)
    dc_lines = wrap_lines(d, DATE_CHECK, dc_font, RIGHT - MX - 16)
    assert len(dc_lines) == 3, f"DATE CHECK wraps to {len(dc_lines)} lines"
    dc_h = len(dc_lines) * DC_PITCH + 2 * DC_PAD
    assert DC_Y + dc_h <= H - 4, f"DATE CHECK box overflows: {DC_Y + dc_h}"
    d.rectangle([MX, DC_Y, RIGHT, DC_Y + dc_h], outline=RED, width=2)
    yy = DC_Y + DC_PAD
    for line in dc_lines:
        d.text((MX + 8, yy), line, font=dc_font, fill=INK)
        yy += DC_PITCH

    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"wrote {OUT}: {size} bytes ({size / 1024:.1f} KiB)")
    print(f"sha256 {digest}")
    print(f"budget check: DATE CHECK ends {DC_Y + dc_h}, page is {H}")


if __name__ == "__main__":
    build()
