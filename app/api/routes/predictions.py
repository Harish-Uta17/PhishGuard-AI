from __future__ import annotations

import io
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.schemas.prediction import BatchPredictionResponse, BatchPredictionSummary, PredictionRecord, PredictionRequest
from app.services.model_service import model_service
from app.services.prediction_store import prediction_store


router = APIRouter()


def _persist_prediction_records(records: list[dict]) -> None:
    for record in records:
        prediction_store.append(record)


@router.post("/predict", response_model=PredictionRecord)
async def predict(request: PredictionRequest) -> PredictionRecord:
    try:
        prediction = await run_in_threadpool(
            model_service.predict,
            request.url,
            request.features,
            "api",
        )
        prediction_store.append(prediction)
        return PredictionRecord(**prediction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(file: UploadFile = File(...)) -> BatchPredictionResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    payload = await file.read()
    dataframe = pd.read_csv(io.BytesIO(payload))
    predictions_df = await run_in_threadpool(model_service.predict_dataframe, dataframe, "batch")
    records = predictions_df.to_dict(orient="records")
    _persist_prediction_records(records)

    summary = BatchPredictionSummary(
        total=len(records),
        phishing_count=sum(1 for record in records if record["prediction"] == "Phishing"),
        legitimate_count=sum(1 for record in records if record["prediction"] == "Legitimate"),
        average_confidence=round(
            sum(float(record["confidence_score"]) for record in records) / len(records),
            4,
        ) if records else 0.0,
    )
    return BatchPredictionResponse(
        summary=summary,
        results=[PredictionRecord(**record) for record in records],
    )


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    settings = get_settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    file_id = uuid4().hex
    destination = Path(settings.uploads_dir) / f"{file_id}_{Path(file.filename).name}"
    content = await file.read()
    destination.write_bytes(content)
    preview = pd.read_csv(io.BytesIO(content)).head(5).to_dict(orient="records")
    return {
        "file_id": file_id,
        "filename": file.filename,
        "stored_path": str(destination),
        "preview": preview,
    }
