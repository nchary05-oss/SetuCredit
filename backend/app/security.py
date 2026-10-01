"""HMAC signing for partner NBFC webhooks (inbound and outbound)."""

import hashlib
import hmac

from app.config import get_settings


def sign(body: bytes, secret: str | None = None) -> str:
    secret = secret or get_settings().webhook_secret
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def verify(signature: str, body: bytes, secret: str | None = None) -> bool:
    expected = sign(body, secret)
    return hmac.compare_digest(expected, signature)
