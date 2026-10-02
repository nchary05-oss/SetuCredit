"""Registry routing: stubs by default, live ULI only when flagged + configured."""

import httpx
import pytest
from app.config import get_settings
from app.dpi import registry, stubs
from app.dpi.uli import UliApiAdapter


@pytest.fixture
def clean_settings(monkeypatch):
    for var in (
        "ULI_MODE",
        "ULI_BASE_URL",
        "ULI_CLIENT_ID",
        "ULI_CLIENT_SECRET",
    ):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _by_id(adapters):
    return {a.source_id: a for a in adapters}


def test_default_is_all_stubs(clean_settings):
    assert isinstance(_by_id(registry.get_adapters())["uli"], stubs.ULIAdapter)


def test_live_mode_without_credentials_stays_stub(clean_settings, monkeypatch):
    monkeypatch.setenv("ULI_MODE", "live")
    get_settings.cache_clear()
    assert isinstance(_by_id(registry.get_adapters())["uli"], stubs.ULIAdapter)


def test_live_mode_with_credentials_uses_api_adapter(clean_settings, monkeypatch):
    monkeypatch.setenv("ULI_MODE", "live")
    monkeypatch.setenv("ULI_CLIENT_ID", "test-id")
    monkeypatch.setenv("ULI_CLIENT_SECRET", "test-secret")
    get_settings.cache_clear()
    assert isinstance(_by_id(registry.get_adapters())["uli"], UliApiAdapter)


async def test_live_adapter_maps_response_shape(clean_settings, monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("oauth/token"):
            return httpx.Response(200, json={"access_token": "tok"})
        return httpx.Response(
            200,
            json={
                "existing_loans": 1,
                "repayment_regular_months": 12,
                "delinquencies_12m": 0,
                "record_count": 3,
            },
        )

    monkeypatch.setenv("ULI_MODE", "live")
    monkeypatch.setenv("ULI_CLIENT_ID", "test-id")
    monkeypatch.setenv("ULI_CLIENT_SECRET", "test-secret")
    get_settings.cache_clear()
    adapter = UliApiAdapter(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://test")
    )

    result = await adapter.fetch("sess-1")
    assert result.ok and result.record_count == 3
    assert result.payload["repayment_regular_months"] == 12
    # Never leak raw gateway payloads beyond the mapped shape.
    assert set(result.payload) == {
        "existing_loans",
        "repayment_regular_months",
        "delinquencies_12m",
    }
