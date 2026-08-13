import copy
import time
from threading import Event

from structlog import getLogger

from domain.types import CoordinateList, FingerPrint, Timeout
from exceptions import StopApplicationError
from models.dto import Titan
from services.fingerprint_match import match_fingerprint
from services.titan_catalog import TitanCatalog
from vision.screen import take_print

logger = getLogger(__name__)


class BattleScannerService:
    def __init__(
        self,
        titan_catalog: TitanCatalog,
        analyze_team_coords: list[CoordinateList],
        timeout: Timeout,
        autobattle_coordinates: CoordinateList,
        autobattle_fingerprint: FingerPrint,
        result_coordinates: CoordinateList,
        result_fingerprints: dict[str, FingerPrint],
    ) -> None:
        self._analyze_team_coords = analyze_team_coords
        self._titan_catalog = titan_catalog
        self._autobattle_coordinates = autobattle_coordinates
        self._autobattle_fingerprint = autobattle_fingerprint
        self._result_coordinates = result_coordinates
        self._result_fingerprints = result_fingerprints
        self._timeout = timeout

    def scan_team(self) -> set[str]:
        time.sleep(1)
        current_team = set()
        catalog: dict[str, Titan] = copy.deepcopy(self._titan_catalog.get_titans())

        for coords in self._analyze_team_coords:
            fingerprint = take_print(coords)

            for name, titan in catalog.items():
                matched = match_fingerprint(fingerprint, titan.fingerprint)

                if matched:
                    logger.info(f"Обнаружен титан: {name}, команда: {current_team}")

                    if titan.name == "<EMPTY>":
                        continue

                    current_team.add(name)
                    break

        return current_team

    def scan_autobattle(self, stop_event: Event) -> None:
        start = time.perf_counter()
        logger.info("Ожидание кнопки автобоя")

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            scanned = take_print(self._autobattle_coordinates)

            if match_fingerprint(scanned, self._autobattle_fingerprint):
                return

            if stop_event.wait(timeout=0.005):
                return

        raise StopApplicationError("Не найдена кнопка автобоя")

    def scan_win_loose(self, stop_event: Event) -> bool:
        """
        Сканирует экран с результатом боя.
        Если победа - возвращает True, проигрыш - False.
        """
        start = time.perf_counter()
        logger.info("Waiting for win/lose screen")
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            scanned = take_print(self._result_coordinates)
            if match_fingerprint(scanned, self._result_fingerprints["win"]):
                logger.info("Battle result: win")
                return True
            if match_fingerprint(scanned, self._result_fingerprints["lose"]):
                logger.info("Battle result: lose")
                return False

            if stop_event.wait(0.005):
                return
        raise StopApplicationError("Не удалось сматчить экран результата боя")
