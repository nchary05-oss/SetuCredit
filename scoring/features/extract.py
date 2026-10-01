"""Feature extraction from in-memory DPI payloads (features only, never records)."""

SOURCES = ("land", "discom", "aa", "uli")


def extract(payloads: dict[str, dict]) -> tuple[dict[str, float], dict[str, bool]]:
    """Return (features, coverage). Missing sources are flagged, not fatal."""
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

    return features, coverage
