import logging

from src.shared.config import get_settings

_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    if not _configured:
        settings = get_settings()
        logging.basicConfig(
            level=settings.log_level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        _configured = True
    return logging.getLogger(name)
