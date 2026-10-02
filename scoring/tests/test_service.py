"""Scoring service endpoint contract — the report payload depends on it."""

from fastapi.testclient import TestClient
from service.main import app

client = TestClient(app)

FULL_PAYLOADS = {
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


def test_full_payloads_report_fields():
    r = client.post("/score", json={"payloads": FULL_PAYLOADS})
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["bri"] <= 100
    assert set(body["attributions"]) == {"land", "discom", "aa", "uli"}
    assert abs(sum(body["max_points"].values()) - 100) <= 0.5
    assert abs(sum(body["attributions"].values()) - body["bri"]) <= 1.5
    assert "land_area_acres" in body["features"]
    assert body["model_version"].startswith("bri-")
    assert "loan_range" in body
    if body["bri"] >= 40:
        assert body["loan_range"]["min_inr"] <= body["loan_range"]["max_inr"]
    else:
        assert body["loan_range"] is None


def test_empty_payloads():
    r = client.post("/score", json={"payloads": {}})
    assert r.status_code == 200
    body = r.json()
    assert body["bri"] == 0
    assert body["attributions"] == {}
    assert body["max_points"] == {}
    assert body["loan_range"] is None
