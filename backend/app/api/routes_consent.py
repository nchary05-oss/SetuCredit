"""Consent grant/revoke (DPDP): required before any DPI pull."""

from fastapi import APIRouter, HTTPException

from app import session as sess
from app.api.routes_sessions import DbDep, load_session_or_404
from app.audit import service as audit
from app.consent import service as consent_service
from app.models import Consent
from app.redis_client import redis_client
from app.schemas import ConsentCreate, ConsentView

router = APIRouter(prefix="/v1/sessions", tags=["consent"])


def _consent_view(consent: Consent) -> ConsentView:
    return ConsentView(
        consent_id=consent.id,
        session_id=consent.session_id,
        scope=consent.scope,
        status=consent.status,
        granted_at=consent.granted_at.isoformat(),
        expires_at=consent.expires_at.isoformat(),
    )


@router.post("/{session_id}/consents", response_model=ConsentView)
async def create_consent(
    session_id: str,
    body: ConsentCreate,
    db: DbDep,
):
    data = await load_session_or_404(session_id)
    sess.require_state(data, "IDENTITY_VERIFIED")
    try:
        consent = await consent_service.grant(db, session_id, body.scope)
    except consent_service.ConsentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    data["consent_id"] = consent.id
    await sess.set_state(redis_client, data, "CONSENT_GRANTED")
    await audit.emit(
        db,
        session_id=session_id,
        event_type="consent.granted",
        consent_id=consent.id,
    )
    await db.commit()
    return _consent_view(consent)


@router.post("/{session_id}/consents/revoke", response_model=ConsentView)
async def revoke_consent(session_id: str, db: DbDep):
    data = await load_session_or_404(session_id)
    sess.require_state(data, "CONSENT_GRANTED", "PULLING", "SCORED", "HANDED_OFF")
    consent = await db.get(Consent, data["consent_id"])
    if consent is None:
        raise HTTPException(status_code=404, detail="consent not found")
    if consent.status == "granted":
        await consent_service.revoke(db, consent)
    data["consent_id"] = None
    await sess.set_state(redis_client, data, "IDENTITY_VERIFIED")
    await audit.emit(
        db,
        session_id=session_id,
        event_type="consent.revoked",
        consent_id=consent.id,
    )
    await db.commit()
    return _consent_view(consent)
