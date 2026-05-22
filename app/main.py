from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_app_logging
from app.core.middleware import RequestContextMiddleware


settings = get_settings()
logger = configure_app_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "docExpansion": "list",
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": -1,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.include_router(api_router, prefix=settings.api_prefix)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed.",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "message": "Internal server error.",
        },
    )


@app.get("/")
async def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
