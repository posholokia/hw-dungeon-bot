from threading import Event

from domain.types import PreviewSeconds
from interfaces.output import IMouseClick
from models.dto import ClickArea


class BattleSelectorService:
    def __init__(
        self,
        clicker: IMouseClick,
        autobattle_button: ClickArea,
        preview_seconds: PreviewSeconds,
    ) -> None:
        self._clicker = clicker
        self._autobattle_button = autobattle_button
        self._preview_seconds = preview_seconds

    def click_autobattle(self, stop_event: Event) -> None:
        self._clicker.mouse_click(
            self._autobattle_button.c,
            self._autobattle_button.width,
            self._autobattle_button.height,
        )
        stop_event.wait(self._preview_seconds)
