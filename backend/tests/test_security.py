"""Webhook HMAC signing — unit tests, no infra required."""

from app.security import sign, verify

BODY = b'{"appraisal_id":"abc","status":"disbursed"}'


def test_roundtrip_sign_verify():
    assert verify(sign(BODY), BODY)


def test_tampered_body_rejected():
    signature = sign(BODY)
    assert not verify(signature, BODY + b" ")


def test_wrong_signature_rejected():
    assert not verify("deadbeef", BODY)


def test_wrong_secret_rejected():
    signature = sign(BODY, secret="other-secret")
    assert not verify(signature, BODY)
