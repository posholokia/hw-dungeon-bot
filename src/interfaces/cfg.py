from typing import Protocol

from domain.types import CoordinateList, FingerPrint
from models.dto import ClickArea


class IScreenButton(Protocol):
    click_area: ClickArea
    coordinates: CoordinateList
    fingerprint: FingerPrint
