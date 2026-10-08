"""UIDAI Aadhaar validation: Verhoeff checksum, masking, demo overrides."""

from app.uidai.validation import (
    demo_mobile_for,
    mask_aadhaar,
    mask_mobile,
    validate_aadhaar,
)


def test_demo_numbers_accepted():
    assert validate_aadhaar("999999990019")
    assert validate_aadhaar("999999980024")


def test_rejects_bad_format():
    assert not validate_aadhaar("")
    assert not validate_aadhaar("123")  # too short
    assert not validate_aadhaar("123456789012")  # bad first digit + checksum
    assert not validate_aadhaar("023456789012")  # leading 0 reserved
    assert not validate_aadhaar("abcdefghijkl")  # non-digits


def test_masking_never_leaks():
    assert mask_aadhaar("999999990019") == "XXXXXXXX0019"
    assert mask_mobile("9876543210") == "••••••3210"


def test_demo_mobile_stable_per_aadhaar():
    assert demo_mobile_for("999999990019") == demo_mobile_for("999999990019")
    assert demo_mobile_for("999999990019") != demo_mobile_for("999999980024")
