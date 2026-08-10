from threading import Event
import time
from exceptions import BadBattleResult, StopApplicationError
from models.dto import State
from services.battle.battle.scaner import BattleScannerService
from services.battle.battle.selector import BattleSelectorService
from services.battle.battle.team_select import TeamSelectService
from services.battle.dto import BattleState
from structlog import getLogger

from services.fingerprint_match import match_fingerprint
from vision.screen import take_print


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
    ) -> None:
        self._scaner = scaner
        self._select_service = select_service
        self._selector = selector

    def execute(self, state: State, battle_state: BattleState, stop_event: Event) -> tuple[BattleState, bool]:
        """
        Сценарий проведения боя в комнате.
        Args:
            state: Состояние прохождения подземки.
            battle_state: Данные проведения боя.
            stop_event: Событие остановки приложения.
        Returns:
            Данные проведения боя и флаг необходимости переигровки (True - переиграть, False - бой успешен)
        """
        self.__select_team(battle_state)
        self.__autobattle()
        win = self._scaner.scan_win_loose(stop_event)
        
        if not win:
            return battle_state, True
        
        # TODO: чек мертвых, чек хп и энергии, чек критериев переигровки (мало хп/энергии)

    def __select_team(self, battle_state: BattleState, stop_event: Event) -> None:
        expected_team = set(battle_state.current_team)
        
        if not expected_team:
            raise StopApplicationError("Все команды провалили бой")
        
        current_team = self._scaner.scan_team()
        tries = 0
        
        while current_team != expected_team:
            self._select_service.select_team(current_team, expected_team)
            current_team = self._scaner.scan_team()
            tries += 1 
        
            if tries >= 5:
                raise StopApplicationError("Не удалось выбрать команду после 5 попыток")
            
            if stop_event.is_set():
                raise StopApplicationError()
    
    def __autobattle(self, stop_event: Event) -> None:
        self._scaner.scan_autobattle(stop_event)
        self._selector.click_autobattle(stop_event)
