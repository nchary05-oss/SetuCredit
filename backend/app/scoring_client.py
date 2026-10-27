"""HTTP client for the scoring microservice (separate process by design)."""

import asyncio
import time

import httpx

from app.config import get_settings


async def score(payloads: dict[str, dict]) -> dict:
    settings = get_settings()
    deadline = time.monotonic() + settings.scoring_timeout_seconds
    last_exc: Exception | None = None

    async with httpx.AsyncClient(base_url=settings.scoring_service_url) as client:
        while time.monotonic() < deadline:
            remaining = max(1.0, deadline - time.monotonic())
            try:
                response = await client.post(
                    "/score",
                    json={"payloads": payloads},
                    timeout=min(remaining, 15.0),
                )
                if response.status_code == 200:
                    return response.json()
                if response.status_code in (502, 503, 504):
                    # Transient gateway response while host (e.g. Render) spins up container
                    await asyncio.sleep(2.0)
                    continue
                response.raise_for_status()
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.HTTPStatusError,
            ) as exc:
                last_exc = exc
                if time.monotonic() + 2.0 < deadline:
                    await asyncio.sleep(2.0)
                    continue
                raise

        if last_exc:
            raise last_exc
        raise httpx.ConnectTimeout("Scoring service request timed out")


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
