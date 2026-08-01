from pathlib import Path
from configs.settings import get_settings
from PIL import Image
import numpy as np

settings = get_settings()



def make_print(
    image: str | Path | Image.Image,
    points: list[tuple[int, int]],
) -> list[tuple[int, int, int]]:
    if isinstance(image, Image.Image):
        img = np.asarray(image.convert("RGB"))
    else:
        img = np.asarray(Image.open(image).convert("RGB"))
    return [tuple(int(c) for c in img[y, x]) for x, y in points]

    
fingerprint = make_print(
    "./trash/CommonUP FireDown.9.png",
    settings.room.coordinates.left,
)
print(fingerprint)

fingerprint = make_print(
    "./trash/FireUP WaterDown.4.png",
    settings.room.coordinates.right,
)
print(fingerprint)

fingerprint = make_print(
    "./trash/FireUP CommonDown.png",
    settings.room.coordinates.center,
)
print(fingerprint)