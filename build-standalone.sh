#!/usr/bin/env bash
# Build the standalone (offline) deployment bundle:
#   dist/setucredit-deploy/          # single folder that runs the whole stack with no image pulls
#   dist/setucredit-deploy.tar.gz    # distributable archive of the above
#
# Bundle layout (matches docs/SetuCredit_Deployment_and_Run_Guide.pdf, Part A):
#   docker-compose.yml  # 5 services, prebuilt image refs, secrets from .env
#   .env.example        # copy to .env and edit
#   images/*.tar.gz     # backend, scoring, frontend, postgres:16-alpine, redis:7-alpine
#   scripts/            # load-images.sh, run.sh, stop.sh
#   docs/               # Deployment & Run Guide PDF
#   README.txt, SHA256SUMS
#
# dist/ is gitignored, so every text file in the bundle is generated below —
# a fresh clone plus Docker is all this script needs (plus the guide PDF in docs/).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BUNDLE="$ROOT/dist/setucredit-deploy"
GUIDE_PDF="docs/SetuCredit_Deployment_and_Run_Guide.pdf"

command -v docker >/dev/null 2>&1 || { echo "error: docker not found" >&2; exit 1; }
[ -f "$GUIDE_PDF" ] || {
  echo "error: $GUIDE_PDF not found — generate it first:" >&2
  echo "  uv run --with reportlab python3 docs/deploy_run_guide_gen.py" >&2
  exit 1
}

echo "==> 1/5 building images"
docker compose -f infra/docker-compose.yml --profile app build
docker pull postgres:16-alpine
docker pull redis:7-alpine

echo "==> 2/5 writing bundle text files"
rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/images" "$BUNDLE/scripts" "$BUNDLE/docs"

cat > "$BUNDLE/docker-compose.yml" <<'EOF'
# SetuCredit — offline deployment bundle.
# Prebuilt images (load with scripts/load-images.sh); no pulls, no builds needed.
# Secrets come from .env (copy .env.example); defaults are safe demo values.
name: setucredit

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: setucredit
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-setucredit}
      POSTGRES_DB: setucredit
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U setucredit"]
      interval: 5s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  scoring:
    image: setucredit-scoring:latest
    profiles: ["app"]
    ports:
      - "8001:8001"

  backend:
    image: setucredit-backend:latest
    profiles: ["app"]
    environment:
      ENV: ${ENV:-dev}
      DATABASE_URL: postgresql+asyncpg://setucredit:${POSTGRES_PASSWORD:-setucredit}@postgres:5432/setucredit
      REDIS_URL: redis://redis:6379/0
      SCORING_SERVICE_URL: http://scoring:8001
      WEBHOOK_SECRET: ${WEBHOOK_SECRET:-dev-webhook-secret}
      PARTNER_WEBHOOK_URL: ${PARTNER_WEBHOOK_URL:-}
      ULI_MODE: ${ULI_MODE:-stub}
      OTP_MODE: ${OTP_MODE:-stub}
      OTP_MAX_ATTEMPTS: ${OTP_MAX_ATTEMPTS:-5}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      scoring:
        condition: service_started

  frontend:
    image: setucredit-frontend:latest
    profiles: ["app"]
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:
  pgdata:
EOF

cat > "$BUNDLE/.env.example" <<'EOF'
# SetuCredit bundle configuration. Copy to `.env` and edit.
# Only these values need attention; service URLs/ports are pre-wired.

# dev = demo mode (OTP shown on screen). Use prod for any real user.
ENV=dev

# Demo defaults — rotate before any production use.
POSTGRES_PASSWORD=setucredit
WEBHOOK_SECRET=dev-webhook-secret

# Unset = simulated lender handoff. Set to the partner NBFC endpoint for live handoff.
PARTNER_WEBHOOK_URL=

# stub = deterministic demo data/providers. live/sms need real credentials.
ULI_MODE=stub
OTP_MODE=stub
OTP_MAX_ATTEMPTS=5
EOF

cat > "$BUNDLE/scripts/load-images.sh" <<'EOF'
#!/bin/bash
# Load all prebuilt bundle images into the local Docker daemon. No network needed.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$HERE"/images/*.tar.gz; do
  echo "loading $f ..."
  gzip -dc "$f" | docker load
done
echo "all images loaded."
EOF

cat > "$BUNDLE/scripts/run.sh" <<'EOF'
#!/bin/bash
# Start the full SetuCredit stack and wait until the backend is healthy.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
if [ ! -f .env ]; then
  echo ".env not found — copying .env.example (edit it for your machine)."
  cp .env.example .env
fi
docker compose --profile app up -d
echo "waiting for backend health ..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:8000/healthz | grep -q '"status":"ok"'; then
    echo "backend healthy."
    break
  fi
  if [ "$i" = "60" ]; then
    echo "backend did not turn healthy in 60s — run: docker compose --profile app logs backend"
    exit 1
  fi
  sleep 5
done
echo "PWA:      http://localhost:8080"
echo "API docs: http://localhost:8000/docs"
EOF

cat > "$BUNDLE/scripts/stop.sh" <<'EOF'
#!/bin/bash
# Stop the stack. Data volumes are kept (restart resumes history).
# Wipe demo data with: docker compose --profile app down -v
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
docker compose --profile app down
echo "stopped (volumes kept). Wipe with: docker compose --profile app down -v"
EOF

cat > "$BUNDLE/README.txt" <<'EOF'
SetuCredit — offline deployment bundle
=========================================

Contents: docker-compose.yml (5 services), .env.example, images/*.tar.gz
(prebuilt backend/scoring/frontend/postgres/redis), scripts/, docs/ (user
guide PDF), SHA256SUMS.

Run:
  1. sha256sum -c SHA256SUMS
  2. ./scripts/load-images.sh
  3. cp .env.example .env   # edit secrets
  4. ./scripts/run.sh

Then open http://localhost:8080 (PWA) and http://localhost:8000/docs (API).
Stop with ./scripts/stop.sh. Full instructions, demo script, borrower
walkthrough, and troubleshooting: docs/SetuCredit_Deployment_and_Run_Guide.pdf.
EOF

chmod +x "$BUNDLE"/scripts/*.sh
cp "$GUIDE_PDF" "$BUNDLE/docs/"

echo "==> 3/5 saving images"
docker save setucredit-backend:latest | gzip > "$BUNDLE/images/backend.tar.gz"
docker save setucredit-scoring:latest | gzip > "$BUNDLE/images/scoring.tar.gz"
docker save setucredit-frontend:latest | gzip > "$BUNDLE/images/frontend.tar.gz"
docker save postgres:16-alpine | gzip > "$BUNDLE/images/postgres.tar.gz"
docker save redis:7-alpine | gzip > "$BUNDLE/images/redis.tar.gz"

echo "==> 4/5 checksums + archive"
if command -v sha256sum >/dev/null 2>&1; then
  SHASUM="sha256sum"
else
  SHASUM="shasum -a 256" # macOS without coreutils
fi
(cd "$BUNDLE" && $SHASUM \
  .env.example \
  docker-compose.yml \
  docs/SetuCredit_Deployment_and_Run_Guide.pdf \
  images/backend.tar.gz \
  images/frontend.tar.gz \
  images/postgres.tar.gz \
  images/redis.tar.gz \
  images/scoring.tar.gz \
  README.txt \
  scripts/load-images.sh \
  scripts/run.sh \
  scripts/stop.sh \
  > SHA256SUMS)
tar -czf dist/setucredit-deploy.tar.gz -C dist setucredit-deploy

echo "==> 5/5 verify"
(cd "$BUNDLE" && $SHASUM -c SHA256SUMS | tail -3)
du -sh "$BUNDLE" dist/setucredit-deploy.tar.gz
echo "OK: standalone bundle ready."
