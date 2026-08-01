from threading import Event
import logging

from configs.settings import get_settings
from flow.click_room import ClickRoomStep
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
    click_areas = {
        "left": settings.room.click_area.left.model_dump(),
        "right": settings.room.click_area.right.model_dump(),
        "center": settings.room.click_area.center.model_dump(),
    }

    stop_event = Event()
    state = State()

    with GlobalStopHotkey("ctrl+shift+q", stop_event.set), LogOverlay() as overlay:
        step1 = FindRoomStep(
            timeout=30,
            room_coordinates=coordinates,
            fingerprint=settings.room.fingerprint,
        )
        step2 = ClickRoomStep(
            click_areas=click_areas,
            show_click=overlay.show_click,
        )
        scenario = Scenario(steps=[step1, step2])
        overlay.run(lambda: scenario.run(state, stop_event), stop_event=stop_event)


if __name__ == "__main__":
    main()
