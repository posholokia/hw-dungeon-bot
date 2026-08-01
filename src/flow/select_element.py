from __future__ import annotations

import logging
import random
from collections.abc import Callable
from threading import Event

from exceptions import ApplicationError
from models.dto import ClickArea, RoomClickAreas, RoomTypes, State


logger = logging.getLogger(__name__)

_PRIORITY: tuple[RoomTypes, ...] = ("common", "water", "earth", "fire")


class SelectElementStep:
    """Pick the highest-priority available element and preview a click on it."""

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
        if not state.available_elements:
            raise ApplicationError("No available elements; run FindElementsStep first")

        available = {item.element: item.position for item in state.available_elements}
        selected = next(
            (element for element in _PRIORITY if element in available),
            None,
        )
        if selected is None:
            raise ApplicationError(f"No priority match among {list(available)}")

        position = available[selected]
        area = self._click_areas[position]
        x, y = _random_point(area)
        logger.info(
            "Available elements: %s; selected: %s at %s; click preview (%s, %s)",
            list(available),
            selected,
            position,
            x,
            y,
        )
        self._show_click(x, y)
        stop_event.wait(self._preview_seconds)


def _random_point(area: ClickArea) -> tuple[int, int]:
    if area["width"] < 1 or area["height"] < 1:
        raise ApplicationError("Click area width/height must be >= 1")
    x = random.randint(area["x"], area["x"] + area["width"] - 1)
    y = random.randint(area["y"], area["y"] + area["height"] - 1)
    return x, y
