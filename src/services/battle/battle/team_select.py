import time
from logging import Logger

from structlog import getLogger

from configs.settings import SelectionConfig
from core.randomizer import randomizer
from domain.types import RoomElement, Timeout
from exceptions import ApplicationError
from interfaces.output import IMouseClick
from models.dto import ClickArea, Titan
from services.fingerprint_match import match_fingerprint
from services.titan_catalog import TitanCatalog
from vision.screen import take_print

logger: Logger = getLogger(__name__)


class TeamSelectService:
    def __init__(
        self,
        titan_catalog: TitanCatalog,
        selected_click_areas: list[ClickArea],
        selection_cfg: SelectionConfig,
        clicker: IMouseClick,
        timeout: Timeout,
    ) -> None:
        self._catalog = titan_catalog
        self._selected_click_areas = selected_click_areas
        self._clicker = clicker
        self._selection_cfg = selection_cfg
        self._timeout = timeout

    def select_team(
        self,
        current_team: set[str],
        expected_team: set[str],
        element: RoomElement,
    ) -> None:
        logger.debug(
            f"Смена команды. Текущая команда: {current_team},"
            f"ожидаемая команда: {expected_team}"
        )
        current_titans, expected_titans = self._load_titans(current_team, expected_team)
        missing = set(expected_titans) - set(current_titans)
        logger.debug(
            f"Требуется убрать: {current_team - expected_team}, добавить: {missing}"
        )
        # убираем лишних титанов
        click_order = self._click_position_order(current_titans, expected_titans)

        for click_area_idx in click_order:
            area = self._selected_click_areas[click_area_idx]
            self._clicker.mouse_click(area.c, area.width, area.height)
            time.sleep(randomizer.uniform(0.35, 0.64))

        self._clicker.hide_mouse()
        # выбираем недостающих титанов
        for titan in missing:
            self._select_titan(titan, element)

    def _load_titans(
        self, current_team: set[str], expected_team: set[str]
    ) -> tuple[list[Titan], list[Titan]]:
        current_titan_team: list[Titan] = []
        expected_titan_team: list[Titan] = []

        for name in current_team.union(expected_team):
            titan = self._catalog.get_titan_by_name(name)
            if titan.name in current_team:
                current_titan_team.append(titan)
            if titan.name in expected_team:
                expected_titan_team.append(titan)

        return current_titan_team, expected_titan_team

    def _click_position_order(
        self, current_titans: list[Titan], expected_titans: list[Titan]
    ) -> list[int]:
        """
        Собирает очередь из позиций на экране, по которым нужно нажать чтобы
        убрать лишних титанов.

        Например, текущая команда: ["Молох", "Вулкан", "Араджи", "Игнис", "Ашерона"].
        Нужно сделать: ["Араджи", "Игнис", "Ашерона"]

        Нужно нажать на Молоха и Вулкана, чтобы их убрать.
        Молох самый первый (0 индекс), после нажатия все титаны сместятся
        и их индексы тоже. На 0 индексе будет Вулкан, соответственно второй
        клик будет тоже по 0 позиции. Т.е метод вернет [0, 0].

        Args:
            current_titans: Список текущей команды
            expected_titans: Список ожидаемой команды.

        Returns:
            Список индексов
        """
        current_titans.sort(key=lambda x: x.position)
        excess = set(current_titans) - set(expected_titans)
        click_order = []
        shift = 0

        for i, titan in enumerate(current_titans):
            if titan in excess:
                click_order.append(i - shift)
                shift += 1

        return click_order

    def _select_titan(self, titan: Titan, element: RoomElement) -> None:
        """
        Выбирает титана в команду.
        Кнопка "Фильтры" -> фильр по элементу -> фильтр по роли -> кнопка "Фильтры" -> клик по титану.
        """
        if element == "common":
            self.__set_filter(titan)

        time.sleep(randomizer.uniform(0.96, 1.47))

        for pos, cfg in self._selection_cfg.check_positions.items():
            fingerprint = take_print(cfg.coordinates)
            logger.debug(f"Чек позиции {pos}, отпечаток: {fingerprint}")

            if match_fingerprint(fingerprint, titan.fingerprint, tolerance=17):
                logger.info(f"Титан {titan.name} обнаружен на позиции {pos}")
                area = cfg.click_area
                self._clicker.mouse_click(area.c, area.width, area.height)
                return

        logger.info(f"Не удалось найти титана: name={titan.name}")
        raise ApplicationError()

    def __set_filter(self, titan: Titan) -> None:
        filter_area = self._selection_cfg.filter_button
        element_area = self._selection_cfg.elements[titan.element]
        role_area = self._selection_cfg.roles[titan.role]
        self._clicker.mouse_click(filter_area.c, filter_area.width, filter_area.height)
        self._clicker.mouse_click(
            element_area.c, element_area.width, element_area.height
        )
        self._clicker.mouse_click(role_area.c, role_area.width, role_area.height)
        self._clicker.mouse_click(filter_area.c, filter_area.width, filter_area.height)
