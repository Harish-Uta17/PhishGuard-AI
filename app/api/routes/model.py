from fastapi import APIRouter

from app.schemas.prediction import ModelInfoResponse
from app.services.model_service import model_service


router = APIRouter()


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info() -> ModelInfoResponse:
    info = model_service.get_model_info()
    return ModelInfoResponse(**info)
