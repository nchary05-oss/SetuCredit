"""Uniform adapter interface for DPI sources (RBI ULI, AA, land, DISCOM)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class SourceResult:
    source_id: str
    ok: bool
    payload: dict | None
    error: str | None
    record_count: int


class DPIAdapter(Protocol):
    source_id: str

    async def fetch(self, session_id: str) -> SourceResult: ...
