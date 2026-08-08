# from pathlib import Path
# from configs.settings import get_settings
# from PIL import Image
# import numpy as np

# settings = get_settings()


# def make_print(
#     image: str | Path | Image.Image,
#     points: list[tuple[int, int]],
# ) -> list[tuple[int, int, int]]:
#     if isinstance(image, Image.Image):
#         img = np.asarray(image.convert("RGB"))
#     else:
#         img = np.asarray(Image.open(image).convert("RGB"))
#     return [tuple(int(c) for c in img[y, x]) for x, y in points]


# fingerprint = make_print(
#     "./trash/CommonUP FireDown.9.png",
#     settings.room.coordinates.left,
# )
# print(fingerprint)

# fingerprint = make_print(
#     "./trash/FireUP WaterDown.4.png",
#     settings.room.coordinates.right,
# )
# print(fingerprint)

# fingerprint = make_print(
#     "./trash/FireUP CommonDown.png",
#     settings.room.coordinates.center,
# )
# print(fingerprint)


from domain.types import RoomPosition
from models.dto import State


def calibrate_current_level(
    state: State,
    room_position: RoomPosition,
) -> None:
    if room_position == "left" and state.current_level % 10 != 0:
        state.calibrate_current_level(10)
    elif room_position == "right" and state.current_level % 10 != 5:
        state.calibrate_current_level(5)
    else:
        state.calibrate_current_level(state.current_level)


s = State()
s.current_level = 5
assert not s.current_level_calibrated
calibrate_current_level(s, "left")
assert s.current_level == 10
assert s.current_level_calibrated

s = State()
s.current_level = 4
assert not s.current_level_calibrated
calibrate_current_level(s, "right")
assert s.current_level == 5
assert s.current_level_calibrated

s = State()
s.current_level = 10
assert not s.current_level_calibrated
calibrate_current_level(s, "left")
assert s.current_level == 10
assert s.current_level_calibrated

s = State()
s.current_level = 5
assert not s.current_level_calibrated
calibrate_current_level(s, "right")
assert s.current_level == 5
assert s.current_level_calibrated
