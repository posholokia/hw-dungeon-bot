import time
from logging import Logger
from threading import Event

from structlog import getLogger

from configs.settings import ButtonConfig, ReplayButtonsConfig
from domain.types import PreviewSeconds, Timeout
from interfaces.output import IMouseClick
from services.battle.dto import TitanStatus
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print

logger: Logger = getLogger(__name__)


class ReplayService:
    def __init__(
        self,
        timeout: Timeout,
        preview_seconds: PreviewSeconds,
        replay_conditions: dict[str, list[str]],
        replay_buttons: ReplayButtonsConfig,
        clicker: IMouseClick,
    ) -> None:
        self._timeout = timeout
        self._preview = preview_seconds
        self._replay_conditions = replay_conditions
        self._replay_buttons = replay_buttons
        self._clicker = clicker

    def check_replay_condition(self, health_list: list[TitanStatus]) -> bool:
        for titan in health_list:
            if titan.name not in self._replay_conditions:
                continue

            for criterion in self._replay_conditions[titan.name]:
                if self.__check_criterion(titan, criterion):
                    return True

        return False

    def replay(self, lose: bool, stop_event: Event) -> None:
        key = "lose" if lose else "win"
        logger.info("Ожидание кнопки 'Еще раз'")
        self.__click_button(self._replay_buttons.replay[key], stop_event)
        logger.info("Ожидание кнопки паузы боя")
        self.__click_button(self._replay_buttons.pause, stop_event)
        logger.info("Ожидание кнопки 'Отступить'")
        self.__click_button(self._replay_buttons.retreat, stop_event)

    def apply_result(self, stop_event: Event) -> None:
        self.__click_button(self._replay_buttons.ok, stop_event)

    def __click_button(self, cfg: ButtonConfig, stop_event: Event) -> None:
        start = time.perf_counter()

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            fingerprint = take_print(cfg.coordinates)

            if match_fingerprint(fingerprint, cfg.fingerprint):
                area = cfg.click_area
                self._clicker.mouse_click(area.c, area.width, area.height)
                stop_event.wait(self._preview)

            stop_event.wait(0.005)

    def __check_criterion(self, titan: TitanStatus, criterion: str) -> bool:
        """
        Проверка критерия для переигровки. Если все условия были удовлетворены,
        значит уровень необходимо переиграть.
        """
        expressions = criterion.split("&")

        for expression in expressions:
            param, val = expression.split("<")

            if not getattr(titan, param) < int(val):
                return False

        logger.info(f"Сработало условие переигровки: {criterion}")
        return True
