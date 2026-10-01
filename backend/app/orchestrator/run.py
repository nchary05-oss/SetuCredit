"""Async parallel fan-out to DPI sources, bounded by per-source timeout."""

import asyncio

from app.config import get_settings
from app.dpi.base import SourceResult
from app.dpi.stubs import ALL_ADAPTERS


async def run_pull(session_id: str, scope: list[str]) -> dict[str, SourceResult]:
    settings = get_settings()
    adapters = [a for a in ALL_ADAPTERS if a.source_id in scope]

    async def one(adapter) -> SourceResult:
        try:
            return await asyncio.wait_for(
                adapter.fetch(session_id), timeout=settings.dpi_timeout_seconds
            )
        except TimeoutError:
            return SourceResult(adapter.source_id, False, None, "timeout", 0)
        except Exception as exc:  # adapter failure must not fail the whole pull
            return SourceResult(adapter.source_id, False, None, str(exc), 0)

    results = await asyncio.gather(*(one(a) for a in adapters))
    return {r.source_id: r for r in results}
