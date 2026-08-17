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
        current_team: set[str] = set()
        catalog: dict[str, Titan] = self._titan_catalog.get_titans()

        for i, coords in enumerate(self._analyze_team_coords, start=1):
            discovered = False
            start = time.perf_counter()
            scans = []  # debug only

            while not discovered and time.perf_counter() - start < 5:
                scanned = take_print(coords)
                scans.append(scanned)

                for name, titan in catalog.items():
                    matched = match_fingerprint(
                        scanned, titan.fingerprint, tolerance=17
                    )
                    if matched:
                        discovered = True
                        if titan.name == "<EMPTY>":
                            logger.info(f"Позиция {i} пустая")
                            continue

                        current_team.add(name)
                        logger.info(
                            f"Обнаружен титан: Позиция {i}, {name}, "
                            f"команда: {current_team}"
                        )
                        break
                time.sleep(0.05)

            if not discovered:
                raise ApplicationError(
                    f"Не удалось сматчить титана в позиции {i}, отпечатки: {scans}"
                )

        return current_team

    # def scan_team(self) -> set[str]:
    #     time.sleep(2.4)
    #     current_team: set[str] = set()
    #     catalog: dict[str, Titan] = self._titan_catalog.get_titans()
    #     fingerprints_by_pos: dict[int, FingerPrint] = {}

    #     for i, coords in enumerate(self._analyze_team_coords, start=1):
    #         fingerprints_by_pos[i] = take_print(coords)

    #     logger.debug(f"Отпечатки команды: {fingerprints_by_pos}")

    #     matched_pos: list[int] = []
    #     for name, titan in catalog.items():
    #         for pos, fingerprint in fingerprints_by_pos.items():
    #             matched = match_fingerprint(
    #                 fingerprint, titan.fingerprint, tolerance=17
    #             )

    #             if matched:
    #                 matched_pos.append(pos)
    #                 if titan.name == "<EMPTY>":
    #                     logger.info(f"Позиция {pos} пустая")
    #                     continue

    #                 current_team.add(name)
    #                 logger.info(
    #                     f"Обнаружен титан: Позиция {pos}, {name}, команда: {current_team}"
    #                 )
    #                 del fingerprints_by_pos[pos]
    #                 break

    #     if len(matched_pos) != 5:
    #         raise ApplicationError(
    #             f"Не удалось сматчить все позиции. Сматчены позиции: {matched_pos}"
    #         )
    #     return current_team

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
