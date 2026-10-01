"""Liveness/readiness: checks Postgres + Redis, 503 when degraded."""

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.api.routes_sessions import DbDep
from app.redis_client import redis_client
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz(response: Response, db: DbDep):
    try:
        await db.execute(text("SELECT 1"))
        postgres = "ok"
    except Exception:
        postgres = "error"
    try:
        await redis_client.ping()
        redis = "ok"
    except Exception:
        redis = "error"

    healthy = postgres == "ok" and redis == "ok"
    response.status_code = 200 if healthy else 503
    return HealthResponse(status="ok" if healthy else "degraded", postgres=postgres, redis=redis)
