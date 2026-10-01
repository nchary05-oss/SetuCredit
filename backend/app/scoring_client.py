"""HTTP client for the scoring microservice (separate process by design)."""

import httpx

from app.config import get_settings


async def score(payloads: dict[str, dict]) -> dict:
    settings = get_settings()
    async with httpx.AsyncClient(base_url=settings.scoring_service_url, timeout=10.0) as client:
        response = await client.post("/score", json={"payloads": payloads})
        response.raise_for_status()
        return response.json()
