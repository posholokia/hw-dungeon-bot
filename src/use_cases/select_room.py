from threading import Event

from structlog import get_logger

from exceptions import ApplicationError, RetryApplicationError
from models.dto import State
from services.battle.dto import BattleState
from services.select_room.scaner import RoomFinderService
from services.select_room.selector import SelectRoomService

logger = get_logger(__name__)


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
            # обнаружение и клик на комнату
            room_position = self._finder.find_room(stop_event)
            logger.debug(f"Room found at {room_position}")
            self._selector.click_room(room_position)
            # обнаружение и выбор элемента в комнате
            elements = self._finder.find_elements(stop_event)
            logger.debug(f"Элементы в комнате: {elements}")
            self._selector.select_room_element(state, battle_state, elements)
        except ApplicationError:
            raise
        except Exception as e:
            logger.exception(e.__str__())
            raise RetryApplicationError(e.__str__())
