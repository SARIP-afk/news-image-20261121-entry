#!/usr/bin/env python3
"""Build the v2 front page for news-image-20261121 (offline, PIL only).

Renders entry.png (1024x1024, <=1 MiB): masthead + giant numbers strip +
three heroes (COP31 overtime, Riyadh missile interception, Peru quake) +
twelve cards with giant colour-block banners + a navy world map + 27
one-line briefs + a six-item DATE CHECK. Every story on the page was
first reported on Saturday 21 November 2026; see VERIFY-REPORT.md.

Run:  python3 build_v2.py            (writes entry.png beside this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

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


def banner(d, x, y, w, h, text, size=20, fill=RED):
    """Giant colour-block banner with white capital text."""
    d.rectangle([x, y, x + w, y + h], fill=fill)
    f = fit_text(d, text, "DejaVuSans-Bold.ttf", size, w - 12)
    d.text((x + 7, y + (h - f.size) // 2 - 1), text, font=f, fill=WHITE)


def chip(d, x, y, text, size=11):
    """Small black tag with white text; returns its width."""
    f = SANSB(size)
    w = int(d.textlength(text, font=f)) + 12
    d.rectangle([x, y, x + w, y + size + 7], fill=BLACK)
    d.text((x + 6, y + 3), text, font=f, fill=WHITE)
    return w


# ---------------------------------------------------------------- scenes
# Every scene is a flat, saturated vector drawing. Dark scenes always
# carry one big glowing element so they read at 300 px.

def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(9, 61, 79))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(6, 38, 50))
    # glowing sun / heat disc
    cx, cy, r = x + w - 52, y + 44, 30
    for rr, col in ((44, (232, 120, 42)), (36, (244, 160, 40)), (28, (255, 205, 60))):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    # globe
    gx, gy, gr = x + 58, y + 58, 34
    d.ellipse([gx - gr - 5, gy - gr - 5, gx + gr + 5, gy + gr + 5],
              fill=(255, 220, 120))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(38, 140, 210))
    d.ellipse([gx - 18, gy - 22, gx + 2, gy - 2], fill=(46, 160, 90))
    d.ellipse([gx - 4, gy + 6, gx + 20, gy + 24], fill=(46, 160, 90))
    # thermometer
    tx = x + w // 2 + 6
    d.rounded_rectangle([tx, y + 22, tx + 16, y + h - 44], 8, fill=WHITE)
    d.ellipse([tx - 6, y + h - 56, tx + 22, y + h - 24], fill=RED)
    d.rectangle([tx + 5, y + 30, tx + 11, y + h - 40], fill=RED)
    # clock
    kx, ky, kr = x + w - 118, y + h - 40, 20
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=WHITE,
              outline=INK, width=2)
    d.line([kx, ky, kx, ky - 13], fill=INK, width=2)
    d.line([kx, ky, kx + 10, ky + 4], fill=INK, width=2)
    # pavilion roofline
    d.polygon([(x, y + h - 26), (x + 70, y + h - 52), (x + 150, y + h - 26)],
              fill=(4, 26, 36))
    d.polygon([(x + 150, y + h - 26), (x + 230, y + h - 58),
               (x + w, y + h - 26)], fill=(4, 26, 36))


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 14, 44))
    # stars
    for sx, sy in ((30, 18), (90, 10), (150, 24), (210, 12), (270, 20),
                   (60, 44), (180, 40), (300, 48)):
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                  fill=(255, 240, 180))
    # skyline
    base = y + h
    for bx, bw, bh in ((0, 34, 46), (38, 26, 66), (68, 40, 38), (112, 30, 74),
                       (146, 36, 50), (186, 28, 84), (218, 34, 44),
                       (256, 30, 62), (290, 36, 40)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(2, 4, 14))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(bx + 5, bx + bw - 5, 10):
                d.rectangle([x + wx, wy, x + wx + 4, wy + 5],
                            fill=(255, 214, 90))
    # glowing missile trails
    for (x0, y0, x1, y1) in ((40, 8, 150, 78), (180, 4, 250, 70),
                             (260, 10, 300, 58)):
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 190, 60),
               width=4)
        d.line([x + x0, y + y0, x + x1, y + y1], fill=WHITE, width=2)
    # interception starbursts
    for cx, cy, r in ((150, 78, 16), (250, 70, 14), (300, 58, 11)):
        for rr, col in ((r + 8, (255, 170, 40)), (r, (255, 230, 120)),
                        (r // 2, WHITE)):
            d.ellipse([x + cx - rr, y + cy - rr, x + cx + rr, y + cy + rr],
                      fill=col)


def scene_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 114, 42))
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(196, 138, 74))
    # sun glow
    sx, sy = x + w - 56, y + 34
    d.ellipse([sx - 26, sy - 26, sx + 26, sy + 26], fill=(255, 236, 150))
    d.ellipse([sx - 17, sy - 17, sx + 17, sy + 17], fill=(255, 250, 210))
    # mountains
    d.polygon([(x, y + h), (x + 90, y + 34), (x + 190, y + h)],
              fill=(96, 62, 32))
    d.polygon([(x + 140, y + h), (x + 250, y + 22), (x + w, y + h)],
              fill=(70, 44, 22))
    d.polygon([(x + 74, y + 46), (x + 90, y + 34), (x + 106, y + 46),
               (x + 98, y + 52), (x + 82, y + 52)], fill=WHITE)
    # house
    hx, hy = x + 26, y + h - 44
    d.rectangle([hx, hy, hx + 44, hy + 26], fill=WHITE)
    d.polygon([(hx - 4, hy), (hx + 22, hy - 18), (hx + 48, hy)],
              fill=RED_DARK)
    d.rectangle([hx + 18, hy + 12, hx + 28, hy + 26], fill=(90, 50, 20))
    # big red seismograph
    pts = [(x + 8, y + h - 52), (x + 60, y + h - 52), (x + 80, y + h - 78),
           (x + 100, y + h - 26), (x + 118, y + h - 84), (x + 138, y + h - 30),
           (x + 158, y + h - 66), (x + 178, y + h - 52), (x + w - 8, y + h - 52)]
    d.line(pts, fill=RED, width=5)
    d.line(pts, fill=(255, 255, 255), width=1)
    # ground crack
    d.line([x + 200, y + h - 8, x + 230, y + h - 22, x + 262, y + h - 10],
           fill=(60, 36, 16), width=3)


def scene_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 14, 26))
    base = y + h
    for bx, bw, bh in ((0, 44, 26), (50, 36, 34), (92, 46, 22), (144, 40, 30),
                       (190, 50, 24)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(5, 4, 10))
        for wy in range(base - bh + 6, base - 4, 10):
            d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 4],
                        fill=(255, 214, 90))
    # fire glow, big: layered flame, not a ball
    fx, fy = x + w // 2, base - 6
    d.polygon([(fx - 34, fy), (fx - 10, fy - 40), (fx + 4, fy - 18),
               (fx + 18, fy - 44), (fx + 34, fy)], fill=(255, 110, 20))
    d.polygon([(fx - 20, fy), (fx - 6, fy - 28), (fx + 6, fy - 12),
               (fx + 16, fy - 30), (fx + 20, fy)], fill=(255, 200, 60))
    d.polygon([(fx - 9, fy), (fx, fy - 18), (fx + 9, fy)], fill=(255, 240, 140))
    # smoke
    for sx, sy, r in ((70, 12, 12), (110, 8, 15), (160, 14, 11)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(120, 118, 130))
    # ambulance cross glow
    ax, ay = x + w - 30, y + 12
    d.ellipse([ax - 14, ay - 14, ax + 14, ay + 14], fill=(255, 255, 255))
    d.rectangle([ax - 3, ay - 9, ax + 3, ay + 9], fill=RED)
    d.rectangle([ax - 9, ay - 3, ax + 9, ay + 3], fill=RED)


def scene_davao(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(47, 155, 232))
    d.ellipse([x + 8, y + 6, x + 60, y + 22], fill=WHITE)
    d.ellipse([x + 170, y + 12, x + 228, y + 26], fill=WHITE)
    # runway
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(70, 70, 78))
    d.line([x + 10, y + h - 6, x + w - 10, y + h - 6], fill=WHITE, width=2)
    # plane
    px, py = x + 40, y + 12
    d.polygon([(px, py + 12), (px + 150, py + 12), (px + 168, py + 18),
               (px + 150, py + 22), (px, py + 22)], fill=WHITE)
    d.polygon([(px + 96, py + 12), (px + 116, py - 2), (px + 128, py + 12)],
              fill=(200, 16, 46))
    d.polygon([(px + 150, py + 12), (px + 168, py + 2), (px + 172, py + 12)],
              fill=(200, 16, 46))
    d.polygon([(px + 60, py + 22), (px + 84, py + 34), (px + 96, py + 22)],
              fill=(220, 225, 235))
    # evacuation slide
    d.polygon([(px + 150, py + 22), (px + 176, py + 22), (px + 196, y + h - 12),
               (px + 182, y + h - 12)], fill=(255, 150, 30))


def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 27, 62))
    # gold coin
    cx, cy, r = x + 34, y + h // 2, 18
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3],
              fill=(255, 214, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    d.text((cx - 8, cy - 11), "₿", font=SANSB(20), fill=WHITE)
    # falling chart
    pts = [(x + 62, y + 8), (x + 100, y + 14), (x + 128, y + 10),
           (x + 160, y + 24), (x + 190, y + 30), (x + 222, y + h - 10)]
    d.line(pts, fill=(255, 70, 70), width=4)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE)
    d.text((x + 150, y + h - 20), "-3.9%", font=SANSB(13), fill=(255, 90, 90))


def scene_rahul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 158, 79))
    d.rectangle([x + 30, y + 6, x + w - 30, y + h - 6], fill=(196, 164, 110))
    # stumps
    sx = x + w - 52
    for i in range(3):
        d.rectangle([sx + i * 7, y + 10, sx + i * 7 + 4, y + 26],
                    fill=(255, 220, 120))
    d.rectangle([sx - 2, y + 8, sx + 20, y + 11], fill=(255, 220, 120))
    # bat
    d.line([x + 60, y + h - 10, x + 108, y + 12], fill=(150, 100, 50),
           width=9)
    d.line([x + 108, y + 12, x + 122, y + 4], fill=(120, 80, 40), width=5)
    # ball
    d.ellipse([x + 130, y + 26, x + 142, y + 38], fill=RED)
    d.ellipse([x + 133, y + 29, x + 139, y + 35], fill=WHITE)
    # crease lines
    d.line([x + 40, y + h - 10, x + w - 40, y + h - 10], fill=WHITE, width=2)


def scene_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 42, 94))
    for i in range(5):
        cx = x + 26 + i * 44
        d.rectangle([cx, y + 6, cx + 12, y + h - 10], fill=(230, 228, 220))
    d.rectangle([x + 10, y + 4, x + w - 10, y + 10], fill=(230, 228, 220))
    # gold scales
    cx, cy = x + w // 2, y + h // 2 + 4
    d.line([cx, cy - 14, cx, cy + 12], fill=GOLD, width=3)
    d.line([cx - 20, cy - 12, cx + 20, cy - 12], fill=GOLD, width=3)
    d.line([cx - 20, cy - 12, cx - 26, cy + 2], fill=GOLD, width=2)
    d.line([cx + 20, cy - 12, cx + 26, cy + 2], fill=GOLD, width=2)
    d.ellipse([cx - 32, cy, cx - 20, cy + 8], fill=GOLD)
    d.ellipse([cx + 20, cy, cx + 32, cy + 8], fill=GOLD)
    d.ellipse([cx - 4, cy + 10, cx + 4, cy + 16], fill=GOLD)


def scene_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(35, 35, 58))
    base = y + h
    for bx, bw, bh in ((0, 40, 24), (46, 32, 34), (84, 44, 20), (134, 36, 30),
                       (176, 40, 22), (220, 24, 28)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(10, 10, 20))
        for wy in range(base - bh + 5, base - 4, 9):
            d.rectangle([x + bx + 5, wy, x + bx + 10, wy + 4],
                        fill=(255, 214, 90))
    # red NO bubble
    cx, cy, r = x + w // 2, y + 14, 13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx - 8, cy - 10), "NO", font=SANSB(11), fill=WHITE)


def scene_ukeu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(63, 158, 77))
    # EU circle of stars
    cx, cy, r = x + 44, y + h // 2, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 51, 153))
    for k in range(8):
        import math
        a = math.pi * 2 * k / 8 - math.pi / 2
        sx, sy = cx + int(10 * math.cos(a)), cy + int(10 * math.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # wheat stalks
    for wx in range(x + 120, x + w - 8, 26):
        d.line([wx, y + h - 4, wx, y + 12], fill=(255, 220, 90), width=3)
        for wy in range(y + 12, y + 30, 7):
            d.ellipse([wx - 7, wy, wx - 1, wy + 6], fill=(255, 205, 60))
            d.ellipse([wx + 1, wy, wx + 7, wy + 6], fill=(255, 205, 60))
    # union jack hint
    d.rectangle([x + 84, y + 8, x + 108, y + 24], fill=(200, 16, 46))
    d.line([x + 84, y + 8, x + 108, y + 24], fill=WHITE, width=2)
    d.line([x + 108, y + 8, x + 84, y + 24], fill=WHITE, width=2)


def scene_oil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 90, 140))
    # red sun
    sx, sy = x + w - 34, y + 16
    d.ellipse([sx - 14, sy - 14, sx + 14, sy + 14], fill=(220, 60, 40))
    # tanker
    d.polygon([(x + 20, y + 22), (x + 150, y + 22), (x + 170, y + 32),
               (x + 30, y + 32)], fill=(30, 30, 36))
    d.rectangle([x + 120, y + 10, x + 146, y + 22], fill=WHITE)
    d.rectangle([x + 40, y + 26, x + 160, y + 34], fill=(180, 20, 30))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(16, 60, 100))
    # barrels
    for bx in (x + 186, x + 208):
        d.rounded_rectangle([bx, y + h - 26, bx + 18, y + h - 10], 3,
                            fill=(20, 20, 24))
        d.rectangle([bx, y + h - 21, bx + 18, y + h - 18], fill=GOLD)


def scene_nsw(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 28, 34))
    # lamp glow
    lx, ly = x + w - 34, y + 12
    d.ellipse([lx - 16, ly - 16, lx + 16, ly + 16], fill=(255, 220, 120))
    d.ellipse([lx - 9, ly - 9, lx + 9, ly + 9], fill=WHITE)
    # excavator
    d.rectangle([x + 16, y + 18, x + 70, y + 32], fill=(255, 190, 30))
    d.rectangle([x + 76, y + 12, x + 96, y + 32], fill=(255, 190, 30))
    d.line([x + 96, y + 20, x + 130, y + 34], fill=(255, 190, 30), width=6)
    d.polygon([(x + 128, y + 30), (x + 146, y + 30), (x + 140, y + 40),
               (x + 126, y + 40)], fill=(180, 180, 190))
    # coal chunks
    for cx, cy, r in ((40, 40, 8), (62, 42, 7), (170, 40, 9), (196, 42, 7),
                      (216, 40, 6)):
        d.polygon([(x + cx - r, y + cy + r), (x + cx, y + cy - r),
                   (x + cx + r, y + cy + r)], fill=(8, 8, 10),
                  outline=(90, 90, 100))


def scene_kenya(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(138, 90, 43))
    d.polygon([(x, y + h), (x + 110, y + 10), (x + w, y + h)],
              fill=(110, 66, 28))
    # teal crystals
    for cx, cy, s in ((80, 22, 9), (120, 16, 11), (160, 24, 8)):
        d.polygon([(x + cx, y + cy - s), (x + cx + s, y + cy + s),
                   (x + cx - s, y + cy + s)], fill=(20, 180, 180),
                  outline=WHITE)
    # pickaxe
    d.line([x + 40, y + 14, x + 66, y + 38], fill=(120, 82, 40), width=5)
    d.arc([x + 52, y + 8, x + 84, y + 30], 200, 340, fill=(200, 200, 210),
          width=4)
    # sun
    d.ellipse([x + w - 30, y + 4, x + w - 6, y + 28], fill=(255, 220, 120))


def scene_sa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 43, 77))
    base = y + h
    for bx, bw, bh in ((0, 46, 20), (52, 40, 28), (98, 48, 18), (152, 44, 26),
                       (202, 42, 20)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(24, 16, 34))
    # candle with big flame
    cx = x + w // 2
    d.rectangle([cx - 6, y + 18, cx + 6, y + h - 8], fill=(240, 235, 220))
    d.ellipse([cx - 16, y - 2, cx + 16, y + 22], fill=(255, 190, 60))
    d.ellipse([cx - 9, y + 2, cx + 9, y + 20], fill=(255, 240, 160))
    d.line([cx, y + 14, cx, y + 18], fill=INK, width=2)


def scene_busts(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 32, 68))
    # siren glow
    d.ellipse([x + 16, y + 6, x + 56, y + 26], fill=(255, 60, 60))
    d.ellipse([x + w - 56, y + 6, x + w - 16, y + 26], fill=(60, 120, 255))
    # handcuffs
    for cx in (x + 84, x + 156):
        d.ellipse([cx - 20, y + 10, cx + 20, y + 40], outline=GOLD, width=5)
    d.line([x + 104, y + 25, x + 136, y + 25], fill=GOLD, width=5)
    d.ellipse([x + w // 2 - 5, y + 20, x + w // 2 + 5, y + 30], fill=GOLD)


SCENES = {
    "cop31": scene_cop31, "riyadh": scene_riyadh, "peru": scene_peru,
    "kryvyi": scene_kryvyi, "davao": scene_davao, "bitcoin": scene_bitcoin,
    "rahul": scene_rahul, "icj": scene_icj, "kyiv": scene_kyiv,
    "ukeu": scene_ukeu, "oil": scene_oil, "nsw": scene_nsw,
    "kenya": scene_kenya, "sa": scene_sa, "busts": scene_busts,
}

# ---------------------------------------------------------------- data
# (banner, loc line, headline, deck, source, scene, region)
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


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DARK)
    for poly in CONTINENTS:
        pts = [(x + fx * w, y + fy * h) for fx, fy in poly]
        d.polygon(pts, fill=TAN, outline=(180, 155, 100))
    for num, (fx, fy) in PINS.items():
        px, py = x + fx * w, y + fy * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=1)
        f = SANSB(10)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 6), t, font=f,
               fill=WHITE)
    for num, (fx, fy) in DOTS.items():
        px, py = x + fx * w, y + fy * h
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 220, 230),
                  outline=WHITE, width=1)


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
    f = fit_text(d, title, "DejaVuSerif-Bold.ttf", 64, right - mx)
    d.text(((W - d.textlength(title, font=f)) / 2, 24), title, font=f,
           fill=INK)
    deck = ("Climate summit runs past its deadline · Three missiles shot "
            "down over Riyadh · Strong quake shakes Peru")
    fd = SERIFI(15)
    d.text(((W - d.textlength(deck, font=fd)) / 2, 92), deck, font=fd,
           fill=INK)

    # ---- numbers strip
    y0, y1 = 112, 184
    d.line([mx, y0, right, y0], fill=INK, width=2)
    d.line([mx, y1, right, y1], fill=INK, width=2)
    cw = (right - mx) / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = mx + i * cw
        fn = fit_text(d, num, "DejaVuSerif-Bold.ttf", 46, cw - 16)
        d.text((cx + 8, y0 + 4), num, font=fn, fill=INK)
        fl = SANS(11)
        for j, line in enumerate(wrap(d, label, fl, cw - 16)):
            d.text((cx + 8, y0 + 46 + j * 12), line, font=fl, fill=GREY)
        if i:
            d.line([cx, y0 + 4, cx, y1 - 4], fill=RED, width=2)

    # ---- region bar
    y0, y1 = 188, 202
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

    # ---- heroes (scene 110 + loc + 2-line headline + 2-line deck)
    hy = 206
    hw = 326
    gap = 9
    hero_chips = ["NO DEAL · DAY 13", "3 SHOT DOWN", "00:09 UTC · 108 KM DEEP"]
    for i, (banner_txt, loc, head, deck_txt, src, scene, _reg) in enumerate(HEROES):
        x = mx + i * (hw + gap)
        SCENES[scene](d, x, hy, hw, 110)
        banner(d, x, hy, hw, 26, banner_txt, size=20)
        chip(d, x + 6, hy + 110 - 24, hero_chips[i])
        d.text((x, hy + 116), loc, font=SANSB(11), fill=RED)
        fh = SERIFB(21)
        lines = wrap(d, head, fh, hw)
        yy = hy + 132
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 25
        fd = SANS(12)
        lines = wrap(d, deck_txt + "  " + src, fd, hw)
        yy = hy + 132 + 2 * 25 + 4
        for line in lines[:2]:
            d.text((x, yy), line, font=fd, fill=(40, 40, 40))
            yy += 14

    # ---- cards header
    cy = 432
    d.text((mx, cy), "MORE FROM SATURDAY", font=SANSB(12), fill=RED)
    rt = "STORIES 4–15"
    d.text((right - d.textlength(rt, font=SANSB(12)), cy), rt,
           font=SANSB(12), fill=INK)
    d.line([mx, cy + 17, right, cy + 17], fill=INK, width=2)

    # ---- cards: 4 cols x 3 rows, scene 36 + loc + 2-line headline + deck
    cw2, ch2 = 243, 100
    gap2 = 8
    top = 456
    for i, (banner_txt, loc, head, deck_txt, src, scene, _reg) in enumerate(CARDS):
        row, col = divmod(i, 4)
        x = mx + col * (cw2 + gap2)
        y = top + row * (ch2 + 4)
        SCENES[scene](d, x, y, cw2, 36)
        banner(d, x, y, cw2, 15, banner_txt, size=12)
        d.text((x, y + 39), loc, font=SANSB(9), fill=RED)
        fh = SERIFB(13)
        lines = wrap(d, head, fh, cw2)
        yy = y + 51
        for line in lines[:2]:
            d.text((x, yy), line, font=fh, fill=INK)
            yy += 15
        fd = SANS(10)
        lines = wrap(d, deck_txt + " " + src, fd, cw2)
        yy = y + 51 + 2 * 15 + 1
        for line in lines[:2]:
            d.text((x, yy), line, font=fd, fill=(40, 40, 40))
            yy += 11

    # ---- bottom: map + briefs
    by = 772
    d.text((mx, by), "WHERE IT HAPPENED", font=SANSB(12), fill=INK)
    bx = 360
    d.text((bx, by), "ALSO ON SATURDAY 21 NOVEMBER 2026 — 27 MORE STORIES",
           font=SANSB(12), fill=INK)
    d.line([mx, by + 17, right, by + 17], fill=INK, width=2)
    draw_map(d, mx, by + 22, 338, 140)
    d.text((mx, by + 166),
           "Pins 1–15 are the lead stories and cards; dots 16–42 are the briefs.",
           font=SANS(10), fill=GREY)
    # briefs in 3 columns x 9 rows
    colw = (right - bx) / 3
    fb = SANS(10)
    for i, (num, text, _reg) in enumerate(BRIEFS):
        col, row = divmod(i, 9)
        x = bx + col * colw
        y = by + 24 + row * 16
        d.text((x, y), f"{num}  {text}", font=fb, fill=INK)

    # ---- DATE CHECK
    dy = 956
    d.rectangle([mx, dy, right, dy + 36], outline=RED, width=2)
    fd = SANS(11)
    lines = wrap(d, DATE_CHECK, fd, right - mx - 16)
    yy = dy + 4
    for line in lines[:3]:
        d.text((mx + 8, yy), line, font=fd, fill=INK)
        yy += 11

    # ---- footer
    foot = ("Every story here happened, or was first reported, on Saturday "
            "21 November 2026. Officials' counts and claims are attributed.")
    d.text((mx, 998), foot, font=SANS(10), fill=GREY)
    rt = "Sources named beside each story · original drawings"
    d.text((right - d.textlength(rt, font=SANS(10)), 998), rt,
           font=SANS(10), fill=GREY)

    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {size} bytes ({size / 1024:.1f} KiB)")


if __name__ == "__main__":
    build()
