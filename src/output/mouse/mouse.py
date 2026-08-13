import random
import time
from logging import Logger

from pynput.mouse import Button, Controller  # type: ignore [import-untyped]
from structlog import getLogger

logger: Logger = getLogger(__name__)


class MouseController:
    def __init__(self) -> None:
        self._mouse = Controller()

    def click(self, x: int, y: int) -> None:
        time.sleep(random.uniform(0.086, 0.134))
        self._mouse.position = (x, y)
        self._mouse.click(Button.left)
        logger.debug(f"Клик мышью по координатам: x={x}, y={y}")
