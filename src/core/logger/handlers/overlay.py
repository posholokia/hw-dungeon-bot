import logging
from collections.abc import Callable

from widgets.log_overlay import LogOverlayWindow

_Level = int | str


__all__ = ("OverlayHandler",)


class OverlayHandler(logging.Handler):
    def __init__(
        self, overlay: Callable[[], LogOverlayWindow], level: _Level = 0
    ) -> None:
        super().__init__(level)
        self._overlay_factory = overlay

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            overlay = self._overlay_factory()
            overlay.append(message)
        except Exception:  # noqa: BLE001
            self.handleError(record)
