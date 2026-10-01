"""Full end-to-end flow against live Postgres + Redis + scoring service."""

import hashlib
import hmac
import json

import pytest

pytestmark = pytest.mark.integration


async def _verified_session(client, language: str = "hi-IN") -> str:
    r = await client.post("/v1/sessions", json={"language": language})
    assert r.status_code == 200
    session_id = r.json()["session_id"]

    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "send"})
    assert r.status_code == 200
    otp = r.json()["dev_otp"]
    assert otp and len(otp) == 6

    wrong = "000000" if otp != "000000" else "999999"
    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "verify", "otp": wrong})
    assert r.status_code == 400

    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "verify", "otp": otp})
    assert r.status_code == 200
    assert r.json()["state"] == "IDENTITY_VERIFIED"
    return session_id


async def test_healthz(client):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "postgres": "ok", "redis": "ok"}


async def test_full_flow(client):
    session_id = await _verified_session(client)

    r = await client.post(f"/v1/sessions/{session_id}/appraise")
    assert r.status_code == 409  # consent gate: not yet CONSENT_GRANTED

    r = await client.post(
        f"/v1/sessions/{session_id}/consents",
        json={"scope": ["land", "discom", "aa", "uli"]},
    )
    assert r.status_code == 200
    consent = r.json()
    assert consent["status"] == "granted"

    r = await client.post(f"/v1/sessions/{session_id}/appraise")
    assert r.status_code == 200, r.text
    result = r.json()
    assert 0 <= result["bri"] <= 100
    assert result["state"] == "HANDED_OFF"
    assert result["handoff"] == "simulated"
    assert all(s["status"] == "ok" for s in result["sources"].values())
    appraisal_id = result["appraisal_id"]

    r = await client.get(f"/v1/appraisals/{appraisal_id}")
    assert r.status_code == 200
    view = r.json()
    assert view["status"] == "handed_off"
    assert view["bri"] == result["bri"]

    r = await client.get(f"/v1/sessions/{session_id}")
    assert r.json()["next_action"] == "done"

    payload = json.dumps({"appraisal_id": appraisal_id, "status": "disbursed"}).encode()
    bad_sig = hmac.new(b"wrong-secret", payload, hashlib.sha256).hexdigest()
    r = await client.post(
        "/v1/webhooks/disbursal", content=payload, headers={"X-Signature": bad_sig}
    )
    assert r.status_code == 401

    good_sig = hmac.new(b"dev-webhook-secret", payload, hashlib.sha256).hexdigest()
    r = await client.post(
        "/v1/webhooks/disbursal", content=payload, headers={"X-Signature": good_sig}
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = await client.get(f"/v1/appraisals/{appraisal_id}")
    view = r.json()
    assert view["status"] == "disbursed"
    assert view["disbursed_at"] is not None


async def test_revoked_consent_blocks_appraise(client):
    session_id = await _verified_session(client)
    r = await client.post(f"/v1/sessions/{session_id}/consents", json={})
    assert r.status_code == 200

    r = await client.post(f"/v1/sessions/{session_id}/consents/revoke")
    assert r.status_code == 200
    assert r.json()["status"] == "revoked"

    r = await client.post(f"/v1/sessions/{session_id}/appraise")
    assert r.status_code == 409  # state rolled back to IDENTITY_VERIFIED


async def test_invalid_scope_rejected(client):
    session_id = await _verified_session(client)
    r = await client.post(f"/v1/sessions/{session_id}/consents", json={"scope": ["bogus"]})
    assert r.status_code == 422


async def test_session_state_guards(client):
    session_id = await _verified_session(client)
    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "send"})
    assert r.status_code == 409  # already identity-verified

    r = await client.get("/v1/sessions/does-not-exist")
    assert r.status_code == 404
