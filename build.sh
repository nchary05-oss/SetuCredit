#!/usr/bin/env bash
# SetuCredit full build: Python workspace -> lint -> infra -> tests -> frontend -> images.
# Usage:
#   ./build.sh                    # everything
#   SKIP_TESTS=1 ./build.sh       # skip pytest (no Postgres/Redis needed)
#   SKIP_FRONTEND=1 ./build.sh    # skip npm build
#   SKIP_DOCKER=1 ./build.sh      # skip `docker compose build`
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "==> 1/5 uv sync"
uv sync --all-packages

echo "==> 2/5 ruff check"
uv run ruff check backend scoring

if [ "${SKIP_TESTS:-0}" != "1" ]; then
  echo "==> 3/5 infra up (postgres, redis)"
  docker compose -f infra/docker-compose.yml up -d postgres redis
  echo "==> 4/5 pytest"
  uv run pytest -q
else
  echo "==> 3-4/5 tests skipped (SKIP_TESTS=1)"
fi

if [ "${SKIP_FRONTEND:-0}" != "1" ]; then
  echo "==> 5/5 frontend build"
  (cd frontend && npm install && npm run build)
else
  echo "==> 5/5 frontend skipped (SKIP_FRONTEND=1)"
fi

if [ "${SKIP_DOCKER:-0}" != "1" ]; then
  echo "==> docker compose build (profile: app)"
  docker compose -f infra/docker-compose.yml --profile app build
else
  echo "==> docker build skipped (SKIP_DOCKER=1)"
fi

echo "OK: build complete."
