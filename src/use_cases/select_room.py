from threading import Event

from structlog import get_logger

from domain.types import RoomPosition
from exceptions import RetryApplicationError, StopApplicationError
from interfaces.output import IMouseClick
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
        clicker: IMouseClick,
    ) -> None:
        self._finder = finder
        self._selector = selector
        self._clicker = clicker

    def execute(
        self, state: State, battle_state: BattleState, stop_event: Event
    ) -> None:
        self._clicker.mouse_click((500, 500))
        try:
            # обнаружение и клик на комнату
            room_position = self._finder.find_room(stop_event)
            logger.debug(f"Room found at {room_position}")
            if not state.current_level_calibrated:
                self._calibrate_current_level(state, room_position)
            self._selector.click_room(room_position, stop_event)
            # обнаружение и выбор элемента в комнате
            elements = self._finder.find_elements(stop_event)
            logger.debug(f"Элементы в комнате: {elements}")
            self._selector.select_room_element(
                state, battle_state, elements, stop_event
            )
        except StopApplicationError:
            raise
        except Exception as e:
            logger.exception(e.__str__())
            raise RetryApplicationError(e.__str__())

    def _calibrate_current_level(
        self,
        state: State,
        room_position: RoomPosition,
    ) -> None:
        """
        Калибровка текущего уровня. Он не равен реально текущему уровню,
        но остаток от деления на 10 равен.
        Например реальный уровень 1195, то после калибровки будет 5.
        Калиброка выполняется единожды после запуска бота.
        """
        if state.current_level == 1:
            # если самая первая комната окажется слева/справа
            # не получится корректно откалибровать,
            # так как не различить 5 и 6 комнату или 0 и 1
            return

        if room_position == "left" and state.current_level % 10 != 0:
            state.calibrate_current_level(10)
        elif room_position == "right" and state.current_level % 10 != 5:
            state.calibrate_current_level(5)
        else:
            # эта ветка нужна на случай если бот начал работу с 1 комнаты этажа
            # и уровень откалибровался в крайней комнате этажа
            state.calibrate_current_level(state.current_level)
        logger.debug(f"Калибровка текущего уровня: {state.current_level}")
