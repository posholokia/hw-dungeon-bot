import logging
from collections.abc import Callable, MutableMapping
from typing import Any

from widgets.log_overlay import LogOverlayWindow

__all__ = ("OverlayProcessor",)


class OverlayProcessor:
    def __init__(self, overlay: Callable[[], LogOverlayWindow]) -> None:
        self._overlay_factory = overlay

    def __call__(
        self,
        logger: logging.Logger,
        method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        overlay = self._overlay_factory()
        overlay.append(event_dict["event"])
        return event_dict
