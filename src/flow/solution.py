import random
import logging
from threading import Event
import time
from typing import Callable
from exceptions import ApplicationError
from flow.utils import match_fingerprint
from interfaces.flow import IStep
from models.dto import ClickArea, State
from vision.screen import take_print

logger = logging.getLogger(__name__)


class SolutionStep:
    """Принимает решение о переигровке или продолжении."""

    def __init__(self,
        timeout: int,
        replay_step: IStep,
        coordinates: list[tuple[int, int]],
        fingerprint: list[tuple[int, int, int]],
        click_area: ClickArea,
        show_click: Callable[[int, int], None],
        preview_seconds: float = 0.8,
    ) -> None:
        self._timeout = timeout
        self._replay_step = replay_step
        self._coordinates = coordinates
        self._fingerprint = fingerprint
        self._click_area = click_area
        self._show_click = show_click
        self._preview_seconds = preview_seconds

    def execute(self, state: State, stop_event: Event) -> None:
        if not state.win or state.has_dead:
            return self._replay_step.execute(state, stop_event)
        
        start = time.perf_counter()
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return
            
            scanned = take_print(self._coordinates)
            if match_fingerprint(scanned, self._fingerprint):
                if state.win and not state.has_dead:
                    self._click(stop_event)
                    return

            time.sleep(0.005)
        
        raise ApplicationError("Cant continue battle")

    def _click(self, stop_event: Event) -> None:
        x, y = _random_point(self._click_area)
        logger.info("Continue click preview at (%s, %s)", x, y)
        self._show_click(x, y)
        stop_event.wait(self._preview_seconds)


def _random_point(area: ClickArea) -> tuple[int, int]:
    if area["width"] < 1 or area["height"] < 1:
        raise ApplicationError("Click area width/height must be >= 1")
    x = random.randint(area["x"], area["x"] + area["width"] - 1)
    y = random.randint(area["y"], area["y"] + area["height"] - 1)
    return x, y
