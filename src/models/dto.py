from dataclasses import dataclass, field
from pydantic import BaseModel
from domain.types import TitalRoles, TitanElements


class ClickArea(BaseModel):
    x: int
    y: int
    width: int
    height: int


@dataclass
class Titan:
    name: str
    health_prc: float
    energy_prc: float
    element: TitanElements
    role: TitalRoles

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Titan):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class State:
    _levels_completed: int = field(default=0, kw_only=True, init=False)
    _current_level: int = field(default=1, kw_only=True, init=False)
    _current_level_calibrated: bool = field(default=False, kw_only=True, init=False)
    _need_healing: set[Titan] = field(default_factory=set, kw_only=True, init=False)

    @property
    def need_healing(self) -> set[Titan]:
        return self._need_healing

    @property
    def current_level(self) -> int:
        return self._current_level

    @property
    def current_level_calibrated(self) -> bool:
        return self._current_level_calibrated

    @property
    def levels_completed(self) -> int:
        return self._levels_completed

    def add_need_healing(self, titan: Titan) -> None:
        if not isinstance(titan, Titan):
            raise TypeError("titan must be a Titan")
        if titan in self._need_healing:
            return
        self._need_healing.add(titan)

    def up_level(self) -> None:
        self._levels_completed += 1
        self.current_level += 1

    def calibrate_current_level(self, level: int) -> None:
        """
        Калибровка текущего уровня. Калибровка выполняется только на крайней
        комнате этажа (последняя цифра уровня 5 или 0).
        Если переданный уровень не является крайней комнатой, то калибровка не выполняется.
        """
        if level != 5 and level != 10:
            return
        self.current_level_calibrated = True
        self.current_level = level

    # @property
    # def win(self) -> bool:
    #     return self._win

    # @win.setter
    # def win(self, value: bool) -> None:
    #     if not isinstance(value, bool):
    #         raise TypeError("win must be a boolean")
    #     self._win = value

    # @property
    # def has_dead(self) -> bool:
    #     return self._has_dead

    # @has_dead.setter
    # def has_dead(self, value: bool) -> None:
    #     if not isinstance(value, bool):
    #         raise TypeError("has_dead must be a boolean")
    #     self._has_dead = value
