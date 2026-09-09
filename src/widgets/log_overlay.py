from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


def _mono_font(point_size: int) -> QFont:
    for family in (
        "Consolas",
        "Cascadia Mono",
        "Menlo",
        "DejaVu Sans Mono",
        "monospace",
    ):
        if family == "monospace" or family in QFontDatabase.families():
            font = QFont(family, point_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(point_size)
    return font


class LogOverlayWindow(QWidget):
    """Оверлей с отображением логов"""

    _append_signal = Signal(str)

    def __init__(
        self,
        *,
        x: int = 1505,
        y: int = 280,
        width: int = 435,
        height: int = 220,
        opacity: float = 0.82,
        max_lines: int = 120,
    ) -> None:
        super().__init__()
        self._max_lines = max_lines
        self._drag_offset: QPoint | None = None

        self.setWindowTitle("hw-dungeon-bot logs")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(opacity)
        self.setGeometry(x, y, width, height)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(4)

        title = QLabel("logs  ·  drag to move")
        title.setStyleSheet("color: #c8c8c8; background: transparent;")
        title.setFont(_mono_font(9))
        root.addWidget(title)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setFrameShape(QTextEdit.Shape.NoFrame)
        self._text.setFont(_mono_font(8))
        self._text.setStyleSheet(
            """
            QTextEdit {
                color: #e8e8e8;
                background-color: rgba(18, 18, 18, 200);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 6px;
                padding: 6px;
            }
            """
        )
        root.addWidget(self._text)
        self._append_signal.connect(self._append_impl)

    def append(self, text: str) -> None:
        """Push one log line; safe to call from any thread."""
        self._append_signal.emit(text)

    def _append_impl(self, text: str) -> None:
        self._text.append(text)
        doc = self._text.document()
        while doc.blockCount() > self._max_lines:
            cursor = self._text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
        self._text.verticalScrollBar().setValue(
            self._text.verticalScrollBar().maximum()
        )

    def _place_bottom_right(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        margin = 16
        self.move(
            geo.right() - self.width() - margin,
            geo.bottom() - self.height() - margin,
        )

    """##############   Перетаскивание оверлея   ##############"""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    """"#######################################################"""
