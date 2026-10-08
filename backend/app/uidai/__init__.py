"""UIDAI package: Aadhaar auth helpers (stub by default, ASA/AUA live swap-in)."""

from app.uidai.provider import get_provider, live_configured
from app.uidai.validation import (
    demo_mobile_for,
    mask_aadhaar,
    mask_mobile,
    validate_aadhaar,
)

__all__ = [
    "demo_mobile_for",
    "get_provider",
    "live_configured",
    "mask_aadhaar",
    "mask_mobile",
    "validate_aadhaar",
]
