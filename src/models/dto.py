from dataclasses import dataclass, field
from pydantic import BaseModel
from domain.types import FingerPrint, RoomElement, TitanRole, TitanElement


class ClickArea(BaseModel):
    x: int
    y: int
    width: int
    height: int

    def c(self) -> tuple[int, int]:
        return (self.x, self.y)


class Titan(BaseModel):
    fingerprint: FingerPrint
    name: str
    element: TitanElement
    role: TitanRole
    position: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Titan):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class State:
    _levels_completed: int = field(default=0, init=False)
    _current_level: int = field(default=1, init=False)
    _current_level_calibrated: bool = field(default=False, init=False)
    _need_healing: set[str] = field(default_factory=set, init=False)
    _room_element: RoomElement | None = field(default=None, init=False)

    @property
    def need_healing(self) -> set[str]:
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

    def add_need_healing(self, titan_name: str) -> None:
        self._need_healing.add(titan_name)

    @property
    def room_element(self) -> RoomElement | None:
        return self._room_element

    @room_element.setter
    def room_element(self, value: RoomElement) -> None:
        self._room_element = value

    def up_level(self) -> None:
        self._levels_completed += 1
        self._current_level += 1

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
