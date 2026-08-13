import random
import time
from logging import Logger

from pynput.mouse import Button, Controller  # type: ignore [import-untyped]
from structlog import getLogger

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
            x = random.randint(c[0], c[0] + width - 1)
            y = random.randint(c[1], c[1] + height - 1)
        else:
            x = c[0]
            y = c[1]
        time.sleep(random.uniform(0.256, 0.434))
        self._mouse.position = (x, y)
        self._mouse.click(Button.left)
        logger.debug(f"Клик мышью по координатам: x={x}, y={y}")
