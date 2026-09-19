"""
Собирает точки с наименьшим tolerance между всеми титанами.
"""

import json
from typing import Any

from points_map import load_position_points  # type: ignore [import-not-found]

INPUT_PATH = "generate_settings/titan_fp_tolerance.json"
OUTPUT_PATH = "generate_settings/points_tolerance.json"


def read_file() -> dict[str, Any]:
    with open(INPUT_PATH) as f:
        return json.load(f)


def write_file(data: dict[str, Any] | list[dict[str, Any]]) -> None:
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate(
    data: dict[str, dict[str, dict[str, int]]], tolerance: int
) -> dict[int, int]:
    indexies = {i: 0 for i in range(1, 5521)}
    for fpt in data.values():
        team_tolerance = fpt["team"]
        selection_tolerance = fpt["selection"]

        for p, t in team_tolerance.items():
            if int(p) in indexies and t > tolerance:
                del indexies[int(p)]
            elif int(p) in indexies and t > indexies[int(p)]:
                indexies[int(p)] = t

        for p, t in selection_tolerance.items():
            if int(p) in indexies and t > tolerance:
                del indexies[int(p)]
            elif int(p) in indexies and t > indexies[int(p)]:
                indexies[int(p)] = t

    indexies = dict(sorted(indexies.items(), key=lambda x: x[1]))
    print(f"Найдено {len(indexies)} точек по условию tolerance <= {tolerance}")
    return indexies


def tolerance_by_points(data: dict[int, int]) -> dict[str, dict[int, dict[str, int]]]:
    team_points, selection_points = load_position_points()
    position_points: dict[str, dict[int, dict[str, int]]] = {
        "team": {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
        },
        "selection": {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
        },
    }
    for pos, points in team_points.items():
        for i, p in enumerate(points, 1):
            if i in data:
                position_points["team"][pos][f"{p[0]}:{p[1]}"] = data[i]

    for pos, points in selection_points.items():
        for i, p in enumerate(points, 1):
            if i in data:
                position_points["selection"][pos][f"{p[0]}:{p[1]}"] = data[i]

    return position_points


def filter_points(tolerance: int) -> None:
    data = read_file()
    fpt = calculate(data, tolerance)
    res = tolerance_by_points(fpt)
    write_file(res)


if __name__ == "__main__":
    filter_points(22)
