"""Fixtures: integration tests need live Postgres + Redis; scoring runs in-process."""

import os
import socket
import threading
import time
from urllib.parse import urlsplit

import httpx
import pytest
from app.config import get_settings
from sqlalchemy.engine import make_url


def _reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def live_infra() -> None:
    settings = get_settings()
    redis_url = urlsplit(settings.redis_url)
    pg = make_url(settings.database_url)
    missing = [
        name
        for name, host, port in (
            ("redis", redis_url.hostname or "localhost", redis_url.port or 6379),
            ("postgres", pg.host or "localhost", pg.port or 5432),
        )
        if not _reachable(host, port)
    ]
    if missing:
        pytest.skip(
            f"missing infra: {', '.join(missing)} — run: "
            "docker compose -f infra/docker-compose.yml up -d postgres redis"
        )


@pytest.fixture(scope="session")
def scoring_url(live_infra: None) -> str:
    """Run the scoring service in a background uvicorn thread on a free port."""
    import uvicorn
    from service.main import app as scoring_app

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = uvicorn.Server(
        uvicorn.Config(scoring_app, host="127.0.0.1", port=port, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if _reachable("127.0.0.1", port):
            break
        time.sleep(0.1)
    else:
        pytest.fail("scoring server did not become reachable")

    os.environ["SCORING_SERVICE_URL"] = f"http://127.0.0.1:{port}"
    get_settings.cache_clear()
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)
    os.environ.pop("SCORING_SERVICE_URL", None)
    get_settings.cache_clear()


@pytest.fixture
async def client(live_infra: None, scoring_url: str):
    from app.db import Base, engine
    from app.main import app as api_app

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = httpx.ASGITransport(app=api_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
