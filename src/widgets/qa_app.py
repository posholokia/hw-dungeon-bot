from __future__ import annotations

import signal
import sys
import threading
from collections.abc import Callable
from threading import Event

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from configs.settings import debug
from widgets.click_marker import ClickMarker
from widgets.heartbeat import HeartbeatWidget
from widgets.log_overlay import LogOverlayWindow


class QaApp:
    """Qt shell for debug overlays: QApplication, log window, optional click marker."""

    def __init__(
        self,
        get_log_window: Callable[[], LogOverlayWindow],
        get_click_marker: Callable[[], ClickMarker],
        get_heartbeat: Callable[[], HeartbeatWidget],
    ) -> None:
        # Factories, not instances — widgets are created only after QApplication.
        self._get_log_window = get_log_window
        self._get_click_marker = get_click_marker
        self._get_heartbeat = get_heartbeat

    def run(
        self,
        work: Callable[[], None] | None = None,
        *,
        stop_event: Event | None = None,
        show_click_marker: bool = False,
    ) -> None:
        """Create QApplication, show overlays, run ``work`` in a background thread.

        Resolve Qt widgets only after QApplication exists. Logging via
        ``overlay_processor`` is safe once ``run`` has started.
        """
        error: list[BaseException] = []

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv[:1])

        if debug():
            overlay = self._get_log_window()
            overlay.show()

        marker: ClickMarker | None = None
        if show_click_marker:
            marker = self._get_click_marker()

        heartbeat = self._get_heartbeat()
        heartbeat.show()
        heartbeat.raise_()

        worker: threading.Thread | None = None
        if work is not None:

            def _target() -> None:
                try:
                    work()
                except BaseException as exc:  # noqa: BLE001 - re-raise after Qt exits
                    error.append(exc)

            worker = threading.Thread(target=_target, name="qa-worker", daemon=True)
            worker.start()

        previous_sigint = signal.getsignal(signal.SIGINT)

        def _request_stop(*_args: object) -> None:
            if stop_event is not None:
                stop_event.set()
            app.quit()

        signal.signal(signal.SIGINT, _request_stop)

        def _poll() -> None:
            if stop_event is not None and stop_event.is_set():
                app.quit()
                return
            if worker is not None and not worker.is_alive():
                app.quit()

        poll = QTimer()
        poll.setInterval(50)
        poll.timeout.connect(_poll)
        poll.start()

        try:
            app.exec()
        finally:
            signal.signal(signal.SIGINT, previous_sigint)
            if stop_event is not None:
                stop_event.set()
            poll.stop()
            if marker is not None:
                marker.hide()
                marker.close()
            heartbeat.hide()
            heartbeat.close()
            if debug():
                overlay.close()

        if worker is not None:
            worker.join(timeout=2)
        if error:
            raise error[0]
