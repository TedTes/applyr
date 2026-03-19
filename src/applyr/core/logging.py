import logging

from applyr.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger(name)
