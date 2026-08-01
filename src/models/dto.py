from dataclasses import dataclass
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


@dataclass
class State:
    room_position: RoomPosition | None = None
