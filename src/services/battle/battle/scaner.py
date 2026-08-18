import time
from threading import Event

from structlog import getLogger

from domain.types import CoordinateList, FingerPrint, Timeout
from exceptions import ApplicationError, StopApplicationError
from interfaces.cfg import IScreenButton
from models.dto import Titan
from services.fingerprint_match import match_fingerprint
from services.titan_catalog import TitanCatalog
from services.wait_clicker import WaitClickCheckService
from vision.screen import take_print

logger = getLogger(__name__)


class BattleScannerService:
    def __init__(
        self,
        titan_catalog: TitanCatalog,
        analyze_team_coords: list[CoordinateList],
        timeout: Timeout,
        autobattle_cfg: IScreenButton,
        result_coordinates: CoordinateList,
        result_fingerprints: dict[str, FingerPrint],
        waiter: WaitClickCheckService,
    ) -> None:
        self._analyze_team_coords = analyze_team_coords
        self._titan_catalog = titan_catalog
        self._autobattle_cfg = autobattle_cfg
        self._result_coordinates = result_coordinates
        self._result_fingerprints = result_fingerprints
        self._timeout = timeout
        self._waiter = waiter

    def scan_team(self) -> set[str]:
        time.sleep(1.2)
        current_team: list[str] = []
        catalog: dict[str, Titan] = self._titan_catalog.get_titans()

        for i in range(1, len(self._analyze_team_coords) + 1):
            name = self.__scan_position(i, catalog)
            if name == "<EMPTY>":
                logger.info(f"Позиция {i} пустая")

            current_team.append(name)
            logger.info(
                f"Обнаружен титан: Позиция {i}, {name}, команда: {current_team}"
            )

        team = self.__validate_team(current_team)
        cleaned_team: set[str] = set()

        for name in team:
            if name != "<EMPTY>":
                cleaned_team.add(name)

        return cleaned_team

    def __validate_team(self, current_team: list[str]) -> list[str]:
        team = current_team.copy()
        team.reverse()
        last_active_position: int | None = None
        catalog: dict[str, Titan] = self._titan_catalog.get_titans()
        replacement: dict[int, str] = {}

        for pos, name in enumerate(team, start=1):
            scan_tries = 0
            if name == "<EMPTY>" and last_active_position is None:
                continue
            elif last_active_position is None:
                last_active_position = pos

            if (
                last_active_position is not None
                and pos > last_active_position
                and name == "<EMPTY>"
            ):
                scan_pos = 6 - pos
                titan_name = name
                while titan_name == name:
                    time.sleep(0.1)
                    scan_tries += 1
                    titan_name = self.__scan_position(pos=scan_pos, catalog=catalog)

                    if scan_tries >= 10:
                        team.reverse()
                        raise ApplicationError(f"Невалидная команда: {team}")

                replacement[scan_pos] = titan_name

        team.reverse()

        for pos, name in replacement.items():
            team[pos - 1] = name

        return team

    def __scan_position(
        self,
        pos: int,
        catalog: dict[str, Titan],
    ) -> str:
        points = self._analyze_team_coords[pos - 1]
        start = time.perf_counter()
        scans = []  # debug only

        while time.perf_counter() - start < 5:
            scanned = take_print(points)
            scans.append(scanned)

            for name, titan in catalog.items():
                matched = match_fingerprint(scanned, titan.fingerprint, tolerance=17)
                if matched:
                    return name
            time.sleep(0.05)

        raise ApplicationError(
            f"Не удалось сматчить титана в позиции {pos}, отпечатки: {scans}"
        )

    def scan_autobattle(self, stop_event: Event) -> None:
        logger.info("Ожидание кнопки автобоя")
        finded = self._waiter.wait(
            coordinates=self._autobattle_cfg.coordinates,
            fingerprint=self._autobattle_cfg.fingerprint,
            stop_event=stop_event,
        )
        if not finded:
            raise ApplicationError("Не найдена кнопка автобоя")

    def scan_win_loose(self, stop_event: Event) -> bool:
        """
        Сканирует экран с результатом боя.
        Если победа - возвращает True, проигрыш - False.
        """
        start = time.perf_counter()
        logger.info("Waiting for win/lose screen")

        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                raise StopApplicationError()

            scanned = take_print(self._result_coordinates)

            if match_fingerprint(scanned, self._result_fingerprints["win"]):
                logger.info("Battle result: win")
                return True

            if match_fingerprint(scanned, self._result_fingerprints["lose"]):
                logger.info("Battle result: lose")
                return False

            if stop_event.wait(0.005):
                raise StopApplicationError()

        raise ApplicationError("Не удалось сматчить экран результата боя")
