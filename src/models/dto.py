from dataclasses import dataclass, field
from typing import Literal, TypedDict


RoomPosition = Literal["left", "right", "center"]
RoomTypes = Literal["common", "earth", "water", "fire"]


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
class State:
    room_position: RoomPosition | None = None
    available_elements: list[FoundElement] = field(default_factory=list)
