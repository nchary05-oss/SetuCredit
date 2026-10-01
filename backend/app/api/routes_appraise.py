"""Appraise: consent-gated parallel DPI pull -> scoring -> NBFC handoff."""

import httpx
from fastapi import APIRouter, HTTPException

from app import session as sess
from app.api.routes_sessions import DbDep, load_session_or_404
from app.audit import service as audit
from app.config import get_settings
from app.consent import service as consent_service
from app.models import Appraisal
from app.orchestrator.run import run_pull
from app.redis_client import redis_client
from app.schemas import AppraisalView, AppraiseResponse, SourceStatus
from app.scoring_client import score
from app.security import sign

router = APIRouter(prefix="/v1", tags=["appraisal"])


async def _revert_to_consent(data: dict) -> None:
    await sess.set_state(redis_client, data, "CONSENT_GRANTED")


@router.post("/sessions/{session_id}/appraise", response_model=AppraiseResponse)
async def appraise(session_id: str, db: DbDep):
    data = await load_session_or_404(session_id)
    sess.require_state(data, "CONSENT_GRANTED")

    try:
        consent = await consent_service.load_active(db, data["consent_id"])
    except consent_service.ConsentError as exc:
        await db.commit()  # persist any expiry update made by load_active
        raise HTTPException(status_code=403, detail=f"consent gate: {exc}") from exc

    await sess.set_state(redis_client, data, "PULLING")
    results = await run_pull(session_id, consent.scope)
    for result in results.values():
        await audit.emit(
            db,
            session_id=session_id,
            event_type="dpi.pull" if result.ok else "dpi.pull_failed",
            consent_id=consent.id,
            source_id=result.source_id,
            record_count=result.record_count,
        )

    ok = {k: v for k, v in results.items() if v.ok}
    if not ok:
        await _revert_to_consent(data)
        await db.commit()
        raise HTTPException(status_code=502, detail="all DPI sources failed")

    try:
        score_result = await score({k: v.payload for k, v in ok.items()})
    except httpx.HTTPError as exc:
        await _revert_to_consent(data)
        await db.commit()
        raise HTTPException(status_code=502, detail="scoring unavailable") from exc

    appraisal = Appraisal(
        session_id=session_id,
        status="scored",
        bri=int(score_result["bri"]),
        model_version=score_result["model_version"],
        sources={k: ("ok" if r.ok else "failed") for k, r in results.items()},
    )
    db.add(appraisal)
    await db.flush()
    data["appraisal_id"] = appraisal.id
    await sess.set_state(redis_client, data, "SCORED")
    await audit.emit(
        db,
        session_id=session_id,
        event_type="score.computed",
        entity_id=appraisal.id,
        consent_id=consent.id,
        model_version=appraisal.model_version,
    )

    handoff = await _hand_off(appraisal)
    if handoff != "failed":
        appraisal.status = "handed_off"
        await sess.set_state(redis_client, data, "HANDED_OFF")
        await audit.emit(
            db,
            session_id=session_id,
            event_type=f"handoff.{handoff}",
            entity_id=appraisal.id,
            model_version=appraisal.model_version,
        )

    await db.commit()
    return AppraiseResponse(
        appraisal_id=appraisal.id,
        state=data["state"],
        bri=appraisal.bri,
        model_version=appraisal.model_version,
        sources={
            k: SourceStatus(
                status="ok" if r.ok else "failed",
                error=r.error,
                record_count=r.record_count,
            )
            for k, r in results.items()
        },
        handoff=handoff,
    )


async def _hand_off(appraisal: Appraisal) -> str:
    """Send pre-underwritten package to partner NBFC; simulate if unconfigured."""
    settings = get_settings()
    if not settings.partner_webhook_url:
        return "simulated"
    body = (
        f'{{"appraisal_id":"{appraisal.id}","session_id":"{appraisal.session_id}",'
        f'"bri":{appraisal.bri},"model_version":"{appraisal.model_version}"}}'
    ).encode()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                settings.partner_webhook_url,
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": sign(body),
                },
            )
        return "sent"
    except httpx.HTTPError:
        return "failed"


@router.get("/appraisals/{appraisal_id}", response_model=AppraisalView)
async def get_appraisal(appraisal_id: str, db: DbDep):
    appraisal = await db.get(Appraisal, appraisal_id)
    if appraisal is None:
        raise HTTPException(status_code=404, detail="appraisal not found")
    return AppraisalView(
        appraisal_id=appraisal.id,
        session_id=appraisal.session_id,
        status=appraisal.status,
        bri=appraisal.bri,
        model_version=appraisal.model_version,
        sources=appraisal.sources,
        created_at=appraisal.created_at.isoformat(),
        disbursed_at=(appraisal.disbursed_at.isoformat() if appraisal.disbursed_at else None),
    )
