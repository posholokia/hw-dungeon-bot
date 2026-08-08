import time
from threading import Event

from structlog import getLogger

from domain.types import (
    CoordinateList,
    ElementPositions,
    FingerPrintList,
    RoomPosition,
    Timeout,
    RoomElements,
)
from exceptions import RetryApplicationError, StopApplicationError
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print

logger = getLogger(__name__)

_POSITIONS: tuple[RoomPosition, ...] = ("left", "right", "center")
_ELEMENTS: tuple[RoomElements, ...] = ("common", "earth", "water", "fire")


class RoomFinderService:
    """Сервис поиска комнаты и элементов в комнате."""

    def __init__(
        self,
        timeout: Timeout,
        room_coordinates: dict[RoomPosition, CoordinateList],
        room_fingerprint: FingerPrintList,
        element_coordinates: dict[ElementPositions, CoordinateList],
        element_fingerprints: dict[RoomElements, FingerPrintList],
    ) -> None:
        self._timeout = timeout
        self._room_coordinates = room_coordinates
        self._room_fingerprint = room_fingerprint
        self._element_coordinates = element_coordinates
        self._element_fingerprints = element_fingerprints

    def find_room(self, stop_event: Event) -> RoomPosition:
        start = time.perf_counter()
        logger.info("Поиск комнаты в left/right/center")

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                raise StopApplicationError("Stop application")

            position = self._find_any_room()
            if position is not None:
                logger.info(f"Комната найдена в {position}")
                return position

            if stop_event.wait(timeout=0.005):
                raise StopApplicationError("Stop application")

        raise StopApplicationError("Room not found")

    def find_elements(self, stop_event: Event) -> dict[RoomElements, ElementPositions]:
        start = time.perf_counter()
        logger.info("Поиск элементов в комнате")

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                raise StopApplicationError("Stop application")

            found = self._find_all_elements()
            if found:
                logger.info(f"Доступные элементы: {found}")
                return found

            if stop_event.wait(timeout=0.005):
                raise RetryApplicationError()

        raise StopApplicationError("No elements found")

    def _find_any_room(self) -> RoomPosition | None:
        for position in _POSITIONS:
            coordinates = self._room_coordinates[position]
            fingerprint = take_print(coordinates)

            if match_fingerprint(fingerprint, self._room_fingerprint):
                return position

        return None

    def _find_all_elements(self) -> dict[RoomElements, ElementPositions]:
        found: dict[RoomElements, ElementPositions] = {}
        for position in _POSITIONS:
            element = self._match_element_position(position)
            if element is not None:
                found[element] = position
        return found

    def _match_element_position(
        self, position: ElementPositions
    ) -> RoomElements | None:
        scanned = take_print(self._element_coordinates[position])
        for element in _ELEMENTS:
            if match_fingerprint(scanned, self._element_fingerprints[element]):
                return element
        return None
