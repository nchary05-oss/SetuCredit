"""Audit ledger writer: event metadata only, never borrower records."""

import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEvent


def payload_hash(payload: bytes | str) -> str:
    if isinstance(payload, str):
        payload = payload.encode()
    return hashlib.sha256(payload).hexdigest()


async def emit(
    db: AsyncSession,
    *,
    session_id: str,
    event_type: str,
    entity_id: str | None = None,
    consent_id: str | None = None,
    source_id: str | None = None,
    record_count: int | None = None,
    model_version: str | None = None,
    payload_hash: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            session_id=session_id,
            event_type=event_type,
            entity_id=entity_id,
            consent_id=consent_id,
            source_id=source_id,
            record_count=record_count,
            model_version=model_version,
            payload_hash=payload_hash,
        )
    )
