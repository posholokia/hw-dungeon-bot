from __future__ import annotations

from structlog import getLogger

from domain.types import ElementPosition, RoomElement, RoomPosition
from interfaces.output import IMouseClick
from models.dto import ClickArea, State
from services.battle.dto import BattleState

logger = getLogger(__name__)


class SelectRoomService:
    PRIORITY: tuple[RoomElement, ...] = ("water", "earth", "common", "fire")
    """Сервис выбора комнаты."""

    def __init__(
        self,
        click_areas: dict[RoomPosition, ClickArea],
        element_areas: dict[ElementPosition, ClickArea],
        click_service: IMouseClick,
    ) -> None:
        self._click_areas = click_areas
        self._click_service = click_service
        self._element_areas = element_areas

    def click_room(self, position: RoomPosition) -> None:
        area = self._click_areas[position]
        self._click_service.mouse_click((area.x, area.y), area.width, area.height)

    def select_room_element(
        self,
        state: State,
        battle_state: BattleState,
        elements: dict[RoomElement, ElementPosition],
    ) -> None:
        if battle_state.need_healing and "common" in elements:
            area = self._click_areas[elements["common"]]
            self._click_service.mouse_click((area.x, area.y), area.width, area.height)
        else:
            for element in self.PRIORITY:
                if element in elements:
                    area = self._click_areas[elements[element]]
                    self._click_service.mouse_click(
                        (area.x, area.y), area.width, area.height
                    )
                    state.room_element = element
                    return
