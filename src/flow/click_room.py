from __future__ import annotations

import logging
import random
from collections.abc import Callable
from threading import Event

from exceptions import ApplicationError
from models.dto import ClickArea, RoomClickAreas, State


logger = logging.getLogger(__name__)


class ClickRoomStep:
    """Pick a random point inside the room click area and preview it (no real click)."""

    def __init__(
        self,
        click_areas: RoomClickAreas,
        show_click: Callable[[int, int], None],
        preview_seconds: float = 0.8,
    ) -> None:
        self._click_areas = click_areas
        self._show_click = show_click
        self._preview_seconds = preview_seconds

    def execute(self, state: State, stop_event: Event) -> None:
        if state.room_position is None:
            raise ApplicationError("Room position is unknown; run FindRoomStep first")

        area = self._click_areas[state.room_position]
        x, y = _random_point(area)
        logger.info(
            "Click preview at (%s, %s) in %s area",
            x,
            y,
            state.room_position,
        )
        self._show_click(x, y)
        stop_event.wait(self._preview_seconds)


def _random_point(area: ClickArea) -> tuple[int, int]:
    if area["width"] < 1 or area["height"] < 1:
        raise ApplicationError("Click area width/height must be >= 1")
    x = random.randint(area["x"], area["x"] + area["width"] - 1)
    y = random.randint(area["y"], area["y"] + area["height"] - 1)
    return x, y
