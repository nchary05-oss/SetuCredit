# SetuCredit — Architecture Diagrams

Visual companion to `docs/ARCHITECTURE.md` (which follows the HLD v1.0). All diagrams are
Mermaid — they render on GitHub and in any Mermaid-capable editor. Diagrams reflect the
**implemented** code (paths shown per diagram).

Printable version: [ARCHITECTURE_DIAGRAMS.pdf](ARCHITECTURE_DIAGRAMS.pdf) (18 pages,
A4 landscape, generated from this file).

Contents:

1. [System context (C4 level 1)](#1-system-context-c4-level-1)
2. [Deployment topology](#2-deployment-topology)
3. [Backend component map](#3-backend-component-map)
4. [End-to-end appraisal sequence (6 stages)](#4-end-to-end-appraisal-sequence-6-stages)
5. [Session state machine](#5-session-state-machine)
6. [Data model and retention](#6-data-model-and-retention)
7. [Scoring pipeline](#7-scoring-pipeline)
8. [Pass-through trust boundary](#8-pass-through-trust-boundary)
9. [API surface](#9-api-surface)

---

## 1. System context (C4 level 1)

SetuCredit is a middleware orchestration layer: it holds no borrower data and makes no
lending decision. It assembles a consented, pre-underwritten package from DPI rails, scores
it (BRI 0-100), and hands it to a partner NBFC.

```mermaid
flowchart LR
    B["Borrower<br/>(rural micro-borrower,<br/>regional dialect)"]

    subgraph SC["SetuCredit — middleware orchestration layer"]
        direction TB
        PWA["React PWA<br/>frontend/<br/>voice-first, 3G/4G friendly"]
        CORE["API + Orchestrator<br/>backend/<br/>FastAPI, consent-gated fan-out"]
        SCR["Scoring service<br/>scoring/<br/>BRI 0-100 + loan band"]
        PG[("Postgres<br/>audit ledger only")]
        RD[("Redis<br/>session + OTP,<br/>TTL-bound")]
    end

    BH["Bhashini<br/>STT / TTS<br/>(12+ languages)"]
    DL["DigiLocker<br/>Aadhaar OTP identity"]
    AA["Sahamati<br/>Account Aggregator<br/>(consent manager)"]
    ULI["RBI ULI<br/>unified lending interface"]
    REG["State land registries<br/>+ DISCOM boards<br/>(Dharani, Bhulekh, …)"]
    NBFC["Partner NBFC<br/>underwriting + webhook"]
    PAY["UPI / IMPS<br/>disbursal"]

    B -->|"speak / tap"| PWA
    PWA <-->|"text + TTS"| BH
    PWA -->|"JSON /v1"| CORE
    CORE -->|"OTP verify"| DL
    CORE -->|"consent grant / revoke"| AA
    CORE -->|"parallel data pull"| ULI
    CORE -->|"parallel data pull"| REG
    CORE <--> RD
    CORE <--> PG
    CORE -->|"feature payloads (in-memory)"| SCR
    CORE -->|"signed webhook:<br/>bri + loan_range + ids"| NBFC
    NBFC -->|"funds credit"| PAY
    PAY -->|"loan amount"| B

    classDef infra fill:#0f172a,color:#e2e8f0,stroke:#38bdf8
    classDef ext fill:#1e293b,color:#e2e8f0,stroke:#64748b
    class PG,RD,PWA,CORE,SCR infra
    class BH,DL,AA,ULI,REG,NBFC,PAY ext
```

**Two invariants (HLD §5)** govern every arrow above: borrower non-financial data is never
persisted (§8), and no DPI pull happens without a valid, unexpired, unrevoked consent
(enforced in `backend/app/consent/service.py` → HTTP 403).

## 2. Deployment topology

Single-host Docker Compose (`infra/docker-compose.yml`), profile `app`:

```mermaid
flowchart TB
    subgraph Browser["Borrower device"]
        BR["Browser<br/>PWA"]
    end

    subgraph Host["Docker host (single machine)"]
        direction TB
        FE["<b>frontend</b> container<br/>nginx :80 → host <b>:8080</b><br/>static assets + /v1 reverse proxy"]

        subgraph Dev["Dev-only processes"]
            VITE["Vite dev server <b>:5173</b><br/>proxies /v1, /healthz → :8000"]
        end

        BE["<b>backend</b> container <b>:8000</b><br/>CMD: alembic upgrade head &&<br/>uvicorn app.main:app<br/>ENV=dev, WEBHOOK_SECRET, SCORING_SERVICE_URL"]
        SCS["<b>scoring</b> container <b>:8001</b><br/>CMD: uvicorn service.main:app<br/>stateless, no DB"]
        PG["<b>postgres:16-alpine</b> :5432<br/>volume pgdata"]
        RD["<b>redis:7-alpine</b> :6379"]
    end

    EXT["Partner NBFC<br/>webhook receiver<br/>(PARTNER_WEBHOOK_URL)"]

    BR -->|"http :8080"| FE
    FE -->|"/v1/, /healthz proxy"| BE
    VITE -.->|"dev mode"| BE
    BE -->|"asyncpg"| PG
    BE -->|"redis-py async"| RD
    BE -->|"httpx POST /score"| SCS
    BE -->|"httpx POST, HMAC X-Signature"| EXT

    classDef c fill:#0f172a,color:#e2e8f0,stroke:#38bdf8
    classDef d fill:#334155,color:#e2e8f0,stroke:#94a3b8,stroke-dasharray: 4 3
    class FE,BE,SCS,PG,RD c
    class VITE d
```

- Only `frontend :8080` and `backend :8000`/`scoring :8001` are reached from outside in a
  demo; Postgres/Redis/scoring are on the compose network.
- Scale-out path (post-hackathon): orchestrator and scoring are already separate processes;
  backend can be replicated behind a load balancer (sessions live in Redis, not in process).
- Non-functional (HLD): PWA stays light for 3G/4G; the fan-out is latency-sensitive hence
  parallel; voice degrades to text in the same language.

## 3. Backend component map

```mermaid
flowchart TB
    subgraph API["backend/app/api — HTTP layer"]
        RS["routes_sessions<br/>POST /v1/sessions<br/>GET /v1/sessions/{id}<br/>POST …/otp (send|verify)"]
        RC["routes_consent<br/>POST …/consents<br/>POST …/consents/revoke"]
        RA["routes_appraise<br/>POST …/appraise<br/>GET /v1/appraisals/{id}"]
        RW["routes_webhooks<br/>POST /v1/webhooks/disbursal"]
        RH["routes_health<br/>GET /healthz (PG+Redis)"]
    end

    subgraph CORE["backend/app — domain services"]
        SESS["session.py<br/>state machine + OTP<br/>require_state → 409"]
        CONS["consent/service.py<br/>grant / load_active / revoke<br/>expiry + revocation gate"]
        ORCH["orchestrator/run.py<br/>asyncio.gather fan-out,<br/>5s timeout per source"]
        AUDIT["audit/service.py<br/>emit(): metadata + sha256<br/>payload_hash — never records"]
        SEC["security.py<br/>HMAC-SHA256 sign / verify<br/>(WEBHOOK_SECRET)"]
        SC["scoring_client.py<br/>httpx POST /score"]
        CFG["config.py<br/>TTLs: session 3600s,<br/>OTP 300s, consent 900s,<br/>DPI timeout 5s"]
    end

    subgraph DPI["backend/app/dpi — adapters (stubs today)"]
        BASE["DPIAdapter protocol<br/>fetch(session_id) → SourceResult"]
        LAND["landAdapter — land"]
        DIS["DiscomAdapter — discom"]
        AA["AAAdapter — aa"]
        ULI["ULIAdapter — uli"]
    end

    subgraph Store["State"]
        RD[("Redis<br/>session:{id}, otp:{id}")]
        PG[("Postgres<br/>audit_events, consents, appraisals")]
    end

    RS --> SESS
    RC --> CONS
    RA --> CONS
    RA --> SESS
    RA --> ORCH
    RA --> SC
    RA --> SEC
    RW --> SEC
    RW --> AUDIT
    ORCH --> BASE
    BASE --> LAND & DIS & AA & ULI
    RS & RC & RA --> AUDIT
    SESS --> RD
    CONS --> PG
    AUDIT --> PG

    classDef api fill:#0f172a,color:#e2e8f0,stroke:#38bdf8
    classDef svc fill:#1e293b,color:#e2e8f0,stroke:#64748b
    classDef dpi fill:#14532d,color:#dcfce7,stroke:#22c55e
    class RS,RC,RA,RW,RH api
    class SESS,CONS,ORCH,AUDIT,SEC,SC,CFG,BASE svc
    class LAND,DIS,AA,ULI dpi
```

Key control points:

- **`require_state`** (session.py:67) — every route declares its legal source states;
  violations raise `StateError` → HTTP 409 (`main.py` handler).
- **Consent gate** (routes_appraise.py:31-34) — `load_active()` re-checks scope, expiry and
  revocation from Postgres right before the pull; failure → 403 and the session reverts to
  `CONSENT_GRANTED`.
- **Adapter isolation** (orchestrator/run.py:15-28) — a timeout or exception in one adapter
  becomes `SourceResult(ok=False)`; one bad rail never fails the appraisal.
- **Adapters are the only entry point for raw borrower records** — nothing downstream of
  `orchestrator` sees raw payloads except `scoring` (as features, in memory).

## 4. End-to-end appraisal sequence (6 stages)

HLD §3 stage numbering: 1 voice → 2 identity → 3 consent → 4 parallel pull → 5 scoring →
6 handoff/disbursal.

```mermaid
sequenceDiagram
    autonumber
    actor B as Borrower
    participant P as PWA (frontend/)
    participant V as Bhashini
    participant A as API + Orchestrator (backend/)
    participant R as Redis
    participant D as Postgres
    participant S as Scoring :8001
    participant X as DPI adapters
    participant N as Partner NBFC

    rect rgb(224, 242, 254)
    Note over B,V: Stage 1 — Voice onboarding
    B->>V: speaks in regional dialect
    V-->>P: STT text (language tag)
    P->>A: POST /v1/sessions {language}
    A->>R: SET session:{id} state=CREATED (TTL 3600s)
    A->>D: audit session.created
    A-->>P: session_id, next_action=otp
    end

    rect rgb(241, 245, 249)
    Note over B,A: Stage 2 — Aadhaar OTP identity (DigiLocker stand-in)
    P->>A: POST …/otp {action: send}
    A->>R: SET otp:{id} 6-digit (TTL 300s)
    A-->>P: dev_otp (only when ENV=dev)
    P->>A: POST …/otp {action: verify, otp}
    A->>R: compare + DEL otp
    A->>R: state=IDENTITY_VERIFIED
    A->>D: audit identity.verified
    end

    rect rgb(220, 252, 231)
    Note over B,D: Stage 3 — AA consent (DPDP: explicit, time-bound, revocable)
    P->>A: POST …/consents {scope: [land, discom, aa, uli]}
    A->>A: require_state(IDENTITY_VERIFIED) else 409
    A->>D: INSERT consents (expires_at = now + 900s)
    A->>R: state=CONSENT_GRANTED
    A->>D: audit consent.granted
    A-->>P: consent_id, scope, expires_at
    end

    rect rgb(254, 243, 199)
    Note over A,X: Stage 4 — Parallel data retrieval (consent-gated, 5s/source)
    P->>A: POST …/appraise
    A->>A: require_state(CONSENT_GRANTED) else 409
    A->>D: load_active(consent) → 403 if expired/revoked
    A->>R: state=PULLING
    par fan-out (asyncio.gather)
        A->>X: fetch land
    and
        A->>X: fetch discom
    and
        A->>X: fetch aa
    and
        A->>X: fetch uli
    end
    X-->>A: SourceResult payloads — held in memory only
    A->>D: audit dpi.pull / dpi.pull_failed (source, count, consent_id)
    end

    rect rgb(237, 233, 254)
    Note over A,S: Stage 5 — Scoring
    alt all sources failed
        A->>R: revert state=CONSENT_GRANTED
        A-->>P: 502 all DPI sources failed
    else at least one source ok
        A->>S: POST /score {payloads}
        S->>S: extract() → features + coverage
        S->>S: score() → BRI + attributions (weights renormalized)
        S->>S: suggest_loan(bri) → loan_range band
        S-->>A: bri, features, attributions, max_points, loan_range
        A->>D: INSERT appraisals (bri, model_version, sources ok/failed)
        A->>R: state=SCORED
        A->>D: audit score.computed
        Note over A,N: Stage 6 — NBFC handoff (pre-underwritten package)
        alt PARTNER_WEBHOOK_URL configured
            A->>N: POST webhook {appraisal_id, session_id, bri,<br/>model_version, loan_range} + X-Signature
        else unconfigured (demo)
            Note over A: handoff = "simulated"
        end
        A->>R: state=HANDED_OFF
        A->>D: audit handoff.sent | handoff.simulated | handoff.failed
        A-->>P: AppraiseResponse (report payload)
        P->>V: TTS "Your Borrower Readiness Index is N out of 100"
        N->>A: POST /v1/webhooks/disbursal (HMAC-verified)
        A->>D: appraisals.status=disbursed, audit disbursal.received
    end
    end
```

Notes:

- Scoring unavailable → `502`, session also reverts to `CONSENT_GRANTED` (routes_appraise.py:54-59).
- A failed *outbound* handoff leaves the session in `SCORED` (only `!= "failed"` advances to
  `HANDED_OFF`), so it can be retried; the response still returns `handoff="failed"`.
- No audio is ever stored: STT/TTS happen in the PWA; the API sees text only.

## 5. Session state machine

Lives in Redis (`backend/app/session.py`), TTL-bound, wiped on expiry. Illegal transitions
→ HTTP 409. Consent revocation is accepted from any post-consent state (DPDP).

```mermaid
stateDiagram-v2
    direction LR
    [*] --> CREATED: POST /v1/sessions
    CREATED --> IDENTITY_VERIFIED: OTP verify ok
    IDENTITY_VERIFIED --> CONSENT_GRANTED: consent granted
    CONSENT_GRANTED --> PULLING: POST appraise
    PULLING --> SCORED: >= 1 source ok + score returned
    SCORED --> HANDED_OFF: webhook sent / simulated

    PULLING --> CONSENT_GRANTED: all DPI sources failed or<br/>scoring unavailable (HTTP 502, revert)
    CONSENT_GRANTED --> IDENTITY_VERIFIED: consent revoked
    PULLING --> IDENTITY_VERIFIED: consent revoked
    SCORED --> IDENTITY_VERIFIED: consent revoked
    HANDED_OFF --> IDENTITY_VERIFIED: consent revoked
    HANDED_OFF --> [*]: disbursed webhook / TTL expiry

    note right of SCORED
        handoff = "failed" keeps
        state at SCORED (retryable)
    end note

    note right of CREATED
        require_state() violations
        from any state → HTTP 409
    end note
```

`next_action` hints returned to the PWA (`schemas.NEXT_ACTION`):
`CREATED→otp`, `IDENTITY_VERIFIED→consent`, `CONSENT_GRANTED→appraise`,
`PULLING→wait`, `SCORED→wait`, `HANDED_OFF→done`.

## 6. Data model and retention

### Postgres — audit ledger only (`backend/migrations/versions/508ab15e2977_…`)

```mermaid
erDiagram
    consents ||--o{ audit_events : "consent.granted / revoked (consent_id)"
    appraisals ||--o{ audit_events : "score.computed / handoff.* / disbursal.received (entity_id)"
    consents ||--o{ appraisals : "same session_id (logical, no FK)"

    consents {
        string id PK
        string session_id "indexed"
        json scope "land|discom|aa|uli"
        string status "granted | revoked | expired"
        datetime granted_at
        datetime expires_at "TTL 900s"
        datetime revoked_at "nullable"
    }
    appraisals {
        string id PK
        string session_id "indexed"
        string status "scored | handed_off | disbursed"
        int bri "0-100"
        string model_version "bri-heuristic-0.1.0"
        json sources "per-source ok|failed — NOT records"
        datetime created_at
        datetime disbursed_at "nullable"
    }
    audit_events {
        string id PK
        string session_id "indexed"
        string event_type "session.created, identity.verified,<br/>consent.granted|revoked, dpi.pull|dpi.pull_failed,<br/>score.computed, handoff.*, disbursal.received"
        string entity_id "nullable — appraisal id"
        string consent_id "nullable"
        string source_id "nullable — land|discom|aa|uli"
        int record_count "nullable — count only"
        string model_version "nullable"
        string payload_hash "sha256 of webhook body"
        datetime created_at
    }
```

### Redis — ephemeral session state (`backend/app/session.py`)

| Key | Value | TTL |
|---|---|---|
| `session:{session_id}` | JSON: state, language, consent_id, appraisal_id | 3600 s |
| `otp:{session_id}` | 6-digit code (single use) | 300 s |

**Never stored anywhere** (pass-through by design): land records, utility bills, bank
transactions, AA/ULI payloads, derived feature values, audio. `loan_range` is computed
in-request and returned to the PWA / sent to the NBFC, but is not written to the ledger.

## 7. Scoring pipeline

Separate, stateless process (`scoring/`): in-memory payloads over HTTP in, BRI out.

```mermaid
flowchart LR
    IN["DPI payloads<br/>{land, discom, aa, uli}<br/>POST /score (in-memory)"]

    subgraph EX["features/extract.py"]
        E1["coverage = which sources present"]
        E2["features = 17 keys<br/>4 presence flags + 13 normalised<br/>values (capped, e.g. balance/50k)"]
    end

    subgraph MD["model/bri.py — BRI 0-100"]
        C1["_component(source)<br/>sub-score 0-1 per source"]
        W1["WEIGHTS<br/>land 0.25, discom 0.25,<br/>aa 0.30, uli 0.20"]
        S1["score():<br/>100 * w/Σw_present * component<br/>weights renormalized over coverage"]
        B1["suggest_loan(bri):<br/>≥80 → ₹1L-5L<br/>≥60 → ₹50k-2L<br/>≥40 → ₹25k-75k<br/>else → null"]
    end

    OUT["ScoreResponse<br/>bri, model_version,<br/>features, attributions,<br/>max_points, loan_range"]

    IN --> E1 --> E2 --> C1
    E2 --> W1 --> S1
    C1 --> S1
    S1 --> B1
    S1 --> OUT
    B1 --> OUT

    classDef in fill:#0f172a,color:#e2e8f0,stroke:#38bdf8
    classDef md fill:#14532d,color:#dcfce7,stroke:#22c55e
    classDef out fill:#422006,color:#fef3c7,stroke:#f59e0b
    class IN in
    class E1,E2,C1,W1,S1,B1 md
    class OUT out
```

Per-source sub-scores (`_component`, bri.py:35-62), all clamped to [0, 1]:

| Source | Formula |
|---|---|
| land | 0.50·(acres/5) + 0.30·clear_title + 0.20·(years/20) |
| discom | 0.60·on_time_ratio + 0.20·(months_paid/24) + 0.20·bill_level |
| aa | 0.40·balance_level + 0.40·inflow_consistency + 0.20·(months/60) − 0.30·emi_ratio |
| uli | 0.50·(1 − loans/4) + 0.30·(repay_months/24) + 0.20·(1 − delinquencies/3) |

- Sparse consents still score: absent sources drop out and the remaining weights
  renormalize (`Σ max_points = 100`).
- `score()` and `suggest_loan()` are pure functions — the HLD's trained XGBoost model drops
  in behind the same interface; `model_version` records which ran.
- BRI bands for the report: **≥80 Strong**, **≥60 Good**, **≥40 Fair**, **<40 Building**
  (loan range absent below 40).

## 8. Pass-through trust boundary

What may cross each boundary, and what may not — the invariant from HLD §5 rendered as a
data-flow diagram:

```mermaid
flowchart LR
    subgraph EXT1["External rails"]
        R1["DPI sources<br/>land / discom / aa / uli"]
    end

    subgraph MEM["Process memory — request lifetime only"]
        RAW["Raw source payloads<br/>(orchestrator)"]
        FEAT["Derived features<br/>(scoring request body)"]
    end

    subgraph RD["Redis — TTL-bound"]
        S1["session + OTP state"]
    end

    subgraph PG["Postgres — persistent"]
        P1["audit_events<br/>metadata + counts + hashes"]
        P2["consents<br/>scope + lifecycle timestamps"]
        P3["appraisals<br/>bri + model_version + source status"]
    end

    subgraph EXT2["External counterparty"]
        N1["Partner NBFC<br/>ids + bri + loan_range<br/>(HMAC-signed)"]
    end

    R1 -->|"records"| RAW
    RAW -->|"features only<br/>(transits, never stored)"| FEAT
    FEAT -.->|"X — never persisted"| PG
    RAW -.->|"X — never persisted"| PG
    RAW -->|"X — no raw records"| RD
    RAW -->|"outcome only"| P1
    FEAT -->|"bri + versions"| P3
    RD -->|"consent lifecycle"| P2
    RAW -->|"package"| N1

    classDef ok fill:#14532d,color:#dcfce7,stroke:#22c55e
    classDef no fill:#450a0a,color:#fecaca,stroke:#ef4444,stroke-dasharray: 5 4
    class P1,P2,P3,S1,N1 ok
```

Compliance posture: purpose limitation (credit appraisal only), retention = audit ledger +
consent records only, revocable consent aborts any in-flight pull (DPDP); TLS 1.3 in
transit, AES-256 for stored audit logs (HLD §5); webhooks to/from the NBFC are
HMAC-SHA256-signed (`security.py`) with the appraisal body hashed into the ledger
(`payload_hash`).

## 9. API surface

| Method & path | Handler | Prerequisite state | On violation |
|---|---|---|---|
| `POST /v1/sessions` | routes_sessions | — | — |
| `GET  /v1/sessions/{id}` | routes_sessions | session exists | 404 |
| `POST /v1/sessions/{id}/otp` | routes_sessions | `CREATED` | 409 / 400 (bad OTP) |
| `POST /v1/sessions/{id}/consents` | routes_consent | `IDENTITY_VERIFIED` | 409 / 422 (bad scope) |
| `POST /v1/sessions/{id}/consents/revoke` | routes_consent | any post-consent state | 409 / 404 |
| `POST /v1/sessions/{id}/appraise` | routes_appraise | `CONSENT_GRANTED` + live consent | 409 / 403 / 502 |
| `GET  /v1/appraisals/{id}` | routes_appraise | appraisal exists | 404 |
| `POST /v1/webhooks/disbursal` | routes_webhooks | valid `X-Signature` | 401 / 400 / 404 / 422 |
| `GET  /healthz` | routes_health | PG + Redis ping | 503 if degraded |
| `POST /score` (internal :8001) | scoring/service | — | — |
| `GET  /healthz` (internal :8001) | scoring/service | — | — |

```mermaid
flowchart LR
    FE["PWA / nginx / Vite"] -->|"JSON over /v1"| GW["FastAPI routers<br/>(state + consent guards)"]
    GW -->|"in-memory payloads"| SCR["scoring :8001<br/>POST /score"]
    GW -->|"signed package"| NBFC["Partner NBFC"]
    NBFC -->|"signed callback"| GW
```

---

*Source of truth: `docs/SetuCredit_HLD_Document.pdf` → `docs/ARCHITECTURE.md` → this file →
code. Keep all four in sync; where they conflict, the HLD wins.*
