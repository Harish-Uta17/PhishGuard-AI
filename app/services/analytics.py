from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Dict, List


def build_threat_statistics(history: List[Dict]) -> Dict:
    if not history:
        return {
            "total_predictions": 0,
            "phishing_count": 0,
            "legitimate_count": 0,
            "by_threat_level": {},
            "by_risk_category": {},
            "trend": [],
        }

    threat_counter = Counter(row.get("threat_level", "Unknown") for row in history)
    risk_counter = Counter(row.get("risk_category", "Unknown") for row in history)
    phishing_count = sum(1 for row in history if row.get("prediction") == "Phishing")
    legitimate_count = sum(1 for row in history if row.get("prediction") == "Legitimate")

    trend = []
    for row in history[-50:]:
        timestamp = row.get("timestamp")
        try:
            parsed = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            trend.append(
                {
                    "timestamp": parsed.isoformat(),
                    "prediction": row.get("prediction", "Unknown"),
                    "confidence_score": float(row.get("confidence_score", 0)),
                }
            )
        except Exception:
            continue

    return {
        "total_predictions": len(history),
        "phishing_count": phishing_count,
        "legitimate_count": legitimate_count,
        "by_threat_level": dict(threat_counter),
        "by_risk_category": dict(risk_counter),
        "trend": trend,
    }
