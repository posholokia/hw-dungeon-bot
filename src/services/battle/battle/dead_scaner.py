from domain.types import CoordinateList, FingerPrint
from interfaces.output import IMouseClick
from services.fingerprint_match import match_fingerprint
from vision.screen import take_print


class DeadScanService:
    def __init__(
        self,
        windows: dict[int, CoordinateList],
        offsets: CoordinateList,
        fingerprint: FingerPrint,
        clicker: IMouseClick,
    ) -> None:
        self._windows = windows
        self._offsets = offsets
        self._fingerprint = fingerprint
        self._clicker = clicker

    def has_dead(self, team_len: int) -> bool:
        windows = self._windows[team_len]
        self._clicker.hide_mouse()

        for window in windows:
            start_x, start_y = window
            points = [(start_x + x, start_y + y) for x, y in self._offsets]
            fingerprint = take_print(points)

            if match_fingerprint(fingerprint, self._fingerprint):
                return True

        return False
