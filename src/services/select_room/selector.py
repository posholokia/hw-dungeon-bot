from __future__ import annotations

from threading import Event

from structlog import getLogger

from domain.types import ElementPositions, PreviewSeconds, RoomPosition, RoomElements
from interfaces.output import IMouseClick
from models.dto import ClickArea, State

logger = getLogger(__name__)


class SelectRoomService:
    PRIORITY: tuple[RoomElements, ...] = ("water", "earth", "common", "fire")
    """Сервис выбора комнаты."""

    def __init__(
        self,
        click_areas: dict[RoomPosition, ClickArea],
        click_service: IMouseClick,
        preview_seconds: PreviewSeconds,
    ) -> None:
        self._click_areas = click_areas
        self._click_service = click_service
        self._preview_seconds = preview_seconds

    def click_room(self, position: RoomPosition, stop_event: Event) -> None:
        area = self._click_areas[position]
        self._click_service.mouse_click((area.x, area.y), area.width, area.height)
        stop_event.wait(self._preview_seconds)

    def select_room_element(
        self,
        state: State,
        elements: dict[RoomElements, ElementPositions],
        stop_event: Event,
    ) -> None:
        if state.need_healing and "common" in elements:
            area = self._click_areas[elements["common"]]
            self._click_service.mouse_click((area.x, area.y), area.width, area.height)
        else:
            for element in self.PRIORITY:
                if element in elements:
                    area = self._click_areas[elements[element]]
                    self._click_service.mouse_click(
                        (area.x, area.y), area.width, area.height
                    )
                    break

        stop_event.wait(self._preview_seconds)
