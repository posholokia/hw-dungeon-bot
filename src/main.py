import sys
from functools import partial
from threading import Event

from core.depends.container import get_container
from core.logger.processors.overlay import OverlayProcessor
from core.logger.setup import setup_logging
from run import BotOrchestration
from widgets.qa_app import QaApp

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore [union-attr]
sys.stderr.reconfigure(encoding="utf-8")  # type: ignore [union-attr]


def _run_bot(
    runner: BotOrchestration,
    stop_event: Event,
    overlay: OverlayProcessor,
) -> None:
    setup_logging(overlay)
    runner.run(stop_event)


def main() -> None:
    container = get_container()
    stop_event = Event()

    bot_runner = container.get(BotOrchestration)
    qa_app = container.get(QaApp)
    overlay = container.get(OverlayProcessor)

    worker = partial(_run_bot, bot_runner, stop_event, overlay)
    qa_app.run(worker, show_click_marker=True)


if __name__ == "__main__":
    main()
