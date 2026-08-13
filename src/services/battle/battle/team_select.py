from configs.settings import SelectionConfig
from interfaces.output import IMouseClick
from models.dto import ClickArea, Titan
from services.titan_catalog import TitanCatalog


class TeamSelectService:
    def __init__(
        self,
        titan_catalog: TitanCatalog,
        selected_click_areas: list[ClickArea],
        selection_cfg: SelectionConfig,
        clicker: IMouseClick,
    ) -> None:
        self._catalog = titan_catalog
        self._selected_click_areas = selected_click_areas
        self._clicker = clicker
        self._selection_cfg = selection_cfg

    def select_team(self, current_team: set[str], expected_team: set[str]) -> None:
        current_titans, expected_titans = self._load_titans(current_team, expected_team)

        # убираем лишних титанов
        click_order = self._click_position_order(current_titans, expected_titans)
        for click_area_idx in click_order:
            area = self._selected_click_areas[click_area_idx]
            self._clicker.mouse_click(area.c, area.width, area.height)

        # выбираем недостающих титанов
        missing = set(expected_titans) - set(current_titans)

        for titan in missing:
            self._select_titan(titan)

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
        current_positions = {t.position for t in current_titans}
        expected_positions = {t.position for t in expected_titans}
        all_positions = list(current_positions) + list(expected_positions)
        all_positions.sort()

        click_order = []
        c = 0

        for pos in all_positions:
            if pos in expected_positions and pos not in current_positions:
                continue
            elif pos in expected_positions and pos in current_positions:
                c += 1
                continue
            elif pos not in expected_positions and pos in current_positions:
                click_order.append(c)
                continue

        return click_order

    def _select_titan(self, titan: Titan) -> None:
        """
        Выбирает титана в команду.
        Кнопка "Фильтры" -> фильр по элементу -> фильтр по роли -> кнопка "Фильтры" -> клик по титану.
        """
        filter_area = self._selection_cfg.filter_button
        element_area = self._selection_cfg.elements[titan.element]
        role_area = self._selection_cfg.roles[titan.role]
        titan_area = self._selection_cfg.titan

        self._clicker.mouse_click(filter_area.c, filter_area.width, filter_area.height)
        self._clicker.mouse_click(
            element_area.c, element_area.width, element_area.height
        )
        self._clicker.mouse_click(role_area.c, role_area.width, role_area.height)
        self._clicker.mouse_click(filter_area.c, filter_area.width, filter_area.height)
        self._clicker.mouse_click(titan_area.c, titan_area.width, titan_area.height)
