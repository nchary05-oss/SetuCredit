"""Deterministic stub adapters for the four DPI sources.

Stand-ins for real ULI/AA/land/DISCOM integrations: payloads are derived
from a hash of (session_id, source) so the same session always produces the
same synthetic records. Real adapters replace these behind DPIAdapter.
"""

import hashlib

from app.dpi.base import SourceResult


def _seed(session_id: str, source: str) -> int:
    digest = hashlib.sha256(f"{session_id}:{source}".encode()).hexdigest()
    return int(digest, 16)


def _unit(seed: int, salt: int) -> float:
    """Deterministic float in [0, 1)."""
    return ((seed >> salt) % 10_000) / 10_000


class LandAdapter:
    source_id = "land"

    async def fetch(self, session_id: str) -> SourceResult:
        s = _seed(session_id, "land")
        ownership = ("clear", "clear", "clear", "inheritance_pending", "disputed")[s % 5]
        payload = {
            "registry": ("dharani", "bhulekh")[s % 2],
            "survey_no": f"{100 + s % 900}",
            "area_acres": round(0.5 + _unit(s, 8) * 7.5, 2),
            "ownership": ownership,
            "years_held": 1 + s % 30,
        }
        return SourceResult(self.source_id, True, payload, None, 1)


class DiscomAdapter:
    source_id = "discom"

    async def fetch(self, session_id: str) -> SourceResult:
        s = _seed(session_id, "discom")
        payload = {
            "utility": f"DISCOM-{1 + s % 5}",
            "consumer_no": f"{s % 10**9:09d}",
            "months_paid": 6 + s % 19,
            "on_time_ratio": round(0.55 + _unit(s, 4) * 0.45, 2),
            "avg_monthly_bill_inr": 300 + s % 2700,
        }
        return SourceResult(self.source_id, True, payload, None, 1)


class AAAdapter:
    source_id = "aa"

    async def fetch(self, session_id: str) -> SourceResult:
        s = _seed(session_id, "aa")
        payload = {
            "bank": f"BANK-{1 + s % 8}",
            "months_active": 6 + s % 54,
            "avg_balance_inr": 500 + s % 49_500,
            "inflow_consistency": round(0.4 + _unit(s, 12) * 0.6, 2),
            "existing_emi_ratio": round(_unit(s, 16) * 0.7, 2),
        }
        return SourceResult(self.source_id, True, payload, None, 1)


class ULIAdapter:
    source_id = "uli"

    async def fetch(self, session_id: str) -> SourceResult:
        s = _seed(session_id, "uli")
        payload = {
            "existing_loans": s % 4,
            "repayment_regular_months": s % 37,
            "delinquencies_12m": (s // 7) % 3,
        }
        return SourceResult(self.source_id, True, payload, None, 1)


ALL_ADAPTERS: list = [LandAdapter(), DiscomAdapter(), AAAdapter(), ULIAdapter()]
