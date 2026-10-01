"""Session + OTP state lives in Redis with TTLs — never in Postgres."""

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
    settings = get_settings()
    await r.set(_otp_key(session_id), code, ex=settings.otp_ttl_seconds)


async def verify_otp(r: aioredis.Redis, session_id: str, code: str) -> bool:
    stored = await r.get(_otp_key(session_id))
    if stored is None or stored != code:
        return False
    await r.delete(_otp_key(session_id))
    return True
