"""HTTP client for the scoring microservice (separate process by design)."""

import httpx

from app.config import get_settings


async def score(payloads: dict[str, dict]) -> dict:
    settings = get_settings()
    async with httpx.AsyncClient(
        base_url=settings.scoring_service_url,
        timeout=settings.scoring_timeout_seconds,
    ) as client:
        response = await client.post("/score", json={"payloads": payloads})
        response.raise_for_status()
        return response.json()


async def warmup() -> None:
    """Best-effort background ping to wake up scoring service on cold-start hosts (e.g. Render)."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(
            base_url=settings.scoring_service_url,
            timeout=5.0,
        ) as client:
            await client.get("/healthz")
    except Exception:
        pass
