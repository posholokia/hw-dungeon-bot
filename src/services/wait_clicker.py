import time
from threading import Event

from domain.types import CoordinateList, FingerPrint, Timeout
from interfaces.cfg import IScreenButton
from interfaces.output import IMouseClick
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
        self._max_iterations = 3

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
        start = time.perf_counter()
        matched = False
        clicked = False
        i = 0
        area = screen_data.click_area

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return False

            fingerprint = take_print(screen_data.coordinates)

            if match_fingerprint(fingerprint, screen_data.fingerprint):
                matched = True
                break

            if stop_event.wait(timeout=0.005):
                return False

        if not matched:
            return False

        while not clicked:
            # кликаем
            self._clicker.mouse_click(area.c, area.width, area.height)
            # ждем
            if stop_event.wait(0.1):
                return clicked
            # проверяем что экран сменился
            fingerprint = take_print(screen_data.coordinates)
            if not match_fingerprint(fingerprint, screen_data.fingerprint):
                clicked = True
                break
            # ограничиваем максимум кликов
            i += 1
            if i >= self._max_iterations:
                return clicked

        return clicked

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
