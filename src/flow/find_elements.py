import logging
import time
from threading import Event

from exceptions import ElementsNotFoundError
from flow.utils import match_fingerprint
from models.dto import (
    FoundElement,
    RoomCoordinates,
    RoomPosition,
    RoomTypes,
    SelectionFingerprints,
    State,
)
from vision.screen import take_print


logger = logging.getLogger(__name__)

_POSITIONS: tuple[RoomPosition, ...] = ("left", "right", "center")
_ELEMENTS: tuple[RoomTypes, ...] = ("common", "earth", "water", "fire")


class FindElementsStep:
    """Scan selection slots and store matched element types in state."""

    def __init__(
        self,
        timeout: int,
        coordinates: RoomCoordinates,
        fingerprints: SelectionFingerprints,
    ) -> None:
        self._timeout = timeout
        self._coordinates = coordinates
        self._fingerprints = fingerprints

    def execute(self, state: State, stop_event: Event) -> None:
        state.available_elements = []
        start = time.perf_counter()
        logger.info("Searching for available elements at left/right/center")
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            found = self._find_all()
            if found:
                state.available_elements = found
                names = [item.element for item in found]
                logger.info("Available elements: %s", names)
                return

            if stop_event.wait(2):
                return

        raise ElementsNotFoundError("No elements found")

    def _find_all(self) -> list[FoundElement]:
        found: list[FoundElement] = []
        for position in _POSITIONS:
            element = self._match_position(position)
            if element is not None:
                found.append(FoundElement(element=element, position=position))
        return found

    def _match_position(self, position: RoomPosition) -> RoomTypes | None:
        scanned = take_print(self._coordinates[position])
        for element in _ELEMENTS:
            if match_fingerprint(scanned, self._fingerprints[element]):
                return element
        return None
