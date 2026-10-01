# AGENTS.md

## Repo status

Hackathon repo, **implemented**: FastAPI backend, BRI scoring microservice, React PWA,
Docker Compose infra — all HLD-aligned. No CI yet.

- Remote: `origin` → https://github.com/nchary05-oss/SetuCredit.git (branch `main`)
- `.DS_Store` is committed (tracked). Don't "clean up" unrelated files unless asked.

## Source of truth: docs/

- `docs/SetuCredit_HLD_Document.pdf` — the product/architecture spec (2 pages). Read this first.
- `docs/ARCHITECTURE.md` — engineering expansion (components, API, data model). Derived from
  the HLD; if they conflict, the HLD wins. Keep it in sync with code.
- `docs/SetuCredit_Pitch_Deck.pdf` / `.pptx` — product/economics context only.

PDFs can't be read directly by all models. Extract text with (`uv` is installed and this is verified to work):

```bash
uv run --with pypdf python3 -c "
from pypdf import PdfReader
for p in PdfReader('docs/SetuCredit_HLD_Document.pdf').pages: print(p.extract_text())"
```

## Commands (repo root unless noted)

Python is a **uv workspace** (root `pyproject.toml`; members `backend/`, `scoring/`).

```bash
uv sync --all-packages                      # install — plain `uv sync` misses workspace members!
uv run ruff check backend scoring           # lint (run before committing)
uv run ruff format backend scoring          # format
uv run pytest -q                            # all tests
uv run pytest backend/tests/test_flow.py::test_full_flow -q   # single test

# tests need live infra (integration tests self-skip with this hint if it's down):
docker compose -f infra/docker-compose.yml up -d postgres redis

# run services locally:
uv run uvicorn app.main:app --port 8000          # backend
uv run uvicorn service.main:app --port 8001      # scoring

# migrations — run from backend/ (alembic.ini uses a relative script path):
uv run alembic upgrade head                       # cwd: backend/
uv run alembic revision --autogenerate -m "..."   # cwd: backend/, needs live Postgres

# frontend:
cd frontend && npm install && npm run dev         # Vite dev server proxies /v1 → :8000

# full container stack:
docker compose -f infra/docker-compose.yml --profile app up --build
#   frontend :8080 (nginx proxies /v1), backend :8000, scoring :8001, postgres, redis
```

## Architecture (HLD v1.0)

Middleware orchestration layer connecting unbanked Indian micro-borrowers to lenders via DPI:

- **Flow**: voice onboarding → Aadhaar OTP (DigiLocker) → AA consent → parallel data pull →
  scoring → partner NBFC webhook → UPI/IMPS disbursal
- **Backend** (`backend/app/`): FastAPI; `orchestrator/` fans out to `dpi/` adapters in
  parallel (currently **deterministic stubs** for land/discom/aa/uli — real integrations
  replace them behind `DPIAdapter`)
- **Scoring** (`scoring/`): separate process; `POST /score` → BRI 0–100. Heuristic v1 in
  `model/bri.py`; XGBoost drops in behind `score(features, coverage)`
- **Frontend** (`frontend/`): React PWA; `src/voice/tts.js` is browser TTS acting as the
  Bhashini swap point (no keys yet)
- **Storage**: Postgres = audit ledger only; Redis = OTP/session state (TTL-bound)

Folder ownership: `backend/app/{api,orchestrator,dpi,consent,audit}/`, `backend/migrations/`,
`frontend/src/{pages,components,voice}/`, `scoring/{features,model,service}/`, `infra/`.

## Non-negotiable design constraints (bake into any code)

- **Pass-through by design**: borrower non-financial data must NOT be persisted — not even
  as derived features. Postgres gets audit/event metadata, consent records, and appraisal
  outcomes only.
- **Consent before data**: every DPI pull requires explicit, time-bound, revocable consent
  (DPDP). Enforced in code (`app/consent/service.py` gate → HTTP 403), not by convention.
- TLS 1.3 in transit; AES-256 for stored audit logs.

## Gotchas

- Tests share **one session-scoped event loop** (`asyncio_*_loop_scope` in root
  `pyproject.toml`) — pooled Redis/SQLAlchemy connections depend on it; don't remove.
- Integration tests drop/recreate tables per test; they expect the compose DB (never point
  them at a real one).
- OTP: API returns `dev_otp` only when `ENV=dev`. Inbound/outbound NBFC webhooks are
  HMAC-signed with `WEBHOOK_SECRET` (default `dev-webhook-secret` in dev/compose).
- Session state machine lives in Redis (`app/session.py`); illegal transitions → 409.
- Test package dirs must stay **without** `__init__.py` (both are named `tests`).
