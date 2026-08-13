import logging

import structlog

from core.logger.processors.overlay import OverlayProcessor


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
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
    )
