from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget
from structlog import getLogger

logger = getLogger(__name__)


class ClickMarker(QWidget):
    """Fullscreen-transparent crosshair shown briefly at a screen point."""

    _SIZE = 36
    _DURATION_MS = 1500

    _flash_signal = Signal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.resize(self._SIZE, self._SIZE)
        self.hide()
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self._flash_signal.connect(
            self._flash_impl,
            Qt.ConnectionType.QueuedConnection,
        )

    def flash_at(self, x: int, y: int) -> None:
        """Показать маркер на экране в точке (x, y)"""
        logger.info(f"Показать маркер на экране в точке ({x}, {y})")
        self._flash_signal.emit(x, y)

    @Slot(int, int)
    def _flash_impl(self, x: int, y: int) -> None:
        self.move(x - self._SIZE // 2, y - self._SIZE // 2)
        self.show()
        self.raise_()
        self._hide_timer.start(self._DURATION_MS)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(255, 64, 64, 230))
        pen.setWidth(3)
        painter.setPen(pen)
        mid = self._SIZE // 2
        painter.drawEllipse(QPoint(mid, mid), mid - 4, mid - 4)
        painter.drawLine(mid, 4, mid, self._SIZE - 4)
        painter.drawLine(4, mid, self._SIZE - 4, mid)
        painter.end()
