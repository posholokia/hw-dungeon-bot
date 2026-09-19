"""
Автогенерация отпечаткой титанов по всем позициям с добавлением их в json.
Изображения должны быть в корне проекта в директории titans разбитые
по подпапкам по именам титанов.

Структура должна выглядеть так:
root
    └── titans
        ├── Ангус
        |   ├── team1.png  # позиция 1 в области команды
        |   ├── team2.png  # позиция 2 в области команды
        |   ├── select1.png  # позиция 1 в области выбора титана
        |   ├── select2.png  # позиция 2 в области выбора титана
        |   └── ...
        ├── Сигурд
        |   └── ...
        └── ...

Именование директорий и файлов имеет важно: подпапки должны называться точно по именам титанов.
Изображения с позициями титанов для сбор отпечатков должны именоваться как:
 - `team{pos}.png` - для изображений с позициями в области команды, где pos - номер позиции.
 - `select{pos}.png` - для изображений с позициями в области выбора титана, где pos - номер позиции.
"""

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, TypedDict, cast

import numpy as np
from PIL import Image

from configs.settings import get_settings
from domain.types import CoordinateList, FingerPrint, TitanElement, TitanRole

IMG_PATH = Path("titans")
settings = get_settings()
EMPTY_IMG_PATH = Path(__file__).resolve().parent.parent / "trash" / "empty.png"
SORT_PRIORITY = {"water": 1, "earth": 2, "fire": 3, "dark": 4, "light": 5, "elarite": 6}


class TitanFP(TypedDict):
    team: dict[int, FingerPrint]
    selection: dict[int, FingerPrint] | FingerPrint


class TitanInfo(TypedDict):
    name: str
    element: TitanElement
    role: TitanRole
    position: int
    fingerprint: TitanFP


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


def match_titan(
    team_files: dict[int, Path],
    selection_files: dict[int, Path],
    team_coordinates: list[CoordinateList],
    selection_coordinates: dict[int, CoordinateList],
    titan: dict[str, Any],
) -> TitanInfo:
    team_pos_fp: dict[int, FingerPrint] = {}
    selection_pos_fp: dict[int, FingerPrint] = {}

    for pos, img_path in team_files.items():
        fp = take_print(img_path, points=team_coordinates[pos - 1])
        team_pos_fp[pos] = fp

    for pos, img_path in selection_files.items():
        fp = take_print(img_path, points=selection_coordinates[pos])
        selection_pos_fp[pos] = fp

    team_pos_fp = dict(sorted(team_pos_fp.items()))
    return TitanInfo(
        name=titan["name"],
        element=titan["element"],
        role=titan["role"],
        position=titan["position"],
        fingerprint={"team": team_pos_fp, "selection": selection_pos_fp},
    )


def get_files(name: str) -> tuple[dict[int, Path], dict[int, Path]] | None:
    dir_list = os.listdir(IMG_PATH)
    if name not in dir_list:
        print(f"Изображений для титана с именем {name} не найдено")
        return None

    titan_path = IMG_PATH / name
    files = os.listdir(titan_path)
    _validate_files(files)
    team_files, selection_files = _sort_files(files)
    return {pos: titan_path / file for pos, file in team_files.items()}, {
        pos: titan_path / file for pos, file in selection_files.items()
    }


def read_titans() -> list[dict[str, Any]]:
    with open("src/configs/titans.json", "r") as f:
        data = json.load(f)
    return data["titans"]


def write_titans(titans: Any, empty: Any) -> None:
    data = {"titans": titans, "empty": empty}
    with open("titans.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def scan_empty(
    team_coordinates: list[CoordinateList],
) -> dict[int, FingerPrint]:
    res = {}
    for i, cords in enumerate(team_coordinates, 1):
        res[i] = take_print(EMPTY_IMG_PATH, cords)
    return res


def update_fingerprints() -> None:
    titans = read_titans()
    updated_titans = []
    team_coordinates = [conf.coordinates for conf in settings.battle.current_team]
    selection_coordinates = {
        k: v.coordinates for k, v in settings.battle.selection.check_positions.items()
    }
    for titan in titans:
        name = titan["name"]
        files = get_files(name)

        if files is None:
            continue

        info = match_titan(
            *files,
            team_coordinates=team_coordinates,
            selection_coordinates=selection_coordinates,
            titan=titan,
        )
        updated_titans.append(info)

    stripped = strip_selection_pos(updated_titans)
    stripped.sort(key=lambda x: (SORT_PRIORITY[x["element"]], x["position"]))
    empty = scan_empty(team_coordinates)
    write_titans(stripped, empty)


def _validate_files(files_list: list[str]) -> None:
    for full_name in files_list:
        _, ext = full_name.split(".")
        if ext != "png":
            raise ValueError(f"Неизвестный формат файла: {full_name}")


def strip_selection_pos(titans: list[TitanInfo]) -> list[TitanInfo]:
    updated = []
    for titan in titans:
        changed = deepcopy(titan)
        if selection := titan["fingerprint"]["selection"]:
            changed["fingerprint"]["selection"] = selection[1]  # type: ignore [typeddict-item]
        updated.append(changed)

    return updated


def _sort_files(files_list: list[str]) -> tuple[dict[int, str], dict[int, str]]:
    team_files: dict[int, str] = {}
    selection_files: dict[int, str] = {}

    for full_name in files_list:
        name = full_name.replace(".png", "")
        pos = int(name[-1])
        if "team" in name:
            team_files[pos] = full_name
        elif "select" in name:
            selection_files[pos] = full_name
        else:
            raise ValueError(
                f"Неопознанный паттерн именования изображения: {full_name}"
            )
    return team_files, selection_files


if __name__ == "__main__":
    update_fingerprints()
