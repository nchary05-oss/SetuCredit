"""Adapter registry: stubs by default, live ULI only when flagged + configured.

Set ULI_MODE=live AND provide ULI_CLIENT_ID / ULI_CLIENT_SECRET (plus
ULI_BASE_URL) to route the "uli" source through UliApiAdapter. Every other
combination keeps the deterministic stub so dev, CI, and tests work with no
credentials.
"""

from app.config import get_settings
from app.dpi import stubs
from app.dpi.uli import UliApiAdapter


def uli_live_configured() -> bool:
    settings = get_settings()
    return bool(
        settings.uli_mode == "live"
        and settings.uli_client_id
        and settings.uli_client_secret
        and settings.uli_base_url
    )


def get_adapters() -> list:
    adapters = list(stubs.ALL_ADAPTERS)
    if uli_live_configured():
        adapters = [a for a in adapters if a.source_id != "uli"]
        adapters.append(UliApiAdapter())
    return adapters
