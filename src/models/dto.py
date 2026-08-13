from dataclasses import dataclass, field

from pydantic import BaseModel

from domain.types import FingerPrint, RoomElement, TitanElement, TitanRole


class ClickArea(BaseModel):
    x: int
    y: int
    width: int
    height: int

    @property
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
    _room_element: RoomElement | None = field(default=None, init=False)

    @property
    def current_level(self) -> int:
        return self._current_level

    @current_level.setter
    def current_level(self, value: int) -> None:
        self._current_level = value

    @property
    def levels_completed(self) -> int:
        return self._levels_completed

    @property
    def room_element(self) -> RoomElement:
        assert self._room_element
        return self._room_element

    @room_element.setter
    def room_element(self, value: RoomElement) -> None:
        self._room_element = value

    def up_level(self) -> None:
        self._levels_completed += 1
        self._current_level += 1
