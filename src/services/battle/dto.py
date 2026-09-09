from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from logging import Logger

from structlog import getLogger

from domain.types import RoomElement

logger: Logger = getLogger(__name__)


@dataclass
class TitanHealth:
    name: str
    health: float

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, type(self)):
            return False

        return self.name == value.name


@dataclass
class BattleState:
    teams: dict[RoomElement, list[list[str]]]
    healing_team: list[str]
    current_team: list[str] = field(default_factory=list, init=False)
    __room_element: RoomElement | None = field(default=None, init=False)
    __team_index: int = field(default=0, init=False)
    __need_healing: deque[TitanHealth] = field(default_factory=deque, init=False)
    __is_healing_try: bool = field(default=False, init=False)

    @property
    def need_healing(self) -> deque[TitanHealth]:
        return self.__need_healing.copy()

    @property
    def is_healing_try(self) -> bool:
        return self.__is_healing_try

    def add_to_leal_list(self, titan: TitanHealth) -> None:
        self.__need_healing.append(titan)

    def remove_from_heal_list(self, titan: TitanHealth) -> None:
        if titan in self.__need_healing:
            self.__need_healing.remove(titan)

    def start(self, element: RoomElement) -> None:
        self.__room_element = element

        if self.need_healing and not self.__team_index and element == "common":
            titan: TitanHealth = next(iter(self.need_healing))
            team = self._get_healing_team()
            team.append(titan.name)
            self.current_team = team
            self.__is_healing_try = True
        else:
            try:
                teams = self._get_element_teams()
                logger.debug(
                    f"Выбор команды: element: {element}, "
                    f"команды: {teams}, index: {self.__team_index}"
                )
                self.current_team = teams[self.__team_index]
            except IndexError:
                logger.debug("Команда не найдена")
                self.current_team = []
            self.__is_healing_try = False

    @property
    def room_element(self) -> RoomElement:
        if self.__room_element is None:
            raise ValueError("Элемент комнтаы еще не проскнирован")
        return self.__room_element

    def _get_element_teams(self) -> list[list[str]]:
        teams = deepcopy(self.teams)
        assert self.__room_element
        return teams[self.__room_element]

    def _get_healing_team(self) -> list[str]:
        return deepcopy(self.healing_team)

    def clear(self) -> None:
        logger.debug("Очистка состояния боя")
        self.__team_index = 0
        self.__room_element = None
        self.current_team.clear()

    def lose(self) -> None:
        logger.debug("Бой проигран")

        if not self.__is_healing_try:
            self.__team_index += 1

        try:
            assert self.__room_element
            teams = self._get_element_teams()
            logger.debug(
                f"Выбор команды: element: {self.__room_element}, "
                f"команды: {teams}, index: {self.__team_index}"
            )
            assert self.__room_element
            self.current_team = teams[self.__team_index]
        except IndexError:
            logger.debug("Команда не найдена")
            self.current_team = []


@dataclass
class TitanStatus:
    name: str
    health: float
    energy: float
