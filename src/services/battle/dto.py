from copy import copy
from dataclasses import dataclass, field
from logging import Logger

from domain.types import RoomElement
from structlog import getLogger


logger: Logger = getLogger(__name__)


@dataclass
class BattleState:
    teams: dict[RoomElement, list[list[str]]]
    healing_team: list[str]
    current_team: list[str] = field(default_factory=list, init=False)
    __room_element: RoomElement | None = field(default=None, init=False)
    __team_index: int = field(default=0, init=False)
    need_healing: set[str] = field(default_factory=set, init=False)

    def start(self, element: RoomElement) -> None:
        self.__room_element = element

        if self.need_healing and not self.__team_index and element == "common":
            titan: str = next(iter(self.need_healing))
            team = copy(self.healing_team)
            team.append(titan)
            self.current_team = team
        else:
            try:
                teams = self.teams[self.__room_element]
                logger.debug(
                    f"Выбор команды: element: {element}, "
                    f"команды: {teams}, index: {self.__team_index}"
                )
                self.current_team = teams[self.__team_index]
            except IndexError:
                logger.debug(f"Команда не найдена")
                self.current_team = []

    def clear(self) -> None:
        logger.debug("Очистка состояния боя")
        self.__team_index = 0
        self.__room_element = None
        self.current_team.clear()

    def lose(self) -> None:
        logger.debug("Бой проигран")
        self.__team_index += 1
        try:
            teams = self.teams[self.__room_element]
            logger.debug(
                f"Выбор команды: element: {self.__room_element}, "
                f"команды: {teams}, index: {self.__team_index}"
            )
            assert self.__room_element
            self.current_team = teams[self.__team_index]
        except IndexError:
            logger.debug(f"Команда не найдена")
            self.current_team = []


@dataclass
class TitanStatus:
    name: str
    health: float
    energy: float
