from collections.abc import Callable

from structlog import getLogger

from configs.settings import BarConfig
from domain.types import Coordinate, CoordinateList, FingerPrint
from interfaces.output import IMouseClick
from models.dto import Titan
from services.battle.dto import BattleState, TitanStatus
from services.titan_catalog import TitanCatalog
from vision.screen import take_print

logger = getLogger(__name__)


def is_green(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r <= 77 and g >= 189 and b <= 49


def is_yellow(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return 194 <= r <= 247 and 171 <= g <= 219 and b <= 39


class HealthScanerService:
    def __init__(
        self,
        windows: dict[int, CoordinateList],
        health_bar: BarConfig,
        energy_bar: BarConfig,
        titan_catalog: TitanCatalog,
        clicker: IMouseClick,
    ) -> None:
        self._windows = windows
        self._health_bar = health_bar
        self._energy_bar = energy_bar
        self._catalog = titan_catalog
        self._clicker = clicker

    def scan_health(self, battle_state: BattleState) -> list[TitanStatus]:
        logger.info("Анализ здоровья/энергии после боя")
        self._clicker.hide_mouse()
        team_len = len(battle_state.current_team)
        windows = self._windows[team_len]
        result: list[TitanStatus] = []
        team: list[Titan] = []
        # нужно отсортировать команду по позициям,
        # чтобы корректно сопоставить сканируемое окно с титаном
        for titan_name in battle_state.current_team:
            titan = self._catalog.get_titan_by_name(titan_name)
            team.append(titan)

        team.sort(key=lambda x: x.position)

        for window, titan in zip(windows, team, strict=True):
            health_print = self.__scan_bar(window, self._health_bar)
            energy_print = self.__scan_bar(window, self._energy_bar)
            health_prc = self.__by_prc(health_print, is_green, self._health_bar.lenght)
            energy_prc = self.__by_prc(energy_print, is_yellow, self._energy_bar.lenght)
            result.append(
                TitanStatus(name=titan.name, health=health_prc, energy=energy_prc)
            )
        for status in result:
            logger.info(f"{status}")
        return result

    def __by_prc(
        self,
        fingerprint: FingerPrint,
        color: Callable[[tuple[int, int, int]], bool],
        divider: int,
    ) -> float:
        color_sum = sum(color(point) for point in fingerprint)
        return (color_sum / divider) * 100

    def __scan_bar(self, window: Coordinate, cfg: BarConfig) -> FingerPrint:
        start_x = window[0] + cfg.x
        start_y = window[1] + cfg.y
        points = [(start_x + i, start_y) for i in range(cfg.lenght)]
        return take_print(points)
