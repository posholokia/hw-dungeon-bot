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
            self._cfg.guild.coordinates, self._cfg.guild.fingerprint, stop_event
        ):
            return False
        logger.debug("Переход в гильдию")
        time.sleep(randomizer.uniform(9.16, 12.74))
        if not self._clicker.click_and_check(
            area=self._cfg.guild.click_area,
            coordinates=self._cfg.dungeon.coordinates,
            fingerprint=self._cfg.dungeon.fingerprint,
            stop_event=stop_event,
            match=True,
        ):
            return False
        logger.debug("Переход в подземелье")
        time.sleep(randomizer.uniform(4.07, 4.43))
        success = self._clicker.wait_click_check(self._cfg.dungeon, stop_event)
        time.sleep(randomizer.uniform(3.44, 4.36))
        return success
