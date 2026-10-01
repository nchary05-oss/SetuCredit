FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/
COPY scoring/pyproject.toml scoring/
RUN uv sync --all-packages --locked --no-dev --no-install-project

COPY scoring scoring
RUN uv sync --all-packages --locked --no-dev

WORKDIR /app/scoring
EXPOSE 8001
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
