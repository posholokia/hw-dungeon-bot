"""
Составляет таблицу координат по всем имеющиммся позициям титанов.
"""

import json
import re
from pathlib import Path
from typing import TypedDict, cast

import numpy as np
from PIL import Image

from domain.types import CoordinateList, FingerPrint

ROOT = Path(__file__).resolve().parent.parent
TITANS_DIR = ROOT / "titans"
AREA_PATH = Path(__file__).resolve().parent / "area.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "titan_fp_all.json"

TEAM_RE = re.compile(r"^team(\d+)\.png$")
SELECT_RE = re.compile(r"^select(\d+)\.png$")


class FingerPrintInfo(TypedDict):
    team: dict[int, FingerPrint]
    selection: dict[int, FingerPrint]


class TitanPositionFP(TypedDict):
    name: str
    fingerprint: FingerPrintInfo


def take_print(img_path: Path | str, points: CoordinateList) -> FingerPrint:
    img = Image.open(img_path)
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    left, top = min(xs), min(ys)
    width, height = max(xs) - left + 1, max(ys) - top + 1
    shot = img.crop((left, top, left + width, top + height))
    array = np.asarray(shot)
    fp = [
        tuple(int(c) for c in array[y - top, x - left][:3])  # RGB
        for x, y in points
    ]
    return cast(FingerPrint, fp)


def _area_to_points(area: dict) -> CoordinateList:
    """Все точки прямоугольника, включая крайние (width+1) × (height+1)."""
    x, y = area["x"], area["y"]
    w, h = area["width"], area["height"]
    return [(px, py) for py in range(y, y + h + 1) for px in range(x, x + w + 1)]


def load_position_points(
    area_path: Path = AREA_PATH,
) -> tuple[dict[int, CoordinateList], dict[int, CoordinateList]]:
    with open(area_path, encoding="utf-8") as f:
        areas = json.load(f)

    team_points = {
        int(pos): _area_to_points(rect) for pos, rect in areas["current_team"].items()
    }
    selection_points = {
        int(pos): _area_to_points(rect) for pos, rect in areas["check_position"].items()
    }
    return team_points, selection_points


def get_titan_fp(
    titans_dir: Path = TITANS_DIR,
    area_path: Path = AREA_PATH,
) -> None:
    """Сканирует titans/, собирает отпечатки team{N}/select{N} по областям area.json."""
    team_points, selection_points = load_position_points(area_path)
    result: list[TitanPositionFP] = []

    for titan_dir in sorted(p for p in titans_dir.iterdir() if p.is_dir()):
        team_fp: dict[int, FingerPrint] = {}
        selection_fp: dict[int, FingerPrint] = {}

        for img_path in sorted(titan_dir.glob("*.png")):
            if m := TEAM_RE.match(img_path.name):
                pos = int(m.group(1))
                team_fp[pos] = take_print(img_path, team_points[pos])
            elif m := SELECT_RE.match(img_path.name):
                pos = int(m.group(1))
                selection_fp[pos] = take_print(img_path, selection_points[pos])

        result.append(
            TitanPositionFP(
                name=titan_dir.name,
                fingerprint=FingerPrintInfo(team=team_fp, selection=selection_fp),
            )
        )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    get_titan_fp()
