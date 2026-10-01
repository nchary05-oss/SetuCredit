"""Session lifecycle: create, inspect, Aadhaar OTP stub (DigiLocker stand-in)."""

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import session as sess
from app.audit import service as audit
from app.config import get_settings
from app.db import get_db
from app.redis_client import redis_client
from app.schemas import (
    NEXT_ACTION,
    OtpRequest,
    OtpResponse,
    SessionCreate,
    SessionView,
)

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _view(data: dict) -> SessionView:
    return SessionView(
        session_id=data["session_id"],
        state=data["state"],
        language=data["language"],
        consent_id=data.get("consent_id"),
        appraisal_id=data.get("appraisal_id"),
        next_action=NEXT_ACTION[data["state"]],
    )


async def load_session_or_404(session_id: str) -> dict:
    data = await sess.get_session(redis_client, session_id)
    if data is None:
        raise HTTPException(status_code=404, detail="session not found")
    return data


@router.post("", response_model=SessionView)
async def create_session(body: SessionCreate, db: DbDep):
    data = await sess.create_session(redis_client, body.language)
    await audit.emit(db, session_id=data["session_id"], event_type="session.created")
    await db.commit()
    return _view(data)


@router.get("/{session_id}", response_model=SessionView)
async def get_session(session_id: str):
    return _view(await load_session_or_404(session_id))


@router.post("/{session_id}/otp", response_model=OtpResponse)
async def otp(
    session_id: str,
    body: OtpRequest,
    db: DbDep,
):
    data = await load_session_or_404(session_id)

    if body.action == "send":
        sess.require_state(data, "CREATED")
        code = f"{secrets.randbelow(10**6):06d}"
        await sess.store_otp(redis_client, session_id, code)
        dev_otp = code if get_settings().env == "dev" else None
        return OtpResponse(sent=True, dev_otp=dev_otp)

    sess.require_state(data, "CREATED")
    if not await sess.verify_otp(redis_client, session_id, body.otp):
        raise HTTPException(status_code=400, detail="invalid otp")
    await sess.set_state(redis_client, data, "IDENTITY_VERIFIED")
    await audit.emit(db, session_id=session_id, event_type="identity.verified")
    await db.commit()
    return OtpResponse(verified=True, state=data["state"])
