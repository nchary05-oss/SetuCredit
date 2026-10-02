"""OTP delivery providers: stub by default, live SMS only when flagged + configured.

Set OTP_MODE=sms AND provide SMS_API_KEY / SMS_BASE_URL (+ sender/DLT
template for India) to send real texts via SmsOtpProvider. Every other
combination keeps StubOtpProvider so dev, CI, and tests work offline.

India note: transactional SMS requires DLT registration — sender ID and
template ID below map to your DLT-approved header/content.
"""

import httpx

from app.config import get_settings


class StubOtpProvider:
    """No-op sender. The dev_otp response field covers the demo path."""

    async def send(self, *, session_id: str, code: str, mobile: str | None) -> None:
        return None


class SmsOtpProvider:
    """Live SMS sender. Finalize path/payload against your gateway + DLT template."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def send(self, *, session_id: str, code: str, mobile: str | None) -> None:
        if not mobile:
            raise RuntimeError("mobile number required for SMS OTP delivery")
        settings = get_settings()
        client = self._client or httpx.AsyncClient(timeout=10.0)
        close = self._client is None
        try:
            # TODO(SMS): match your gateway's send API + DLT template vars.
            resp = await client.post(
                settings.sms_base_url,
                json={
                    "to": mobile,
                    "from": settings.sms_sender_id,
                    "template_id": settings.sms_template_id,
                    "message": f"Your SetuCredit OTP is {code}. Valid for 5 minutes.",
                    "session_ref": session_id,
                },
                headers={"Authorization": f"Bearer {settings.sms_api_key}"},
            )
            resp.raise_for_status()
        finally:
            if close:
                await client.aclose()


def sms_configured() -> bool:
    settings = get_settings()
    return bool(settings.otp_mode == "sms" and settings.sms_api_key and settings.sms_base_url)


def get_provider():
    if sms_configured():
        return SmsOtpProvider()
    return StubOtpProvider()
