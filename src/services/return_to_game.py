import time
from logging import Logger
from threading import Event

from structlog import getLogger

from configs.settings import DropGameConfig
from interfaces.output import IMouseClick
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print

logger: Logger = getLogger(__name__)


class ReturnGameService:
    def __init__(
        self,
        cfg: DropGameConfig,
        clicker: IMouseClick,
    ) -> None:
        self._cfg = cfg
        self._clicker = clicker
        self._timeout = 60

    def execute(self, stop_event: Event) -> bool:
        """
        Returns:
            bool - это экран вылета игры и сценарий выполнен успешно
        """
        if stop_event.wait(5):
            return False

        if self.__is_drop_screen():
            area = self._cfg.screen.click_area
            self._clicker.mouse_click(area.c, area.width, area.height)

        logger.debug("Ожидание загрузки игры")
        if not self.__wait_and_click_guild(stop_event):
            return False

        if stop_event.wait(3):
            return False

        area = self._cfg.dungeon
        self._clicker.mouse_click(area.c, area.width, area.height)
        return True

    def __is_drop_screen(self) -> bool:
        points = self._cfg.screen.coordinates
        fingerprint = take_print(points)

        if match_fingerprint(fingerprint, self._cfg.screen.fingerprint):
            logger.debug("Выявлен экран вылета игры")
            return True

        logger.debug("Экран вылета игры не выявлен")
        return False

    def __wait_and_click_guild(self, stop_event: Event) -> bool:
        start = time.perf_counter()
        points = self._cfg.guild.coordinates
        area = self._cfg.guild.click_area

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return False

            fingerprint = take_print(points)

            if match_fingerprint(fingerprint, self._cfg.guild.fingerprint):
                logger.debug("Иконка гильдии найдена")
                self._clicker.mouse_click(area.c, area.width, area.height)
                return True

            if stop_event.wait(5):
                return False

        return False
