#!/usr/bin/env python3
"""Draw the 23 November 2026 front page from news.json to entry.png.

A newspaper front page, 1024 by 1024: masthead, one hero story with a
drawn globe, a 3 by 2 grid of shorter stories, a ticker and a sources
line. Everything is drawn with Pillow; the output is deterministic.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024
MARGIN = 36
PAPER = (248, 244, 233)
INK = (22, 21, 19)
MUTED = (90, 86, 77)
RED = (179, 32, 44)
BLUE = (31, 78, 121)
PALE_BLUE = (219, 231, 240)

FONTS = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
# No DejaVu italic or oblique on this machine, so the standfirst and
# caption use the regular serif instead.
SERIF_I = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(text, fnt, width, draw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, leading, color=INK):
    for line in wrap(text, fnt, width, draw):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def rule(draw, x0, x1, y, width=2, color=INK):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def draw_globe(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PALE_BLUE,
                 outline=BLUE, width=4)
    for frac in (-0.55, 0.0, 0.55):
        x = cx + frac * r
        half = r * math.sqrt(max(0.0, 1.0 - frac * frac))
        draw.line([(x, cy - half), (x, cy + half)], fill=BLUE, width=2)
    for frac in (-0.5, 0.0, 0.5):
        y = cy + frac * r
        half = r * math.sqrt(max(0.0, 1.0 - frac * frac))
        draw.line([(cx - half, y), (cx + half, y)], fill=BLUE, width=2)
    crack = [(cx - 12, cy - r + 8), (cx + 10, cy - r * 0.55),
             (cx - 14, cy - r * 0.15), (cx + 12, cy + r * 0.25),
             (cx - 8, cy + r * 0.6), (cx + 6, cy + r - 10)]
    draw.line(crack, fill=RED, width=5, joint="curve")


def build(data):
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)
    right = SIZE - MARGIN

    # Masthead
    title = SERIF_B(56)
    d.text((SIZE / 2, 30), data["masthead"], font=title, fill=INK,
           anchor="ma")
    date_f = SANS_B(17)
    d.text((MARGIN, 102), "MONDAY", font=date_f, fill=INK)
    d.text((right, 102), "23 NOVEMBER 2026", font=date_f, fill=INK,
           anchor="ra")
    rule(d, MARGIN, right, 132, 3)
    rule(d, MARGIN, right, 138, 1)

    # Hero
    hero = data["hero"]
    hx, hy = MARGIN, 156
    text_w = 560
    d.text((hx, hy), hero["kicker"], font=SANS_B(19), fill=RED)
    y = para(d, hx, hy + 30, hero["headline"], SERIF_B(50), text_w, 56)
    y = para(d, hx, y + 8, hero["standfirst"], SERIF_I(21), text_w, 27,
             color=(44, 42, 38))
    for chunk in hero["body"]:
        y = para(d, hx, y + 10, chunk, SANS(18), text_w, 24)
    # Globe panel on the right
    gx = 660
    draw_globe(d, gx + 130, 300, 92)
    cap_y = para(d, gx, 415, hero["caption"], SERIF_I(15), 328, 20,
                 color=MUTED)

    rule(d, MARGIN, right, 496, 2)

    # Story grid, 3 columns by 2 rows
    col_w = 306
    gap = 19
    row_h = 188
    top = 514
    for idx, story in enumerate(data["stories"]):
        col, row = idx % 3, idx // 3
        x = MARGIN + col * (col_w + gap)
        yy = top + row * row_h
        d.text((x, yy), story["tag"], font=SANS_B(15),
               fill=tuple(int(story["color"][i:i + 2], 16)
                          for i in (1, 3, 5)))
        yy = para(d, x, yy + 24, story["headline"], SERIF_B(21), col_w, 26)
        para(d, x, yy + 4, story["body"], SANS(15), col_w, 20,
             color=(44, 42, 38))

    # Ticker
    rule(d, MARGIN, right, 896, 2)
    tick = data["ticker"]
    y = para(d, MARGIN, 910, tick, SANS(15), right - MARGIN, 20)

    # Footer
    rule(d, MARGIN, right, 988, 1)
    d.text((SIZE / 2, 994), data["sources"], font=SANS(12), fill=MUTED,
           anchor="ma")
    return img


def main():
    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = build(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
