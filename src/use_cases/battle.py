from threading import Event

from structlog import getLogger

from exceptions import ApplicationError, StopApplicationError
from services.battle.battle.dead_scaner import DeadScanService
from services.battle.battle.healing import HealthObserveService
from services.battle.battle.health_scaner import HealthScanerService
from services.battle.battle.replay import ReplayService
from services.battle.battle.scaner import BattleScannerService
from services.battle.battle.selector import BattleSelectorService
from services.battle.battle.team_select import TeamSelectService
from services.battle.dto import BattleState

logger = getLogger(__name__)


class BattleUseCase:
    """
    Сценарий боя. Управляет анализом и выбором команды,
    запуском боя, анализом результата, переигровкой.
    """

    def __init__(
        self,
        scaner: BattleScannerService,
        select_service: TeamSelectService,
        selector: BattleSelectorService,
        dead_scaner: DeadScanService,
        health_scaner: HealthScanerService,
        replay_service: ReplayService,
        health_observe: HealthObserveService,
    ) -> None:
        self._scaner = scaner
        self._select_service = select_service
        self._selector = selector
        self._dead_scaner = dead_scaner
        self._health_scaner = health_scaner
        self._replay_service = replay_service
        self._health_observe = health_observe

    def execute(
        self, battle_state: BattleState, stop_event: Event
    ) -> tuple[BattleState, bool]:
        """
        Сценарий проведения боя в комнате.
        Args:
            state: Состояние прохождения подземки.
            battle_state: Данные проведения боя.
            stop_event: Событие остановки приложения.
        Returns:
            Данные проведения боя и флаг необходимости переигровки (True - переиграть, False - бой успешен)
        """
        # ожидание кнопки автобоя, чтобы убедиться что сейчас на нужном экране
        self._scaner.scan_autobattle(stop_event)
        self.__select_team(battle_state, stop_event)
        self._selector.click_autobattle(stop_event)
        win = self._scaner.scan_win_loose(stop_event)

        if not win:
            logger.info("Переигровка уровня: поражение")
            self._replay_service.replay(lose=True, stop_event=stop_event)
            return battle_state, True

        has_dead = self._dead_scaner.has_dead(team_len=len(battle_state.current_team))

        if has_dead:
            logger.info("Переигровка уровня: умер титан")
            self._replay_service.replay(lose=False, stop_event=stop_event)
            return battle_state, True

        # ожидаем, так как анимация перекрывает полоски здоровья/энергии
        if stop_event.wait(2):
            raise StopApplicationError()

        health_list = self._health_scaner.scan_health(battle_state)
        need_replay = self._replay_service.check_replay_condition(health_list)

        if need_replay:
            self._replay_service.replay(lose=False, stop_event=stop_event)
            return battle_state, True

        self._health_observe.observe(health_list, battle_state)
        self._replay_service.apply_result(stop_event)
        return battle_state, False

    def __select_team(self, battle_state: BattleState, stop_event: Event) -> None:
        expected_team = set(battle_state.current_team)

        if not expected_team:
            raise ApplicationError("Все команды провалили бой")

        current_team = self._scaner.scan_team()
        logger.info(f"Текущая команда титанов: {current_team}")

        tries = 0

        while current_team != expected_team:
            self._select_service.select_team(current_team, expected_team)
            current_team = self._scaner.scan_team()
            tries += 1

            if tries >= 5:
                raise ApplicationError("Не удалось выбрать команду после 5 попыток")

            if stop_event.is_set():
                raise ApplicationError()
