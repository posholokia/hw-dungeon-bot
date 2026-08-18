from logging import Logger
from threading import Event

from structlog import getLogger

from interfaces.cfg import IScreenButton
from output.keyboard import KeyBoardOutput
from services.return_to_game import ReturnGameService
from services.wait_clicker import WaitClickCheckService

logger: Logger = getLogger(__name__)


class ReloadGameUseCase:
    def __init__(
        self,
        return_game_service: ReturnGameService,
        keyboard: KeyBoardOutput,
        clicker: WaitClickCheckService,
        drop_screen: IScreenButton,
    ) -> None:
        self._return_game_service = return_game_service
        self._keyboard = keyboard
        self._clicker = clicker
        self._drop_screen = drop_screen

    def reload_after_error(self, stop_event: Event) -> bool:
        self._keyboard.tap_f5()
        return self._return_game_service.execute(stop_event)

    def reload_after_drop(self, stop_event: Event) -> bool:
        is_drop_screen = self._clicker.wait_click_check(self._drop_screen, stop_event)

        if not is_drop_screen:
            logger.debug("Экран вылета игры не выявлен")
            return False

        logger.debug("Выявлен экран вылета игры")
        return self._return_game_service.execute(stop_event)
