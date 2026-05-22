from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import configure_app_logging


logger = configure_app_logging()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.upload_limit_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": "Payload too large for the configured upload limit."},
            )

        start_time = perf_counter()
        response = await call_next(request)
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        logger.info(
            "%s %s -> %s in %sms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Process-Time-ms"] = str(duration_ms)
        return response
