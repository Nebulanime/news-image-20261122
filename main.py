#!/usr/bin/env python3
"""The World in One Image — 22 November 2026.

Deterministic newspaper front page (1024x1024 PNG) summarising the day's
world news. Renders with Pillow; if Pillow is unavailable, falls back to
copying the bundled entry.png next to this script.

Output: /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Running this program twice produces byte-identical output: no randomness,
no timestamps, no network.
"""

import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - fallback path
    Image = None

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (250, 246, 238)
INK = (17, 17, 17)
RED = (166, 25, 46)
GRAY = (85, 85, 85)
RULE = (150, 150, 150)
SEA = (205, 224, 236)
LAND = (232, 220, 192)
LAND2 = (226, 210, 178)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


F_SERIF_B = lambda s: load_font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: load_font("DejaVuSerif.ttf", s)
F_SANS_B = lambda s: load_font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: load_font("DejaVuSans.ttf", s)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap using real glyph widths. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(draw, text, font, x, y, max_width, line_h, fill=INK):
    """Draw wrapped text, return y just below the last line."""
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_centered(draw, text, font, cx, y, fill=INK):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return y


def draw_rule(draw, x0, x1, y, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_gulf_map(draw, x0, y0, x1, y1):
    """Simple schematic map of the Gulf region (not to scale)."""
    draw.rectangle([x0, y0, x1, y1], fill=SEA, outline=INK, width=2)
    # Iran (top-right landmass)
    draw.polygon(
        [(x0 + 150, y0), (x1, y0), (x1, y0 + 78), (x0 + 205, y0 + 95),
         (x0 + 170, y0 + 60)],
        fill=LAND2, outline=INK)
    # Arabian Peninsula (left/bottom landmass)
    draw.polygon(
        [(x0, y0 + 30), (x0 + 150, y0), (x0 + 170, y0 + 60),
         (x0 + 205, y0 + 95), (x0 + 150, y0 + 150), (x0 + 60, y0 + 190),
         (x0, y0 + 190)],
        fill=LAND, outline=INK)
    # Strait of Hormuz (narrow gap, red dashes)
    for i in range(5):
        yy = y0 + 96 + i * 7
        draw.line([(x0 + 205, yy), (x0 + 218, yy + 4)], fill=RED, width=3)
    # Labels
    small = F_SANS_B(11)
    tiny = F_SANS(10)
    draw.text((x0 + 8, y0 + 6), "IRAN", font=small, fill=INK)
    draw.text((x0 + 8, y0 + 120), "SAUDI ARABIA", font=tiny, fill=GRAY)
    draw.text((x0 + 198, y0 + 148), "GULF OF OMAN", font=tiny, fill=(40, 70, 100))
    draw.text((x0 + 8, y0 + 168), "OMAN", font=small, fill=INK)
    # Strike dots
    def dot(cx, cy, color=RED):
        r = 5
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
                     outline=(255, 255, 255), width=1)

    dot(x0 + 78, y0 + 42)   # Kuwait
    draw.text((x0 + 88, y0 + 34), "KUWAIT", font=small, fill=RED)
    dot(x0 + 148, y0 + 92)  # Bahrain
    draw.text((x0 + 158, y0 + 84), "BAHRAIN", font=small, fill=RED)
    dot(x0 + 212, y0 + 100)  # Hormuz
    draw.text((x0 + 222, y0 + 92), "HORMUZ", font=small, fill=RED)
    dot(x0 + 120, y0 + 165, color=(30, 80, 140))  # Oman coast
    draw.text((x0 + 130, y0 + 157), "TANKER HIT", font=small,
              fill=(30, 80, 140))


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    cx = W // 2

    # ---- Masthead ----
    y = 26
    draw_centered(d, "THE WORLD IN ONE IMAGE", F_SERIF_B(58), cx, y)
    y = 96
    draw_rule(d, x0, x1, y, 1)
    y = 104
    d.text((x0, y), "SUNDAY, 22 NOVEMBER 2026", font=F_SANS_B(14), fill=INK)
    draw_centered(d, "WORLD NEWS IN ONE PAGE", F_SANS_B(14), cx, y)
    right = "No. 22  •  FREE"
    d.text((x1 - d.textlength(right, font=F_SANS_B(14)), y), right,
           font=F_SANS_B(14), fill=INK)
    y = 126
    draw_rule(d, x0, x1, y, 3)
    draw_rule(d, x0, x1, y + 5, 1)

    # ---- Lead kicker + headline ----
    y = 142
    d.text((x0, y), "★  GULF CRISIS — IRAN STRIKES U.S. BASES",
           font=F_SANS_B(16), fill=RED)
    y = 166
    y = draw_block(d, "IRAN STRIKES U.S. BASES IN KUWAIT AND BAHRAIN",
                   F_SERIF_B(38), x0, y, CW, 46)
    y += 2
    y = draw_block(
        d,
        "Gulf escalation widens as tankers come under fire off Oman — an "
        "ADNOC vessel is attacked, one crewman missing; Britain reports two "
        "tanker incidents near the Strait of Hormuz.",
        F_SERIF(18), x0, y, CW, 24, fill=(40, 40, 40))
    y += 6

    # ---- Lead body (left) + map (right) ----
    body_x, body_w = x0, 600
    map_x0, map_x1 = 660, x1
    top = y
    y = draw_block(
        d,
        "Iranian missiles struck United States air bases in Kuwait and "
        "targets in Bahrain on Sunday, in the sharpest escalation of the "
        "Gulf crisis, as tankers were hit by projectiles off Oman and near "
        "the Strait of Hormuz.",
        F_SERIF(16), body_x, y, body_w, 22)
    y += 6
    y = draw_block(
        d,
        "Britain reported two tanker incidents near Oman. An ADNOC vessel "
        "was attacked and one crewman is missing, and Tehran claimed a ship "
        "struck a mine east of Hormuz. Washington raised economic pressure "
        "on Iran.",
        F_SERIF(16), body_x, y, body_w, 22)
    y += 6
    y = draw_block(
        d,
        "President Trump is pressing for a permanent nuclear deal with "
        "Tehran. Vice President Vance refused to back an American attack "
        "on Iran.",
        F_SERIF(16), body_x, y, body_w, 22)
    body_bottom = y

    # Map box
    map_y0, map_y1 = top, top + 252
    d.rectangle([map_x0, map_y0, map_x1, map_y1], outline=INK, width=2)
    draw_centered(d, "THE GULF — WHERE IT HAPPENED", F_SANS_B(12),
                  (map_x0 + map_x1) // 2, map_y0 + 8)
    draw_rule(d, map_x0 + 8, map_x1 - 8, map_y0 + 28, 1)
    draw_gulf_map(d, map_x0 + 10, map_y0 + 36, map_x1 - 10, map_y1 - 40)
    draw_centered(d, "Tankers hit off Oman; mine claimed east of Hormuz.",
                  F_SERIF(12), (map_x0 + map_x1) // 2, map_y1 - 26,
                  fill=GRAY)

    y = max(body_bottom, map_y1) + 12
    draw_rule(d, x0, x1, y, 2)
    y += 12

    # ---- Two medium cards ----
    mid_y = y
    col_w = (CW - 24) // 2
    c1x, c2x = x0, x0 + col_w + 24
    d.text((c1x, mid_y), "APEC  •  SHENZHEN", font=F_SANS_B(13), fill=RED)
    d.text((c2x, mid_y), "EARTHQUAKE  •  PERU", font=F_SANS_B(13), fill=RED)
    y1 = draw_block(d, "TRUMP LANDS IN SHENZHEN FOR APEC SUMMIT",
                    F_SERIF_B(21), c1x, mid_y + 22, col_w, 26)
    y2 = draw_block(d, "6.9 QUAKE SHAKES PERU'S ANDES",
                    F_SERIF_B(21), c2x, mid_y + 22, col_w, 26)
    y1 = draw_block(
        d,
        "President Trump arrived in Shenzhen for the APEC summit, calling "
        "it “momentous.” A trilateral meeting with China’s Xi Jinping and "
        "Russia’s Vladimir Putin is planned.",
        F_SERIF(15), c1x, y1 + 4, col_w, 20)
    y2 = draw_block(
        d,
        "A magnitude 6.9 earthquake shook the Andes in Peru on Sunday. No "
        "damage or casualties had been reported by press time.",
        F_SERIF(15), c2x, y2 + 4, col_w, 20)
    y = max(y1, y2)
    # vertical divider between the two cards
    d.line([(x0 + col_w + 12, mid_y), (x0 + col_w + 12, y)],
           fill=RULE, width=1)
    y += 10
    draw_rule(d, x0, x1, y, 2)
    y += 12

    # ---- Three small cards ----
    small_y = y
    sw = (CW - 2 * 20) // 3
    cols = [x0, x0 + sw + 20, x0 + 2 * (sw + 20)]
    cards = [
        ("ESTONIA", "ESTONIA SHUTS BORDER WITH RUSSIA",
         "Moscow denounced the closure as a “new Iron Curtain.”"),
        ("BALTIC SEA", "DRONE HITS RUSSIAN CARGO SHIP",
         "Denmark expelled a Russian diplomat over an alleged plot to kill "
         "a Ukrainian rapper."),
        ("MYANMAR  •  ICJ", "FRANCE SEEKS U.N. ACTION ON MYANMAR",
         "Paris asked the Security Council to intervene after Myanmar "
         "rejected an International Court of Justice ruling."),
    ]
    bottoms = []
    for (kick, head, body), cx0 in zip(cards, cols):
        d.text((cx0, small_y), kick, font=F_SANS_B(12), fill=RED)
        yy = draw_block(d, head, F_SERIF_B(17), cx0, small_y + 20, sw, 21)
        yy = draw_block(d, body, F_SERIF(14), cx0, yy + 3, sw, 19)
        bottoms.append(yy)
    for cx0 in cols[1:]:
        d.line([(cx0 - 10, small_y), (cx0 - 10, max(bottoms))],
               fill=RULE, width=1)
    y = max(bottoms) + 10
    draw_rule(d, x0, x1, y, 2)
    y += 10

    # ---- Also Today ticker ----
    label = "ALSO TODAY"
    lab_font = F_SANS_B(13)
    lab_w = d.textlength(label, font=lab_font) + 16
    d.rectangle([x0, y, x0 + lab_w, y + 24], fill=INK)
    d.text((x0 + 8, y + 4), label, font=lab_font, fill=(255, 255, 255))
    tick = ("Melania Trump: Russia–Ukraine ceasefire possible before "
            "Christmas  •  Mexico arrests cartel boss “El Chapo Isidro”; "
            "11 killed in Sinaloa  •  Bolsonaro in ICU with acute bowel "
            "obstruction  •  UNIFIL begins handover in southern Lebanon")
    y = draw_block(d, tick, F_SANS(13), x0 + lab_w + 10, y + 2,
                   CW - lab_w - 10, 18)
    y += 6
    draw_rule(d, x0, x1, y, 1, fill=RULE)
    y += 8

    # ---- Footer ----
    draw_centered(
        d,
        "Sources: The Daily Jagran • ARY News • Times of India • wire "
        "reports  —  The World in One Image, Sunday 22 November 2026",
        F_SANS(11), cx, y, fill=GRAY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = Path(out_dir) / "entry.png"
    if Image is None:
        src = Path(__file__).resolve().parent / "entry.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, out_path)
        print("Pillow missing: copied bundled entry.png to", out_path)
        return 0
    img = render()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    # Keep a bundled copy next to this script for the no-Pillow fallback.
    try:
        here = Path(__file__).resolve().parent / "entry.png"
        if here.resolve() != out_path.resolve():
            img.save(here, format="PNG")
    except OSError:
        pass
    print("wrote", out_path, img.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
