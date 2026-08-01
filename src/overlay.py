from __future__ import annotations

import logging
import queue
import signal
import sys
import threading
from collections.abc import Callable
from contextlib import AbstractContextManager
from threading import Event

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel, QTextEdit, QVBoxLayout, QWidget


def _mono_font(point_size: int) -> QFont:
    """Prefer a real monospace face on Windows/Linux/macOS."""
    for family in ("Consolas", "Cascadia Mono", "Menlo", "DejaVu Sans Mono", "monospace"):
        if family == "monospace" or family in QFontDatabase.families():
            font = QFont(family, point_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(point_size)
    return font


class _QueueLogHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue[str], maxsize: int = 500) -> None:
        super().__init__()
        self._queue = log_queue
        self._maxsize = maxsize

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            while self._queue.qsize() >= self._maxsize:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
            self._queue.put_nowait(msg)
        except Exception:
            self.handleError(record)


class _OverlayWindow(QWidget):
    def __init__(
        self,
        log_queue: queue.Queue[str],
        *,
        width: int = 420,
        height: int = 220,
        opacity: float = 0.82,
        max_lines: int = 120,
    ) -> None:
        super().__init__()
        self._queue = log_queue
        self._max_lines = max_lines
        self._drag_offset: tuple[int, int] | None = None

        self.setWindowTitle("hw-dungeon-bot logs")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(opacity)
        self.resize(width, height)

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
        self._text.setFont(_mono_font(10))
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

        self._place_bottom_right()

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._drain_queue)
        self._timer.start()

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

    def _drain_queue(self) -> None:
        changed = False
        while True:
            try:
                line = self._queue.get_nowait()
            except queue.Empty:
                break
            self._text.append(line)
            changed = True

        if not changed:
            return

        doc = self._text.document()
        while doc.blockCount() > self._max_lines:
            cursor = self._text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self._text.verticalScrollBar().setValue(self._text.verticalScrollBar().maximum())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class LogOverlay(AbstractContextManager["LogOverlay"]):
    """Always-on-top semi-transparent log window.

    Qt runs on the calling thread; pass the bot loop to :meth:`run`.
    """

    def __init__(
        self,
        *,
        logger_name: str | None = None,
        level: int = logging.INFO,
        width: int = 420,
        height: int = 220,
        opacity: float = 0.82,
    ) -> None:
        self._logger_name = logger_name
        self._level = level
        self._width = width
        self._height = height
        self._opacity = opacity

        self._queue: queue.Queue[str] = queue.Queue(maxsize=500)
        self._handler: _QueueLogHandler | None = None
        self._own_stream: logging.Handler | None = None

    def __enter__(self) -> LogOverlay:
        self._handler = _QueueLogHandler(self._queue)
        self._handler.setLevel(self._level)
        self._handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
        )

        target = logging.getLogger(self._logger_name) if self._logger_name else logging.getLogger()
        target.setLevel(self._level)
        target.addHandler(self._handler)

        has_stream = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in target.handlers
        )
        if not has_stream:
            stream = logging.StreamHandler(sys.stderr)
            stream.setLevel(self._level)
            stream.setFormatter(self._handler.formatter)
            target.addHandler(stream)
            self._own_stream = stream

        return self

    def __exit__(self, *exc: object) -> None:
        target = logging.getLogger(self._logger_name) if self._logger_name else logging.getLogger()
        if self._handler is not None:
            target.removeHandler(self._handler)
            self._handler = None
        if self._own_stream is not None:
            target.removeHandler(self._own_stream)
            self._own_stream = None

    def run(self, work: Callable[[], None], *, stop_event: Event | None = None) -> None:
        """Show the overlay and run ``work`` in a background thread until it returns.

        ``stop_event`` (hotkey / Ctrl+C) closes the Qt window immediately; the worker
        is expected to notice the same event and exit soon after.
        """
        error: list[BaseException] = []

        def _target() -> None:
            try:
                work()
            except BaseException as exc:  # noqa: BLE001 - re-raise after Qt exits
                error.append(exc)

        worker = threading.Thread(target=_target, name="bot-worker", daemon=True)
        worker.start()

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv[:1])

        window = _OverlayWindow(
            self._queue,
            width=self._width,
            height=self._height,
            opacity=self._opacity,
        )
        window.show()

        previous_sigint = signal.getsignal(signal.SIGINT)

        def _request_stop(*_args: object) -> None:
            if stop_event is not None:
                stop_event.set()
            app.quit()

        # Qt's C++ loop swallows the default KeyboardInterrupt; handle SIGINT ourselves.
        # The poll timer below regularly returns into Python so the handler can run.
        signal.signal(signal.SIGINT, _request_stop)

        def _poll_worker() -> None:
            if not worker.is_alive() or (stop_event is not None and stop_event.is_set()):
                app.quit()

        poll = QTimer()
        poll.setInterval(150)
        poll.timeout.connect(_poll_worker)
        poll.start()

        try:
            app.exec()
        finally:
            signal.signal(signal.SIGINT, previous_sigint)
            if stop_event is not None:
                stop_event.set()
            poll.stop()
            window.close()

        worker.join(timeout=2)
        if error:
            raise error[0]
