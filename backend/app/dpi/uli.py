"""Live RBI ULI adapter (scaffold).

Implements DPIAdapter against the RBIH ULI gateway. Finalize the exact
token path, API path, and HMAC header scheme from the developer portal
(https://am.nonprod.rbihub.io/devportal) for each subscribed API — the
integration points are marked TODO(ULI) below.

Stubs remain the default: this adapter is only constructed by
app.dpi.registry when ULI_MODE=live AND credentials are configured.
"""

import hashlib
import hmac
import json
import time

import httpx

from app.config import get_settings
from app.dpi.base import SourceResult


class UliApiAdapter:
    """Lending-history source backed by the live RBI ULI gateway."""

    source_id = "uli"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    def _client_for(self, settings) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        cert = None
        if settings.uli_mtls_cert:
            cert = (settings.uli_mtls_cert, settings.uli_mtls_key or settings.uli_mtls_cert)
        return httpx.AsyncClient(base_url=settings.uli_base_url, cert=cert, timeout=10.0)

    async def _token(self, client: httpx.AsyncClient, settings) -> str:
        # TODO(ULI): confirm the token path/grant from the RBIH auth service
        # docs for your subscription (non-prod: https://auth.nonprod.rbihub.io/).
        resp = await client.post(
            settings.uli_token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.uli_client_id,
                "client_secret": settings.uli_client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _signature(self, body: bytes, settings) -> str:
        # TODO(ULI): confirm the HMAC header scheme in the RBIH
        # "HMAC request signing" guide (canonical string + header names).
        return hmac.new(
            (settings.uli_client_secret or "").encode(), body, hashlib.sha256
        ).hexdigest()

    async def fetch(self, session_id: str) -> SourceResult:
        settings = get_settings()
        client = self._client_for(settings)
        close = self._client is None
        try:
            token = await self._token(client, settings)
            # TODO(ULI): replace the path with the subscribed lending-history
            # API path from docs.rbihub.in; consent_ref carries the borrower's
            # DPDP consent proof for this pull.
            body = json.dumps({"session_ref": session_id, "consent_ref": session_id}).encode()
            resp = await client.post(
                "/uli/lending-history",
                content=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-Request-Ts": str(int(time.time())),
                    "X-Signature": self._signature(body, settings),
                },
            )
            resp.raise_for_status()
            data = resp.json()
            payload = {
                "existing_loans": int(data.get("existing_loans", 0)),
                "repayment_regular_months": int(data.get("repayment_regular_months", 0)),
                "delinquencies_12m": int(data.get("delinquencies_12m", 0)),
            }
            count = int(data.get("record_count", 1))
            return SourceResult(self.source_id, True, payload, None, count)
        finally:
            if close:
                await client.aclose()
