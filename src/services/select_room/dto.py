from dataclasses import dataclass

from domain.types import ElementPositions, RoomElements


@dataclass
class FoundElement:
    element: RoomElements
    position: ElementPositions
