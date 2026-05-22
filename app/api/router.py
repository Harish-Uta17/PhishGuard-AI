from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.model import router as model_router
from app.api.routes.predictions import router as prediction_router
from app.api.routes.stats import router as stats_router


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(model_router, tags=["model"])
api_router.include_router(prediction_router, tags=["predictions"])
api_router.include_router(stats_router, tags=["analytics"])
