from __future__ import annotations

from collections.abc import Mapping
from logging import Logger
from threading import Event

from structlog import getLogger

from domain.types import ElementPosition, RoomElement, RoomPosition
from exceptions import ApplicationError
from interfaces.cfg import IScreenButton
from models.dto import ClickArea
from services.battle.dto import BattleState
from services.wait_clicker import WaitClickCheckService

logger: Logger = getLogger(__name__)


class SelectRoomService:
    PRIORITY: tuple[RoomElement, ...] = ("common", "water", "earth", "fire")
    """Сервис выбора комнаты."""

    def __init__(
        self,
        room_cfg: Mapping[RoomPosition, IScreenButton],
        element_areas: dict[ElementPosition, ClickArea],
        check_element: IScreenButton,
        clicker: WaitClickCheckService,
    ) -> None:
        self._room_cfg = room_cfg
        self._clicker = clicker
        self._element_areas = element_areas
        self._check_element = check_element

    def select_room(self, stop_event: Event) -> None:
        room_pos = self._clicker.find_and_click_check(
            screen=self._room_cfg, stop_event=stop_event
        )
        logger.info(f"Комната найдена в позиции '{room_pos}'")

    def select_room_element(
        self,
        battle_state: BattleState,
        elements: dict[RoomElement, ElementPosition],
        stop_event: Event,
    ) -> RoomElement:
        if battle_state.need_healing and "common" in elements:
            room_element: RoomElement = "common"
        else:
            for element in self.PRIORITY:
                if element in elements:
                    room_element = element
                    break
            else:
                raise ApplicationError("Неизвестный элемент комнаты")

        clicked = self._clicker.click_and_check(
            area=self._element_areas[elements[room_element]],
            coordinates=self._check_element.coordinates,
            fingerprint=self._check_element.fingerprint,
            stop_event=stop_event,
            match=True,
        )
        if clicked:
            return room_element

        raise ApplicationError("не удалось выбрать элемент комнаты")
