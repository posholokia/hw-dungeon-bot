import time
from collections.abc import Hashable, Mapping
from threading import Event

from pydantic.types import HashableItemType

from domain.types import CoordinateList, FingerPrint, Timeout
from exceptions import ApplicationError
from interfaces.cfg import IScreenButton
from interfaces.output import IMouseClick
from models.dto import ClickArea
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print


class WaitClickCheckService:
    """
    Сервис выполняет задачу ожидания экрана,
    нажатия кнопки, проверки что экран поменялся.
    """

    def __init__(
        self,
        clicker: IMouseClick,
        timeout: Timeout,
    ) -> None:
        self._clicker = clicker
        self._timeout = timeout
        self._max_iterations = 7

    def wait_click_check(
        self,
        screen_data: IScreenButton,
        stop_event: Event,
    ) -> bool:
        """
        Ожидает появления экрана, выполняет клик мышью
        и проверяет что экран изменился. Если экран не изменился,
        повторяет клик мышью.

        Args:
            screen_data: Данные для выполнения - область клика,
                координаты сканирования и отпечаток.
            stop_event: Событие остановки приложения.
        Returns:
            True: Экран обнаружен, клик мышью выполнен и экран сменился.
            False: Любой из этих этапов не был выполнен.
        """
        matched = self.wait(
            coordinates=screen_data.coordinates,
            fingerprint=screen_data.fingerprint,
            stop_event=stop_event,
        )

        if not matched:
            return False

        return self.click_and_check(
            area=screen_data.click_area,
            coordinates=screen_data.coordinates,
            fingerprint=screen_data.fingerprint,
            stop_event=stop_event,
            match=False,
        )

    def wait(
        self,
        coordinates: CoordinateList,
        fingerprint: FingerPrint,
        stop_event: Event,
    ) -> bool:
        """
        Ожидание экрана.

        Args:
            coordinates: Список координат для сканирования.
            fingerprint: Отпечаток координат.
            stop_event: Событие остановки приложения.
        Returns:
            True: Экран появился.
            False: Экран не появился.
        """
        start = time.perf_counter()

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return False

            scanned = take_print(coordinates)

            if match_fingerprint(scanned, fingerprint):
                return True

            if stop_event.wait(timeout=0.005):
                return False

        return False

    def find_and_click_check(
        self,
        screen: Mapping[HashableItemType, IScreenButton],
        stop_event: Event,
    ) -> Hashable:
        """
        Ищет по нужный элемент по списку возможных расположений,
        выбирает его и проверяет что экран сменился.

        Args:
            screen: Словарь возможных расположений.
            stop_event: Событие остановки приложения.
        Returns:
            Ключ словаря, под которым было найдено расположение.
        """
        start = time.perf_counter()
        founded: HashableItemType | None = None

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                raise ApplicationError()

            for key, cfg in screen.items():
                scanned = take_print(cfg.coordinates)
                if match_fingerprint(scanned, cfg.fingerprint):
                    founded = key
                    break

            if founded is not None:
                break

            if stop_event.wait(timeout=0.005):
                raise ApplicationError()

        if not founded:
            raise ApplicationError()

        cfg = screen[founded]
        area = cfg.click_area

        clicked = self.click_and_check(
            area=area,
            coordinates=cfg.coordinates,
            fingerprint=cfg.fingerprint,
            stop_event=stop_event,
            match=False,
        )
        if clicked:
            return founded

        raise ApplicationError()

    def click_and_check(
        self,
        area: ClickArea,
        coordinates: CoordinateList,
        fingerprint: FingerPrint,
        stop_event: Event,
        match: bool = True,
    ) -> bool:
        """
        Клик по области с проверкой, что экран сменился.

        Args:
            area: Область клика.
            coordinates: Координаты точке сканирования.
            fingerprint: Отпечаток точек.
            stop_event: Событие остановки приложения.
            match: Если True - проверяется что после клика экран совпадает
                с отпечатком (сменился на конкретный экран),
                если False - то не совпадает (сменился на любой другой).
                При match=False надо убедиться что перед вызовом экран
                ранее совпадал с отпечатком.
        Returns:
            True: Клик успешный.
            False: После клика не появился ожидаемый экран.
        """
        i = 0
        # кликаем
        self._clicker.mouse_click(area.c, area.width, area.height)
        # ждем
        if stop_event.wait(0.3):
            return False

        while True:
            # проверяем что экран сменился
            scanned = take_print(coordinates)
            if (
                match
                and match_fingerprint(scanned, fingerprint)
                or not match
                and not match_fingerprint(scanned, fingerprint)
            ):
                return True

            # ограничиваем максимум кликов
            i += 1
            if i >= self._max_iterations:
                return False

            self._clicker.mouse_click(area.c, area.width, area.height)

            if stop_event.wait(1):
                return False
