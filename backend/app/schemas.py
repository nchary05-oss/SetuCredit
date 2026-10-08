"""Pydantic request/response models for the public API."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

# Session states (HLD flow + ARCHITECTURE.md state machine)
SESSION_STATES = (
    "CREATED",
    "IDENTITY_VERIFIED",
    "CONSENT_GRANTED",
    "PULLING",
    "SCORED",
    "HANDED_OFF",
)

NEXT_ACTION = {
    "CREATED": "otp",
    "IDENTITY_VERIFIED": "consent",
    "CONSENT_GRANTED": "appraise",
    "PULLING": "wait",
    "SCORED": "wait",
    "HANDED_OFF": "done",
}


class SessionCreate(BaseModel):
    language: str = Field(default="hi-IN", max_length=16)


class SessionView(BaseModel):
    session_id: str
    state: str
    language: str
    consent_id: str | None = None
    appraisal_id: str | None = None
    next_action: str


class OtpSend(BaseModel):
    action: Literal["send"]
    # 12-digit Aadhaar number + explicit resident consent for UIDAI OTP Auth.
    # The full number is never persisted (Redis hash + masked refs only).
    aadhaar_number: str = Field(min_length=12, max_length=12)
    consent: bool = False


class OtpVerify(BaseModel):
    action: Literal["verify"]
    otp: str = Field(min_length=6, max_length=6)


OtpRequest = Annotated[OtpSend | OtpVerify, Field(discriminator="action")]


class OtpResponse(BaseModel):
    sent: bool | None = None
    verified: bool | None = None
    dev_otp: str | None = None
    state: str | None = None
    # UIDAI OTP Auth references: transaction id + masked hints only.
    txn_id: str | None = None
    masked_mobile: str | None = None
    masked_aadhaar: str | None = None


class ConsentCreate(BaseModel):
    scope: list[str] = Field(default_factory=lambda: ["land", "discom", "aa", "uli"])


class ConsentView(BaseModel):
    consent_id: str
    session_id: str
    scope: list[str]
    status: str
    granted_at: str
    expires_at: str


class SourceStatus(BaseModel):
    status: Literal["ok", "failed"]
    error: str | None = None
    record_count: int = 0


class AppraiseResponse(BaseModel):
    appraisal_id: str
    state: str
    bri: int
    model_version: str
    sources: dict[str, SourceStatus]
    handoff: Literal["sent", "simulated", "failed"]
    features: dict[str, float]
    attributions: dict[str, float]
    max_points: dict[str, float]
    loan_range: dict[str, int] | None = None


class AppraisalView(BaseModel):
    appraisal_id: str
    session_id: str
    status: str
    bri: int
    model_version: str
    sources: dict[str, str]
    created_at: str
    disbursed_at: str | None = None


class HealthResponse(BaseModel):
    status: str
    postgres: str
    redis: str
