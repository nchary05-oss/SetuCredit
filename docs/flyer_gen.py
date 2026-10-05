#!/usr/bin/env python3
"""SetuCredit A5 4-page flyer generator (reportlab, print-ready)."""
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math

W, H = A5  # 419.5 x 595.3 pt

NAVY = HexColor("#0F172A")
SURFACE = HexColor("#1E293B")
SURFACE2 = HexColor("#131F38")
LINE = HexColor("#334155")
ACCENT = HexColor("#38BDF8")
ACTION = HexColor("#0EA5E9")
DEEP = HexColor("#0369A1")
GREEN = HexColor("#34D399")
GREENDK = HexColor("#052E16")
YELLOW = HexColor("#FBBF24")
MUTED = HexColor("#94A3B8")
DIM = HexColor("#CBD5E1")
TEXT = HexColor("#E2E8F0")
INK = HexColor("#0F172A")
PAPER = HexColor("#FFFFFF")
LIGHTBG = HexColor("#F1F5F9")
CHIPBG = HexColor("#E0F2FE")

OUT = "/Volumes/data/Projects/SetuCredit/docs/SetuCredit_Flyer_A5.pdf"


def rounded(c, x, y, w, h, r, fill=None, stroke=None, sw=1):
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    c.setLineWidth(sw)
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
    if fill and stroke:
        c.setLineWidth(sw)
        c.drawPath(p, stroke=1, fill=1)
    elif fill:
        c.drawPath(p, stroke=0, fill=1)
    else:
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def text(c, x, y, s, size=10, color=INK, font="Helvetica-Bold", align="left", leading=None):
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)
    c.restoreState()


def wrapped(c, x, y, maxw, s, size=8.5, color=INK, font="Helvetica", leading=None, align="left", max_lines=None):
    from reportlab.lib.utils import simpleSplit
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    lh = leading or size * 1.35
    lines = simpleSplit(s, font, size, maxw)
    if max_lines:
        lines = lines[:max_lines]
    cy = y
    for ln in lines:
        if align == "center":
            c.drawCentredString(x, cy, ln)
        elif align == "right":
            c.drawRightString(x, cy, ln)
        else:
            c.drawString(x, cy, ln)
        cy -= lh
    c.restoreState()
    return cy


def bridge_mark(c, x, y, s=30):
    rounded(c, x, y, s, s, s * 0.28, fill=HexColor("#0C4A6E"), stroke=None)
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.setLineCap(1)
    # deck
    c.line(x + s*0.12, y + s*0.42, x + s*0.88, y + s*0.42)
    # arch
    p = c.beginPath()
    p.moveTo(x + s*0.16, y + s*0.25)
    p.curveTo(x + s*0.3, y + s*0.62, x + s*0.7, y + s*0.62, x + s*0.84, y + s*0.25)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def phone(c, x, y, w, h, title, body_lines, cta, accent_bar=True, otp=False, checks=None):
    # frame
    rounded(c, x, y, w, h, 14, fill=HexColor("#0B1223"), stroke=LINE, sw=1.2)
    # notch
    c.saveState()
    c.setFillColor(HexColor("#1E293B"))
    rounded(c, x + w/2 - 28, y + h - 12, 56, 8, 4, fill=HexColor("#1E293B"), stroke=None)
    c.restoreState()
    sx = x + 10
    sw = w - 20
    cy = y + h - 30
    # top brand row
    c.saveState()
    c.setFillColor(HexColor("#0C4A6E"))
    rounded(c, sx, cy - 4, 18, 18, 5, fill=HexColor("#0C4A6E"), stroke=None)
    c.restoreState()
    text(c, sx + 23, cy, "SetuCredit", size=7.5, color=PAPER, font="Helvetica-Bold")
    cy -= 20
    # progress dots
    for i in range(5):
        c.saveState()
        c.setFillColor(ACCENT if i <= 2 else HexColor("#334155"))
        c.circle(sx + 8 + i*16, cy, 5, stroke=0, fill=1)
        c.restoreState()
    cy -= 16
    # card
    rounded(c, sx, cy - 118, sw, 122, 9, fill=SURFACE, stroke=HexColor("#243352"), sw=0.8)
    text(c, sx + 10, cy - 12, title, size=8, color=PAPER, font="Helvetica-Bold")
    ly = cy - 26
    if otp:
        rounded(c, sx+10, ly-22, sw-20, 24, 6, fill=NAVY, stroke=LINE, sw=0.8)
        text(c, sx+sw/2, ly-8, "• •  4  8  • •", size=10, color=PAPER, font="Helvetica-Bold", align="center")
        ly -= 34
        c.saveState()
        c.setFillColor(GREEN)
        rounded(c, sx+10, ly-14, sw-20, 18, 5, fill=ACTION, stroke=None)
        c.restoreState()
        text(c, sx+sw/2, ly-3, cta, size=7, color=HexColor("#082F49"), font="Helvetica-Bold", align="center")
    elif checks:
        for ch in checks[:4]:
            c.saveState()
            c.setFillColor(HexColor("#0B3D24"))
            c.circle(sx+15, ly-3, 6, stroke=0, fill=1)
            c.setFillColor(GREEN)
            c.setFont("Helvetica-Bold", 6)
            c.drawCentredString(sx+15, ly-1, "✓")
            c.restoreState()
            text(c, sx+26, ly-2, ch, size=6.5, color=DIM, font="Helvetica")
            ly -= 15
        rounded(c, sx+10, ly-20, sw-20, 20, 5, fill=ACTION, stroke=None)
        text(c, sx+sw/2, ly-8, cta, size=7, color=HexColor("#082F49"), font="Helvetica-Bold", align="center")
    else:
        for bl in body_lines[:3]:
            wrapped(c, sx+10, ly, sw-20, bl, size=6.5, color=DIM, font="Helvetica", leading=8.5, max_lines=2)
            ly -= 20
        rounded(c, sx+10, ly-16, sw-20, 20, 5, fill=ACTION, stroke=None)
        text(c, sx+sw/2, ly-4, cta, size=7, color=HexColor("#082F49"), font="Helvetica-Bold", align="center")


def gauge(c, cx, cy, r, score=72):
    # track = upper semicircle (east -> north -> west)
    c.saveState()
    c.setStrokeColor(HexColor("#CBD5E1"))
    c.setLineWidth(10)
    c.setLineCap(1)
    c.arc(cx-r, cy-r, cx+r, cy+r, startAng=0, extent=180)
    # value arc: filled from west (left) clockwise over the top
    c.setStrokeColor(ACTION)
    c.setLineWidth(10)
    frac = score/100.0
    c.arc(cx-r, cy-r, cx+r, cy+r, startAng=180, extent=-180*frac)
    # needle dot at the value end (angle measured from east, CCW)
    ang_deg = 180 - 180*frac
    ang = math.radians(ang_deg)
    nx = cx + (r)*math.cos(ang)
    ny = cy + (r)*math.sin(ang)
    c.setFillColor(DEEP)
    c.circle(nx, ny, 5, stroke=0, fill=1)
    c.restoreState()
    text(c, cx, cy - 34, str(score), size=30, color=INK, font="Helvetica-Bold", align="center")
    text(c, cx, cy - 46, "/ 100  •  GOOD", size=7.5, color=HexColor("#64748B"), font="Helvetica-Bold", align="center")


# ---------------- pages ----------------

def page1(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # glow
    c.saveState()
    c.setFillColor(HexColor("#13294B"))
    c.circle(W/2, H-170, 150, stroke=0, fill=1)
    c.restoreState()
    # top brand
    bridge_mark(c, 36, H-64, 30)
    text(c, 72, H-52, "SetuCredit", size=14, color=PAPER, font="Helvetica-Bold")
    text(c, 72, H-64, "VOICE-FIRST  •  DPI-POWERED", size=6.5, color=ACCENT, font="Helvetica-Bold")
    text(c, W-36, H-50, "Page 1 / Cover", size=6, color=MUTED, font="Helvetica", align="right")

    text(c, 36, H-110, "VOICE-FIRST  •  CONSENT-FIRST", size=7.5, color=ACCENT, font="Helvetica-Bold")
    text(c, 36, H-142, "Your records are", size=29, color=PAPER, font="Helvetica-Bold")
    text(c, 36, H-172, "already a credit", size=29, color=ACCENT, font="Helvetica-Bold")
    text(c, 36, H-202, "history.", size=29, color=ACCENT, font="Helvetica-Bold")
    wrapped(c, 36, H-228, W-90,
        "Land ownership, electricity bills and bank activity say more than a bureau file ever could. SetuCredit turns them into an index a lender can act on.",
        size=9, color=DIM, font="Helvetica", leading=13.5)

    # chips
    chips = ["Consent first", "Data never stored", "6 languages"]
    cx = 36
    chip_y = H-288
    for ch in chips:
        tw = c.stringWidth(ch, "Helvetica-Bold", 7.5) + 26
        rounded(c, cx, chip_y, tw, 22, 11, fill=SURFACE, stroke=LINE, sw=0.8)
        c.saveState()
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx+9, chip_y+7, "✓")
        c.restoreState()
        text(c, cx+21, chip_y+7, ch, size=7.5, color=DIM, font="Helvetica-Bold")
        cx += tw + 8

    # bridge illustration strip
    ill_top = H-304
    ill_h = 124
    rounded(c, 36, ill_top-ill_h, W-72, ill_h, 14, fill=SURFACE2, stroke=HexColor("#243352"), sw=1)
    # deck line
    c.saveState()
    c.setStrokeColor(ACCENT); c.setLineWidth(2.2); c.setLineCap(1)
    deck_y = ill_top - 58
    c.line(56, deck_y, W-56, deck_y)
    c.setStrokeColor(HexColor("#475569")); c.setLineWidth(5)
    tx1, tx2 = 80, W-80
    c.line(tx1, ill_top-28, tx1, ill_top-ill_h+10); c.line(tx2, ill_top-28, tx2, ill_top-ill_h+10)
    c.setStrokeColor(ACCENT); c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(tx1, ill_top-ill_h+28); p.curveTo(140, ill_top-28, W-140, ill_top-28, tx2, ill_top-ill_h+28)
    c.drawPath(p, stroke=1, fill=0)
    # phone + bank glyphs
    rounded(c, 60, deck_y-22, 44, 56, 7, fill=NAVY, stroke=LINE, sw=1)
    text(c, 82, deck_y+8, "◂)))", size=9, color=ACCENT, font="Helvetica-Bold", align="center")
    text(c, 82, deck_y-8, "APP", size=7, color=DIM, font="Helvetica-Bold", align="center")
    rounded(c, W-104, deck_y-22, 44, 56, 7, fill=SURFACE, stroke=LINE, sw=1)
    text(c, W-82, deck_y+6, "₹", size=16, color=GREEN, font="Helvetica-Bold", align="center")
    text(c, W-82, deck_y-8, "NBFC", size=6.5, color=DIM, font="Helvetica-Bold", align="center")
    # waves
    c.setStrokeColor(HexColor("#0EA5E9"))
    c.setLineWidth(1.4)
    for i, wy in enumerate([ill_top-ill_h+28, ill_top-ill_h+22, ill_top-ill_h+16]):
        p = c.beginPath()
        p.moveTo(150, wy)
        for k in range(4):
            p.curveTo(160+k*32, wy-5, 170+k*32, wy+5, 182+k*32, wy)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    text(c, W/2, ill_top-ill_h-14, "Borrower phone  →  SetuCredit bridge  →  Partner NBFC  →  UPI / IMPS", size=6.5, color=MUTED, font="Helvetica-Bold", align="center")

    # CTA row
    rounded(c, 36, 96, W-72, 56, 10, fill=ACTION, stroke=None)
    text(c, W/2, 128, "Start onboarding  •  Takes about 2 minutes", size=10, color=HexColor("#082F49"), font="Helvetica-Bold", align="center")
    text(c, W/2, 114, "Keep your Aadhaar-linked phone handy  •  Hindi  Bengali  Tamil  Telugu  Marathi  English", size=6.5, color=HexColor("#082F49"), font="Helvetica", align="center")
    text(c, 36, 74, "Middleware orchestration over India's DPI  •  Bhashini  •  DigiLocker  •  Sahamati AA  •  RBI ULI", size=6, color=MUTED, font="Helvetica", align="left")
    text(c, 36, 40, "Consent first  •  Pass-through by default  •  Data never stored", size=6.5, color=DIM, font="Helvetica-Bold")
    text(c, W-36, 40, "setucredit.in", size=7, color=ACCENT, font="Helvetica-Bold", align="right")


def page2(c):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    # header bar
    c.setFillColor(NAVY); c.rect(0, H-78, W, 78, stroke=0, fill=1)
    bridge_mark(c, 30, H-58, 24)
    text(c, 60, H-46, "How it works — four steps, one bridge", size=11, color=PAPER, font="Helvetica-Bold")
    text(c, 60, H-60, "Inside  •  Page 2  •  Guided in your language, by voice or text", size=7, color=MUTED, font="Helvetica")
    text(c, W-30, H-46, "2 MIN", size=16, color=ACCENT, font="Helvetica-Bold", align="right")
    text(c, W-30, H-60, "approx. journey", size=6.5, color=MUTED, font="Helvetica", align="right")

    y = H-108
    steps = [
        ("1", "Speak or type", "Six Indian languages, one step at a time.", "Start onboarding"),
        ("2", "Verify once with OTP", "6-digit code to your Aadhaar-linked mobile.", "Verify OTP"),
        ("3", "Consent — then only then", "Tick exactly what you share. Time-bound.", "Grant consent"),
        ("4", "Get your Readiness Index", "Parallel pull → BRI 0–100 → lender handoff.", "Check readiness"),
    ]
    for num, t1, t2, _ in steps:
        c.saveState()
        c.setFillColor(CHIPBG)
        c.circle(44, y-6, 11, stroke=0, fill=1)
        c.setFillColor(DEEP)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(44, y-3, num)
        c.restoreState()
        text(c, 62, y, t1, size=9, color=INK, font="Helvetica-Bold")
        text(c, 62, y-12, t2, size=7.5, color=HexColor("#475569"), font="Helvetica")
        y -= 32
    y -= 2
    text(c, 30, y, "Live app screens (PWA — 3G/4G friendly, low storage)", size=7.5, color=DEEP, font="Helvetica-Bold")
    y -= 10
    # 3 phones
    pw, ph = 112, 218
    gap = (W - 60 - 3*pw)/2
    px = 30
    phone(c, px, y-ph, pw, ph, "Get started",
          ["Choose language", "Voice guides you", "2-min journey"], "Start")
    px += pw + gap
    phone(c, px, y-ph, pw, ph, "Verify number", [], "Verify OTP", otp=True)
    px += pw + gap
    phone(c, px, y-ph, pw, ph, "Grant consent", [], "Grant consent", checks=["Land registry", "Electricity bills", "Bank summary", "ULI history"])
    y = y - ph - 14
    # Aadhaar note
    rounded(c, 30, y-52, W-60, 52, 8, fill=HexColor("#EFF6FF"), stroke=HexColor("#BFDBFE"), sw=0.8)
    text(c, 42, y-16, "Aadhaar verification — we never ask for your 12-digit number.", size=7.5, color=DEEP, font="Helvetica-Bold")
    wrapped(c, 42, y-28, W-84, "OTP proves possession of your Aadhaar-linked mobile. DigiLocker eKYC accepted where offered. Nothing is stored.", size=7, color=HexColor("#475569"), font="Helvetica", leading=9.5)
    y -= 64
    text(c, 30, y, "No bureau file? No problem. Your everyday records speak for you.", size=7.5, color=HexColor("#475569"), font="Helvetica-Bold")


def page3(c):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY); c.rect(0, H-78, W, 78, stroke=0, fill=1)
    bridge_mark(c, 30, H-58, 24)
    text(c, 60, H-46, "Your score — the Borrower Readiness Index", size=11, color=PAPER, font="Helvetica-Bold")
    text(c, 60, H-60, "Inside  •  Page 3  •  Explainable, consented, handed to the lender", size=7, color=MUTED, font="Helvetica")
    text(c, W-30, H-46, "0–100", size=16, color=ACCENT, font="Helvetica-Bold", align="right")

    gauge(c, W/2, H-210, 62, score=72)
    # bands
    bands = [("STRONG 80+", "#34D399"), ("GOOD 60+", "#38BDF8"), ("FAIR 40+", "#FBBF24"), ("BUILDING <40", "#CBD5E1")]
    bx = 30
    bw = (W-60-3*8)/4
    for name, col in bands:
        rounded(c, bx, H-288, bw, 24, 12, fill=HexColor(col), stroke=None)
        # text size adjust
        fs = 6.5 if len(name) > 9 else 7
        text(c, bx+bw/2, H-274, name, size=fs, color=INK, font="Helvetica-Bold", align="center")
        bx += bw + 8
    wrapped(c, 30, H-304, W-60, "Suggested loan range travels with the score. Bands help the partner NBFC decide in minutes — the lending decision stays with them.", size=7.5, color=HexColor("#475569"), font="Helvetica", leading=10.5, align="center")

    text(c, 30, H-340, "Four consented sources, pulled in parallel", size=8.5, color=INK, font="Helvetica-Bold")
    y = H-352
    sources = [
        ("Land registry", "Dharani / Bhulekh", "ownership"),
        ("Electricity bills", "State DISCOMs", "repayment discipline"),
        ("Bank summary", "Sahamati AA", "cash-flow activity"),
        ("Lending history", "RBI ULI", "past borrowing"),
    ]
    cols = 2
    tw = (W-60-10)/2
    for i, (a, b, d) in enumerate(sources):
        col = i % 2; row = i // 2
        x = 30 + col*(tw+10)
        yy = y - row*62
        rounded(c, x, yy-56, tw, 56, 9, fill=LIGHTBG, stroke=HexColor("#E2E8F0"), sw=0.8)
        c.saveState()
        c.setFillColor(HexColor("#0C4A6E"))
        rounded(c, x+10, yy-24, 22, 22, 6, fill=HexColor("#0C4A6E"), stroke=None)
        c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x+21, yy-10, "✓" if i < 3 else "₹")
        c.restoreState()
        text(c, x+38, yy-14, a, size=8, color=INK, font="Helvetica-Bold")
        text(c, x+38, yy-25, b + "  •  " + d, size=6.5, color=HexColor("#64748B"), font="Helvetica")
        rounded(c, x+10, yy-46, 52, 14, 7, fill=HexColor("#DCFCE7"), stroke=None)
        text(c, x+36, yy-37, "PULLED ✓", size=6, color=HexColor("#166534"), font="Helvetica-Bold", align="center")

    y2 = H-352-2*62-8
    rounded(c, 30, y2-88, W-60, 88, 10, fill=NAVY, stroke=None)
    text(c, 44, y2-20, "Pass-through by design — record contents are never stored.", size=8, color=PAPER, font="Helvetica-Bold")
    bullets = [
        "Consent gate enforced in code (HTTP 403 without valid consent).",
        "Features computed in memory; Postgres keeps audit metadata only.",
        "Every pull logged: source, time, count, consent ID — never payloads.",
    ]
    by = y2 - 34
    for b in bullets:
        text(c, 44, by, "•  " + b, size=7, color=DIM, font="Helvetica")
        by -= 13
    text(c, 30, y2-100, "DPDP: explicit, time-bound, revocable consent. Revocation aborts in-flight pulls.", size=7, color=HexColor("#64748B"), font="Helvetica-Bold")


def page4(c):
    c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
    bridge_mark(c, 36, H-64, 30)
    text(c, 72, H-52, "SetuCredit", size=14, color=PAPER, font="Helvetica-Bold")
    text(c, 72, H-64, "THE MIDDLEWARE BRIDGE", size=6.5, color=ACCENT, font="Helvetica-Bold")
    text(c, W-36, H-50, "Back  •  Page 4", size=6, color=MUTED, font="Helvetica", align="right")

    text(c, 36, H-104, "Two minutes to a lender-ready package.", size=13, color=PAPER, font="Helvetica-Bold")
    text(c, 36, H-118, "What happens after you tap “Check my readiness”", size=8, color=MUTED, font="Helvetica")

    # timeline
    y = H-140
    tl = [
        ("0:00", "Parallel pull", "Land • power • bank • ULI, 5s timeout each"),
        ("0:40", "BRI scoring", "In-memory features → 0–100 + attributions"),
        ("1:20", "Signed handoff", "HMAC webhook to partner NBFC"),
        ("2:00", "Disbursal", "UPI / IMPS on the lender's rails"),
    ]
    for t, h1, h2 in tl:
        c.saveState()
        c.setFillColor(ACTION)
        c.circle(48, y-6, 5, stroke=0, fill=1)
        if y > H-140-3*44:
            c.setStrokeColor(HexColor("#334155")); c.setLineWidth(1.5)
            c.line(48, y-12, 48, y-44)
        c.restoreState()
        text(c, 62, y, t, size=7, color=ACCENT, font="Helvetica-Bold")
        text(c, 100, y, h1, size=9, color=PAPER, font="Helvetica-Bold")
        text(c, 100, y-13, h2, size=7.5, color=MUTED, font="Helvetica")
        y -= 44

    # DPI strip
    rounded(c, 36, y-72, W-72, 72, 10, fill=SURFACE, stroke=LINE, sw=0.8)
    text(c, 50, y-20, "Built on India's public rails", size=8, color=PAPER, font="Helvetica-Bold")
    rails = ["Bhashini", "DigiLocker", "Sahamati AA", "RBI ULI", "UPI/IMPS"]
    rx = 50
    for r in rails:
        tw = c.stringWidth(r, "Helvetica-Bold", 7) + 18
        rounded(c, rx, y-50, tw, 20, 10, fill=NAVY, stroke=HexColor("#243352"), sw=0.8)
        text(c, rx+tw/2, y-37, r, size=7, color=ACCENT, font="Helvetica-Bold", align="center")
        rx += tw + 6

    y -= 88
    # QR + contact split
    rounded(c, 36, y-108, 120, 108, 10, fill=PAPER, stroke=None)
    # fake QR
    import random
    random.seed(7)
    qx, qy = 48, y-96
    for i in range(12):
        for j in range(12):
            if random.random() > 0.45:
                c.setFillColor(INK)
                c.rect(qx+i*7, qy+j*7, 6.2, 6.2, stroke=0, fill=1)
    text(c, 96, y-114, "SCAN TO TRY", size=6.5, color=DEEP, font="Helvetica-Bold", align="center")
    # contact
    text(c, 170, y-16, "Talk to us", size=10, color=PAPER, font="Helvetica-Bold")
    wrapped(c, 170, y-32, W-170-36, "Pilot with your NBFC or SHG federation. Voice onboarding in 6 languages, printable BRI report, HMAC-signed handoff.", size=8, color=DIM, font="Helvetica", leading=11.5)
    text(c, 170, y-72, "Email: hello@setucredit.in     Web: setucredit.in", size=8, color=ACCENT, font="Helvetica-Bold")
    text(c, 170, y-86, "Hackathon build — stubs behind DPIAdapter; production via RBIH onboarding.", size=6.5, color=MUTED, font="Helvetica")

    c.saveState()
    c.setStrokeColor(HexColor("#243352")); c.setLineWidth(0.8)
    c.line(36, 44, W-36, 44)
    c.restoreState()
    text(c, 36, 30, "Consent first  •  Pass-through by default  •  Data never stored", size=6.5, color=DIM, font="Helvetica-Bold")
    text(c, W-36, 30, "SetuCredit  •  BRI v1", size=6.5, color=MUTED, font="Helvetica", align="right")


def build():
    c = canvas.Canvas(OUT, pagesize=A5)
    c.setAuthor("SetuCredit")
    c.setTitle("SetuCredit — 4-page A5 flyer (front + back)")
    c.setSubject("Voice-first DPI-powered credit bridge")
    page1(c); c.showPage()
    page2(c); c.showPage()
    page3(c); c.showPage()
    page4(c); c.showPage()
    c.save()
    print("wrote", OUT)


if __name__ == "__main__":
    build()
