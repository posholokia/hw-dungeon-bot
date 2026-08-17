import time
from logging import Logger

from pynput.mouse import Button, Controller  # type: ignore [import-untyped]
from structlog import getLogger

from core.randomizer import randomizer
from domain.types import Coordinate, no_value
from interfaces.output import IMouseClick

logger: Logger = getLogger(__name__)


class MouseController(IMouseClick):
    def __init__(self) -> None:
        self._mouse = Controller()

    def mouse_click(
        self, c: Coordinate, width: int = no_value, height: int = no_value
    ) -> None:
        if width and height:
            x = randomizer.randint(c[0], c[0] + width - 1)
            y = randomizer.randint(c[1], c[1] + height - 1)
        else:
            x = c[0]
            y = c[1]
        time.sleep(randomizer.uniform(0.126, 0.284))
        self._mouse.position = (x, y)
        self._mouse.click(Button.left)
        logger.debug(f"Клик мышью по координатам: x={x}, y={y}")

    def hide_mouse(self) -> None:
        self._mouse.position = (
            randomizer.randint(851, 1167),
            randomizer.randint(571, 744),
        )
