import pathlib
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, JsonConfigSettingsSource, PydanticBaseSettingsSource


def _configs_dir() -> pathlib.Path:
    # PyInstaller onefile extracts to sys._MEIPASS; settings.json is bundled under configs/.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return pathlib.Path(sys._MEIPASS) / "configs"
    return pathlib.Path(__file__).parent


_CURRENT_DIR = _configs_dir()


class RoomCoordinates(BaseSettings):
    left: list[tuple[int, int]]
    right: list[tuple[int, int]]
    center: list[tuple[int, int]]


class ClickArea(BaseSettings):
    x: int
    y: int
    width: int
    height: int


class RoomClickArea(BaseSettings):
    right: ClickArea
    left: ClickArea
    center: ClickArea


class RoomConfigs(BaseSettings):
    coordinates: RoomCoordinates = Field(default_factory=RoomCoordinates)
    click_area: RoomClickArea = Field(default_factory=RoomClickArea)
    fingerprint: list[tuple[int, int, int]]


class SelectionCoordinates(BaseSettings):
    left: list[tuple[int, int]]
    right: list[tuple[int, int]]
    center: list[tuple[int, int]]


class SelectionFingerprint(BaseSettings):
    common: list[tuple[int, int, int]]
    earth: list[tuple[int, int, int]]
    water: list[tuple[int, int, int]]
    fire: list[tuple[int, int, int]]


class SelectionClickArea(BaseSettings):
    left: ClickArea
    right: ClickArea
    center: ClickArea


class SelectionConfigs(BaseSettings):
    coordinates: SelectionCoordinates = Field(default_factory=SelectionCoordinates)
    fingerprint: SelectionFingerprint = Field(default_factory=SelectionFingerprint)
    click_area: SelectionClickArea = Field(default_factory=SelectionClickArea)


class AutobattleConfigs(BaseSettings):
    coordinates: list[tuple[int, int]]
    click_area: ClickArea = Field(default_factory=ClickArea)
    fingerprint: list[tuple[int, int, int]]


class BattleResultFingerprint(BaseSettings):
    win: list[tuple[int, int, int]]
    lose: list[tuple[int, int, int]]


class BattleResultConfigs(BaseSettings):
    coordinates: list[tuple[int, int]]
    fingerprint: BattleResultFingerprint = Field(default_factory=BattleResultFingerprint)


class TitanCountConfigs(BaseSettings):
    coordinates: dict[str, list[tuple[int, int]]]
    fingerprint: dict[str, list[tuple[int, int, int]]]


class TitanDeadConfigs(BaseSettings):
    """Offsets from each titan icon center to sample points for the МЁРТВ label."""

    sample_offsets: list[tuple[int, int]]


class TitanIconConfigs(BaseSettings):
    """Battle-result icon bbox relative to titan_count edge-pair center."""

    dx: int
    dy: int
    size: int


class TitanCatalogEntry(BaseSettings):
    name: str
    element: str
    role: str
    fingerprint: list[tuple[int, int, int]]


class TitansConfigs(BaseSettings):
    icon: TitanIconConfigs = Field(default_factory=TitanIconConfigs)
    fingerprint_offsets: list[tuple[int, int]]
    health_offset_y: int
    energy_offset_y: int
    bar_half_width: int
    catalog: list[TitanCatalogEntry]


class AppSettings(BaseSettings):
    room: RoomConfigs = Field(default_factory=RoomConfigs)
    selection: SelectionConfigs = Field(default_factory=SelectionConfigs)
    autobattle: AutobattleConfigs = Field(default_factory=AutobattleConfigs)
    battle_result: BattleResultConfigs = Field(default_factory=BattleResultConfigs)
    titan_count: TitanCountConfigs = Field(default_factory=TitanCountConfigs)
    titan_dead: TitanDeadConfigs = Field(default_factory=TitanDeadConfigs)
    titans: TitansConfigs = Field(default_factory=TitansConfigs)
    
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


def get_settings() -> AppSettings:
    return AppSettings()
