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
            bool - это экран вылета игры и сценарий выполнен успешно
        """
        is_drop_screen = self._clicker.wait_click_check(self._cfg.screen, stop_event)
        if not is_drop_screen:
            logger.debug("Экран вылета игры не выявлен")
            return False

        logger.debug("Выявлен экран вылета игры")
        logger.debug("Ожидание загрузки игры")
        if not self._clicker.wait(
            self._cfg.guild.coordinates, self._cfg.guild.fingerprint, stop_event
        ):
            return False
        logger.debug("Переход в гильдию")
        time.sleep(randomizer.uniform(3.16, 3.74))
        if not self._clicker.click_and_check(
            area=self._cfg.guild.click_area,
            coordinates=self._cfg.guild.coordinates,
            fingerprint=self._cfg.guild.fingerprint,
            stop_event=stop_event,
            match=False,
        ):
            return False
        logger.debug("Переход в подземелье")
        time.sleep(randomizer.uniform(4.07, 4.43))
        res = self._clicker.wait_click_check(self._cfg.dungeon, stop_event)
        time.sleep(randomizer.uniform(3.44, 4.36))
        return res
