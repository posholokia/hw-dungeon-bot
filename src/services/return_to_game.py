from logging import Logger
from threading import Event

from structlog import getLogger

from configs.settings import DropGameConfig
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
        logger.debug("Переход в гильдию")
        if not self._clicker.wait_click_check(self._cfg.guild, stop_event):
            return False

        logger.debug("Переход в подземелье")
        return self._clicker.wait_click_check(self._cfg.dungeon, stop_event)
