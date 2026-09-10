import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import structlog

from configs.settings import debug
from core.logger.handlers.overlay import OverlayHandler


def setup_logging(
    overlay_handler: OverlayHandler,
    level: int = logging.DEBUG,
) -> None:
    log_path = Path("logs/bot.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler: logging.Handler = RotatingFileHandler(
        log_path,
        encoding="utf-8",
        maxBytes=10 * 1024 * 1024,  # 10 МБ на файл
        backupCount=5,   
    )
    stream_handler: logging.Handler = logging.StreamHandler()
    handlers = [file_handler, stream_handler]

    if debug():
        handlers.append(overlay_handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    plain_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(colors=False),
        ],
    )
    for handler in handlers:
        handler.setFormatter(plain_formatter)

    logging.basicConfig(
        handlers=handlers,
        level=level,
        force=True,
    )
