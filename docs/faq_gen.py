#!/usr/bin/env python3
"""SetuCredit application FAQ generator (reportlab platypus, A4)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
    PageBreak, HRFlowable,
)

W, H = A4
OUT = "/Volumes/data/Projects/SetuCredit/docs/SetuCredit_FAQ.pdf"

NAVY = HexColor("#0F172A")
DEEP = HexColor("#0369A1")
ACCENT = HexColor("#0EA5E9")
INK = HexColor("#1E293B")
MUTED = HexColor("#64748B")
LINE = HexColor("#CBD5E1")
CHIPBG = HexColor("#EFF6FF")

TITLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=NAVY)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED)
SECT = ParagraphStyle("sect", fontName="Helvetica-Bold", fontSize=13, leading=16,
                      textColor=NAVY, spaceBefore=14, spaceAfter=4)
Q = ParagraphStyle("q", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
                   textColor=DEEP, spaceBefore=8, spaceAfter=2)
A = ParagraphStyle("a", fontName="Helvetica", fontSize=9, leading=13, textColor=INK,
                   spaceAfter=2, leftIndent=0)
BUL = ParagraphStyle("bul", parent=A, leftIndent=14, bulletIndent=4, spaceAfter=1)
NOTE = ParagraphStyle("note", parent=A, textColor=MUTED, fontSize=8.5)

FAQ = [
    ("Getting started", [
        ("What is SetuCredit?",
         "A voice-first middleware that connects micro-borrowers with no bureau credit history to partner lenders over India's public digital infrastructure (DPI). It assembles a consented, pre-underwritten package, scores it as a Borrower Readiness Index (BRI 0–100), and hands it to a partner NBFC. SetuCredit itself never lends and never decides who gets a loan."),
        ("Who is it for?",
         "Unbanked and thin-file Indian micro-borrowers whose everyday records — land ownership, electricity-bill payments, bank activity, past borrowing — can stand in for a bureau file; and the NBFCs / SHG federations that want to underwrite them."),
        ("How long does it take?",
         "About two minutes: language selection, a 6-digit OTP to your Aadhaar-linked mobile, consent, parallel data pull with scoring, and a printable result."),
        ("Does it cost anything?",
         "There is no fee inside the app. If a partner lender approves you, their own interest and charges apply under their terms."),
        ("What do I need before I begin?",
         ["Your Aadhaar-linked mobile phone, switched on, with that SIM in the phone.",
          "About two minutes and the web app open in Chrome or Edge.",
          "Volume up — every step is spoken aloud in your language."]),
        ("Which languages work?",
         "Hindi, Bengali, Tamil, Telugu, Marathi, and English. Buttons, instructions, and voice prompts all switch instantly when you pick one."),
        ("I have no CIBIL / bureau record. Can I still apply?",
         "Yes — that is the point. Land, electricity, bank, and ULI lending records are read (with your consent) and turned into a BRI score a lender can act on."),
        ("What kinds of loans can this help with?",
         "The ULI data behind the score supports Kisan Credit Card and other farm loans, MSME working-capital loans, secured loans against property, and housing loans — with borrower consent, the lender pulls exactly the records each product needs. SetuCredit itself targets micro-borrowers, including farmers and first-time borrowers."),
    ]),
    ("OTP and Aadhaar verification", [
        ("Why do you send an OTP?",
         "The 6-digit code goes only to your Aadhaar-linked mobile and proves the session belongs to you. Nothing else is collected at this stage."),
        ("Will you ask for my 12-digit Aadhaar number?",
         "Never — not on screen, not on call, not in storage. Verification is mobile-OTP possession proof plus DigiLocker masked eKYC where the lender offers it."),
        ("I am not getting the OTP. What do I do?",
         ["Confirm the SIM registered with your Aadhaar is in your phone and has signal; wait 60 seconds.",
          "Forgot which number is linked? Check the mAadhaar app or the UIDAI portal's Verify Mobile service.",
          "Changed number or never linked one? Visit an Aadhaar Seva Kendra with ID proof — linking needs an in-person biometric.",
          "Still nothing? Go back and start a fresh session for a new code."]),
        ("I entered the wrong number / wrong OTP. What now?",
         "Tap 'Resend OTP' on the same screen for a fresh code — resending also resets the 5-guess counter. If the number itself is wrong, go back and start a fresh session."),
        ("What is the 'Dev mode OTP' shown on screen?",
         "A testing shortcut visible only when the system runs in development mode (ENV=dev). It never appears in production."),
    ]),
    ("Consent and privacy", [
        ("What exactly am I sharing?",
         "Only what you tick: land-registry records, electricity-bill payments, bank-account summary (via Account Aggregator), and lending history (via RBI ULI). Nothing is read before you grant consent, and the consent gate is enforced in code — pulls without valid consent are rejected (HTTP 403)."),
        ("What is the difference between ULI and Account Aggregator?",
         "Both move your data only with consent, but they do different jobs. Account Aggregators are licensed companies that share your financial data (bank statements and the like) with whoever you approve. ULI is a single platform by the RBI Innovation Hub that standardises access to financial and non-financial records — including government databases such as GST and digital land records — so a lender needs one integration instead of many bilateral ones. They complement each other: AAs can feed consolidated financial data into ULI's wider pool. That is why the consent screen lists them as two separate ticks."),
        ("Must I share all four sources?",
         "No. Tick only what you are comfortable with. Sparse consents still score — the remaining source weights renormalize — though fewer sources can lower confidence in the score."),
        ("How long does consent last? Can I take it back?",
         "Consent is explicit, time-bound, and revocable under the DPDP Act, 2023. Revoking ends the session's consent, resets the flow, and aborts any in-flight data pull."),
        ("What is stored about me?",
         "Almost nothing. Postgres keeps only the audit ledger (what happened, when, record counts, consent ID), consent records, and appraisal outcomes (score, per-source ok/failed). Borrower records, derived features, and voice audio are processed in memory and never written to disk — not even as features."),
        ("Who sees my data?",
         "The scoring service sees source payloads in transit to compute the score; the partner lender receives a signed package with appraisal ID, BRI, model version, and suggested loan range — never your raw records."),
        ("What is the audit ledger?",
         "An append-only log of events (source pulled, score computed, handoff sent) with timestamps, counts, and consent references — used for compliance and debugging. It contains no record contents."),
    ]),
    ("Your score and result", [
        ("What is the Borrower Readiness Index (BRI)?",
         "A 0–100 score computed from your consented records, with per-source attributions so you can see what drove it. The current model is heuristic v1; a trained model plugs in behind the same interface later."),
        ("What do the bands mean?",
         "TABLE:Strong|80–100|Eligible for larger loan amounts|Good|60–79|Likely to qualify with most partner lenders|Fair|40–59|Smaller loans; on-time bills and an active bank account improve it|Building|0–39|Not ready yet — build bill/repayment history, then check again"),
        ("My score is low. What should I do?",
         "Pay electricity bills on time, keep your bank account active with regular inflows, and keep up any existing repayments — then run a fresh session. The Fair and Building guidance on your report says exactly this."),
        ("Is the suggested loan range guaranteed?",
         "No. It is indicative for the partner lender from BRI 40 upwards; the final amount is set by the lender after their own assessment."),
        ("One of my sources shows 'failed'. Is my result still valid?",
         "Yes, if the minimum required sources succeeded — the result carries per-source status and the score accounts for missing coverage. If every source fails, the appraisal stops and you return to the consent step."),
        ("Can I keep or print my report?",
         "Yes — the result page has a 'Print / Save as PDF' button that produces a clean printable report."),
    ]),
    ("Lender handoff and money", [
        ("Who actually gives the loan?",
         "A partner NBFC, never SetuCredit. We hand over a signed, pre-underwritten package; the lender approves and disburses on their own rails."),
        ("Does ULI itself approve my loan?",
         "No. ULI is a backend data-exchange platform: the flow is loan request, consented data fetch, data response, and then the lender's own loan decision. SetuCredit mirrors this — we prepare the package and the score, the partner lender decides."),
        ("How does the money reach me?",
         "By UPI or IMPS transfer after the lender's approval. Timelines depend on the lender."),
        ("What does 'handoff: simulated' mean?",
         "The lender webhook is not configured in this environment, so the handoff was simulated instead of sent. In production it is an HMAC-signed webhook post."),
        ("My package could not be shared. What now?",
         "Start a new session and try again. If it repeats, the lender endpoint may be down — the report's handoff status will say so."),
        ("How do I know the loan was disbursed?",
         "The lender confirms back through a signed callback, which stamps the appraisal as disbursed with a timestamp."),
    ]),
    ("Troubleshooting", [
        ("I am stuck mid-flow. How do I recover?",
         "Use 'Start over' in the header to begin a fresh session. Sessions also expire on their own (short-lived server state) if you abandon them."),
        ("What do error messages mean?",
         "TABLE:Consent error (403)|No valid consent covers the request — grant or re-grant consent.|Conflict (409)|The step is out of order for this session — follow the progress bar order.|All sources failed (502)|Every data pull failed or scoring is unreachable — retry; if it persists, a source or the scoring service is down."),
        ("Does it work on slow networks or without internet?",
         "The PWA is built light for 3G/4G, but OTP delivery, consent, and the data pull all need connectivity. Mini­mum: a data connection that can load the app and receive SMS."),
    ]),
    ("For developers and integrators", [
        ("What is the system made of?",
         "FastAPI backend (orchestrator + consent gate + audit ledger), a separate BRI scoring microservice, a React PWA with 6-language UI and voice, Postgres for audit metadata only, and Redis for OTP/session state."),
        ("What are the key API endpoints?",
         "TABLE:POST /v1/sessions|Create appraisal session|POST /v1/sessions/{id}/otp|Send / verify Aadhaar OTP|POST /v1/sessions/{id}/consents|Grant scoped consent|POST /v1/sessions/{id}/appraise|Pull, score, hand off|GET /v1/appraisals/{id}|Appraisal + disbursal state|POST /v1/webhooks/disbursal|Lender callback (HMAC-signed)"),
        ("Are webhooks secured?",
         "Yes — outbound handoff and inbound disbursal callbacks are HMAC-signed with WEBHOOK_SECRET (default 'dev-webhook-secret' in dev/compose; rotate in production), timestamped, and replay-protected."),
        ("How do I run it locally?",
         "TABLE:Full stack|docker compose -f infra/docker-compose.yml --profile app up --build  (PWA :8080, backend :8000, scoring :8001)|Infra only|docker compose -f infra/docker-compose.yml up -d postgres redis|Backend|uv run uvicorn app.main:app --port 8000|Scoring|uv run uvicorn service.main:app --port 8001|Frontend|cd frontend && npm install && npm run dev"),
        ("Do tests need anything running?",
         "Yes — integration tests expect local Postgres and Redis from compose, and self-skip with a hint if they are down. Install with 'uv sync --all-packages', lint with 'uv run ruff check backend scoring'."),
        ("How do live ULI / SMS plug in?",
         "Set ULI_MODE=live with RBIH credentials for the real lending-history adapter (default is a deterministic stub), and OTP_MODE=sms with DLT sender/template for a real SMS provider. Scale context from the ULI pilot (Oct 2024 figures): 27 lenders, 12 loan journeys, 54 APIs, 5 Account Aggregators onboarded. DigiLocker eKYC and the first NBFC pilot are the remaining production steps."),
    ]),
]


def footer(canv, doc):
    canv.saveState()
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(20 * mm, 12 * mm, "SetuCredit — Application FAQ  •  Consent first  •  Pass-through by default  •  Data never stored")
    canv.drawRightString(W - 20 * mm, 12 * mm, f"Page {doc.page}")
    # top brand bar on first page only
    if doc.page == 1:
        canv.setFillColor(NAVY)
        canv.rect(0, H - 18 * mm, W, 18 * mm, stroke=0, fill=1)
        canv.setFillColor(HexColor("#38BDF8"))
        canv.setFont("Helvetica-Bold", 11)
        canv.drawString(20 * mm, H - 11.5 * mm, "SetuCredit")
        canv.setFillColor(HexColor("#94A3B8"))
        canv.setFont("Helvetica", 8)
        canv.drawRightString(W - 20 * mm, H - 11.5 * mm, "Application FAQ")
    canv.restoreState()


CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=INK)
CELL_H = ParagraphStyle("cellH", parent=CELL, fontName="Helvetica-Bold", textColor=DEEP)


def band_table(rows):
    data = [[Paragraph("Band", CELL_H), Paragraph("Range", CELL_H), Paragraph("What it means", CELL_H)]]
    for r in rows:
        data.append([Paragraph(r[0], CELL_H), Paragraph(r[1], CELL), Paragraph(r[2], CELL)])
    t = Table(data, colWidths=[28 * mm, 24 * mm, 118 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11.5),
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def kv_table(rows):
    data = [[Paragraph(k, CELL_H), Paragraph(v, CELL)] for k, v in rows]
    t = Table(data, colWidths=[60 * mm, 106 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11.5),
        ("TEXTCOLOR", (0, 0), (0, -1), DEEP),
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4,
                            leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=24 * mm, bottomMargin=18 * mm,
                            title="SetuCredit — Application FAQ",
                            author="SetuCredit")
    story = []
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Application FAQ", TITLE))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Borrowers, lenders, and integrators ask these most. Answers follow the shipped app, "
        "the user guide, and the handbook — consent first, pass-through by default, data never stored.",
        SUB))
    story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=4, spaceBefore=6))

    for sec_title, items in FAQ:
        story.append(Paragraph(sec_title, SECT))
        for q, a in items:
            block = [Paragraph(q, Q)]
            if isinstance(a, list):
                for b in a:
                    block.append(Paragraph(b, BUL, bulletText="•"))
            elif a.startswith("TABLE:"):
                cells = a[len("TABLE:"):].split("|")
                if q.startswith("What do the bands"):
                    block.append(band_table([cells[i:i + 3] for i in range(0, len(cells), 3)]))
                elif len(cells) % 2 == 0:
                    block.append(kv_table([cells[i:i + 2] for i in range(0, len(cells), 2)]))
                else:
                    block.append(Paragraph(a, A))
            else:
                block.append(Paragraph(a, A))
            story.append(KeepTogether(block))

    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=4, spaceBefore=4))
    story.append(Paragraph(
        "Still stuck? Start a fresh session from the app's 'Start over' button — most transient errors clear that way. "
        "Sources: README.md, docs/ARCHITECTURE.md, SetuCredit User Guide, Handbook, in-app help text, "
        "and PwC 'Unified Lending Interface (ULI): Changing the credit landscape in India' (Dec 2024).",
        NOTE))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
