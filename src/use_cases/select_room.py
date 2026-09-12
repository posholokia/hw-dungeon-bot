from logging import Logger
from threading import Event

from structlog import get_logger

from exceptions import ApplicationError, RetryApplicationError, StopApplicationError
from models.dto import State
from services.battle.dto import BattleState
from services.select_room.scaner import RoomFinderService
from services.select_room.selector import SelectRoomService

logger: Logger = get_logger(__name__)


class SelectRoomUseCase:
    """Сценарий обнаружения и выбора комнаты подземелья."""

    def __init__(
        self,
        finder: RoomFinderService,
        selector: SelectRoomService,
    ) -> None:
        self._finder = finder
        self._selector = selector

    def execute(
        self, state: State, battle_state: BattleState, stop_event: Event
    ) -> None:
        try:
            logger.info("Поиск комнаты в left/right/center")
            self._selector.select_room(stop_event)
            # обнаружение и выбор элемента в комнате
            elements = self._finder.find_elements(stop_event)
            logger.debug(f"Элементы в комнате: {elements}")
            element = self._selector.select_room_element(
                battle_state, elements, stop_event
            )
            state.room_element = element
            logger.debug(f"Выбран элемент {element}")
        except (ApplicationError, StopApplicationError):
            raise
        except Exception as err:
            logger.exception(err.__str__())
            raise RetryApplicationError() from err
