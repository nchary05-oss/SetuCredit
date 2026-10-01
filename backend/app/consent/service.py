"""DPDP consent: explicit, time-bound, revocable — gates every DPI pull."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import KNOWN_SOURCES, get_settings
from app.models import Consent


class ConsentError(Exception):
    pass


async def grant(db: AsyncSession, session_id: str, scope: list[str]) -> Consent:
    invalid = set(scope) - set(KNOWN_SOURCES)
    if invalid or not scope:
        raise ConsentError(f"invalid scope: {sorted(invalid) or scope}")
    now = datetime.now(UTC)
    consent = Consent(
        session_id=session_id,
        scope=sorted(scope),
        status="granted",
        granted_at=now,
        expires_at=now + timedelta(seconds=get_settings().consent_ttl_seconds),
    )
    db.add(consent)
    await db.flush()
    return consent


async def load_active(db: AsyncSession, consent_id: str) -> Consent:
    consent = await db.get(Consent, consent_id)
    if consent is None:
        raise ConsentError("consent not found")
    if consent.status != "granted":
        raise ConsentError(f"consent {consent.status}")
    if consent.expires_at <= datetime.now(UTC):
        consent.status = "expired"
        await db.flush()
        raise ConsentError("consent expired")
    return consent


async def revoke(db: AsyncSession, consent: Consent) -> None:
    consent.status = "revoked"
    consent.revoked_at = datetime.now(UTC)
    await db.flush()
