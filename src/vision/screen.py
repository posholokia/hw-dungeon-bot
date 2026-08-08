from typing import cast

import mss
import numpy as np


def take_print(points: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    left, top = min(xs), min(ys)
    width, height = max(xs) - left + 1, max(ys) - top + 1
    with mss.mss() as sct:
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
        img = np.asarray(shot)

    fingerprint = [
        tuple(int(c) for c in img[y - top, x - left, :3][::-1])  # RGB
        for x, y in points
    ]
    return cast(list[tuple[int, int, int]], fingerprint)
