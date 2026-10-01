"""SetuCredit API entrypoint: FastAPI app with consent-gated appraisal flow."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import (
    routes_appraise,
    routes_consent,
    routes_health,
    routes_sessions,
    routes_webhooks,
)
from app.db import dispose_engine
from app.redis_client import redis_client
from app.session import StateError


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await redis_client.aclose()
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SetuCredit API",
        version="0.1.0",
        description="Consent-gated middleware orchestration layer (HLD v1.0)",
        lifespan=lifespan,
    )

    @app.exception_handler(StateError)
    async def state_error_handler(request: Request, exc: StateError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    for router in (
        routes_sessions.router,
        routes_consent.router,
        routes_appraise.router,
        routes_webhooks.router,
        routes_health.router,
    ):
        app.include_router(router)
    return app


app = create_app()
