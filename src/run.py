from threading import Event
import logging

from configs.settings import get_settings
from flow.find_room import FindRoomStep
from flow.scenario import Scenario
from input import GlobalStopHotkey
from models.dto import State
from overlay import LogOverlay


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    settings = get_settings()

    coordinates = {
        "left": settings.room.coordinates.left,
        "right": settings.room.coordinates.right,
        "center": settings.room.coordinates.center,
    }
    step1 = FindRoomStep(
        timeout=30,
        room_coordinates=coordinates,
        fingerprint=settings.room.fingerprint,
    )

    state = State(level=100)
    scenario = Scenario(steps=[step1])
    stop_event = Event()

    with GlobalStopHotkey("ctrl+shift+q", stop_event.set), LogOverlay() as overlay:
        overlay.run(lambda: scenario.run(state, stop_event), stop_event=stop_event)


if __name__ == "__main__":
    main()
