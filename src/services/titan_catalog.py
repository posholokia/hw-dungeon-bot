import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from domain.types import FingerPrint
from models.dto import Titan


class TitanCatalog:
    def __init__(self, catalog_path: Path):
        self._titans: list[Titan] = []
        raw_data = json.load(catalog_path.open(encoding="utf-8"))
        for item in raw_data["titans"]:
            self._titans.append(Titan.model_validate(item))

        self._titans_by_name = {titan.name: titan for titan in self._titans}
        self._by_position: dict[int, dict[str, Titan]] = defaultdict(dict)

        for titan in self._titans:
            info = {titan.name: titan}
            for position in titan.fingerprint.team:
                self._by_position[position].update(info)

        self._empty_cells = {}
        for pos, fp in raw_data["empty"].items():
            fingerprint = [tuple(point) for point in fp]
            self._empty_cells[int(pos)] = fingerprint

    def get_titan_by_name(self, name: str) -> Titan:
        return self._titans_by_name[name]

    def get_titans(self) -> dict[str, Titan]:
        return deepcopy(self._titans_by_name)

    def get_titans_for_position(self, pos: int) -> dict[str, Titan]:
        return deepcopy(self._by_position[pos])

    def get_empty_cell_fp(self, pos: int) -> FingerPrint:
        return deepcopy(self._empty_cells[pos])
