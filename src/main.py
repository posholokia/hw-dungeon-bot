import argparse
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
    level: int,
    complete: int,
) -> None:
    setup_logging(overlay)
    runner.run(level, complete, stop_event)


def main() -> None:
    parser = argparse.ArgumentParser(description="Мой Python-скрипт")

    parser.add_argument(
        "-l",
        "--level",
        type=int,
        required=False,
        help="Максимальный уровень",
        default=0,
    )
    parser.add_argument(
        "-c",
        "--complete",
        type=int,
        required=False,
        help="Пройти уровней",
        default=0,
    )
    args = parser.parse_args()

    container = get_container()
    stop_event = Event()

    bot_runner = container.get(BotOrchestration)
    qa_app = container.get(QaApp)
    overlay = container.get(OverlayProcessor)

    worker = partial(
        _run_bot, bot_runner, stop_event, overlay, args.level, args.complete
    )
    qa_app.run(worker, show_click_marker=True)


if __name__ == "__main__":
    main()
