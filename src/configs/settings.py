import pathlib
import sys
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from domain.types import (
    CoordinateList,
    ElementPosition,
    FingerPrint,
    RoomElement,
    RoomPosition,
    TitanElement,
    TitanRole,
)
from models.dto import ClickArea


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


class WindowCheckConfig(BaseSettings):
    windows: dict[int, CoordinateList]
    height: int
    width: int


class DeadStatusConfig(BaseSettings):
    offsets: CoordinateList
    fingerprint: FingerPrint


class BarConfig(BaseSettings):
    x: int  # относительная координата
    y: int  # относительная координата
    lenght: int


class TitanStatusConfig(BaseSettings):
    check: WindowCheckConfig
    dead_status: DeadStatusConfig
    health: BarConfig
    energy: BarConfig


class ButtonConfig(BaseSettings):
    click_area: ClickArea
    coordinates: CoordinateList
    fingerprint: FingerPrint


class ReplayButtonsConfig(BaseSettings):
    replay: dict[str, ButtonConfig]  # кнопки сдвигаются при поражении
    ok: ButtonConfig
    pause: ButtonConfig
    retreat: ButtonConfig


class ReplayConfig(BaseSettings):
    replay_conditions: dict[str, list[str]]
    buttons: ReplayButtonsConfig


class BattleConfigs(BaseSettings):
    current_team: list[TitanTeamConfig]
    teams: dict[RoomElement, list[list[str]]]  # имена титанов
    healing_team: list[str]  # имена титанов
    healing_rules: HealingRulesConfig
    selection: SelectionConfig
    autobattle: AutobattleConfig
    battle_result: BattleResultConfig
    titan_status: TitanStatusConfig
    replay: ReplayConfig

    @model_validator(mode="after")
    def healing_validate(self) -> Self:
        if set(self.healing_team) & set(self.healing_rules.titans):
            raise ValueError(
                "Титаны, выбранные для лечения не должны состоять в команде лечения"
            )
        return self


class FloorTransitConfig(BaseSettings):
    right: ButtonConfig
    left: ButtonConfig
    ok: ButtonConfig


class AppSettings(BaseSettings):
    room: RoomConfigs = Field(default_factory=RoomConfigs)
    selection: SelectionConfigs = Field(default_factory=SelectionConfigs)
    battle: BattleConfigs = Field(default_factory=BattleConfigs)
    floor_transit: FloorTransitConfig = Field(default_factory=FloorTransitConfig)

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
