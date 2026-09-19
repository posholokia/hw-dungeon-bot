from typing import cast

import mss
import numpy as np

from configs.settings import get_settings


def take_print(points: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    settings = get_settings()
    shift_y = settings.local_settings.scan_shift_y
    xs = [x for x, _ in points]
    ys = [y + shift_y for _, y in points]
    left, top = min(xs), min(ys)
    width, height = max(xs) - left + 1, max(ys) - top + 1
    with mss.mss() as sct:
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
        img = np.asarray(shot)

    fingerprint = [
        tuple(int(c) for c in img[y + shift_y - top, x - left, :3][::-1])  # RGB
        for x, y in points
    ]
    return cast(list[tuple[int, int, int]], fingerprint)
