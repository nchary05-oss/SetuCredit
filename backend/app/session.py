"""Session + OTP state lives in Redis with TTLs — never in Postgres."""

import hashlib
import hmac
import json
import uuid

import redis.asyncio as aioredis

from app.config import get_settings


def new_session_id() -> str:
    return uuid.uuid4().hex


def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


def _otp_key(session_id: str) -> str:
    return f"otp:{session_id}"


def _otp_attempts_key(session_id: str) -> str:
    return f"otp_attempts:{session_id}"


def _aadhaar_txn_key(session_id: str) -> str:
    return f"aadhaar_txn:{session_id}"


def aadhaar_hash(aadhaar_number: str) -> str:
    return hashlib.sha256(f"aadhaar:{aadhaar_number}".encode()).hexdigest()


def _otp_hash(session_id: str, code: str) -> str:
    return hashlib.sha256(f"{session_id}:{code}".encode()).hexdigest()


async def create_session(r: aioredis.Redis, language: str) -> dict:
    settings = get_settings()
    data = {
        "session_id": new_session_id(),
        "state": "CREATED",
        "language": language,
        "consent_id": None,
        "appraisal_id": None,
    }
    await r.set(
        _session_key(data["session_id"]),
        json.dumps(data),
        ex=settings.session_ttl_seconds,
    )
    return data


async def get_session(r: aioredis.Redis, session_id: str) -> dict | None:
    raw = await r.get(_session_key(session_id))
    return json.loads(raw) if raw else None


async def save_session(r: aioredis.Redis, data: dict) -> None:
    settings = get_settings()
    await r.set(
        _session_key(data["session_id"]),
        json.dumps(data),
        ex=settings.session_ttl_seconds,
    )


async def set_state(r: aioredis.Redis, data: dict, to: str) -> dict:
    data["state"] = to
    await save_session(r, data)
    return data


class StateError(Exception):
    def __init__(self, current: str, allowed: tuple[str, ...]):
        self.current = current
        self.allowed = allowed
        super().__init__(f"session state {current} not in {allowed}")


def require_state(data: dict, *allowed: str) -> None:
    if data["state"] not in allowed:
        raise StateError(data["state"], allowed)


async def store_otp(r: aioredis.Redis, session_id: str, code: str) -> None:
    """Store only the OTP hash (never plaintext); reset the attempts counter."""
    settings = get_settings()
    await r.set(_otp_key(session_id), _otp_hash(session_id, code), ex=settings.otp_ttl_seconds)
    await r.set(_otp_attempts_key(session_id), 0, ex=settings.otp_ttl_seconds)


async def verify_otp(r: aioredis.Redis, session_id: str, code: str) -> bool:
    settings = get_settings()
    attempts = await r.get(_otp_attempts_key(session_id))
    if attempts is not None and int(attempts) >= settings.otp_max_attempts:
        return False
    stored = await r.get(_otp_key(session_id))
    if stored is None:
        return False
    if not hmac.compare_digest(stored, _otp_hash(session_id, code)):
        await r.incr(_otp_attempts_key(session_id))
        return False
    await r.delete(_otp_key(session_id))
    await r.delete(_otp_attempts_key(session_id))
    return True


async def store_aadhaar_txn(
    r: aioredis.Redis,
    session_id: str,
    *,
    txn_id: str,
    aadhaar_number: str,
    masked_aadhaar: str,
    masked_mobile: str,
) -> None:
    """Bind a UIDAI txn to the session; store only hash + masked refs."""
    settings = get_settings()
    payload = json.dumps(
        {
            "txn_id": txn_id,
            "aadhaar_hash": aadhaar_hash(aadhaar_number),
            "masked_aadhaar": masked_aadhaar,
            "masked_mobile": masked_mobile,
        }
    )
    await r.set(_aadhaar_txn_key(session_id), payload, ex=settings.otp_ttl_seconds)


async def get_aadhaar_txn(r: aioredis.Redis, session_id: str) -> dict | None:
    raw = await r.get(_aadhaar_txn_key(session_id))
    return json.loads(raw) if raw else None


async def clear_aadhaar_txn(r: aioredis.Redis, session_id: str) -> None:
    await r.delete(_aadhaar_txn_key(session_id))
