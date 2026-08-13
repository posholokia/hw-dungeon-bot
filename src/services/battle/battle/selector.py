from threading import Event

from interfaces.output import IMouseClick
from models.dto import ClickArea


class BattleSelectorService:
    def __init__(
        self,
        clicker: IMouseClick,
        autobattle_button: ClickArea,
    ) -> None:
        self._clicker = clicker
        self._autobattle_button = autobattle_button

    def click_autobattle(self, stop_event: Event) -> None:
        self._clicker.mouse_click(
            self._autobattle_button.c,
            self._autobattle_button.width,
            self._autobattle_button.height,
        )
