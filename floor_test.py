from functools import partial
from threading import Event

from core.depends.container import get_container
from core.logger.processors.overlay import OverlayProcessor
from core.logger.setup import setup_logging
from models.dto import State
from services.battle.battle.scaner import BattleScannerService
from services.floor_transit import FloorTransitService
from widgets.qa_app import QaApp

state = State()
state.current_level = 5


def _run_bot(
    runner: BattleScannerService,
    stop_event: Event,
    overlay: OverlayProcessor,
) -> None:
    setup_logging(overlay)
    res = runner.scan_team()
    print(f"{res=}")


def main() -> None:
    container = get_container()
    stop_event = Event()

    bot_runner = container.get(BattleScannerService)
    qa_app = container.get(QaApp)
    overlay = container.get(OverlayProcessor)

    worker = partial(_run_bot, bot_runner, stop_event, overlay)
    qa_app.run(worker, show_click_marker=True)


if __name__ == "__main__":
    main()


