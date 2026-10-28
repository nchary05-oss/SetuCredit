#!/usr/bin/env python3
"""SetuCredit BRI scoring specification, CIBIL comparison & DPI data sources generator (A4).

Produces a publication-grade, 4-page executive architectural whitepaper:
docs/SetuCredit_BRI_Scoring_and_CIBIL_Comparison.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

W, H = A4
OUT = "/Volumes/data/Projects/SetuCredit/docs/SetuCredit_BRI_Scoring_and_CIBIL_Comparison.pdf"

# Palette aligned with SetuCredit design language
NAVY = HexColor("#0F172A")
DEEP = HexColor("#0369A1")
SKY = HexColor("#0284C7")
LIGHT_SKY = HexColor("#38BDF8")
INK = HexColor("#1E293B")
MUTED = HexColor("#64748B")
LINE = HexColor("#CBD5E1")
WHITE = HexColor("#FFFFFF")
ZEBRA = HexColor("#F8FAFC")
EMERALD_BG = HexColor("#ECFDF5")
EMERALD_TXT = HexColor("#047857")
AMBER_BG = HexColor("#FFFBEB")
AMBER_TXT = HexColor("#B45309")
BLUE_BG = HexColor("#EFF6FF")
CODE_BG = HexColor("#0F172A")
CODE_FG = HexColor("#BAE6FD")

# Typography Styles
TITLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY)
SUBTITLE = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=8.8, leading=12.5, textColor=MUTED)
PART = ParagraphStyle(
    "part", fontName="Helvetica-Bold", fontSize=10.2, leading=13.2,
    textColor=WHITE, backColor=NAVY, borderPadding=(3.5, 6, 3.5),
    spaceBefore=6, spaceAfter=4
)
SECT = ParagraphStyle(
    "sect", fontName="Helvetica-Bold", fontSize=9, leading=11.8,
    textColor=DEEP, spaceBefore=4.5, spaceAfter=2.5
)
SUBSECT = ParagraphStyle(
    "subsect", fontName="Helvetica-Bold", fontSize=8, leading=10.2,
    textColor=NAVY, spaceBefore=3.5, spaceAfter=1.5
)
BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=7.6, leading=10.6,
    textColor=INK, spaceAfter=2.5
)
BUL = ParagraphStyle(
    "bul", parent=BODY, leftIndent=10, bulletIndent=3, spaceAfter=1.2
)
CALLOUT = ParagraphStyle(
    "callout", parent=BODY, fontSize=7.4, leading=10.2, textColor=INK,
    borderPadding=(5, 6, 5), backColor=BLUE_BG, spaceBefore=3, spaceAfter=4
)
CALLOUT_SUCCESS = ParagraphStyle(
    "calloutSuccess", parent=BODY, fontSize=7.4, leading=10.2, textColor=EMERALD_TXT,
    borderPadding=(5, 6, 5), backColor=EMERALD_BG, spaceBefore=3, spaceAfter=4
)
FORMULA = ParagraphStyle(
    "formula", fontName="Courier-Bold", fontSize=7, leading=9.4,
    textColor=CODE_FG, backColor=CODE_BG, borderPadding=(3, 5, 3),
    spaceBefore=1.5, spaceAfter=2.5
)

# Table cell styles
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=6.9, leading=9, textColor=INK)
CELL_BOLD = ParagraphStyle("cellB", parent=CELL, fontName="Helvetica-Bold", textColor=NAVY)
CELL_H = ParagraphStyle("cellH", parent=CELL, fontName="Helvetica-Bold", textColor=WHITE)
CELL_C = ParagraphStyle("cellC", parent=CELL, fontName="Courier", fontSize=6.5, leading=8.4)


def page_decorator(canv, doc):
    canv.saveState()
    # Top running banner
    canv.setFillColor(NAVY)
    canv.rect(0, H - 12 * mm, W, 12 * mm, stroke=0, fill=1)
    canv.setFillColor(LIGHT_SKY)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawString(16 * mm, H - 8 * mm, "SetuCredit")
    canv.setFillColor(HexColor("#94A3B8"))
    canv.setFont("Helvetica", 7.2)
    canv.drawString(38 * mm, H - 8 * mm, "|   Whitepaper: BRI Scoring Architecture, Data Sources & CIBIL Comparison")
    canv.drawRightString(W - 16 * mm, H - 8 * mm, "CONFIDENTIAL & PROPRIETARY  •  HLD v1.0")

    # Bottom running footer
    canv.setStrokeColor(LINE)
    canv.setLineWidth(0.5)
    canv.line(16 * mm, 12 * mm, W - 16 * mm, 12 * mm)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7)
    canv.drawString(16 * mm, 8 * mm, "SetuCredit Protocol  •  Middleware for Rural Credit Inclusion  •  DPI Orchestration")
    canv.drawRightString(W - 16 * mm, 8 * mm, f"Page {doc.page} of 4")
    canv.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    s = []

    # =========================================================================
    # PAGE 1: EXECUTIVE SUMMARY, THE EXCLUSION TRAP, AND BRI 5-PILLAR WEIGHTS
    # =========================================================================
    s.append(Spacer(1, 2 * mm))
    s.append(Paragraph("SetuCredit: Borrower Readiness Index (BRI)", TITLE))
    s.append(Paragraph(
        "Alternative Underwriting Architecture, Authoritative DPI Data Sources, Comparative Bureau (CIBIL) Analysis, and "
        "Financial Inclusion for India's 300 Million Unbanked Micro-Borrowers",
        SUBTITLE
    ))
    s.append(Spacer(1, 1 * mm))
    s.append(HRFlowable(width="100%", thickness=1.2, color=DEEP, spaceBefore=1, spaceAfter=4))

    # Executive Summary Card
    s.append(Paragraph(
        "<b>Executive Summary:</b> Traditional credit bureaus (CIBIL, Experian, CRIF, Equifax) rely exclusively on past debt "
        "repayment track records, penalizing informal rural workers, smallholder farmers, and micro-entrepreneurs with a "
        "default <b>'No History' (-1 / 0)</b> rating. SetuCredit's <b>Borrower Readiness Index (BRI, 0–100)</b> replaces "
        "manual, paper-intensive underwriting with an automated, explainable index computed in real time from India's "
        "Digital Public Infrastructure (DPI) — combining Account Aggregator (AA) cashflows, state land registries, "
        "utility payments (DISCOM), Bharat BillPay (BBPS), and the RBI Unified Lending Interface (ULI). Operating strictly as an "
        "in-memory pass-through layer, SetuCredit acts as the bridge that turns previously invisible borrowers into prime, bankable citizens.",
        CALLOUT
    ))

    # Part 1: The Inclusion Problem & CIBIL Limitations
    s.append(Paragraph("Part 1: The Credit Exclusion Paradox & Bureau Failure", PART))
    s.append(Paragraph(
        "In India, over 300 million adults operate outside the formal banking perimeter. While they lack credit cards and formal "
        "term loans, they possess continuous, verifiable economic activity: paying electricity bills every month, cultivating title-cleared "
        "agricultural land, executing micro-transfers via UPI, and maintaining cellular recharges. Traditional credit models fail to capture "
        "this reality due to structural architectural assumptions:",
        BODY
    ))

    for point in [
        "<b>The Catch-22 of Formal Credit:</b> To obtain a formal loan, a borrower must have a credit score; but to build a credit score, "
        "they must have already taken and repaid a formal loan. First-time micro-borrowers remain permanently locked out.",
        "<b>Lagged Batch Reporting:</b> Bureau scores update in 30-to-45 day batch reporting cycles from member institutions, making "
        "real-time instant micro-lending impossible.",
        "<b>Asymmetrical Information Cost:</b> Verifying an unbanked borrower through physical field visits, patwari land records, "
        "and manual inspection costs lenders ₹1,500–₹3,500 per file — uneconomical for ₹25,000 to ₹100,000 micro-ticket sizes.",
        "<b>High Vulnerability to Informal Lenders:</b> Denied formal credit, micro-borrowers resort to unregistered moneylenders "
        "charging 36% to 120% APR, triggering generational cycles of rural debt distress.",
    ]:
        s.append(Paragraph(point, BUL, bulletText="•"))

    # Part 2: How BRI is Calculated - Weights Table
    s.append(Paragraph("Part 2: How BRI (Borrower Readiness Index) is Calculated", PART))
    s.append(Paragraph(
        "The Borrower Readiness Index (BRI) is an explainable index bounded within <b>[0, 100]</b>, executed in a dedicated "
        "scoring microservice (<font face='Courier'>scoring/model/bri.py</font>). The model synthesizes 5 DPI data pillars, "
        "each assigned a deterministic point weight representing maximum attainable points:",
        BODY
    ))

    w_data = [
        [Paragraph("Pillar & Source ID", CELL_H), Paragraph("Weight", CELL_H), Paragraph("Max Points", CELL_H),
         Paragraph("Regulatory / Tech Rail", CELL_H), Paragraph("Core Extracted Behavioral Features", CELL_H)],
        [Paragraph("<b>Account Aggregator (aa)</b>", CELL_BOLD), Paragraph("25%", CELL), Paragraph("25 pts", CELL),
         Paragraph("Sahamati / RBI NBFC-AA", CELL),
         Paragraph("Average balance (norm ₹50k), inflow consistency, account vintage (up to 60 mos), existing EMI burden ratio", CELL)],
        [Paragraph("<b>Land Registry (land)</b>", CELL_BOLD), Paragraph("20%", CELL), Paragraph("20 pts", CELL),
         Paragraph("State Portals (Dharani, Bhulekh)", CELL),
         Paragraph("Agricultural parcel area (norm 5 acres), verified unencumbered title, years parcel held (norm 20 yrs)", CELL)],
        [Paragraph("<b>Utility / Power (discom)</b>", CELL_BOLD), Paragraph("20%", CELL), Paragraph("20 pts", CELL),
         Paragraph("State Electricity Boards", CELL),
         Paragraph("On-time payment ratio, consecutive billing history (norm 24 mos), monthly consumption tier (norm ₹3,000)", CELL)],
        [Paragraph("<b>Telecom & Bills (bbps)</b>", CELL_BOLD), Paragraph("20%", CELL), Paragraph("20 pts", CELL),
         Paragraph("NPCI Bharat BillPay", CELL),
         Paragraph("Prepaid recharge consistency, SIM active vintage (norm 24 mos), monthly recharge tier (norm ₹500)", CELL)],
        [Paragraph("<b>Credit & History (uli)</b>", CELL_BOLD), Paragraph("15%", CELL), Paragraph("15 pts", CELL),
         Paragraph("RBI Unified Lending Interface", CELL),
         Paragraph("Existing active loan burden (cap 4), regular repayment history (norm 24 mos), past 12-month delinquencies", CELL)],
    ]
    t_weights = Table(w_data, colWidths=[38 * mm, 13 * mm, 16 * mm, 38 * mm, 73 * mm])
    t_weights.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
    ]))
    s.append(t_weights)

    # Force Page Break -> Page 2
    s.append(PageBreak())

    # =========================================================================
    # PAGE 2: FORMULAS, BANDS TABLE, AND 10-POINT COMPARISON MATRIX
    # =========================================================================
    s.append(Spacer(1, 2 * mm))
    s.append(Paragraph("Sub-Component Normalization & Mathematical Formulations", SECT))
    s.append(Paragraph(
        "Each raw payload maps to an in-memory feature vector (<font face='Courier'>scoring/features/extract.py</font>). "
        "Subscores $C_s \\in [0, 1]$ are computed via monotonic clamping $\\text{clamp}(x) = \\max(0, \\min(1, x))$:",
        BODY
    ))

    # Formulas in a 2-column compact table
    f_data = [
        [
            Paragraph("<b>Land:</b> <font face='Courier'>clamp(0.50*(acres/5) + 0.30*clear + 0.20*(years/20))</font>", CELL),
            Paragraph("<b>DISCOM:</b> <font face='Courier'>clamp(0.60*on_time + 0.20*(mos/24) + 0.20*(bill/3000))</font>", CELL)
        ],
        [
            Paragraph("<b>AA (Bank):</b> <font face='Courier'>clamp(0.40*(bal/50k) + 0.40*inflow + 0.20*(mos/60) - 0.30*emi)</font>", CELL),
            Paragraph("<b>BBPS:</b> <font face='Courier'>clamp(0.50*consistency + 0.30*(mos/24) + 0.20*(recharge/500))</font>", CELL)
        ],
        [
            Paragraph("<b>ULI:</b> <font face='Courier'>clamp(0.50*(1 - loans/4) + 0.30*(repay/24) + 0.20*(1 - delinq/3))</font>", CELL),
            Paragraph("<b>Aggregated Score:</b> <font face='Courier'>BRI = round( sum( 100 * Weight_s * C_s ) )</font>", CELL_BOLD)
        ]
    ]
    t_form = Table(f_data, colWidths=[88 * mm, 90 * mm])
    t_form.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ZEBRA),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, LINE),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    s.append(t_form)
    s.append(Spacer(1, 1.5 * mm))

    s.append(Paragraph(
        "<b>Zero-Inflation Policy:</b> Every source is worth $100 \\times W_s$ fixed points. Absent or withheld sources contribute 0 points "
        "rather than renormalizing remaining weights, eliminating consent-withholding gaming. Lender policy requires minimum mandatory "
        "consent for <font face='Courier'>aa</font> and <font face='Courier'>uli</font> to run an appraisal.",
        BODY
    ))

    # Bands Table
    s.append(Paragraph("Readiness Tiers & Indicative Micro-Loan Sizing", SECT))
    b_data = [
        [Paragraph("Score Tier", CELL_H), Paragraph("Readiness Band", CELL_H), Paragraph("Indicative Loan Band", CELL_H),
         Paragraph("Underwriting Policy & Action", CELL_H)],
        [Paragraph("<b>80 – 100</b>", CELL_BOLD), Paragraph("<font color='#047857'><b>Strong</b></font>", CELL),
         Paragraph("₹1,00,000 – ₹5,00,000", CELL),
         Paragraph("Instant straight-through processing (STP) disbursal via partner NBFC over UPI/IMPS rails.", CELL)],
        [Paragraph("<b>60 – 79</b>", CELL_BOLD), Paragraph("<font color='#0284C7'><b>Good</b></font>", CELL),
         Paragraph("₹50,000 – ₹2,00,000", CELL),
         Paragraph("Standard algorithmic approval; recommended for seasonal agricultural working capital.", CELL)],
        [Paragraph("<b>40 – 59</b>", CELL_BOLD), Paragraph("<font color='#B45309'><b>Fair</b></font>", CELL),
         Paragraph("₹25,000 – ₹75,000", CELL),
         Paragraph("Micro-credit starter loan. Fast repayment lifts borrower to 'Good' within 6 months.", CELL)],
        [Paragraph("<b>< 40</b>", CELL_BOLD), Paragraph("<font color='#B91C1C'><b>Building</b></font>", CELL),
         Paragraph("<i>None (Below floor)</i>", CELL),
         Paragraph("Declined for immediate lending. UI generates automated advisory on lifting electricity regularity and balances.", CELL)],
    ]
    t_bands = Table(b_data, colWidths=[24 * mm, 26 * mm, 40 * mm, 88 * mm])
    t_bands.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, LINE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ZEBRA]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    s.append(t_bands)

    # Part 3: Comparative Analysis Matrix (10 Dimensions)
    s.append(Paragraph("Part 3: Deep Comparative Analysis — BRI vs. CIBIL Bureau", PART))
    comp_data = [
        [Paragraph("Dimension", CELL_H), Paragraph("Traditional Bureau (CIBIL)", CELL_H), Paragraph("SetuCredit BRI", CELL_H)],
        [Paragraph("<b>Primary Purpose</b>", CELL_BOLD),
         Paragraph("Assess default probability on formal credit lines based on past credit debt.", CELL),
         Paragraph("Evaluate operational viability & income readiness for thin-file / unbanked borrowers.", CELL)],
        [Paragraph("<b>Score Range</b>", CELL_BOLD),
         Paragraph("300 to 900 (Industry prime threshold typically >= 750).", CELL),
         Paragraph("0 to 100 (Explainable multi-source index with calibrated micro-loan bands).", CELL)],
        [Paragraph("<b>Handling of New-To-Credit (NTC)</b>", CELL_BOLD),
         Paragraph("Returns <b>-1 or 0 (NH: No History)</b>. Result: Automatic rejection or predatory rates.", CELL),
         Paragraph("Evaluates non-financial operational records. Produces a full score even with zero prior loans.", CELL)],
        [Paragraph("<b>Data Sources</b>", CELL_BOLD),
         Paragraph("Exclusively financial institutions: credit cards, term loans, mortgages, overdrafts.", CELL),
         Paragraph("DPI rails: Land registries (Dharani/Bhulekh), DISCOM utilities, BBPS telecom, AA bank flows.", CELL)],
        [Paragraph("<b>Data Ingestion Model</b>", CELL_BOLD),
         Paragraph("Batch reporting: Lenders upload files monthly (30–45 day latency).", CELL),
         Paragraph("Real-time parallel API fan-out: Synchronous DPI pull completed in under 5 seconds.", CELL)],
        [Paragraph("<b>Data Privacy & Storage</b>", CELL_BOLD),
         Paragraph("Perpetual data warehouse storing decades of loan, balance, and default history.", CELL),
         Paragraph("<b>Strict pass-through</b>: Non-financial data processed in RAM and immediately dropped. Never persisted.", CELL)],
        [Paragraph("<b>Consent & Regulation</b>", CELL_BOLD),
         Paragraph("CIC Act; blanket consent signed at loan application.", CELL),
         Paragraph("DPDP Act compliant: Explicit, granular, time-bound (900s TTL), instantly revocable.", CELL)],
        [Paragraph("<b>Explainability</b>", CELL_BOLD),
         Paragraph("Proprietary black-box algorithm; adverse action notices provide generic codes.", CELL),
         Paragraph("100% transparent point attribution: Borrower sees exact points earned per DPI pillar.", CELL)],
        [Paragraph("<b>Cost per Appraisal</b>", CELL_BOLD),
         Paragraph("Direct bureau pull fees plus massive field verification / document collection overhead.", CELL),
         Paragraph("Zero field paperwork. Automated DPI fetch costs a fraction of physical verification.", CELL)],
        [Paragraph("<b>Inclusivity Focus</b>", CELL_BOLD),
         Paragraph("Biased towards formal, salaried urban workers with documented income statements.", CELL),
         Paragraph("Designed natively for rural smallholders, SHGs, gig workers, and micro-entrepreneurs.", CELL)],
    ]
    t_comp = Table(comp_data, colWidths=[36 * mm, 71 * mm, 71 * mm])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, LINE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ZEBRA]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    s.append(t_comp)

    # Force Page Break -> Page 3
    s.append(PageBreak())

    # =========================================================================
    # PAGE 3: SOURCE DETAILS FOR ALL DATA EXTRACTIONS (EXHAUSTIVE TECHNICAL BREAKDOWN)
    # =========================================================================
    s.append(Spacer(1, 2 * mm))
    s.append(Paragraph("Part 4: Authoritative Data Extraction Sources & Technical Rails", PART))
    s.append(Paragraph(
        "SetuCredit extracts features exclusively from authoritative government, regulatory, and public digital rails. "
        "No unverified, self-reported, or third-party web-scraped data enters the pipeline. Below is the complete source-level mapping:",
        BODY
    ))

    # Comprehensive Source Mapping Table
    src_data = [
        [Paragraph("Pillar & Source ID", CELL_H), Paragraph("Governing Authority & Rail", CELL_H),
         Paragraph("Primary Query Keys", CELL_H), Paragraph("Exact In-Memory Extracted Schema", CELL_H),
         Paragraph("Underwriting Significance", CELL_H)],

        [Paragraph("<b>State Land Registries</b><br/><font face='Courier'>source_id: land</font>", CELL_BOLD),
         Paragraph("<b>State Revenue Depts</b><br/>• Dharani (Telangana)<br/>• Bhulekh (UP, Odisha, Bihar)<br/>• Bhoomi (Karnataka)<br/>• MahaBhulekh (MH)", CELL),
         Paragraph("• Cadastral Survey No.<br/>• District / Mandal / Tehsil<br/>• Village Code / Khatauni", CELL),
         Paragraph("<font face='Courier'>area_acres (float)<br/>ownership (clear|disputed)<br/>years_held (int 1-30)<br/>registry (str)</font>", CELL_C),
         Paragraph("Validates immovable asset-backing and rural livelihood stability. Clear tenure eliminates mortgage registration costs for micro-loans.", CELL)],

        [Paragraph("<b>Electricity Utilities</b><br/><font face='Courier'>source_id: discom</font>", CELL_BOLD),
         Paragraph("<b>Ministry of Power / DISCOMs</b><br/>• State Utilities (e.g. TSSPDCL, UPPCL, BESCOM, MSEDCL)<br/>• Urja Mitra / NPP API", CELL),
         Paragraph("• Consumer CA Number<br/>• Service Connection ID<br/>• Aadhaar-linked Mobile", CELL),
         Paragraph("<font face='Courier'>months_paid (int 6-24)<br/>on_time_ratio (float 0-1)<br/>avg_monthly_bill_inr (int)<br/>utility (str)</font>", CELL_C),
         Paragraph("24-month recurring utility payments serve as an ironclad proxy for payment discipline and household cashflow stability.", CELL)],

        [Paragraph("<b>Account Aggregator</b><br/><font face='Courier'>source_id: aa</font>", CELL_BOLD),
         Paragraph("<b>Reserve Bank of India</b><br/>• Sahamati Ecosystem<br/>• Licensed NBFC-AAs (Setu, Anumati, Finvu, OneMoney)<br/>• FIPs: Commercial/RRBs", CELL),
         Paragraph("• AA Handle (<font face='Courier'>mobile@aa</font>)<br/>• Time-bound DPDP Consent Token<br/>• Linked Bank FIP Account", CELL),
         Paragraph("<font face='Courier'>avg_balance_inr (int)<br/>inflow_consistency (float)<br/>months_active (int 6-60)<br/>existing_emi_ratio (float)</font>", CELL_C),
         Paragraph("Evaluates true transaction velocity, seasonal crop/cash deposits, and existing debt outflows without requiring ITRs or salary slips.", CELL)],

        [Paragraph("<b>Bharat BillPay</b><br/><font face='Courier'>source_id: bbps</font>", CELL_BOLD),
         Paragraph("<b>NPCI Bharat BillPay</b><br/>• Central BBPS Switch<br/>• Telecom Operators (Jio, Airtel, Vi, BSNL)<br/>• Gas / DTH / Utility Billers", CELL),
         Paragraph("• Subscriber Mobile MSISDN<br/>• Biller Consumer Number<br/>• Biller Operating Unit (BOU)", CELL),
         Paragraph("<font face='Courier'>months_recharged (int 3-24)<br/>recharge_consistency (float)<br/>avg_monthly_recharge_inr<br/>biller (str)</font>", CELL_C),
         Paragraph("The essential 'thin-file footprint'. Continuous prepaid recharges on a single SIM demonstrate location stability and disposable income.", CELL)],

        [Paragraph("<b>Unified Lending Interface</b><br/><font face='Courier'>source_id: uli</font>", CELL_BOLD),
         Paragraph("<b>Reserve Bank Innovation Hub</b><br/>• RBI ULI National Gateway<br/>• Non-prod: <font face='Courier'>extgw.nonprod.rbihub.io</font><br/>• Production ULI Rail", CELL),
         Paragraph("• Borrower Session Ref<br/>• DPDP Consent Certificate<br/>• Mutual TLS + HMAC-SHA256", CELL),
         Paragraph("<font face='Courier'>existing_loans (int 0-4)<br/>repayment_regular_months<br/>delinquencies_12m (int)<br/>record_count (int)</font>", CELL_C),
         Paragraph("Captures historical priority-sector credit, Kisan Credit Card (KCC) history, and SHG bank linkage loans missed by traditional bureaus.", CELL)],

        [Paragraph("<b>Identity & Verification</b><br/><font face='Courier'>gate: identity</font>", CELL_BOLD),
         Paragraph("<b>UIDAI & MeitY</b><br/>• Licensed ASA/AUA Gateway<br/>• DigiLocker eKYC API", CELL),
         Paragraph("• Aadhaar registered mobile<br/>• 6-digit one-time passcode", CELL),
         Paragraph("<font face='Courier'>txn_id (str)<br/>mobile_verified (bool)<br/>masked_uid (str, demo)</font>", CELL_C),
         Paragraph("Proves session ownership without collecting or storing the raw 12-digit Aadhaar number (UIDAI regulatory compliance).", CELL)],
    ]
    t_src = Table(src_data, colWidths=[30 * mm, 38 * mm, 30 * mm, 38 * mm, 42 * mm])
    t_src.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, LINE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ZEBRA]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    s.append(t_src)

    # Force Page Break -> Page 4
    s.append(PageBreak())

    # =========================================================================
    # PAGE 4: BRIDGING THE GAP, EXPANSION RAILS, SECURITY, AND SIGN-OFF
    # =========================================================================
    s.append(Spacer(1, 2 * mm))
    s.append(Paragraph("Part 5: Bridging the Credit Gap Using Operational Surrogates", PART))
    s.append(Paragraph(
        "A common misconception is that unbanked borrowers lack data. They do not lack data — they lack <b>structured aggregation</b>. "
        "India's DPI stack provides authoritative, tamper-proof operational records that act as direct mathematical surrogates for creditworthiness:",
        BODY
    ))

    surrogates = [
        ("Electricity Bills as Debt-Service Surrogate",
         "A consumer who pays their DISCOM electricity bill on time every month for 24 months has established an ironclad habit of debt servicing. "
         "Power bills are recurring obligations with severe consequences for non-payment (disconnection), making payment discipline directly predictive of loan repayment."),
        ("Prepaid Mobile Recharges as Disposable Income Proxy",
         "India's rural informal economy runs on prepaid cellular connectivity. Consistent monthly recharges on a single mobile number "
         "over 12–24 months prove personal stability, location continuity, and steady disposable micro-cashflow."),
        ("Account Aggregator as Alternative Income Statement",
         "Micro-borrowers rarely possess formal payslips or audited balance sheets. Account Aggregator (AA) rails analyze digital transaction "
         "velocity, daily UPI inflows, Jan Dhan deposits, and seasonal crop sale receipts to calculate actual debt-servicing capacity."),
        ("State Land Registries as Collateral Anchor",
         "Land ownership records verified via state portals (e.g., Dharani, Bhulekh) provide definitive proof of rural asset ownership. "
         "Verifying parcel size, unencumbered status, and historical tenure gives lenders confidence without requiring mortgage deeds."),
    ]
    for title, desc in surrogates:
        s.append(Paragraph(f"• <b>{title}:</b> {desc}", BUL))

    s.append(Spacer(1, 1.5 * mm))
    s.append(Paragraph(
        "<b>The Day-0 to Prime Credit Ladder:</b><br/>"
        "BRI does not attempt to displace credit bureaus permanently. Instead, it serves as the <b>Day-0 onboarding catalyst</b>. "
        "When an NTC borrower is approved for an initial ₹50,000 working capital loan via SetuCredit, the partner NBFC reports subsequent "
        "repayments to CIBIL and CRIF. Within 12 months, the borrower establishes a formal bureau score of 750+, graduating into mainstream banking.",
        CALLOUT_SUCCESS
    ))

    s.append(Paragraph("Expansion Rails: Filling the Gap with Additional Operational Feeds", SECT))
    s.append(Paragraph(
        "SetuCredit's modular adapter architecture (<font face='Courier'>backend/app/dpi/base.py</font>) enables rapid integration of "
        "emerging public digital registers without modifying scoring consumer interfaces:",
        BODY
    ))
    for ext in [
        "<b>Dairy & Agri-Cooperatives (NDDB/PACS):</b> Daily milk pour records and cooperative payment logs act as verified weekly cashflow proofs.",
        "<b>GSTN & Trade Invoicing:</b> Micro-merchant invoices and e-way bills underwrite rural kirana stores and trade supply chains.",
        "<b>PM-KISAN & Direct Benefit Transfers (DBT):</b> Verifiable government agricultural support payouts prove subsidy stability.",
        "<b>DigiLocker Vehicle Records:</b> Commercial tractor, auto-rickshaw, and light commercial vehicle RC proofs anchor mobility loans.",
    ]:
        s.append(Paragraph(f"• {ext}", BUL))

    s.append(Paragraph("Part 6: Architecture, Compliance & Pass-Through Trust Boundary", PART))
    s.append(Paragraph(
        "To protect rural borrowers from predatory profiling and comply strictly with India's Digital Personal Data Protection (DPDP) Act, "
        "SetuCredit enforces non-negotiable architectural constraints:",
        BODY
    ))

    for sec in [
        "<b>Strict Pass-Through by Design:</b> Non-financial borrower payloads (land acreage, electricity bills, bank statements) "
        "live strictly in ephemeral RAM for the duration of the scoring request. They are NEVER written to disk, PostgreSQL, or logs.",
        "<b>Audit Ledger Isolation:</b> PostgreSQL stores only tamper-proof metadata: event timestamps, record counts, consent references, "
        "and SHA-256 payload digests for regulatory verification.",
        "<b>Stateful Consent Gate:</b> Every DPI adapter call is guarded in code by <font face='Courier'>app.consent.service</font>. "
        "Calls without active, unexpired consent return immediate HTTP 403 Forbidden.",
        "<b>HMAC Signed Handoff:</b> Pre-underwritten appraisal packages are cryptographically signed with HMAC-SHA256 before webhook transmission "
        "to partner NBFCs, guaranteeing message integrity over public networks.",
    ]:
        s.append(Paragraph(f"• {sec}", BUL))

    s.append(Spacer(1, 3 * mm))
    s.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=1, spaceAfter=3))
    s.append(Paragraph(
        "SetuCredit Whitepaper Series  •  Ref: HLD-SC-2026-V1  •  Engineered with FastAPI, Redis, PostgreSQL, React, and Python ReportLab. "
        "Repository: https://github.com/nchary05-oss/SetuCredit",
        ParagraphStyle("footerNote", fontName="Helvetica", fontSize=6.8, leading=8.8, textColor=MUTED)
    ))

    doc.build(s, onFirstPage=page_decorator, onLaterPages=page_decorator)
    print(f"Generated PDF successfully at: {OUT}")


if __name__ == "__main__":
    build_pdf()
