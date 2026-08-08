import random
from collections.abc import Callable

from structlog import get_logger

from domain.types import Coordinate, no_value
from widgets.click_marker import ClickMarker

logger = get_logger(__name__)


class DesignationClick:
    def __init__(self, marker: Callable[[], ClickMarker]) -> None:
        self._marker_factory = marker

    def mouse_click(
        self, c: Coordinate, width: int = no_value, height: int = no_value
    ) -> None:
        """
        Показывает курсор куда будет клик на экране.
        Если ширина и высота не указаны, то клик будет в точке 'c', иначе в случайной области клика.

        Args:
            c: Отправная точка клика (координата)
            width: Ширина области клика
            height: Высота области клика
        """
        try:
            if width and height:
                x = random.randint(c[0], c[0] + width - 1)
                y = random.randint(c[1], c[1] + height - 1)
            else:
                x = c[0]
                y = c[1]
            marker = self._marker_factory()
            marker.flash_at(x, y)
        except ValueError:
            logger.error(f"Invalid coordinates: {c}, width: {width}, height: {height}")
            raise
