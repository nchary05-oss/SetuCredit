#!/usr/bin/env python3
"""SetuCredit deployment & run guide generator (reportlab platypus, A4).

Covers both audiences in one document:
  Part A — Operator: install, configure, run, verify, troubleshoot.
  Part B — Borrower: step-by-step app walkthrough.
Output: docs/SetuCredit_Deployment_and_Run_Guide.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable,
)

W, H = A4
OUT = "/Volumes/data/Projects/SetuCredit/docs/SetuCredit_Deployment_and_Run_Guide.pdf"

NAVY = HexColor("#0F172A")
DEEP = HexColor("#0369A1")
INK = HexColor("#1E293B")
MUTED = HexColor("#64748B")
LINE = HexColor("#CBD5E1")
WHITE = HexColor("#FFFFFF")
ZEBRA = HexColor("#F8FAFC")
CODE_BG = HexColor("#0F172A")
CODE_FG = HexColor("#BAE6FD")

TITLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=NAVY)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED)
PART = ParagraphStyle("part", fontName="Helvetica-Bold", fontSize=15, leading=19,
                      textColor=WHITE, backColor=NAVY, borderPadding=(6, 8, 6),
                      spaceBefore=16, spaceAfter=4)
SECT = ParagraphStyle("sect", fontName="Helvetica-Bold", fontSize=12, leading=15,
                      textColor=NAVY, spaceBefore=12, spaceAfter=4)
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=13.2,
                      textColor=INK, spaceAfter=3)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=1.5)
NUM = ParagraphStyle("num", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=1.5)
NOTE = ParagraphStyle("note", parent=BODY, textColor=MUTED, fontSize=8.5,
                      borderPadding=(6, 6, 6), backColor=ZEBRA, spaceBefore=4, spaceAfter=4)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=8.2, leading=11.5,
                      textColor=CODE_FG, backColor=CODE_BG, borderPadding=(6, 6, 6),
                      spaceBefore=3, spaceAfter=5)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=INK)
CELL_H = ParagraphStyle("cellH", parent=CELL, fontName="Helvetica-Bold", textColor=DEEP)
CELL_C = ParagraphStyle("cellC", parent=CELL, fontName="Courier", fontSize=8)
CELL_CH = ParagraphStyle("cellCH", parent=CELL_C, fontName="Courier-Bold", textColor=DEEP)


def footer(canv, doc):
    canv.saveState()
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(20 * mm, 12 * mm,
                    "SetuCredit \u2014 Deployment & Run Guide  \u2022  Offline Docker bundle")
    canv.drawRightString(W - 20 * mm, 12 * mm, f"Page {doc.page}")
    if doc.page == 1:
        canv.setFillColor(NAVY)
        canv.rect(0, H - 18 * mm, W, 18 * mm, stroke=0, fill=1)
        canv.setFillColor(HexColor("#38BDF8"))
        canv.setFont("Helvetica-Bold", 11)
        canv.drawString(20 * mm, H - 11.5 * mm, "SetuCredit")
        canv.setFillColor(HexColor("#94A3B8"))
        canv.setFont("Helvetica", 8)
        canv.drawRightString(W - 20 * mm, H - 11.5 * mm, "Deployment & Run Guide")
    canv.restoreState()


def kv_table(rows, widths=(52 * mm, 114 * mm)):
    data = [[Paragraph(k, CELL_H), Paragraph(v, CELL)] for k, v in rows]
    t = Table(data, colWidths=list(widths))
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, ZEBRA]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def code_table(rows, widths=(52 * mm, 114 * mm)):
    data = [[Paragraph(k, CELL_CH), Paragraph(v, CELL_C)] for k, v in rows]
    t = Table(data, colWidths=list(widths))
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, ZEBRA]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=24 * mm, bottomMargin=18 * mm,
        title="SetuCredit \u2014 Deployment & Run Guide",
        author="SetuCredit")
    s = []
    s.append(Spacer(1, 6 * mm))
    s.append(Paragraph("Deployment &amp; Run Guide", TITLE))
    s.append(Spacer(1, 2 * mm))
    s.append(Paragraph(
        "Offline Docker bundle: install, run, demo, and troubleshoot the full SetuCredit stack "
        "without internet access \u2014 plus the borrower walkthrough for operators running a demo. "
        "Stack: React PWA (port 8080), FastAPI backend (8000), BRI scoring service (8001), "
        "Postgres, Redis.", SUB))
    s.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=4, spaceBefore=6))

    # ---------------- Part A ----------------
    s.append(Paragraph("Part A \u2014 Operator: deploy and run", PART))

    s.append(Paragraph("1 &nbsp; What is in the bundle", SECT))
    s.append(Paragraph(
        "The offline bundle is a single folder (<b>setucredit-deploy/</b>) that runs the whole "
        "system with no image pulls. Keep it together \u2014 the compose file refers to the "
        "image archives by name.", BODY))
    s.append(kv_table([
        ("docker-compose.yml", "Full 5-service stack (frontend, backend, scoring, postgres, redis). "
         "Pre-wired ports and in-network URLs; secrets read from <b>.env</b> with safe dev defaults."),
        (".env.example", "Copy to <b>.env</b> and edit. Every knob the stack reads (see \u00a74)."),
        ("images/*.tar.gz", "Prebuilt Docker images, one archive each: backend, scoring, frontend, "
         "postgres:16-alpine, redis:7-alpine. Load with <b>scripts/load-images.sh</b>."),
        ("scripts/run.sh", "Starts everything detached and waits until the backend reports healthy."),
        ("scripts/stop.sh", "Stops the stack (data volumes kept; flag to wipe, see \u00a78)."),
        ("docs/*.pdf", "This guide. Print it or keep it on the demo laptop."),
        ("SHA256SUMS", "Integrity hashes for every file \u2014 verify before loading images."),
    ]))

    s.append(Paragraph("2 &nbsp; Prerequisites", SECT))
    s.append(kv_table([
        ("OS / CPU", "64-bit Linux, macOS, or Windows + WSL2. Images are linux/amd64."),
        ("Docker", "Docker Engine 24+ with Compose v2 (<b>docker compose version</b>)."),
        ("RAM / disk", "4 GB RAM free; ~4 GB free disk for images + DB volume. Bundled images total ~1.6 GB uncompressed."),
        ("Ports free", "8080 (PWA), 8000 (API), 8001 (scoring), 5432 (Postgres), 6379 (Redis)."),
        ("Network", "None required after loading images \u2014 except SMS/ULI live modes and OTP delivery in a real demo."),
    ]))

    s.append(Paragraph("3 &nbsp; Install and start (3 steps)", SECT))
    s.append(Paragraph("<b>Step 1 \u2014 verify integrity</b> (from the bundle root):", BODY))
    s.append(Paragraph("sha256sum -c SHA256SUMS", CODE))
    s.append(Paragraph("<b>Step 2 \u2014 load the prebuilt images:</b>", BODY))
    s.append(Paragraph("./scripts/load-images.sh", CODE))
    s.append(Paragraph("<b>Step 3 \u2014 configure and start:</b>", BODY))
    s.append(Paragraph("cp .env.example .env&nbsp;&nbsp;# edit secrets for your machine<br/>./scripts/run.sh", CODE))
    s.append(Paragraph(
        "run.sh starts all five containers detached, runs DB migrations automatically, and polls "
        "the backend health endpoint until it answers. Expect everything green within 1\u20132 minutes "
        "on a laptop.", NOTE))

    s.append(Paragraph("4 &nbsp; Check it is up", SECT))
    s.append(code_table([
        ("PWA", "http://localhost:8080/"),
        ("API docs", "http://localhost:8000/docs"),
        ("Backend health", "curl http://localhost:8000/healthz"),
        ("Scoring health", "curl http://localhost:8001/healthz"),
    ]))
    s.append(Paragraph(
        "Healthy backend answers <b>{\"status\":\"ok\",\"postgres\":\"ok\",\"redis\":\"ok\"}</b>. "
        "If it answers <b>\"degraded\"</b> (HTTP 503), Postgres or Redis is not reachable \u2014 see \u00a77. "
        "Scoring answers <b>{\"status\":\"ok\",\"model_version\":\"bri-heuristic-0.1.0\"}</b>.", BODY))

    s.append(Paragraph("5 &nbsp; Configuration (.env)", SECT))
    s.append(Paragraph(
        "Only <b>.env</b> needs editing; the compose file already wires service-to-service URLs. "
        "Unset optional hooks keep safe demo behaviour (simulated lender handoff, stub data, stub OTP).", BODY))
    s.append(kv_table([
        ("ENV (default dev)", "dev exposes the OTP on screen for demos (<b>dev_otp</b>). Set <b>prod</b> for any real user."),
        ("WEBHOOK_SECRET", "HMAC key for lender webhooks. Default <b>dev-webhook-secret</b> \u2014 rotate in production."),
        ("PARTNER_WEBHOOK_URL (unset)", "Partner NBFC endpoint. Unset = handoff recorded as <b>\"simulated\"</b>; set it to send the real signed webhook."),
        ("ULI_MODE (stub)", "Deterministic lending-history data. Set <b>live</b> with RBIH credentials for the real ULI adapter."),
        ("OTP_MODE (stub)", "On-screen codes. Set <b>sms</b> with DLT sender/template for a real SMS provider."),
        ("OTP_MAX_ATTEMPTS (5)", "Wrong-guess cap per code; resending resets it."),
    ]))

    s.append(Paragraph("6 &nbsp; Two-minute demo script", SECT))
    s.append(Paragraph(
        "Open <b>http://localhost:8080</b> (Chrome/Edge, volume up) and narrate the consent-first story:", BODY))
    for i, step in enumerate([
        "<b>Language (10s)</b> \u2014 pick Hindi/Bengali/Tamil/Telugu/Marathi/English; UI and voice follow instantly.",
        "<b>OTP (30s)</b> \u2014 enter the Aadhaar-linked mobile, read the on-screen code (dev mode), verify. Point out the 12-digit number is never asked or stored.",
        "<b>Consent (20s)</b> \u2014 tick the sources; note it is time-bound, revocable, and enforced in code (pulls without consent get HTTP 403).",
        "<b>Appraise (30s)</b> \u2014 parallel pull across land, electricity, bank, ULI \u2192 BRI score + suggested loan range.",
        "<b>Result (30s)</b> \u2014 gauge with legends below, band note, biggest-lever tip, per-source breakdown, lender handoff status, Print / Save as PDF.",
    ], 1):
        s.append(Paragraph(f"{i}. &nbsp;{step}", NUM))
    s.append(Paragraph(
        "Score bands: <b>Strong 80\u2013100</b> (larger loans) \u00b7 <b>Good 60\u201379</b> (most partner lenders) "
        "\u00b7 <b>Fair 40\u201359</b> (smaller loans; bills + activity improve it) \u00b7 "
        "<b>Building 0\u201339</b> (build history, then check again). Loan-range suggestion appears from BRI 40 up.", NOTE))

    s.append(Paragraph("7 &nbsp; Troubleshooting", SECT))
    s.append(kv_table([
        ("Port already in use", "<b>docker compose ps</b>; free the port or stop the other stack. Compose error names the clash."),
        ("Backend \"degraded\" / 503", "Postgres/Redis still starting or down: <b>docker compose ps</b>, then <b>docker compose logs postgres redis</b>. Data is intact; wait or restart."),
        ("Frontend blank / API unreachable", "<b>docker compose logs backend frontend</b>. Check http://localhost:8000/healthz directly."),
        ("HTTP 403 on appraise", "No valid consent covers the request \u2014 grant/re-grant consent in the app. This is the DPDP gate working as designed."),
        ("HTTP 409", "Step run out of order (e.g. appraise before OTP). Follow the progress bar; or start a fresh session."),
        ("All sources failed / scoring down", "<b>docker compose logs scoring backend</b>; restart scoring. Partial-source results still score if the minimum set succeeded."),
        ("Fresh start", "<b>./scripts/stop.sh</b> then <b>./scripts/run.sh</b>. Nuclear: <b>docker compose --profile app down -v</b> wipes DB volumes."),
    ]))

    s.append(Paragraph("8 &nbsp; Stop, update, back up", SECT))
    s.append(Paragraph("./scripts/stop.sh", CODE))
    s.append(Paragraph(
        "Keeps the <b>pgdata</b> volume (audit ledger, consents, outcomes) so a restart resumes history. "
        "To wipe demo data between shows, use <b>docker compose --profile app down -v</b>. "
        "To update: replace the bundle folder, re-run load + run. Back up Postgres with <b>pg_dump</b> "
        "against localhost:5432 if the ledger matters.", BODY))

    s.append(Paragraph("9 &nbsp; Security notes (read before any real user)", SECT))
    for b in [
        "Bundle defaults are <b>demo credentials</b> (postgres password, webhook secret). Rotate them via <b>.env</b> before production.",
        "<b>ENV=dev</b> prints OTPs on screen \u2014 never use dev mode with real borrowers; set <b>ENV=prod</b> and <b>OTP_MODE=sms</b>.",
        "Pass-through by design: Postgres holds audit metadata, consent records, and appraisal outcomes only \u2014 never borrower records or features.",
        "Serve traffic over TLS (reverse proxy) and keep Redis/Postgres off the public internet.",
    ]:
        s.append(Paragraph(b, BUL, bulletText="\u2022"))

    # ---------------- Part B ----------------
    s.append(Paragraph("Part B \u2014 Borrower walkthrough", PART))
    s.append(Paragraph(
        "For the operator to narrate \u2014 or print for the borrower. Five steps, about two minutes.", BODY))

    s.append(Paragraph("Step 1 \u2014 Language", SECT))
    s.append(Paragraph(
        "Choose Hindi, Bengali, Tamil, Telugu, Marathi, or English on the first screen. Buttons, "
        "instructions, and the spoken voice switch immediately. Keep the volume up \u2014 every step is read aloud.", BODY))

    s.append(Paragraph("Step 2 \u2014 Mobile OTP (identity check)", SECT))
    s.append(Paragraph(
        "Enter the mobile number linked to Aadhaar and tap Send. A 6-digit code arrives by SMS "
        "(on the demo screen it is also shown). Enter it to prove the session belongs to you.", BODY))
    for b in [
        "The 12-digit Aadhaar number is <b>never</b> asked for, spoken, or stored.",
        "No SMS? Check the Aadhaar-linked SIM is in the phone with signal, wait 60 seconds, then Resend (resending resets the 5-guess counter).",
        "Wrong number linked, or never linked? Check mAadhaar / UIDAI Verify-Mobile; linking or changes need an in-person visit to an Aadhaar Seva Kendra.",
    ]:
        s.append(Paragraph(b, BUL, bulletText="\u2022"))

    s.append(Paragraph("Step 3 \u2014 Consent (your permission slip)", SECT))
    s.append(Paragraph(
        "Tick exactly the records you agree to share: land registry, electricity-bill payments, "
        "bank-account summary (Account Aggregator), lending history (RBI ULI). Nothing is read before "
        "you agree. Consent is time-bound and revocable \u2014 revoking stops the flow and aborts any "
        "in-flight pull. You may share fewer sources; the score still works but with lower confidence.", BODY))

    s.append(Paragraph("Step 4 \u2014 Automatic check (about 30 seconds)", SECT))
    s.append(Paragraph(
        "The system pulls the consented records in parallel, turns them into a Borrower Readiness Index "
        "(BRI, 0\u2013100), and prepares a signed package for the partner lender. You wait on a progress "
        "screen \u2014 nothing to fill in.", BODY))

    s.append(Paragraph("Step 5 \u2014 Result and next steps", SECT))
    s.append(Paragraph(
        "A gauge shows the score with the band legends beneath it (Strong / Good / Fair / Building). "
        "Below: what the band means, the one action that would lift the score most (\"biggest lever\"), "
        "points earned per source, the partner-lender handoff status, and \u2014 from BRI 40 up \u2014 an "
        "indicative loan range (the lender sets the final amount). Use <b>Print / Save as PDF</b> to keep the report.", BODY))
    s.append(Paragraph(
        "If the package could not reach the lender, start a new session and try again. The report's handoff "
        "line always says what happened (\"simulated\" on a demo machine means no lender endpoint is configured).", NOTE))

    s.append(Paragraph("Your data and privacy, in one paragraph", SECT))
    s.append(Paragraph(
        "Records are processed in memory for this request only and never stored \u2014 not even as derived "
        "features. Only the audit trail (what happened, when, how many records, consent reference), the "
        "consent itself, and the outcome (score, per-source ok/failed, handoff state) are kept, so the "
        "process can be audited. The lender receives appraisal ID, score, model version, and loan range \u2014 "
        "never raw records. SetuCredit never lends and never decides; the partner NBFC approves and pays out "
        "over UPI/IMPS.", BODY))

    s.append(Spacer(1, 6 * mm))
    s.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=4, spaceBefore=4))
    s.append(Paragraph(
        "Sources: README.md, docs/ARCHITECTURE.md, SetuCredit User Guide &amp; Handbook, in-app help text. "
        "Bundle: setucredit-deploy/ (compose + prebuilt images + this guide). Endpoints: PWA :8080, API :8000, scoring :8001.",
        NOTE))

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
