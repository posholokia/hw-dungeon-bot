from __future__ import annotations

import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class HeartbeatWidget(QWidget):
    """Зелёный кружок: процесс жив, пока крутится Qt-цикл."""

    def __init__(
        self,
        *,
        x: int = 1831,
        y: int = 257,
        size: int = 48,
    ) -> None:
        super().__init__()
        self._size = size
        self._phase = 0.0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setGeometry(x, y, size, size)

        self._pulse = QTimer(self)
        self._pulse.setInterval(40)
        self._pulse.timeout.connect(self._tick)

    def showEvent(self, event) -> None:
        self._pulse.start()
        super().showEvent(event)

    def hideEvent(self, event) -> None:
        self._pulse.stop()
        super().hideEvent(event)

    def _tick(self) -> None:
        self._phase = (self._phase + 0.08) % math.tau
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        alpha = int(140 + 90 * (0.5 + 0.5 * math.sin(self._phase)))
        inset = 4
        diameter = self._size - inset * 2
        painter.setPen(QPen(QColor(40, 180, 70, 220), 2))
        painter.setBrush(QColor(50, 220, 90, alpha))
        painter.drawEllipse(inset, inset, diameter, diameter)
        painter.end()
