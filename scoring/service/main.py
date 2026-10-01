"""Thin inference API: in-memory payloads -> BRI. Stateless, no borrower store."""

from fastapi import FastAPI
from features.extract import extract
from model.bri import MODEL_VERSION, score
from pydantic import BaseModel

app = FastAPI(title="SetuCredit Scoring", version=MODEL_VERSION)


class ScoreRequest(BaseModel):
    payloads: dict[str, dict]


class ScoreResponse(BaseModel):
    bri: int
    model_version: str
    features: dict[str, float]
    attributions: dict[str, float]


@app.post("/score", response_model=ScoreResponse)
def compute_score(request: ScoreRequest) -> ScoreResponse:
    features, coverage = extract(request.payloads)
    bri, attributions = score(features, coverage)
    return ScoreResponse(
        bri=bri,
        model_version=MODEL_VERSION,
        features=features,
        attributions=attributions,
    )


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "model_version": MODEL_VERSION}
