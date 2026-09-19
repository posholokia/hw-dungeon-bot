"""
Пересборка json файла с настройками приложения.
Находит по имеющимся скринам максимально близкие друг к другу точки
для сканированя позиций титанов и собирает отпечатки по обновленным точкам.

"""

import json
from pathlib import Path

from calculate_diff import calculate_diff  # type: ignore [import-not-found]
from filter_points import filter_points  # type: ignore [import-not-found]
from points_map import get_titan_fp  # type: ignore [import-not-found]
from titan_fp import update_fingerprints  # type: ignore [import-not-found]

from configs.settings import get_settings
from domain.types import CoordinateList

ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "points_tolerance.json"
OUTPUT_PATH = ROOT.parent / "settings.json"


def extract_coordinates(cords: list[str]) -> CoordinateList:
    coordinates = []
    for str_point in cords:
        x, y = str_point.split(":")
        coordinates.append((int(x), int(y)))
    return coordinates


def load_coords() -> dict[str, dict[int, CoordinateList]]:
    res: dict[str, dict[int, CoordinateList]] = {}
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    team_cords = data["team"]
    res["team"] = {}
    for pos, cords in team_cords.items():
        cords_list = list(cords.keys())
        res["team"][int(pos)] = extract_coordinates(cords_list)

    res["selection"] = {}
    selection_cords = data["selection"]
    for pos, cords in selection_cords.items():
        cords_list = list(cords.keys())
        res["selection"][int(pos)] = extract_coordinates(cords_list)

    return res


def rebuild_settings():
    settings = get_settings()
    coordinates = load_coords()

    for i, (k, v) in enumerate(coordinates["team"].items()):
        new_cords = coordinates["team"][i + 1]
        settings.battle.current_team[i].coordinates = new_cords

    for i, (k, v) in enumerate(coordinates["selection"].items(), 1):
        new_cords = coordinates["selection"][i]
        settings.battle.selection.check_positions[i].coordinates = new_cords

    settings_dict = settings.model_dump()
    settings_dict.update(
        {"room_fingerprint": next(iter(settings.room.values())).fingerprint}
    )
    for v in settings_dict["room"].values():
        del v["fingerprint"]

    with open("settings.json", "w") as f:
        json.dump(settings_dict, f, indent=4, ensure_ascii=False)


def main() -> None:
    # Шаг 1: Сборка отпечатков по всей сканируемой области
    get_titan_fp()
    # Шаг 2: По каждой точке вычисляем максимальное отклонение между всеми позициями титанов
    calculate_diff()
    # Шаг 3: Отфильровывает точки по tolerance. Если хотя бы у одного титана разница выше порога,
    # то точка убирается.
    filter_points(22)
    # Шаг 4: Пересборка настроек с новыми координатами для сканирования
    rebuild_settings()
    # Шаг 5: Обновление отпечатков у титанов по новым координатам
    # (нужно сперва заменить configs/settings.json на сгенерированный на шаге 4).
    update_fingerprints()


if __name__ == "__main__":
    rebuild_settings()
