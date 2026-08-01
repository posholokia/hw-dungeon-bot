from dataclasses import dataclass
from typing import Literal, TypedDict


RoomPosition = Literal["left", "right", "center"]
RoomTypes = Literal["common", "earth", "water", "fire"]


class RoomCoordinates(TypedDict):
    left: list[tuple[int, int]]
    right: list[tuple[int, int]]
    center: list[tuple[int, int]]


@dataclass
class State:
    level: int

    def up_level(self) -> None:
        self.level = self.level + 1

    def get_room_position(self) -> RoomPosition:
        if self.level % 10 == 0 or self.level % 10 == 1:
            return "left"
        elif self.level % 10 == 5 or self.level % 10 == 6:
            return "right"
        else:
            return "center"
