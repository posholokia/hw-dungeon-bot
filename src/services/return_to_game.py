import time
from logging import Logger
from threading import Event

from structlog import getLogger

from configs.settings import DropGameConfig
from core.randomizer import randomizer
from services.wait_clicker import WaitClickCheckService

logger: Logger = getLogger(__name__)


class ReturnGameService:
    def __init__(
        self,
        cfg: DropGameConfig,
        clicker: WaitClickCheckService,
    ) -> None:
        self._cfg = cfg
        self._clicker = clicker

    def execute(self, stop_event: Event) -> bool:
        """
        Returns:
            bool - статус перехода в подземелье
        """
        logger.debug("Ожидание загрузки игры")
        
        if not self._clicker.wait(
            self._cfg.battles.coordinates, self._cfg.battles.fingerprint, stop_event
        ):
            return False
        
        logger.debug("Переход в 'Сражения'")
        time.sleep(randomizer.uniform(1.16, 1.74))
        if not self._clicker.click_and_check(
            area=self._cfg.battles.click_area,
            coordinates=self._cfg.battles_tab.coordinates,
            fingerprint=self._cfg.battles_tab.fingerprint,
            stop_event=stop_event,
            match=True,
        ):
            return False
       
        logger.debug("Переход во вкладку сражений")
        if not self._clicker.click_and_check(
            area=self._cfg.battles_tab.click_area,
            coordinates=self._cfg.dungeon.coordinates,
            fingerprint=self._cfg.dungeon.fingerprint,
            stop_event=stop_event,
            match=True,
        ):
            return False
        
        time.sleep(randomizer.uniform(2.07, 4.43))
        success = self._clicker.click_and_check(
            area=self._cfg.dungeon.click_area,
            coordinates=self._cfg.dungeon.coordinates,
            fingerprint=self._cfg.dungeon.fingerprint,
            stop_event=stop_event,
            match=False,
        )
        
        if success:
            time.sleep(randomizer.uniform(3.44, 4.36))

        return success
