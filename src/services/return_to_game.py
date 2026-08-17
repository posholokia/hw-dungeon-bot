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
        if not self._clicker.wait_click_check(self._cfg.guild, stop_event):
            return False
        time.sleep(randomizer.uniform(1.76, 2.94))
        logger.debug("Переход в подземелье")
        res = self._clicker.wait_click_check(self._cfg.dungeon, stop_event)
        time.sleep(randomizer.uniform(2.44, 3.36))
        return res
