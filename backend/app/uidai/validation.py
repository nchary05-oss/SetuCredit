"""Aadhaar number validation + masking helpers.

UIDAI uses the Verhoeff checksum for Aadhaar numbers. This module implements
it so the demo accepts only well-formed numbers (plus explicit demo overrides),
without ever persisting the full number.
"""

import hashlib

# Verhoeff tables (standard).
_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 7, 2, 5),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)
_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)

# UIDAI staging/demo numbers that bypass the checksum so the hackathon
# demo works without a real card. Never real numbers.
DEMO_BYPASS_NUMBERS = frozenset({"999999990019", "999999980024"})


def _verhoeff_check(number: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(number)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c == 0


def validate_aadhaar(number: str) -> bool:
    """True for a well-formed 12-digit Aadhaar number.

    Rules: 12 digits, first digit 2-9 (UIDAI reserves 0/1), Verhoeff checksum.
    Known demo numbers bypass the checksum.
    """
    if not number or len(number) != 12 or not number.isdigit():
        return False
    if number[0] not in "23456789":
        return False
    if number in DEMO_BYPASS_NUMBERS:
        return True
    return _verhoeff_check(number)


def mask_aadhaar(number: str) -> str:
    """Mask for display/audit: ``XXXXXXXX1234``. Never log the full number."""
    return f"XXXXXXXX{number[-4:]}" if len(number) == 12 else "XXXXXXXXXXXX"


def demo_mobile_for(aadhaar_number: str) -> str:
    """Deterministic demo stand-in for the UIDAI-registered mobile's last digits.

    Real UIDAI reveals only the masked registered mobile; the stub derives a
    stable pseudo-mobile from the Aadhaar hash so each demo number maps to a
    stable hint. Clearly demo-only.
    """

    digest = hashlib.sha256(f"uidai-demo-mobile:{aadhaar_number}".encode()).hexdigest()
    pseudo = f"{int(digest[:8], 16) % 10_000_000_000:010d}"
    return pseudo


def mask_mobile(mobile: str) -> str:
    """Mask a 10-digit mobile: ``••••••1234``."""
    return f"••••••{mobile[-4:]}" if len(mobile) == 10 else "••••••••••"
