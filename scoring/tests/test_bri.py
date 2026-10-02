from features.extract import extract
from model.bri import MODEL_VERSION, WEIGHTS, score, suggest_loan


def _full_payloads() -> dict[str, dict]:
    return {
        "land": {"area_acres": 3.2, "ownership": "clear", "years_held": 12},
        "discom": {"on_time_ratio": 0.9, "months_paid": 18, "avg_monthly_bill_inr": 900},
        "aa": {
            "avg_balance_inr": 25000,
            "inflow_consistency": 0.8,
            "months_active": 36,
            "existing_emi_ratio": 0.2,
        },
        "uli": {"existing_loans": 1, "repayment_regular_months": 24, "delinquencies_12m": 0},
    }


def test_bri_in_bounds_for_full_payloads():
    features, coverage = extract(_full_payloads())
    bri, attributions = score(features, coverage)
    assert 0 <= bri <= 100
    assert set(attributions) == set(WEIGHTS)
    assert abs(sum(attributions.values()) - bri) <= 1.0


def test_empty_payloads_score_zero():
    features, coverage = extract({})
    bri, attributions = score(features, coverage)
    assert bri == 0
    assert attributions == {}


def test_partial_coverage_renormalizes():
    payloads = _full_payloads()
    del payloads["discom"]
    del payloads["aa"]
    del payloads["uli"]
    features, coverage = extract(payloads)
    bri, attributions = score(features, coverage)
    assert set(attributions) == {"land"}
    assert 0 <= bri <= 100


def test_missing_feature_keys_do_not_crash():
    features, coverage = extract({"land": {}, "uli": {}})
    bri, _ = score(features, coverage)
    assert 0 <= bri <= 100


def test_model_version_exported():
    assert MODEL_VERSION.startswith("bri-")


def test_suggest_loan_bands():
    assert suggest_loan(85) == {"min_inr": 100_000, "max_inr": 500_000}
    assert suggest_loan(80) == {"min_inr": 100_000, "max_inr": 500_000}
    assert suggest_loan(60) == {"min_inr": 50_000, "max_inr": 200_000}
    assert suggest_loan(40) == {"min_inr": 25_000, "max_inr": 75_000}
    assert suggest_loan(39) is None
    assert suggest_loan(0) is None
