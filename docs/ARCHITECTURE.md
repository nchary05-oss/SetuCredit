# SetuCredit — Architecture

Engineering expansion of **HLD v1.0** (`docs/SetuCredit_HLD_Document.pdf`). The HLD is the
product spec; if this document ever conflicts with it, the HLD wins until both are revised.

Status: **implemented for the hackathon** — runnable code under `backend/`, `scoring/`,
`frontend/`, `infra/` (see `AGENTS.md` for exact commands). This document and the code
should be kept in sync; where they diverge, the code is what runs.

---

## 1. System context

SetuCredit is a **middleware orchestration layer**: it does not hold borrower data and does
not make lending decisions. It assembles a consented, pre-underwritten package from India's
DPI rails, scores it (BRI 0–100), and hands it to a partner NBFC, which disburses via
UPI/IMPS.

```
Borrower (PWA, voice) ──► SetuCredit ──► Partner NBFC ──► UPI/IMPS disbursal
                            │
                            ├── Bhashini (STT/TTS)
                            ├── DigiLocker / Aadhaar OTP (identity)
                            ├── Sahamati Account Aggregator (consent)
                            ├── RBI ULI + state land/DISCOM registries (data)
                            └── Postgres (audit ledger) + Redis (OTP/session)
```

Two invariants govern every design decision (from HLD §5):

1. **Pass-through by design** — borrower non-financial data lives in memory only, for the
   duration of one appraisal request. Postgres stores the audit ledger and nothing else.
2. **Consent before data** — no DPI call may be issued without a valid, unexpired,
   unrevoked consent covering that data source (DPDP Act).

## 2. Logical components

| Layer | Component | Code location | Notes |
|---|---|---|---|
| Experience | React PWA | `frontend/src/{pages,components}` | Low-storage, 3G/4G friendly |
| Experience | Bhashini voice | `frontend/src/voice` | STT/TTS, 12+ languages |
| Orchestration | API gateway | `backend/app/api` | FastAPI routes, session handling |
| Orchestration | Orchestrator | `backend/app/orchestrator` | Async fan-out to DPI sources |
| Orchestration | Consent service | `backend/app/consent` | Gate for every `dpi/` pull |
| DPI rails | Source adapters | `backend/app/dpi` | One adapter per source |
| Intelligence | Scoring engine | `scoring/{features,model,service}` | Separate service, XGBoost → BRI |
| Persistence | Audit ledger | `backend/app/audit` + `backend/migrations` | Postgres, metadata only |
| Persistence | OTP/session cache | Redis (via `backend/app/api`) | TTL-bound, not in Postgres |
| Lending | NBFC webhook client | `backend/app/api` | Signed outbound webhook |

### DPI adapters (`backend/app/dpi/`)

One adapter per source, uniform interface (proposed):

```python
class DPIAdapter(Protocol):
    source_id: str
    async def fetch(self, consent: Consent, scope: Scope) -> SourceResult: ...
```

Adapters planned: `uli/` (RBI Unified Lending Interface), `aa/` (Sahamati Account
Aggregator), `land/` (Dharani, Bhulekh), `discom/` (state utility boards). Adapters are the
**only** place raw borrower data enters the process; data never leaves `orchestrator`
memory except as derived features sent to `scoring/`.

### Orchestrator (`backend/app/orchestrator/`)

- Fans out adapter calls concurrently (`asyncio.gather`), per-source timeout (proposed
  5 s), one retry on transient failure.
- **Partial results**: an appraisal may complete with a subset of sources only if the
  minimum required set (per scoring config) succeeded; the result carries per-source
  status so the scoring layer can apply a confidence penalty.
- Emits audit events (source, timestamp, record counts, consent id) — never record
  payloads.

## 3. End-to-end request flow (HLD §3, with session detail)

```
PWA            Bhashini      API/Orchestrator   Redis    DigiLocker   AA/DPI      Scoring     NBFC
 │  speak         │                │               │          │           │           │          │
 │───────────────►│  STT text      │               │          │           │           │          │
 │                │───────────────►│ create session│          │           │           │          │
 │                │                │──────────────►│          │           │           │          │
 │                │                │  OTP req/verify (stage 2)│           │           │          │
 │                │                │──────────────────────────►│          │           │          │
 │                │                │  consent grant (stage 3)  │          │           │          │
 │                │                │─────────────────────────────────────►          │           │
 │                │                │  parallel pull (stage 4)  │          │           │          │
 │                │                │─────────────────────────────────────►          │          │
 │                │                │  features (in-memory) ─────────────────────────►│          │
 │                │                │  ◄────────────── BRI + feature summary ─────────│          │
 │                │                │  webhook: pre-underwritten package ────────────────────────►│
 │  TTS result    │◄───────────────│               │          │           │           │          │
 │◄───────────────│                │               │          │           │           │          │
```

Stages (HLD numbering): 1 voice onboarding → 2 Aadhaar OTP identity → 3 AA consent →
4 parallel data retrieval → 5 scoring → 6 NBFC webhook + UPI/IMPS disbursal.

Session state machine (lives in Redis, TTL-bound):

```
CREATED → IDENTITY_VERIFIED → CONSENT_GRANTED → PULLING → SCORED → HANDED_OFF
```

No stage may run before its prerequisite; the consent gate is enforced in code
(`consent/` → `dpi/`), not by convention.

## 4. Proposed API surface (`backend/app/api/`)

Draft — refine when scaffolding:

| Method & path | Purpose |
|---|---|
| `POST /v1/sessions` | Create appraisal session (returns `session_id`) |
| `POST /v1/sessions/{id}/otp` | Send/verify Aadhaar OTP (DigiLocker) |
| `GET  /v1/sessions/{id}` | Session state + next action for the PWA |
| `POST /v1/sessions/{id}/consents` | Initiate AA consent grant; polls scope + expiry |
| `POST /v1/sessions/{id}/consents/revoke` | Revoke active consent (DPDP), resets session state |
| `POST /v1/sessions/{id}/appraise` | Fan-out pull → scoring; requires `CONSENT_GRANTED` |
| `GET  /v1/appraisals/{id}` | BRI, per-source status, package handoff status |
| `POST /v1/webhooks/disbursal` | Inbound NBFC callback (HMAC-signed) |
| `GET  /healthz` | Liveness |

Voice: STT/TTS happen in the PWA against Bhashini; the API receives text (or a transient
audio reference) — no audio is stored.

## 5. Persistence model

**Postgres — audit ledger only** (`backend/migrations/`), metadata and compliance records:

- `audit_events` — append-only: `session_id`, `event_type`, `entity_id`, `consent_id`,
  `source_id`, `record_count`, `model_version`, `payload_hash`, `created_at`
- `consents` — consent lifecycle: scope, granted/expiry/revocation timestamps, status
- `appraisals` — outcome record: `bri`, model version, per-source ok/failed status,
  handoff/disbursal state (the borrower's underlying records **and** derived feature
  values are **not** here)

**Redis** — OTP codes and session state with short TTLs; wiped on completion/expiry.

Rule of thumb: if a row would contain a borrower's land, utility, or transaction *record*,
it does not belong in Postgres.

## 6. Scoring service (`scoring/`)

- Separate process; receives **in-memory source payloads** over the internal API (they
  transit but are never persisted), returns `BRI ∈ [0, 100]` + model version + features +
  per-source attributions (explainability is an HLD design principle).
- `features/` — feature extraction & transformations; `model/` — BRI logic (heuristic v1
  behind a stable `score(features, coverage)` interface; the trained XGBoost model drops
  in here); `service/` — thin inference API (`POST /score`).
- Coverage is derived from which payloads are present, so sparse consents still score
  (remaining source weights renormalize) instead of failing outright.
- Scoring is stateless w.r.t. the borrower: no feature store of borrower data.

## 7. Security & compliance (HLD §5)

- TLS 1.3 in transit (including service-to-service in the compose network); AES-256 for
  stored audit logs/ledgers at rest.
- Consent is explicit, time-bound, revocable — revocation must abort any in-flight pull.
- Webhooks to/from the NBFC: HMAC-signed, timestamped, replay-protected.
- DPDP posture: purpose limitation (credit appraisal only), retention = audit ledger only,
  pass-through everywhere else.

## 8. Deployment topology (`infra/`)

Implemented for the hackathon: single-host `docker compose` with `backend`, `scoring`,
`frontend` (nginx static), `postgres`, `redis` — see `infra/docker-compose.yml`. Scale-out
path (post-hackathon): orchestrator and scoring are already separate processes.

Non-functional notes from the HLD: PWA must stay light for 3G/4G; every DPI fan-out is
latency-sensitive (parallel by design); voice UX must degrade gracefully to text in the
same language.
