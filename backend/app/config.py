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


@lru_cache
def get_settings() -> Settings:
    return Settings()
