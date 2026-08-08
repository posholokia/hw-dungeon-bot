from time import sleep

from structlog import get_logger

from core.depends.container import get_container
from core.logger.processors.overlay import OverlayProcessor
from core.logger.setup import setup_logging
from widgets.click_marker import ClickMarker
from widgets.qa_app import QaApp

overlay = get_container().get(OverlayProcessor)
setup_logging(overlay)
logger = get_logger()


def _work() -> None:
    # After QaApp.run started QApplication — widgets are safe to resolve.
    marker = get_container().get(ClickMarker)
    for i in range(10):
        logger.info(f"Test {i}")
        sleep(0.2)
        marker.flash_at(100 + i * 50, 100 + i * 50)
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.exception(e.__str__())


if __name__ == "__main__":
    # QaApp is fine before QApplication: it only holds factories.
    # Do NOT get(ClickMarker) / get(LogOverlayWindow) here.
    qa_app = get_container().get(QaApp)
    qa_app.run(_work, show_click_marker=True)
