import copy
from dataclasses import dataclass
from threading import Event

from structlog import get_logger

from domain.types import RoomElement
from exceptions import RetryApplicationError, StopApplicationError
from models.dto import State
from services.battle.dto import BattleState
from services.floor_transit import FloorTransitService
from use_cases.battle import BattleUseCase
from use_cases.select_room import SelectRoomUseCase

logger = get_logger(__name__)


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
    ) -> None:
        self._select_room = select_room_use_case
        self._battle = battle_use_case
        self._cfg = cfg
        self._floor_service = floor_service

    def run(self, stop_event: Event) -> None:
        state = State()
        battle_state = BattleState(
            teams=copy.deepcopy(self._cfg.teams),
            healing_team=copy.deepcopy(self._cfg.healing_team),
        )

        while not stop_event.is_set():
            try:
                self._select_room.execute(state, battle_state, stop_event)
                battle_state.start(element=state.room_element)
                battle_state, replay = self._battle.execute(battle_state, stop_event)

                if replay:
                    battle_state.lose()
                    continue

                self._win(battle_state, state)
                self._floor_service.transit(state, stop_event)

                if state.levels_completed >= 10:
                    logger.info("Лимит уровней пройден")
                    return

                logger.info(f"Пройдено {state.levels_completed} уровней")
                logger.debug(f"Текущий уровень: {state.current_level}")
                logger.debug(f"Калибровка уровня: {state.current_level_calibrated}")
            except StopApplicationError as e:
                battle_state.clear()
                logger.info(e.__str__())
                return
            except RetryApplicationError as e:
                battle_state.clear()
                logger.info(e.__str__())
                logger.info("Пауза перед следующим циклом...")
                stop_event.wait(60)
                continue
            except Exception as e:
                battle_state.clear()
                logger.exception(e.__str__())
                return

        logger.info("Bot stopped")

    def _win(self, battle_state: BattleState, state: State) -> None:
        battle_state.clear()
        state.up_level()
