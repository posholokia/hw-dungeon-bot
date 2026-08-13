import json
from pathlib import Path

from domain.types import FingerPrint
from models.dto import Titan


class TitanCatalog:
    def __init__(self, catalog_path: Path):
        self._titans = []
        raw_list = json.load(catalog_path.open(encoding="utf-8"))
        for item in raw_list:
            self._titans.append(Titan.model_validate(item))

        self._titans_by_name = {titan.name: titan for titan in self._titans}
        self._titans_by_fingerprint = {}

        for titan in self._titans:
            points = tuple(titan.fingerprint)
            self._titans_by_fingerprint[points] = titan

    def get_titan_by_name(self, name: str) -> Titan:
        return self._titans_by_name[name]

    def get_titan_by_fingerprint(self, fingerprint: FingerPrint) -> Titan:
        points = tuple(fingerprint)
        return self._titans_by_fingerprint[points]

    def get_titans(self) -> dict[str, Titan]:
        return self._titans_by_name
