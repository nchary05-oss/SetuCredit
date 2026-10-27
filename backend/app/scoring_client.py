"""HTTP client for the scoring microservice, with in-process fallback."""

import logging

import httpx

from app.config import get_settings
from app.scoring_fallback import compute_in_process

logger = logging.getLogger(__name__)


async def score(payloads: dict[str, dict]) -> dict:
    """Score DPI payloads: tries microservice; falls back to in-process engine if cold."""
    settings = get_settings()

    # Try microservice with short timeout so cold starts on free hosts don't stall the user
    try:
        async with httpx.AsyncClient(base_url=settings.scoring_service_url, timeout=4.0) as client:
            response = await client.post("/score", json={"payloads": payloads})
            if response.status_code == 200:
                return response.json()
            logger.info("Scoring microservice returned %s; using fallback", response.status_code)
    except Exception as exc:
        logger.info("Scoring microservice unavailable (%s); using fallback", exc)

    # In-process calculation ensures appraisal NEVER fails on cold start or network hiccups
    return compute_in_process(payloads)


async def warmup() -> None:
    """Best-effort background ping to wake up scoring service on cold-start hosts (e.g. Render)."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(
            base_url=settings.scoring_service_url,
            timeout=settings.scoring_timeout_seconds,
        ) as client:
            await client.get("/healthz")
    except Exception:
        pass
