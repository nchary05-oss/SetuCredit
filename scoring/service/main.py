"""Thin inference API: in-memory payloads -> BRI. Stateless, no borrower store."""

from fastapi import FastAPI
from features.extract import extract
from model.bri import MODEL_VERSION, WEIGHTS, score, suggest_loan
from pydantic import BaseModel

app = FastAPI(title="SetuCredit Scoring", version=MODEL_VERSION)


class ScoreRequest(BaseModel):
    payloads: dict[str, dict]


class ScoreResponse(BaseModel):
    bri: int
    model_version: str
    features: dict[str, float]
    attributions: dict[str, float]
    max_points: dict[str, float]
    loan_range: dict[str, int] | None = None


@app.post("/score", response_model=ScoreResponse)
def compute_score(request: ScoreRequest) -> ScoreResponse:
    features, coverage = extract(request.payloads)
    bri, attributions = score(features, coverage)
    present = [s for s in WEIGHTS if coverage.get(s)]
    total_weight = sum(WEIGHTS[s] for s in present)
    max_points = (
        {s: round(100.0 * WEIGHTS[s] / total_weight, 1) for s in present} if total_weight else {}
    )
    return ScoreResponse(
        bri=bri,
        model_version=MODEL_VERSION,
        features=features,
        attributions=attributions,
        max_points=max_points,
        loan_range=suggest_loan(bri),
    )


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "model_version": MODEL_VERSION}
