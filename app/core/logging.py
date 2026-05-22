import logging
from pathlib import Path

from app.core.config import get_settings


def configure_app_logging() -> logging.Logger:
    settings = get_settings()
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("networksecurity.app")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(Path(settings.logs_dir) / "api.log", encoding="utf-8")
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s %(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
