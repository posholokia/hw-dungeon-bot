import pathlib
import sys

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from domain.types import (
    CoordinateList,
    ElementPositions,
    FingerPrintList,
    RoomElements,
)
from models.dto import ClickArea, RoomPosition


def _configs_dir() -> pathlib.Path:
    # PyInstaller onefile extracts to sys._MEIPASS; settings.json is bundled under configs/.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return pathlib.Path(sys._MEIPASS) / "configs"
    return pathlib.Path(__file__).parent


_CURRENT_DIR = _configs_dir()


# class RoomCoordinates(BaseSettings):
#     left: CoordinateList
#     right: CoordinateList
#     center: CoordinateList


class RoomConfigs(BaseSettings):
    coordinates: dict[RoomPosition, CoordinateList]
    click_area: dict[RoomPosition, ClickArea]
    fingerprint: FingerPrintList


class SelectionConfigs(BaseSettings):
    coordinates: dict[ElementPositions, CoordinateList]
    fingerprint: dict[RoomElements, FingerPrintList]
    click_area: dict[ElementPositions, ClickArea]


# class AutobattleConfigs(BaseSettings):
#     coordinates: CoordinateList
#     click_area: ClickArea = Field(default_factory=ClickArea)
#     fingerprint: FingerPrintList


# class BattleResultFingerprint(BaseSettings):
#     win: FingerPrintList
#     lose: FingerPrintList


# class BattleResultConfigs(BaseSettings):
#     coordinates: CoordinateList
#     fingerprint: BattleResultFingerprint = Field(
#         default_factory=BattleResultFingerprint
#     )


# class TitanCountConfigs(BaseSettings):
#     coordinates: dict[str, CoordinateList]
#     fingerprint: dict[str, FingerPrintList]


# class TitanDeadConfigs(BaseSettings):
#     """Offsets from each titan icon center to sample points for the МЁРТВ label."""

#     sample_offsets: list[tuple[int, int]]


# class TitanIconConfigs(BaseSettings):
#     """Battle-result icon bbox relative to titan_count edge-pair center."""

#     dx: int
#     dy: int
#     size: int


# class TitanCatalogEntry(BaseSettings):
#     name: str
#     element: str
#     role: str
#     fingerprint: list[tuple[int, int, int]]
#     position: int


# class TitansConfigs(BaseSettings):
#     icon: TitanIconConfigs = Field(default_factory=TitanIconConfigs)
#     fingerprint_offsets: list[tuple[int, int]]
#     health_offset_y: int
#     energy_offset_y: int
#     bar_half_width: int
#     catalog: list[TitanCatalogEntry]


# class HealingTeamConfigs(BaseSettings):
#     team: list[str]
#     titans: list[str]
#     low_then: int


# class ReplayRulesConfigs(BaseSettings):
#     health: int
#     health_energy: int


# class FlowConfigs(BaseSettings):
#     common_teams: dict[str, list[str]]
#     fire_teams: dict[str, list[str]]
#     replay_rules: dict[str, ReplayRulesConfigs]
#     heal_rules: HealingTeamConfigs

#     @classmethod
#     def settings_customise_sources(
#         cls,
#         settings_cls: type[BaseSettings],
#         init_settings: PydanticBaseSettingsSource,
#         env_settings: PydanticBaseSettingsSource,
#         dotenv_settings: PydanticBaseSettingsSource,
#         file_secret_settings: PydanticBaseSettingsSource,
#     ) -> tuple[PydanticBaseSettingsSource, ...]:
#         return (
#             JsonConfigSettingsSource(
#                 settings_cls,
#                 json_file=_CURRENT_DIR / "flow_cfg.json",
#                 json_file_encoding="utf-8",
#             ),
#             env_settings,
#             dotenv_settings,
#             file_secret_settings,
#         )


# class SolutionConfigs(BaseSettings):
#     coordinates: list[tuple[int, int]]
#     fingerprint: list[tuple[int, int, int]]
#     click_area: ClickArea = Field(default_factory=ClickArea)


# class ReplayConfigs(BaseSettings):
#     coordinates: dict[str, list[tuple[int, int]]]
#     fingerprint: dict[str, list[tuple[int, int, int]]]
#     click_area: dict[str, ClickArea] = Field(default_factory=dict[str, ClickArea])


class AppSettings(BaseSettings):
    room: RoomConfigs = Field(default_factory=RoomConfigs)
    selection: SelectionConfigs = Field(default_factory=SelectionConfigs)
    # autobattle: AutobattleConfigs = Field(default_factory=AutobattleConfigs)
    # battle_result: BattleResultConfigs = Field(default_factory=BattleResultConfigs)
    # titan_count: TitanCountConfigs = Field(default_factory=TitanCountConfigs)
    # titan_dead: TitanDeadConfigs = Field(default_factory=TitanDeadConfigs)
    # titans: TitansConfigs = Field(default_factory=TitansConfigs)
    # solution: SolutionConfigs = Field(default_factory=SolutionConfigs)
    # replay: ReplayConfigs = Field(default_factory=ReplayConfigs)
    # flow: FlowConfigs = Field(default_factory=FlowConfigs)

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


def get_settings() -> AppSettings:
    return AppSettings()
