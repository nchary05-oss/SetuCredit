"""Application settings loaded from environment (see .env.example)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

KNOWN_SOURCES = ("land", "discom", "aa", "uli")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str = "postgresql+asyncpg://setucredit:setucredit@localhost:5432/setucredit"
    redis_url: str = "redis://localhost:6379/0"
    scoring_service_url: str = "http://localhost:8001"
    partner_webhook_url: str | None = None
    webhook_secret: str = "dev-webhook-secret"

    session_ttl_seconds: int = 3600
    otp_ttl_seconds: int = 300
    consent_ttl_seconds: int = 900
    dpi_timeout_seconds: float = 5.0

    # RBI ULI gateway. "stub" (default) uses deterministic in-process
    # adapters; "live" + credentials routes "uli" via UliApiAdapter
    # (see app/dpi/registry.py). Non-prod gateway/token defaults below.
    uli_mode: str = "stub"
    uli_base_url: str = "https://extgw.nonprod.rbihub.io"
    uli_token_url: str = "https://auth.nonprod.rbihub.io/oauth/token"
    uli_client_id: str | None = None
    uli_client_secret: str | None = None
    uli_mtls_cert: str | None = None
    uli_mtls_key: str | None = None

    # OTP delivery. "stub" (default) is a no-op sender; "sms" + credentials
    # routes sends via SmsOtpProvider (see app/otp/provider.py).
    otp_mode: str = "stub"
    otp_max_attempts: int = 5
    sms_base_url: str | None = None
    sms_api_key: str | None = None
    sms_sender_id: str | None = None
    sms_template_id: str | None = None

    # UIDAI OTP Auth via licensed ASA/AUA. "stub" (default) simulates the
    # txnId + registered-mobile flow in-process (see app/uidai/provider.py);
    # "live" + credentials routes OTP requests via LiveAsaAuaProvider.
    uidai_mode: str = "stub"
    uidai_base_url: str | None = None
    uidai_aua_code: str | None = None
    uidai_asa_license_key: str | None = None
    uidai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
