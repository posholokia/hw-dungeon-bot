import pathlib
import sys
from typing import Any

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from domain.types import (
    Coordinate,
    CoordinateList,
    ElementPosition,
    FingerPrint,
    RoomElement,
    TitanRole,
    TitanElement,
)
from models.dto import ClickArea, RoomPosition


def _configs_dir() -> pathlib.Path:
    # PyInstaller onefile extracts to sys._MEIPASS; settings.json is bundled under configs/.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return pathlib.Path(sys._MEIPASS) / "configs"
    return pathlib.Path(__file__).parent


_CURRENT_DIR = _configs_dir()


class RoomConfigs(BaseSettings):
    coordinates: dict[RoomPosition, CoordinateList]
    click_area: dict[RoomPosition, ClickArea]
    fingerprint: FingerPrint


class SelectionConfigs(BaseSettings):
    coordinates: dict[ElementPosition, CoordinateList]
    fingerprint: dict[RoomElement, FingerPrint]
    click_area: dict[ElementPosition, ClickArea]



class TitanTeamConfig(BaseSettings):
    click_area: ClickArea
    coordinates: CoordinateList


class HealingRulesConfig(BaseSettings):
    titans: list[str]  # имена титанов
    heal_below: int  # проценты


class SelectionConfig(BaseSettings):
    filter_button: ClickArea
    elements: dict[TitanElement, ClickArea]
    roles: dict[TitanRole, ClickArea]
    titan: ClickArea


class AutobattleConfig(BaseSettings):
    coordinates: CoordinateList
    click_area: ClickArea
    fingerprint: FingerPrint


class BattleResultConfig(BaseSettings):
    coordinates: CoordinateList
    fingerprints: dict[str, FingerPrint]


class BattleConfigs(BaseSettings):
    current_team: list[TitanTeamConfig]
    teams: dict[RoomElement, list[list[str]]]  # имена титанов
    healing_team: list[str]  # имена титанов
    healing_rules: HealingRulesConfig
    selection: SelectionConfig
    autobattle: AutobattleConfig
    battle_result: BattleResultConfig
    

class AppSettings(BaseSettings):
    room: RoomConfigs = Field(default_factory=RoomConfigs)
    selection: SelectionConfigs = Field(default_factory=SelectionConfigs)
    battle: BattleConfigs = Field(default_factory=BattleConfigs)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            JsonConfigSettingsSource(
                settings_cls,
                json_file=_CURRENT_DIR / "settings.json",
                json_file_encoding="utf-8",
            ),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def titan_catalog_dir(self) -> pathlib.Path:
        return _CURRENT_DIR / "titans.json"


def get_settings() -> AppSettings:
    return AppSettings()
