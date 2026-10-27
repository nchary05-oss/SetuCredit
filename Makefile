# SetuCredit — one entrypoint for run/deploy/test commands.
#   make help        list targets
#   make setup       first-time install (python deps + .env + frontend deps)
#   make infra       start postgres + redis (dev infra for local services/tests)
#   make backend     run backend API on :8000 (reload)
#   make scoring     run scoring service on :8001 (reload)
#   make frontend    run Vite dev server on :5173 (proxies /v1 → :8000)
#   make up          full container stack (frontend :8080, backend :8000, scoring :8001)
#   make down        stop the compose stack
#   make test        run all tests
#   make lint        ruff check
#   make fmt         ruff format

COMPOSE := docker compose -f infra/docker-compose.yml

.DEFAULT_GOAL := help
.PHONY: help setup cicd infra db-upgrade db-revision backend scoring frontend up down test lint fmt

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## first-time install: python deps, .env, frontend deps
	uv sync --all-packages
	@test -f .env || cp .env.example .env
	@echo ".env ready (copied from template if it did not exist)"
	cd frontend && npm install

infra: ## start dev infra (postgres + redis)
	$(COMPOSE) up -d postgres redis
	@echo "postgres :5432  redis :6379   (logs: $(COMPOSE) logs -f redis)"

db-upgrade: ## apply migrations (reads root .env)
	cd backend && uv run --env-file ../.env alembic upgrade head

db-revision: ## autogenerate a migration:  make db-revision m="describe it"
	cd backend && uv run --env-file ../.env alembic revision --autogenerate -m "$(m)"

backend: ## run backend API :8000 with reload
	uv run uvicorn app.main:app --reload --port 8000

scoring: ## run scoring service :8001 with reload
	uv run uvicorn service.main:app --reload --port 8001

frontend: ## Vite dev server :5173 → proxies /v1 to backend
	cd frontend && npm run dev

up: ## full container stack (builds images): PWA :8080
	$(COMPOSE) --profile app up --build

down: ## stop + remove the compose stack
	$(COMPOSE) --profile app down

test: ## pytest (self-skips integration tests if infra is down)
	uv run pytest -q

lint: ## ruff check backend scoring
	uv run ruff check backend scoring

fmt: ## ruff format backend scoring
	uv run ruff format backend scoring
