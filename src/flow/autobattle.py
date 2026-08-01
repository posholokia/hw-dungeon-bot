from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from threading import Event

from exceptions import ApplicationError, AutobattleNotFoundError
from flow.utils import match_fingerprint
from models.dto import ClickArea, State
from vision.screen import take_print


logger = logging.getLogger(__name__)


class AutobattleStep:
    """Wait until the battle button is visible, then preview a click on it."""

    def __init__(
        self,
        timeout: int,
        coordinates: list[tuple[int, int]],
        fingerprint: list[tuple[int, int, int]],
        click_area: ClickArea,
        show_click: Callable[[int, int], None],
        preview_seconds: float = 0.8,
    ) -> None:
        self._timeout = timeout
        self._coordinates = coordinates
        self._fingerprint = fingerprint
        self._click_area = click_area
        self._show_click = show_click
        self._preview_seconds = preview_seconds

    def execute(self, state: State, stop_event: Event) -> None:
        start = time.perf_counter()
        logger.info("Waiting for autobattle button")
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            scanned = take_print(self._coordinates)
            if match_fingerprint(scanned, self._fingerprint):
                logger.info("Autobattle button found")
                self._click(stop_event)
                return

            if stop_event.wait(timeout=0.005):
                return

        raise AutobattleNotFoundError("Autobattle button not found")

    def _click(self, stop_event: Event) -> None:
        x, y = _random_point(self._click_area)
        logger.info("Autobattle click preview at (%s, %s)", x, y)
        self._show_click(x, y)
        stop_event.wait(self._preview_seconds)


def _random_point(area: ClickArea) -> tuple[int, int]:
    if area["width"] < 1 or area["height"] < 1:
        raise ApplicationError("Click area width/height must be >= 1")
    x = random.randint(area["x"], area["x"] + area["width"] - 1)
    y = random.randint(area["y"], area["y"] + area["height"] - 1)
    return x, y
