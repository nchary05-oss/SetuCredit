# AGENTS.md

## Repo status (verify before assuming anything)

Design-stage hackathon repo — **no application code, no build/test/lint config, no CI yet.**
Tracked files: only `.gitattributes` and `.DS_Store`. `docs/` and `AGENTS.md` exist locally but are **untracked**.

- Remote: `origin` → https://github.com/nchary05-oss/SetuCredit.git (branch `main`)
- No `.gitignore` yet; `.DS_Store` is committed. Don't "clean up" unrelated files unless asked.

## Source of truth: docs/

- `docs/SetuCredit_HLD_Document.pdf` — the architecture spec (2 pages). Read this before scaffolding.
- `docs/SetuCredit_Pitch_Deck.pdf` / `.pptx` — product/economics context only.

PDFs can't be read directly by all models. Extract text with (`uv` is installed and this is verified to work):

```bash
uv run --with pypdf python3 -c "
from pypdf import PdfReader
for p in PdfReader('docs/SetuCredit_HLD_Document.pdf').pages: print(p.extract_text())"
```

## Planned architecture (from HLD v1.0 — future code should match)

Middleware orchestration layer connecting unbanked Indian micro-borrowers to lenders via DPI:

- **API Gateway/Orchestrator**: Python FastAPI, async parallel DPI calls, in-memory pass-through
- **Frontend**: React.js PWA, voice-first via Bhashini (STT/TTS, 12+ languages)
- **Data rails**: RBI ULI + Sahamati Account Aggregator + state land/DISCOM registries (Dharani, Bhulekh)
- **Scoring**: separate service, Scikit-Learn/XGBoost → Borrower Readiness Index (BRI, 0–100)
- **Storage**: PostgreSQL (audit ledger only) + Redis (OTP session cache)
- **Flow**: voice onboarding → Aadhaar OTP (DigiLocker) → AA consent → parallel data pull → scoring → partner NBFC webhook → UPI/IMPS disbursal

## Folder structure (created, empty — placeholder `.gitkeep` only)

Maps HLD components to directories; fill these in when scaffolding:

- `backend/app/orchestrator/` — FastAPI async fan-out to DPI sources; `backend/app/api/` — routes
- `backend/app/dpi/` — clients for RBI ULI, Sahamati AA, state land/DISCOM registries
- `backend/app/consent/` — DPDP consent capture (must run before any `dpi/` pull)
- `backend/app/audit/` + `backend/migrations/` — Postgres audit ledger (the only persisted data)
- `frontend/src/voice/` — Bhashini STT/TTS; `frontend/src/{pages,components}/` — React PWA
- `scoring/{features,model,service}/` — separate BRI scoring service (XGBoost)
- `infra/` — Postgres/Redis runtime config (OTP cache is Redis, not Postgres)

## Non-negotiable design constraints (bake into any code)

- **Pass-through by design**: borrower non-financial data must NOT be persisted on app servers — only the audit ledger goes to Postgres.
- **Consent before data**: every DPI pull requires explicit, time-bound, revocable consent captured first (DPDP Act).
- TLS 1.3 in transit; AES-256 for stored audit logs.

## Conventions

- Nothing is standardized yet (no formatter/linter/test runner). If you introduce one, add the exact
  commands (`lint`, `typecheck`, `test`, single-test invocation) to this file in the same change.
