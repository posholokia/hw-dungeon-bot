import copy
import time
from dataclasses import dataclass
from logging import Logger
from threading import Event

from structlog import get_logger

from domain.types import RoomElement
from exceptions import RetryApplicationError, StopApplicationError
from models.dto import State
from services.battle.dto import BattleState
from services.floor_transit import FloorTransitService
from use_cases.battle import BattleUseCase
from use_cases.reloader import ReloadGameUseCase
from use_cases.select_room import SelectRoomUseCase

logger: Logger = get_logger(__name__)


@dataclass
class BattleStateCfg:
    teams: dict[RoomElement, list[list[str]]]
    healing_team: list[str]


class BotOrchestration:
    def __init__(
        self,
        select_room_use_case: SelectRoomUseCase,
        battle_use_case: BattleUseCase,
        floor_service: FloorTransitService,
        cfg: BattleStateCfg,
        return_service: ReloadGameUseCase,
    ) -> None:
        self._select_room = select_room_use_case
        self._battle = battle_use_case
        self._cfg = cfg
        self._floor_service = floor_service
        self._return_service = return_service

    def run(
        self,
        target_level: int,
        complete: int,
        current_level: int,
        stop_event: Event,
    ) -> None:
        state = State()
        battle_state = BattleState(
            teams=copy.deepcopy(self._cfg.teams),
            healing_team=copy.deepcopy(self._cfg.healing_team),
        )
        complete = complete or 1000

        level: str | int
        if not current_level:
            level = input("Текущий уровень: ")
        else:
            level = current_level

        state.current_level = int(level)
        start = time.perf_counter()
        bot_reloaded = False

        if target_level:
            logger.info(f"Условие остановки бота: достигнуть уровня {target_level}")
        else:
            logger.info(f"Условие остановки бота: пройти {complete} уровней")

        while not stop_event.is_set():
            try:
                self._select_room.execute(state, battle_state, stop_event)
                battle_state.start(element=state.room_element)
                battle_state, replay = self._battle.execute(battle_state, stop_event)

                if replay:
                    battle_state.lose()
                    continue

                self._floor_service.transit(state, stop_event)
                self._win(battle_state, state)

                logger.info(f"Пройдено {state.levels_completed} уровней")
                logger.debug(f"Текущий уровень: {state.current_level}")

                if target_level and state.current_level > target_level:
                    logger.info(
                        f"Уровень {target_level} достигнут, завершение работы..."
                    )
                    return
                elif not target_level and state.levels_completed > complete:
                    logger.info(f"Пройдено {complete} уровней, завершение работы...")
                    return

                if state.levels_completed % 10 == 0:
                    time_per_level = (
                        time.perf_counter() - start
                    ) / state.levels_completed
                    time_per_100 = round(time_per_level * 100 / 60, 1)
                    logger.debug(
                        f"Скорость прохождения уровней: {time_per_100} минут на 100 уровней"
                    )
                bot_reloaded = False
            except StopApplicationError as e:
                battle_state.clear()
                logger.info("Остановка приложения...")
                return
            except RetryApplicationError as e:
                battle_state.clear()
                logger.info(e.__str__())
                logger.debug("Проверка игры на вылет")
                game_dropped = self._return_service.reload_after_drop(stop_event)

                if game_dropped:
                    continue
                else:
                    if bot_reloaded:
                        logger.warning("Ошибка приложения, завершение работы...")
                        return

                    reloaded = self._return_service.reload_after_error(stop_event)
                    if reloaded:
                        bot_reloaded = True
                        continue
                    else:
                        logger.warning("Ошибка приложения, завершение работы...")
                        return
            except Exception as e:
                battle_state.clear()
                logger.exception(e.__str__())
                return

        logger.info("Bot stopped")

    def _win(self, battle_state: BattleState, state: State) -> None:
        battle_state.clear()
        state.up_level()
