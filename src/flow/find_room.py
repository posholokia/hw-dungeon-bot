import logging
import time
from threading import Event

from exceptions import RoomNotFoundError
from flow.utils import match_fingerprint
from models.dto import RoomCoordinates, RoomPosition, State
from vision.screen import take_print


logger = logging.getLogger(__name__)

_POSITIONS: tuple[RoomPosition, ...] = ("left", "right", "center")


class FindRoomStep:
    """Scan all three room points and store the matched position in state."""

    def __init__(
        self,
        timeout: int,
        room_coordinates: RoomCoordinates,
        fingerprint: list[tuple[int, int, int]],
    ) -> None:
        self._timeout = timeout
        self._room_coordinates = room_coordinates
        self._fingerprint = fingerprint

    def execute(self, state: State, stop_event: Event) -> None:
        state.room_position = None
        start = time.perf_counter()
        logger.info("Searching for room at left/right/center")
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            position = self._find_any()
            if position is not None:
                state.room_position = position
                logger.info("Room found at %s", position)
                return

            if stop_event.wait(timeout=0.005):
                return

        raise RoomNotFoundError("Room not found")

    def _find_any(self) -> RoomPosition | None:
        for position in _POSITIONS:
            coordinates = self._room_coordinates[position]
            fingerprint = take_print(coordinates)
            if match_fingerprint(fingerprint, self._fingerprint):
                return position
        return None
