"""Borrower Readiness Index (BRI, 0-100).

Heuristic v1 stand-in for the XGBoost model specified in the HLD: same
interface (features + coverage -> score + attributions), so the trained
model swaps in behind `score()` without touching callers.
"""

MODEL_VERSION = "bri-heuristic-0.1.0"

WEIGHTS = {"land": 0.25, "discom": 0.25, "aa": 0.30, "uli": 0.20}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _component(source: str, f: dict[str, float]) -> float:
    """Per-source subscore in [0, 1]."""
    if source == "land":
        return _clamp(
            0.50 * _clamp(f["land_area_acres"] / 5.0)
            + 0.30 * f["land_ownership_clear"]
            + 0.20 * _clamp(f["land_years_held"] / 20.0)
        )
    if source == "discom":
        return _clamp(
            0.60 * f["utility_on_time_ratio"]
            + 0.20 * (f["utility_months_paid"] / 24.0)
            + 0.20 * f["utility_bill_level"]
        )
    if source == "aa":
        return _clamp(
            0.40 * f["bank_balance_level"]
            + 0.40 * f["bank_inflow_consistency"]
            + 0.20 * _clamp(f["bank_months_active"] / 60.0)
            - 0.30 * _clamp(f["bank_emi_ratio"])
        )
    if source == "uli":
        return _clamp(
            0.50 * (1.0 - _clamp(f["credit_existing_loans"] / 4.0))
            + 0.30 * _clamp(f["credit_repayment_regular_months"] / 24.0)
            + 0.20 * (1.0 - _clamp(f["credit_delinquencies"] / 3.0))
        )
    return 0.0


def score(features: dict[str, float], coverage: dict[str, bool]) -> tuple[int, dict[str, float]]:
    """Compute BRI and per-source point attributions (renormalized over present sources)."""
    present = [s for s in WEIGHTS if coverage.get(s)]
    if not present:
        return 0, {}
    total_weight = sum(WEIGHTS[s] for s in present)

    attributions: dict[str, float] = {}
    points = 0.0
    for source in present:
        contribution = 100.0 * (WEIGHTS[source] / total_weight) * _component(source, features)
        attributions[source] = round(contribution, 1)
        points += contribution
    return int(round(points)), attributions
