from threading import Event
import logging

from configs.settings import get_settings
from flow.analyze_battle import AnalyzeBattleStep, TitanCatalogItem, TitansConfig
from flow.autobattle import AutobattleStep
from flow.click_room import ClickRoomStep
from flow.find_elements import FindElementsStep
from flow.find_room import FindRoomStep
from flow.scenario import Scenario
from flow.select_element import SelectElementStep
from input import GlobalStopHotkey
from models.dto import State
from overlay import LogOverlay


def _titans_config_from_settings(settings) -> TitansConfig:
    return TitansConfig(
        icon_dx=settings.titans.icon.dx,
        icon_dy=settings.titans.icon.dy,
        icon_size=settings.titans.icon.size,
        fingerprint_offsets=settings.titans.fingerprint_offsets,
        health_offset_y=settings.titans.health_offset_y,
        energy_offset_y=settings.titans.energy_offset_y,
        bar_half_width=settings.titans.bar_half_width,
        catalog=[
            TitanCatalogItem(
                name=entry.name,
                element=entry.element,  # pyright: ignore[reportArgumentType]
                role=entry.role,  # pyright: ignore[reportArgumentType]
                fingerprint=entry.fingerprint,
            )
            for entry in settings.titans.catalog
        ],
    )

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
    selection_coordinates = {
        "left": settings.selection.coordinates.left,
        "right": settings.selection.coordinates.right,
        "center": settings.selection.coordinates.center,
    }
    selection_fingerprints = {
        "common": settings.selection.fingerprint.common,
        "earth": settings.selection.fingerprint.earth,
        "water": settings.selection.fingerprint.water,
        "fire": settings.selection.fingerprint.fire,
    }
    selection_click_areas = {
        "left": settings.selection.click_area.left.model_dump(),
        "right": settings.selection.click_area.right.model_dump(),
        "center": settings.selection.click_area.center.model_dump(),
    }

    stop_event = Event()
    state = State()
    preview_seconds = 0.3
    timeout = 30
    with GlobalStopHotkey("ctrl+shift+q", stop_event.set), LogOverlay() as overlay:
        step1 = FindRoomStep(
            timeout=timeout,
            room_coordinates=coordinates,
            fingerprint=settings.room.fingerprint,
        )
        step2 = ClickRoomStep(
            click_areas=click_areas,
            show_click=overlay.show_click,
            preview_seconds=preview_seconds,
        )
        step3 = FindElementsStep(
            timeout=timeout,
            coordinates=selection_coordinates,
            fingerprints=selection_fingerprints,
        )
        step4 = SelectElementStep(
            click_areas=selection_click_areas,
            show_click=overlay.show_click,
            preview_seconds=preview_seconds,
        )
        step5 = AutobattleStep(
            timeout=timeout,
            coordinates=settings.autobattle.coordinates,
            fingerprint=settings.autobattle.fingerprint,
            click_area=settings.autobattle.click_area.model_dump(),
            show_click=overlay.show_click,
            preview_seconds=preview_seconds,
        )
        step6 = AnalyzeBattleStep(
            timeout=timeout,
            coordinates=settings.battle_result.coordinates,
            fingerprints={
                "win": settings.battle_result.fingerprint.win,
                "lose": settings.battle_result.fingerprint.lose,
            },
            titan_count_coordinates=settings.titan_count.coordinates,
            titan_count_fingerprints=settings.titan_count.fingerprint,
            dead_sample_offsets=settings.titan_dead.sample_offsets,
            titans=_titans_config_from_settings(settings),
        )
        scenario = Scenario(steps=[step1, step2, step3, step4, step5, step6])
        overlay.run(lambda: scenario.run(state, stop_event), stop_event=stop_event)


if __name__ == "__main__":
    main()
