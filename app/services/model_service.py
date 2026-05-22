from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from app.core.config import get_settings
from app.core.logging import configure_app_logging
from app.services.feature_engineering import feature_frame_columns, normalize_feature_payload
from app.services.threat_scoring import threat_profile
from networksecurity.utils.main_utils.utils import load_numpy_array_data, load_object


logger = configure_app_logging()


@dataclass
class ModelSnapshot:
    model: object | None
    preprocessor: object | None
    metrics: Dict[str, float]
    latest_artifact_dir: str | None
    feature_names: List[str]


class ModelService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._snapshot = self._load_snapshot()

    def _latest_artifact_dir(self) -> Path | None:
        if not self.settings.artifacts_dir.exists():
            return None
        runs = [path for path in self.settings.artifacts_dir.iterdir() if path.is_dir()]
        return sorted(runs)[-1] if runs else None

    def _load_snapshot(self) -> ModelSnapshot:
        model = None
        preprocessor = None
        metrics: Dict[str, float] = {}
        feature_names = feature_frame_columns()
        latest_artifact_dir = self._latest_artifact_dir()

        try:
            if self.settings.preprocessor_path.exists():
                preprocessor = load_object(str(self.settings.preprocessor_path))
            if self.settings.model_path.exists():
                model = load_object(str(self.settings.model_path))
        except Exception as exc:
            logger.warning("Failed to load model artifacts: %s", exc)

        if latest_artifact_dir:
            test_path = latest_artifact_dir / "data_transformation" / "transformed" / "test.npy"
            if test_path.exists() and model is not None and preprocessor is not None:
                try:
                    test_arr = load_numpy_array_data(str(test_path))
                    x_test, y_test = test_arr[:, :-1], test_arr[:, -1]
                    x_test_df = pd.DataFrame(x_test, columns=feature_names)
                    x_transformed = preprocessor.transform(x_test_df)
                    predictions = model.predict(x_transformed)
                    metrics = {
                        "accuracy": float(accuracy_score(y_test, predictions)),
                        "precision": float(precision_score(y_test, predictions, zero_division=0)),
                        "recall": float(recall_score(y_test, predictions, zero_division=0)),
                        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
                    }
                    try:
                        if hasattr(model, "predict_proba"):
                            probabilities = model.predict_proba(x_transformed)
                            metrics["roc_auc"] = float(roc_auc_score(y_test, probabilities[:, 1]))
                    except Exception:
                        pass
                    tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
                    metrics.update(
                        {
                            "true_negative": float(tn),
                            "false_positive": float(fp),
                            "false_negative": float(fn),
                            "true_positive": float(tp),
                        }
                    )
                except Exception as exc:
                    logger.warning("Failed to compute model metrics: %s", exc)

        return ModelSnapshot(
            model=model,
            preprocessor=preprocessor,
            metrics=metrics,
            latest_artifact_dir=str(latest_artifact_dir) if latest_artifact_dir else None,
            feature_names=feature_names,
        )

    @property
    def is_ready(self) -> bool:
        return self._snapshot.model is not None and self._snapshot.preprocessor is not None

    def _build_frame(self, url: str | None, features: Dict[str, float] | None) -> pd.DataFrame:
        payload = normalize_feature_payload(url=url, features=features)
        return pd.DataFrame([payload.features], columns=self._snapshot.feature_names)

    def _predict_probability(self, transformed_frame) -> np.ndarray:
        estimator = self._snapshot.model
        if estimator is not None and hasattr(estimator, "predict_proba"):
            probabilities = estimator.predict_proba(transformed_frame)
            if probabilities.ndim == 1:
                return np.stack([1 - probabilities, probabilities], axis=1)
            return probabilities
        if estimator is not None and hasattr(estimator, "decision_function"):
            scores = estimator.decision_function(transformed_frame)
            normalized = 1 / (1 + np.exp(-np.asarray(scores)))
            if normalized.ndim == 1:
                return np.stack([1 - normalized, normalized], axis=1)
            return normalized
        return np.full((len(transformed_frame), 2), 0.5)

    def predict(self, url: str | None = None, features: Dict[str, float] | None = None, source: str = "api") -> Dict:
        if not self.is_ready:
            raise RuntimeError("Model artifacts are not available. Train the model before predicting.")

        input_frame = self._build_frame(url=url, features=features)
        transformed_frame = self._snapshot.preprocessor.transform(input_frame)
        predictions = self._snapshot.model.predict(transformed_frame)
        probabilities = self._predict_probability(transformed_frame)

        predicted_label = int(predictions[0])
        confidence = float(probabilities[0][predicted_label])
        threat_level, risk_category, score = threat_profile(prediction=predicted_label, confidence=confidence)
        prediction_label = "Legitimate" if predicted_label == 1 else "Phishing"

        return {
            "url": url or "feature-input",
            "prediction": prediction_label,
            "confidence_score": round(confidence, 4),
            "threat_level": threat_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_category": risk_category,
            "score": round(float(score), 4),
            "source": source,
        }

    def predict_dataframe(self, dataframe: pd.DataFrame, source: str = "batch") -> pd.DataFrame:
        if dataframe.empty:
            return pd.DataFrame()

        feature_names = self._snapshot.feature_names
        lower_columns = [column.lower() for column in dataframe.columns]
        if "url" in lower_columns:
            url_column = next(column for column in dataframe.columns if column.lower() == "url")
            records = [self.predict(url=str(row[url_column]), source=source) for _, row in dataframe.iterrows()]
            return pd.DataFrame(records)

        input_frame = dataframe.reindex(columns=feature_names, fill_value=0)
        transformed_frame = self._snapshot.preprocessor.transform(input_frame)
        predictions = self._snapshot.model.predict(transformed_frame)
        probabilities = self._predict_probability(transformed_frame)

        records = []
        for position, (_, row) in enumerate(dataframe.iterrows()):
            predicted_label = int(predictions[position])
            confidence = float(probabilities[position][predicted_label])
            threat_level, risk_category, score = threat_profile(prediction=predicted_label, confidence=confidence)
            records.append(
                {
                    "url": str(row.get("url", row.get("URL", f"row-{position}"))),
                    "prediction": "Legitimate" if predicted_label == 1 else "Phishing",
                    "confidence_score": round(confidence, 4),
                    "threat_level": threat_level,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "risk_category": risk_category,
                    "score": round(float(score), 4),
                    "source": source,
                }
            )

        return pd.DataFrame(records)

    def get_model_info(self) -> Dict:
        snapshot = self._snapshot
        return {
            "model_name": snapshot.model.__class__.__name__ if snapshot.model else "Unavailable",
            "model_path": str(self.settings.model_path),
            "preprocessor_path": str(self.settings.preprocessor_path),
            "feature_count": len(snapshot.feature_names),
            "trained_artifact_dir": snapshot.latest_artifact_dir,
            "metrics": snapshot.metrics,
        }

    def get_health_snapshot(self) -> Dict:
        return {
            "status": "healthy" if self.is_ready else "degraded",
            "model_ready": self.is_ready,
            "metrics": self._snapshot.metrics,
        }


model_service = ModelService()
