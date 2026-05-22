from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path
from threading import Lock
from typing import Dict, List

from app.core.config import get_settings


class PredictionStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.path = Path(self.settings.history_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def append(self, record: Dict) -> None:
        payload = dict(record)
        payload.setdefault("timestamp", datetime.utcnow().isoformat())
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, default=str) + "\n")

    def load(self, limit: int | None = None) -> List[Dict]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]

        return rows[-limit:] if limit else rows

    def summary(self, limit: int = 100) -> Dict:
        rows = self.load(limit=limit)
        threat_counter = Counter(row.get("threat_level", "Unknown") for row in rows)
        risk_counter = Counter(row.get("risk_category", "Unknown") for row in rows)
        phishing_count = sum(1 for row in rows if row.get("prediction") == "Phishing")
        legitimate_count = sum(1 for row in rows if row.get("prediction") == "Legitimate")
        avg_confidence = round(
            sum(float(row.get("confidence_score", 0)) for row in rows) / len(rows), 4
        ) if rows else 0.0
        return {
            "total_predictions": len(rows),
            "phishing_count": phishing_count,
            "legitimate_count": legitimate_count,
            "average_confidence": avg_confidence,
            "by_threat_level": dict(threat_counter),
            "by_risk_category": dict(risk_counter),
            "recent_predictions": rows[-10:],
        }


prediction_store = PredictionStore()
