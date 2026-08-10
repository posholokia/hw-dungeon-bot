from dataclasses import dataclass

from domain.types import ElementPosition, RoomElement


@dataclass
class FoundElement:
    element: RoomElement
    position: ElementPosition
