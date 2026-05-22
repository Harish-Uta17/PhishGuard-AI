from fastapi import APIRouter

from app.schemas.prediction import PredictionRecord, ThreatStatsResponse
from app.services.analytics import build_threat_statistics
from app.services.prediction_store import prediction_store


router = APIRouter()


@router.get("/threat-stats", response_model=ThreatStatsResponse)
async def threat_stats() -> ThreatStatsResponse:
    history = prediction_store.load(limit=500)
    payload = build_threat_statistics(history)
    return ThreatStatsResponse(
        total_predictions=payload["total_predictions"],
        phishing_count=payload["phishing_count"],
        legitimate_count=payload["legitimate_count"],
        by_threat_level=payload["by_threat_level"],
        by_risk_category=payload["by_risk_category"],
        recent_predictions=[PredictionRecord(**record) for record in history[-10:]],
    )
