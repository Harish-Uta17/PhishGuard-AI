"""Reusable helpers for batch prediction workflows.

The production API uses app.services.model_service directly, but this module is
retained for compatibility with the original package layout and can be reused
by notebooks or scripts that want to run offline batch inference.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.services.model_service import model_service


class BatchPredictionPipeline:
	def __init__(self, model_service_instance=model_service) -> None:
		self.model_service = model_service_instance

	def predict_file(self, file_path: str | Path) -> pd.DataFrame:
		dataframe = pd.read_csv(file_path)
		return self.model_service.predict_dataframe(dataframe, source="offline-batch")

	def predict_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		return self.model_service.predict_dataframe(dataframe, source="offline-batch")

