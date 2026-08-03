from dataclasses import dataclass, field
from typing import Literal, TypedDict


RoomPosition = Literal["left", "right", "center"]
RoomTypes = Literal["common", "earth", "water", "fire"]
TitanElements = Literal["earth", "water", "fire", "light", "dark", "elarit"]
TitalRoles = Literal["tank", "archer", "summomer", "super", "support"]


class RoomCoordinates(TypedDict):
    left: list[tuple[int, int]]
    right: list[tuple[int, int]]
    center: list[tuple[int, int]]


class ClickArea(TypedDict):
    x: int
    y: int
    width: int
    height: int


class RoomClickAreas(TypedDict):
    left: ClickArea
    right: ClickArea
    center: ClickArea


class SelectionFingerprints(TypedDict):
    common: list[tuple[int, int, int]]
    earth: list[tuple[int, int, int]]
    water: list[tuple[int, int, int]]
    fire: list[tuple[int, int, int]]


@dataclass
class FoundElement:
    element: RoomTypes
    position: RoomPosition


@dataclass
class Titan:
    name: str
    health_prc: float
    energy_prc: float
    element: TitanElements
    role: TitalRoles


@dataclass
class State:
    room_position: RoomPosition | None = None
    available_elements: list[FoundElement] = field(default_factory=list)
    titan_count: int | None = None
    titans: list[Titan] = field(default_factory=list)
    _win: bool = False
    _has_dead: bool = False

    @property
    def win(self) -> bool:
        return self._win

    @win.setter
    def win(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("win must be a boolean")
        self._win = value
    
    @property
    def has_dead(self) -> bool:
        return self._has_dead

    @has_dead.setter
    def has_dead(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("has_dead must be a boolean")
        self._has_dead = value