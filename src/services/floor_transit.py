import time
from threading import Event

from configs.settings import ButtonConfig, FloorTransitConfig
from domain.types import Timeout
from interfaces.output import IMouseClick
from models.dto import State
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print


class FloorTransitService:
    def __init__(
        self,
        buttons_cfg: FloorTransitConfig,
        clicker: IMouseClick,
        timeout: Timeout,
    ) -> None:
        self._buttons_cfg = buttons_cfg
        self._clicker = clicker
        self._timeout = timeout

    def transit(self, state: State, stop_event: Event) -> None:
        if state.current_level % 10 == 0:
            button = self._buttons_cfg.left
        elif state.current_level % 10 == 5:
            button = self._buttons_cfg.right
        else:
            return

        self.__click(button, stop_event)
        self.__click(self._buttons_cfg.ok, stop_event)

    def __click(self, cfg: ButtonConfig, stop_event: Event) -> None:
        start = time.perf_counter()

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            fingerprint = take_print(cfg.coordinates)

            if match_fingerprint(fingerprint, cfg.fingerprint):
                area = cfg.click_area
                self._clicker.mouse_click(area.c, area.width, area.height)
                return

            if stop_event.wait(timeout=0.005):
                return
