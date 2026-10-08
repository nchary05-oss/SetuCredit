"""OTP provider routing, hash-at-rest, and attempts cap."""

import httpx
import pytest
from app.config import get_settings
from app.otp import provider as otp_provider
from app.redis_client import redis_client

pytestmark = pytest.mark.integration


@pytest.fixture
def clean_settings(monkeypatch):
    for var in ("OTP_MODE", "SMS_BASE_URL", "SMS_API_KEY", "SMS_SENDER_ID", "SMS_TEMPLATE_ID"):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_provider_is_stub(clean_settings):
    assert isinstance(otp_provider.get_provider(), otp_provider.StubOtpProvider)


def test_sms_mode_without_credentials_stays_stub(clean_settings, monkeypatch):
    monkeypatch.setenv("OTP_MODE", "sms")
    get_settings.cache_clear()
    assert isinstance(otp_provider.get_provider(), otp_provider.StubOtpProvider)


def test_sms_mode_with_credentials_uses_sms(clean_settings, monkeypatch):
    monkeypatch.setenv("OTP_MODE", "sms")
    monkeypatch.setenv("SMS_API_KEY", "test-key")
    monkeypatch.setenv("SMS_BASE_URL", "https://sms.example/send")
    get_settings.cache_clear()
    assert isinstance(otp_provider.get_provider(), otp_provider.SmsOtpProvider)


async def test_sms_provider_posts_gateway_shape(clean_settings, monkeypatch):
    seen = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = request.read().decode()
        return httpx.Response(200, json={"status": "queued"})

    monkeypatch.setenv("OTP_MODE", "sms")
    monkeypatch.setenv("SMS_API_KEY", "test-key")
    monkeypatch.setenv("SMS_BASE_URL", "https://sms.example/send")
    get_settings.cache_clear()
    sender = otp_provider.SmsOtpProvider(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )
    await sender.send(session_id="sess-1", code="123456", mobile="+911234567890")
    assert seen["auth"] == "Bearer test-key"
    assert "123456" in seen["body"] and "+911234567890" in seen["body"]


async def test_otp_stored_as_hash_not_plaintext(client):
    r = await client.post("/v1/sessions", json={"language": "en-IN"})
    session_id = r.json()["session_id"]
    r = await client.post(
        f"/v1/sessions/{session_id}/otp",
        json={"action": "send", "aadhaar_number": "999999990019", "consent": True},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["txn_id"] and body["masked_aadhaar"] == "XXXXXXXX0019"
    code = body["dev_otp"]
    stored = await redis_client.get(f"otp:{session_id}")
    assert stored is not None and stored != code
    assert len(stored) == 64  # sha256 hex
    # Full Aadhaar must never be stored — only hash + masked refs.
    txn_raw = await redis_client.get(f"aadhaar_txn:{session_id}")
    assert txn_raw is not None and "999999990019" not in txn_raw
    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "verify", "otp": code})
    assert r.status_code == 200
    assert await redis_client.get(f"aadhaar_txn:{session_id}") is None


async def test_attempts_capped_then_reset_on_resend(client):
    r = await client.post("/v1/sessions", json={"language": "en-IN"})
    session_id = r.json()["session_id"]
    send = {"action": "send", "aadhaar_number": "999999990019", "consent": True}
    r = await client.post(f"/v1/sessions/{session_id}/otp", json=send)
    code = r.json()["dev_otp"]
    wrong = "000000" if code != "000000" else "999999"
    for _ in range(get_settings().otp_max_attempts):
        r = await client.post(
            f"/v1/sessions/{session_id}/otp", json={"action": "verify", "otp": wrong}
        )
        assert r.status_code == 400
    # Correct code is now locked out.
    r = await client.post(f"/v1/sessions/{session_id}/otp", json={"action": "verify", "otp": code})
    assert r.status_code == 400
    # Resend resets the counter; the new code verifies.
    r = await client.post(f"/v1/sessions/{session_id}/otp", json=send)
    assert r.status_code == 200
    r = await client.post(
        f"/v1/sessions/{session_id}/otp",
        json={"action": "verify", "otp": r.json()["dev_otp"]},
    )
    assert r.status_code == 200
