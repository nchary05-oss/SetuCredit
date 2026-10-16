# SetuCredit — Build Budget & Timeline

**Scope:** productionisation and live pilot (not the hackathon prototype, which is already built).
**Horizon:** today → completed pilot with one partner NBFC.
**Currency:** INR. Rates are India-market loaded costs (salary + ~30% overhead), 2026. All figures ±20%.

---

## Submission summary

| Metric | Value |
|---|---|
| **Estimated budget** | **₹75L – ₹1.2Cr** (lean → comfortable), ≈ $90k–140k |
| **Estimated duration** | **165 days (~5.5 months)** from today to pilot completion |
| Already built (no cost) | Working end-to-end prototype: FastAPI orchestration, React PWA, BRI scoring service, Postgres audit ledger, Redis sessions, Docker stack |

---

## 1. Phase plan — budget and duration

### Phase 1 — Foundation & sandbox readiness (30 days)

| Item | Cost |
|---|---|
| Team burn (30 days × ₹10–13L/month) | ₹10–13L |
| Legal: DPDP compliance, AA TSP/FIU agreements, company registrations | ₹5–10L |
| Cloud & tooling baseline | ₹0.5–1L |
| **Phase total** | **₹15–24L** |

### Phase 2 — Sandbox validation & NBFC integration (45 days)

| Item | Cost |
|---|---|
| Team burn (45 days) | ₹15–20L |
| Security: VAPT + CERT-In empanelled audit | ₹6–12L |
| Infra & DPI APIs | ₹1.5–3L |
| **Phase total** | **₹23–35L** |

### Phase 3 — Live pilot, 10–15k appraisals (90 days)

| Item | Cost |
|---|---|
| Team burn (90 days) | ₹30–39L |
| Infra & DPI APIs at pilot volume (see §3) | ₹4.5–9L |
| ISO 27001 (optional, gates larger lenders) | ₹8–15L |
| **Phase total** | **₹35–48L** (₹43–63L with ISO 27001) |

### Grand total — 165 days

| Variant | Cost |
|---|---|
| Lean (no ISO yet, tight scope) | **₹75–85L** |
| Comfortable (ISO 27001 included) | **₹90L–1.2Cr** |

---

## 2. Team (dominant cost, ~70% of budget)

| Role | Loaded monthly cost | FTE |
|---|---|---|
| Senior backend/platform (FastAPI, DPI integrations) | ₹2.5–3.5L | 2 |
| ML/data engineer (BRI model, feature pipeline) | ₹2.5–3L | 1 |
| Frontend (PWA, voice UX) | ₹1.8–2.5L | 1 |
| Product/design (vernacular voice UX) | ₹1.5L | 0.5 |
| Compliance/ops (DPDP, AA paperwork) | ₹1.5L | 0.5 |
| Fractional CTO/security advisor | ₹1L | — |
| **Total burn** | **₹10–13L/month** | ~5–6 people |

---

## 3. Infra & DPI APIs — pilot volume (6 months, 10–15k appraisals)

| Item | Cost |
|---|---|
| Cloud (small footprint; AWS Activate / cloud credits reduce this) | ₹3–6L |
| AA data pulls (~₹8–20/consent, commercially negotiated) | ₹1.2–3L |
| Aadhaar OTP/KYC (~₹5–10 × 10k) | ₹0.5–1L |
| Bhashini STT/TTS (govt rates; near-free at pilot scale) | ₹0.5–1L |
| SMS/OTP, monitoring, tooling | ₹1–1.5L |
| **Subtotal** | **₹6–13L** |

Per-appraisal variable cost: **~₹15–35** — consistent with the deck's <₹50 CAC.
Per *approved* loan: that figure ÷ approval rate.

---

## 4. Workstream durations (parallel tracks)

| Workstream | Duration (days) |
|---|---|
| Platform hardening (auth, observability, idempotency, rate limits) | 25 |
| DPI adapters — real land registry, DISCOM, BBPS integrations | 45 |
| AA TSP selection, agreements, and integration (legal lead time 30–60 days) | 40 |
| Bhashini voice swap (replaces browser TTS) | 12 |
| BRI model v2 — XGBoost + explainability | 45 |
| Security & compliance — VAPT, CERT-In audit, DPDP | 40 |
| NBFC partner integration — webhooks, disbursal, reconciliation | 30 |
| Pilot operations & iteration | 90 (overlaps) |

**Critical path: ~150–180 days.** Phase sum of 165 days assumes normal overlap.

---

## 5. Cost-recovery levers

- **Revenue floor:** 0.75–1.5% origination fee on ₹25–40k average ticket = ₹190–600 per originated loan — contribution-positive even at a 25% approval rate.
- **Cash savers:** AWS Activate / Google for Startups credits ($1k–100k), Bhashini public-good access, RBI sandbox is free, hackathon placement → grants/incubation can cover Phase 1 entirely.
- **Lean variant:** 3 people instead of 5–6 → ~₹50L for 165 days, at the cost of a longer tail on model v2 and integrations.

---

## 6. Assumptions

- India salary benchmarks for senior fintech engineers, 2026, loaded with ~30% overhead.
- API pricing (AA pulls, ULI access, KYC) is commercially negotiated, not published — ranges reflect market quotes from TSPs.
- Timeline assumes one cooperative NBFC partner with a live webhook sandbox.
- Excludes: borrower acquisition/field ops, interest subsidy, and any credit losses (partner NBFC risk).
