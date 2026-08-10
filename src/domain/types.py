from typing import Any, Literal, NewType

Coordinate = tuple[int, int]

CoordinateList = list[Coordinate]
FingerPrint = list[tuple[int, int, int]]


class NoValueObj:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NoValue"

    def __str__(self) -> str:
        return "NoValue"

    def __eq__(self, other: object) -> bool:
        return False


no_value: Any = NoValueObj()

RoomPosition = Literal["left", "right", "center"]
ElementPosition = Literal["left", "right", "center"]
RoomElement = Literal["common", "earth", "water", "fire"]
Timeout = NewType("Timeout", int)
PreviewSeconds = NewType("PreviewSeconds", float)
TitanElement = Literal["earth", "water", "fire", "light", "dark", "elarit"]
TitanRole = Literal["tank", "archer", "summomer", "super", "support"]
