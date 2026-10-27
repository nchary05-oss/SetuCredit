"""In-process BRI scoring engine fallback for cold-start host resiliency."""

SOURCES = ("land", "discom", "aa", "uli", "bbps")
MODEL_VERSION = "bri-heuristic-0.1.0"
WEIGHTS = {"land": 0.20, "discom": 0.20, "aa": 0.25, "uli": 0.15, "bbps": 0.20}
LOAN_BANDS = (
    (80, (100_000, 500_000)),
    (60, (50_000, 200_000)),
    (40, (25_000, 75_000)),
)


def suggest_loan(bri: int) -> dict[str, int] | None:
    for floor, (low, high) in LOAN_BANDS:
        if bri >= floor:
            return {"min_inr": low, "max_inr": high}
    return None


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _component(source: str, f: dict[str, float]) -> float:
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
    if source == "bbps":
        return _clamp(
            0.50 * f["bbps_recharge_consistency"]
            + 0.30 * (f["bbps_months_recharged"] / 24.0)
            + 0.20 * f["bbps_recharge_level"]
        )
    return 0.0


def extract(payloads: dict[str, dict]) -> tuple[dict[str, float], dict[str, bool]]:
    coverage = {s: s in payloads for s in SOURCES}
    features: dict[str, float] = {f"{s}_present": 1.0 if coverage[s] else 0.0 for s in SOURCES}

    if coverage["land"]:
        p = payloads["land"]
        features["land_area_acres"] = float(p.get("area_acres", 0.0))
        features["land_ownership_clear"] = 1.0 if p.get("ownership") == "clear" else 0.0
        features["land_years_held"] = float(p.get("years_held", 0))

    if coverage["discom"]:
        p = payloads["discom"]
        features["utility_on_time_ratio"] = float(p.get("on_time_ratio", 0.0))
        features["utility_months_paid"] = float(min(int(p.get("months_paid", 0)), 24))
        features["utility_bill_level"] = min(
            float(p.get("avg_monthly_bill_inr", 0.0)) / 3000.0, 1.0
        )

    if coverage["aa"]:
        p = payloads["aa"]
        features["bank_balance_level"] = min(float(p.get("avg_balance_inr", 0.0)) / 50000.0, 1.0)
        features["bank_inflow_consistency"] = float(p.get("inflow_consistency", 0.0))
        features["bank_months_active"] = min(float(p.get("months_active", 0)), 60.0)
        features["bank_emi_ratio"] = float(p.get("existing_emi_ratio", 0.0))

    if coverage["uli"]:
        p = payloads["uli"]
        features["credit_existing_loans"] = float(p.get("existing_loans", 0))
        features["credit_repayment_regular_months"] = min(
            float(p.get("repayment_regular_months", 0)), 36.0
        )
        features["credit_delinquencies"] = float(p.get("delinquencies_12m", 0))

    if coverage["bbps"]:
        p = payloads["bbps"]
        features["bbps_recharge_consistency"] = float(p.get("recharge_consistency", 0.0))
        features["bbps_months_recharged"] = float(min(int(p.get("months_recharged", 0)), 24))
        features["bbps_recharge_level"] = min(
            float(p.get("avg_monthly_recharge_inr", 0.0)) / 500.0, 1.0
        )

    return features, coverage


def compute_in_process(payloads: dict[str, dict]) -> dict:
    features, coverage = extract(payloads)
    present = [s for s in WEIGHTS if coverage.get(s)]
    if not present:
        bri, attributions = 0, {}
    else:
        attributions = {}
        points = 0.0
        for source in WEIGHTS:
            if coverage.get(source):
                contribution = 100.0 * WEIGHTS[source] * _component(source, features)
            else:
                contribution = 0.0
            attributions[source] = round(contribution, 1)
            points += contribution
        bri, attributions = int(round(points)), attributions

    max_points = {s: round(100.0 * WEIGHTS[s], 1) for s in WEIGHTS} if present else {}
    return {
        "bri": bri,
        "model_version": MODEL_VERSION,
        "features": features,
        "attributions": attributions,
        "max_points": max_points,
        "loan_range": suggest_loan(bri),
    }
