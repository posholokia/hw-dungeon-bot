"""
Считает разницу по каждой точке отпечатков титанов.
По каждому титану выбираются поочередно по 1 точке из каждой позиции.
Затем считается максимальная разница по каждому отпечатку.
Например:
{
    "name": "Авалон",
    "fingerprint": {
      "team": {
        "1": [
          [
            1,
            2,
            3
          ],
          [
            4,
            30,
            6
          ],
          ...
        ],
        "2": [
          [
            11,
            4,
            3
          ],
          [
            24,
            5,
            8
          ],
          ...
        ],
        "3": [
          [
            1,
            4,
            3
          ],
          [
            14,
            40,
            8
          ],
          ...
        ],
        ...
    }
Сравниваем отпечаток первой точки из первой позиции со второй и третьей - максимальная разница по каналу red - 10 (между 1 и 2 точками).
А во второй точке максимальная разница 35 по каналу green (между 2 и 3 точками).
Формируется ответ формата:
[
    "Авалон": {
        "team": {
            1: 10,
            2: 35,
            ...
        },
        "selection": {
            ...
        }
    },
    ...
]
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "titan_fp_all.json"
OUTPUT_PATH = ROOT / "titan_fp_tolerance.json"


def _max_channel_diff(colors: list[list[int]]) -> int:
    """Максимум (max − min) по каналам RGB среди цветов одной точки."""
    if len(colors) < 2:
        return 0
    max_diff = 0
    for channel in range(3):
        values = [color[channel] for color in colors]
        max_diff = max(max_diff, max(values) - min(values))
    return max_diff


def _section_point_diffs(positions: dict[str, list[list[int]]]) -> dict[int, int]:
    fps = list(positions.values())
    if not fps:
        return {}

    n_points = min(len(fp) for fp in fps)
    return {
        index + 1: _max_channel_diff([fp[index] for fp in fps])
        for index in range(n_points)
    }


def calculate_fingerprint_diffs(
    titans: list[dict],
) -> dict[str, dict[str, dict[int, int]]]:
    """Максимальная канальная разница по каждой точке team/selection."""
    result: dict[str, dict[str, dict[int, int]]] = {}
    for titan in titans:
        fingerprint = titan["fingerprint"]
        result[titan["name"]] = {
            "team": _section_point_diffs(fingerprint["team"]),
            "selection": _section_point_diffs(fingerprint["selection"]),
        }
    return result


def calculate_diff() -> None:
    with open(INPUT_PATH, encoding="utf-8") as f:
        titans = json.load(f)

    diffs = calculate_fingerprint_diffs(titans)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(diffs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    calculate_diff()
