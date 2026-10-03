# SetuCredit

Voice-first middleware connecting unbanked Indian micro-borrowers to lenders over
public digital infrastructure — with borrower consent, in the borrower's language,
in about two minutes.

**Flow:** language selection → Aadhaar-linked mobile OTP → DPDP consent →
parallel DPI pull (land, electricity, bank, ULI lending history) → Borrower
Readiness Index (0–100) → signed handoff to a partner NBFC → disbursal over
UPI/IMPS on the lender's rails. Borrower records are processed in memory and
never persisted — not even as derived features.

## Repository layout

| Path | What it is |
|---|---|
| `backend/app/` | FastAPI gateway: `api/`, `orchestrator/` (parallel fan-out), `dpi/` (source adapters), `consent/` (403 gate), `audit/` (ledger), `otp/` (SMS provider flag), `session.py` (Redis state machine) |
| `backend/migrations/` | Alembic migrations (run from `backend/`) |
| `scoring/` | Separate BRI scoring microservice (`POST /score` → 0–100 + loan range) |
| `frontend/src/` | React 19 + Vite PWA: 5-step wizard, 6-language UI + voice (`i18n.js`, `voice/tts.js`) |
| `infra/` | Docker Compose stack + Dockerfiles |
| `docs/` | HLD (source of truth), `ARCHITECTURE.md`, pitch decks, integration/user guides, handbook |

## Quickstart

```bash
# full container stack (PWA :8080, backend :8000, scoring :8001)
docker compose -f infra/docker-compose.yml --profile app up --build

# infra only, then run services locally
docker compose -f infra/docker-compose.yml up -d postgres redis
uv sync --all-packages
uv run uvicorn app.main:app --port 8000          # backend (repo root resolves workspace)
uv run uvicorn service.main:app --port 8001      # scoring
cd frontend && npm install && npm run dev        # Vite proxies /v1 → :8000
```

Migrations run from `backend/`:

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "..."   # needs live Postgres
```

## Borrower journey

1. **Language** — Hindi, Bengali, Tamil, Telugu, Marathi, English; UI + voice follow instantly.
2. **OTP** — 6-digit code to the Aadhaar-linked mobile. An on-screen note explains
   verification (12-digit number never asked/stored; DigiLocker accepted where
   offered) plus a "Not getting the OTP?" helper (mAadhaar/UIDAI check, Seva Kendra
   for linking). `dev_otp` is returned only when `ENV=dev`.
3. **Consent** — tick exactly the sources shared; time-bound, revocable, audit-logged.
4. **Appraise** — parallel pull → BRI + suggested loan range.
5. **Result** — band (Strong 80+ / Good 60+ / Fair 40+ / Building <40), breakdown,
   handoff status; printable report.

## API (backend :8000)

| Method & path | Purpose |
|---|---|
| `POST /v1/sessions` | Create session (`{language}`) |
| `GET /v1/sessions/{id}` | Inspect state / next action |
| `POST /v1/sessions/{id}/otp` | `{action: send}` / `{action: verify, otp}` |
| `POST /v1/sessions/{id}/consents` | Grant scoped consent |
| `POST /v1/sessions/{id}/appraise` | Pull → score → lender handoff |
| `GET /v1/appraisals/{id}` | Appraisal + `disbursed_at` |
| `POST /v1/webhooks/disbursal` | Lender callback (HMAC, `appraisal_id`) → `disbursed` |

Outbound handoff and inbound disbursal webhooks are HMAC-signed (`WEBHOOK_SECRET`;
default `dev-webhook-secret` in dev/compose). No `PARTNER_WEBHOOK_URL` →
handoff returns `"simulated"`.

## Configuration

| Var | Default | Notes |
|---|---|---|
| `ENV` | `dev` | `dev` exposes `dev_otp` |
| `DATABASE_URL` / `REDIS_URL` | localhost | Compose overrides for containers |
| `SCORING_SERVICE_URL` | `http://localhost:8001` | |
| `PARTNER_WEBHOOK_URL` | — | Unset = simulated handoff |
| `WEBHOOK_SECRET` | `dev-webhook-secret` | Rotate in prod |
| `ULI_MODE` | `stub` | `live` + `ULI_*` creds → `UliApiAdapter` (OAuth2/HMAC/mTLS) |
| `OTP_MODE` | `stub` | `sms` + `SMS_*` creds → `SmsOtpProvider` (DLT sender/template) |
| `OTP_MAX_ATTEMPTS` | `5` | Wrong-guess cap per code; resend resets |

## Design constraints (non-negotiable)

- **Pass-through:** Postgres gets audit/event metadata, consent records, appraisal
  outcomes only. No borrower payloads, features, or audio — ever.
- **Consent before data:** `app/consent/service.py` gate → HTTP 403, enforced in code.
- **No Aadhaar numbers:** mobile-OTP possession proof + DigiLocker masked eKYC only.
  Raw 12-digit numbers must never be collected or stored (see `docs/SetuCredit_Handbook.pdf`, Part E).
- **OTP hygiene:** codes stored as `sha256` hashes in Redis (TTL-bound), 5-attempt cap.
- TLS 1.3 in transit; AES-256 for stored audit logs.

## Testing & lint

```bash
uv run pytest -q                                   # full suite (needs compose infra up)
uv run pytest backend/tests/test_flow.py::test_full_flow -q
uv run ruff check backend scoring                  # run before committing
uv run ruff format backend scoring
```

Integration tests self-skip with a hint if Postgres/Redis are down. Tests share one
session-scoped event loop (root `pyproject.toml`) — pooled connections depend on it.
Test package dirs stay **without** `__init__.py`.

## Docs

- `docs/SetuCredit_HLD_Document.pdf` — product/architecture spec (**source of truth**).
- `docs/ARCHITECTURE.md` — engineering expansion (HLD wins on conflict).
- `docs/SetuCredit_Pitch_Hackathon.pdf` — hackathon pitch (fact-checked, live screenshots).
- `docs/SetuCredit_ULI_Integration_Guide.pdf` — RBIH onboarding + `UliApiAdapter` steps.
- `docs/SetuCredit_User_Guide.pdf` — borrower visual walkthrough.
- `docs/SetuCredit_Handbook.pdf` — all users + RBI/Aadhaar rules + glossary.

PDF text extraction (for models that can't read PDFs):

```bash
uv run --with pypdf python3 -c "
from pypdf import PdfReader
for p in PdfReader('docs/SetuCredit_HLD_Document.pdf').pages: print(p.extract_text())"
```

## Status

Hackathon repo, HLD-aligned and demo-complete: real borrower flow, stubs for
land/discom/AA/ULI behind `DPIAdapter`, SMS behind `OTP_MODE`, lender handoff
simulated until configured. Production path: RBIH ULI onboarding, DLT SMS
registration, DigiLocker eKYC, first NBFC pilot. No CI yet.
