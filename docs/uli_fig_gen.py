#!/usr/bin/env python3
"""Redraw PwC ULI whitepaper Figure 4 (functional architecture) as PNG.

Reference: PwC 'Unified Lending Interface (ULI): Changing the credit
landscape in India' (Dec 2024), Figure 4. Original: docs/ULI.pdf.
"""
from PIL import Image, ImageDraw, ImageFont

OUT = "/Volumes/data/Projects/SetuCredit/docs/ULI_architecture.png"

W, H = 1400, 1000
BG = (255, 255, 255)
GRAY = (217, 217, 217)
DARK = (38, 38, 38)
ORANGE = (199, 91, 18)
INK = (20, 20, 20)
MUTED = (110, 110, 110)

def font(size, bold=False):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
F_TITLE = font(34, True)
F_HEAD = font(24, True)
F_BOX = font(24, True)
F_SMALL = font(20)
F_LBL = font(22, True)
F_ATTR = font(18)


def box(x, y, w, h, fill, outline=None):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=outline or fill, width=2)


def centered(x, y, w, lines, fnt, fill):
    cy = y
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=fnt)
        d.text((x + (w - (bb[2] - bb[0])) / 2, cy), ln, font=fnt, fill=fill)
        cy += (bb[3] - bb[1]) + 8


def arrow(x1, y1, x2, y2, color, width=10, both=False):
    d.line([x1, y1, x2, y2], fill=color, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 26
    for ex, ey, aa in ((x2, y2, ang), (x1, y1, ang + math.pi) if both else (None, None, None)):
        if ex is None:
            continue
        d.polygon([(ex, ey),
                   (ex - L * math.cos(aa - 0.42), ey - L * math.sin(aa - 0.42)),
                   (ex - L * math.cos(aa + 0.42), ey - L * math.sin(aa + 0.42))],
                  fill=color)


def panel(px, py, pw, ph, title, cells):
    """Gray panel with dark sub-boxes. cells: list of (label, x, y, w, h)."""
    box(px, py, pw, ph, GRAY)
    bb = d.textbbox((0, 0), title, font=F_HEAD)
    d.text((px + (pw - (bb[2] - bb[0])) / 2, py + 12), title, font=F_HEAD, fill=INK)
    for label, cx, cy, cw, ch in cells:
        box(px + cx, py + cy, cw, ch, DARK)
        bb2 = d.multiline_textbbox((0, 0), label, font=F_BOX)
        d.multiline_text((px + cx + (cw - (bb2[2] - bb2[0])) / 2,
                          py + cy + (ch - (bb2[3] - bb2[1])) / 2),
                         label, font=F_BOX, fill=(255, 255, 255), align="center")


# title + attribution
d.text((60, 30), "Figure 4: ULI functional architecture", font=F_TITLE, fill=INK)
d.text((60, 80), "Redrawn from PwC 'Unified Lending Interface (ULI): Changing the credit landscape in India' (Dec 2024).",
       font=F_ATTR, fill=MUTED)

# Lenders (top-left)
panel(60, 150, 470, 230, "Lenders",
      [("Banks", 30, 110, 195, 90), ("Non-banks", 245, 110, 195, 90)])
# ULI central (top-right)
box(870, 150, 300, 230, ORANGE)
centered(870, 215, 300, ["ULI", "central", "system"], font(32, True), (255, 255, 255))
# Borrowers (bottom-left)
panel(60, 590, 470, 330, "Borrowers",
      [("Retail", 30, 110, 195, 85), ("MSME", 245, 110, 195, 85),
       ("Agri", 30, 210, 195, 85), ("Dairy", 245, 210, 195, 85)])
d.text((60 + 470 - 130, 590 + 330 - 40), "...Others", font=F_SMALL, fill=INK)
# Data sources (bottom-right)
panel(700, 590, 640, 330, "Data sources",
      [("Aadhaar", 25, 105, 135, 70), ("PAN", 170, 105, 135, 70),
       ("Land records", 315, 105, 150, 70), ("GST", 475, 105, 140, 70),
       ("ONDC", 25, 190, 135, 70), ("OCEN", 170, 190, 135, 70),
       ("Account aggregators", 315, 190, 300, 70)])
d.text((700 + 640 - 130, 590 + 330 - 40), "...Others", font=F_SMALL, fill=INK)

# 1. Loan request (orange, borrowers -> lenders)
arrow(200, 560, 200, 410, ORANGE)
d.text((80, 470), "1. Loan", font=F_LBL, fill=INK)
d.text((80, 500), "request", font=F_LBL, fill=INK)
# 5. Loan decision (dark, lenders -> borrowers)
arrow(330, 410, 330, 560, DARK)
d.text((360, 470), "5. Loan", font=F_LBL, fill=INK)
d.text((360, 500), "decision", font=F_LBL, fill=INK)
# 2. Data request (orange, lenders -> ULI)
arrow(530, 220, 840, 220, ORANGE)
d.text((600, 165), "2. Data request", font=F_LBL, fill=INK)
# 4. Data response (dark, ULI -> lenders)
arrow(840, 320, 530, 320, DARK)
d.text((600, 335), "4. Data response", font=F_LBL, fill=INK)
# 3. Fetch data (orange double, ULI <-> sources)
arrow(1020, 410, 1020, 560, ORANGE, both=True)
d.text((830, 470), "3. Fetch data", font=F_LBL, fill=INK)

img.save(OUT)
print("wrote", OUT, img.size)
