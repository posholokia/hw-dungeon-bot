from abc import abstractmethod
from typing import Protocol

from domain.types import Coordinate, no_value


class IMouseClick(Protocol):
    @abstractmethod
    def mouse_click(
        self, c: Coordinate, width: int = no_value, height: int = no_value
    ) -> None:
        """
        Клик мыши на экране.
        Если ширина и высота не указаны, то клик будет в точке 'c', иначе в случайной области клика.

        Args:
            c: Отправная точка клика (координата)
            width: Ширина области клика
            height: Высота области клика
        """
