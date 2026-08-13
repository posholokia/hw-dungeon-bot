from copy import copy
from dataclasses import dataclass, field

from domain.types import RoomElement


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

        if need_heal := self.need_healing and not self.__team_index:
            titan: str = next(iter(need_heal))
            team = copy(self.healing_team)
            team.append(titan)
            self.current_team = team
        else:
            try:
                self.current_team = self.teams[self.__room_element][self.__team_index]
            except IndexError:
                self.current_team = []

    def win(self) -> None:
        self.__team_index = 0
        self.__room_element = None
        self.current_team.clear()

    def lose(self) -> None:
        self.__team_index += 1
        try:
            self.current_team = self.teams[self.__room_element][self.__team_index]
        except IndexError:
            self.current_team = []


@dataclass
class TitanStatus:
    name: str
    health: int
    energy: int
