# """DEPRECATED"""

# import logging
# import random
# import time
# from collections.abc import Callable
# from threading import Event

# from flow.utils import match_fingerprint

# from exceptions import ApplicationError, StopApplicationError
# from models.dto import ClickArea, State
# from vision.screen import take_print

# logger = logging.getLogger(__name__)


# class ReplayStep:
#     """Переигровка боя."""

#     def __init__(
#         self,
#         timeout: int,
#         coordinates: dict[str, list[tuple[int, int]]],
#         fingerprint: dict[str, list[tuple[int, int, int]]],
#         click_area: dict[str, ClickArea],
#         show_click: Callable[[int, int], None],
#         preview_seconds: float = 0.8,
#     ) -> None:
#         self._timeout = timeout
#         self._coordinates = coordinates
#         self._fingerprint = fingerprint
#         self._click_area = click_area
#         self._show_click = show_click
#         self._preview_seconds = preview_seconds

#     def execute(self, state: State, stop_event: Event) -> None:
#         self._click_replay()
#         self._click_pause()
#         self._click_retreat()
#         raise StopApplicationError("Level failed")

#     def _click_replay(self) -> None:
#         start = time.perf_counter()
#         coordinates = self._coordinates["replay"]
#         fingerprint = self._fingerprint["replay"]
#         click_area = self._click_area["replay"]

#         while time.perf_counter() - start < self._timeout:
#             scanned = take_print(coordinates)
#             if match_fingerprint(scanned, fingerprint):
#                 self._click(click_area)
#                 return
#             time.sleep(0.1)

#         raise ApplicationError("Cant click replay")

#     def _click_pause(self) -> None:
#         start = time.perf_counter()
#         coordinates = self._coordinates["pause"]
#         fingerprint = self._fingerprint["pause"]
#         click_area = self._click_area["pause"]

#         while time.perf_counter() - start < self._timeout:
#             scanned = take_print(coordinates)
#             if match_fingerprint(scanned, fingerprint):
#                 self._click(click_area)
#                 return
#             time.sleep(0.1)

#         raise ApplicationError("Cant click pause")

#     def _click_retreat(self) -> None:
#         start = time.perf_counter()
#         coordinates = self._coordinates["retreat"]
#         fingerprint = self._fingerprint["retreat"]
#         click_area = self._click_area["retreat"]

#         while time.perf_counter() - start < self._timeout:
#             scanned = take_print(coordinates)
#             if match_fingerprint(scanned, fingerprint):
#                 self._click(click_area)
#                 return
#             time.sleep(0.1)

#         raise ApplicationError("Cant click retreat")

#     def _click(self, click_area: ClickArea) -> None:
#         x, y = _random_point(click_area)
#         logger.info("Click replay preview at (%s, %s)", x, y)
#         self._show_click(x, y)
#         time.sleep(self._preview_seconds)


# def _random_point(area: ClickArea) -> tuple[int, int]:
#     if area["width"] < 1 or area["height"] < 1:
#         raise ApplicationError("Click area width/height must be >= 1")
#     x = random.randint(area["x"], area["x"] + area["width"] - 1)
#     y = random.randint(area["y"], area["y"] + area["height"] - 1)
#     return x, y
