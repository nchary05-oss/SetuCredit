"""Inbound webhooks from partner NBFC (HMAC-signed, replay-protected by digest)."""

import json
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request

from app.api.routes_sessions import DbDep
from app.audit import service as audit
from app.models import Appraisal
from app.security import verify

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/disbursal")
async def disbursal(request: Request, db: DbDep):
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    if not verify(signature, body):
        raise HTTPException(status_code=401, detail="invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid json") from exc

    appraisal_id = payload.get("appraisal_id")
    if not appraisal_id:
        raise HTTPException(status_code=422, detail="appraisal_id required")

    appraisal = await db.get(Appraisal, appraisal_id)
    if appraisal is None:
        raise HTTPException(status_code=404, detail="appraisal not found")

    appraisal.status = "disbursed"
    appraisal.disbursed_at = datetime.now(UTC)
    await audit.emit(
        db,
        session_id=appraisal.session_id,
        event_type="disbursal.received",
        entity_id=appraisal.id,
        payload_hash=audit.payload_hash(body),
    )
    await db.commit()
    return {"ok": True}
