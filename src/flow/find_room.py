import logging
import time
from threading import Event

from exceptions import RoomNotFoundError
from flow.utils import match_fingerprint
from models.dto import RoomCoordinates, State
from vision.screen import take_print


logger = logging.getLogger(__name__)


class FindRoomStep:
    """
    Шаг поиска комнаты на этаже.
    """
    def __init__(
        self,
        timeout: int,
        room_coordinates: list[RoomCoordinates],
        fingerprint: list[tuple[int, int, int]],
    ) -> None:
        self._timeout = timeout
        self._room_coordinates = room_coordinates
        self._fingerprint = fingerprint

    def execute(self, state: State, stop_event: Event) -> None:
        """
        Выполнить шаг поиска комнаты на этаже.
        Пока уровень не известен, ищем во всех возможных координатах.
        Как только уровень известен, ищем в соответствующих координатах (слева, справа, центр).
        """
        start = time.perf_counter()
        position = state.get_room_position()
        logger.info("Searching for room at %s for level %s", position, state.level)
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            if self._find(state):
                return

            # wait() returns True if the event was set — exit promptly on stop hotkey
            if stop_event.wait(0.005):
                return

        raise RoomNotFoundError("Room not found")

    def _find(self, state: State) -> bool:
        position = state.get_room_position()
        coordinates = self._room_coordinates[position]
        fingerprint = take_print(coordinates)

        if match_fingerprint(fingerprint, self._fingerprint):
            logger.info("Room found at %s", position)
            return True

        return False
