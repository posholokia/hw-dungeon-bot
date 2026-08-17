import time
from threading import Event

from structlog import getLogger

from domain.types import (
    CoordinateList,
    ElementPosition,
    FingerPrint,
    RoomElement,
    RoomPosition,
    Timeout,
)
from exceptions import ApplicationError, StopApplicationError
from interfaces.output import IMouseClick
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print

logger = getLogger(__name__)

_POSITIONS: tuple[RoomPosition, ...] = ("left", "right", "center")
_ELEMENTS: tuple[RoomElement, ...] = ("common", "earth", "water", "fire")


class RoomFinderService:
    """Сервис поиска комнаты и элементов в комнате."""

    def __init__(
        self,
        timeout: Timeout,
        element_coordinates: dict[ElementPosition, CoordinateList],
        element_fingerprints: dict[RoomElement, FingerPrint],
        clicker: IMouseClick,
    ) -> None:
        self._timeout = timeout
        self._element_coordinates = element_coordinates
        self._element_fingerprints = element_fingerprints
        self._clicker = clicker

    def find_elements(self, stop_event: Event) -> dict[RoomElement, ElementPosition]:
        start = time.perf_counter()
        logger.info("Поиск элементов в комнате")
        self._clicker.hide_mouse()

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                raise StopApplicationError()

            found = self._find_all_elements()
            if found:
                return found

            if stop_event.wait(timeout=0.005):
                raise StopApplicationError()

        raise ApplicationError("No elements found")

    def _find_all_elements(self) -> dict[RoomElement, ElementPosition]:
        found: dict[RoomElement, ElementPosition] = {}
        for position in _POSITIONS:
            element = self._match_element_position(position)
            if element is not None:
                found[element] = position
        return found

    def _match_element_position(self, position: ElementPosition) -> RoomElement | None:
        scanned = take_print(self._element_coordinates[position])
        for element in _ELEMENTS:
            if match_fingerprint(scanned, self._element_fingerprints[element]):
                return element
        return None
