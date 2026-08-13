import logging
from typing import Any, MutableMapping

import structlog

from configs.settings import get_settings
from core.logger.processors.overlay import OverlayProcessor


def file_proc(
    self,
    logger: logging.Logger,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    try:
        settings = get_settings()
        with open(settings.titan_catalog_dir / "bot.log", "a") as f:
            f.write(event_dict["event"]) 
    except Exception:
        pass

    return event_dict



def setup_logging(
    overlay: OverlayProcessor,
    level: int = logging.DEBUG,
) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            overlay,
            file_proc,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
    )
