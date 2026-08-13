from functools import lru_cache

from rodi import ActivationScope, Container, ServiceLifeStyle, Services

from configs.settings import get_settings
from core.logger.processors.overlay import OverlayProcessor
from domain.types import PreviewSeconds, Timeout
from interfaces.output import IMouseClick
from output.mouse.designation import DesignationClick
from run import BattleStateCfg, BotOrchestration
from services.battle.battle.dead_scaner import DeadScanService
from services.battle.battle.healing import HealthObserveService
from services.battle.battle.health_scaner import HealthScanerService
from services.battle.battle.replay import ReplayService
from services.battle.battle.scaner import BattleScannerService
from services.battle.battle.selector import BattleSelectorService
from services.battle.battle.team_select import TeamSelectService
from services.floor_transit import FloorTransitService
from services.select_room.scaner import RoomFinderService
from services.select_room.selector import SelectRoomService
from services.titan_catalog import TitanCatalog
from use_cases.battle import BattleUseCase
from use_cases.select_room import SelectRoomUseCase
from widgets.click_marker import ClickMarker
from widgets.log_overlay import LogOverlayWindow
from widgets.qa_app import QaApp


@lru_cache(1)
def get_container() -> Services:
    return DiContainer().initialize().provider


class DiContainer:
    def __init__(self) -> None:
        self._container = Container()
        self._config = get_settings()

    def initialize(self) -> Container:
        self.__init_qa_widgets()
        self.__init_types()
        self.__init_use_cases()
        self.__init_services()
        return self._container

    def __init_qa_widgets(self) -> None:
        # Виджеты должны быть инициированы после QApplication (внутри QaApp.run).
        self._container.add_singleton_by_factory(
            lambda: LogOverlayWindow(),
            LogOverlayWindow,
        )
        self._container.add_singleton_by_factory(
            lambda: ClickMarker(),
            ClickMarker,
        )
        # QaApp можно создавать заранее: он только хранит фабрики, не QWidgets.
        self._container.add_singleton_by_factory(
            lambda: QaApp(
                get_log_window=lambda: get_container().get(LogOverlayWindow),
                get_click_marker=lambda: get_container().get(ClickMarker),
            ),
            QaApp,
        )

    def __init_use_cases(self) -> None:
        self._container.register(SelectRoomUseCase, SelectRoomUseCase)
        self._container.register(BattleUseCase, BattleUseCase)

        def build_orchestration(context: ActivationScope) -> BotOrchestration:
            select_uc = context.get(SelectRoomUseCase)
            battle_uc = context.get(BattleUseCase)
            floor_service = context.get(FloorTransitService)
            battle_state = BattleStateCfg(
                teams=self._config.battle.teams,
                healing_team=self._config.battle.healing_team,
            )
            return BotOrchestration(
                select_room_use_case=select_uc,
                battle_use_case=battle_uc,
                floor_service=floor_service,
                cfg=battle_state,
            )

        self._container.register_factory(
            build_orchestration, BotOrchestration, life_style=ServiceLifeStyle.SINGLETON
        )

    def __init_services(self) -> None:
        def build_overlay_processor(context: ActivationScope) -> OverlayProcessor:
            return OverlayProcessor(
                overlay=lambda: context.get(LogOverlayWindow),
            )

        self._container.add_singleton_by_factory(
            build_overlay_processor, OverlayProcessor
        )

        def build_designation_click(context: ActivationScope) -> DesignationClick:
            marker = lambda: context.get(ClickMarker)
            preview = context.get(PreviewSeconds)
            return DesignationClick(marker=marker, preview_seconds=preview)

        self._container.register_factory(
            build_designation_click, IMouseClick, life_style=ServiceLifeStyle.TRANSIENT
        )

        def build_dead_scaner() -> DeadScanService:
            return DeadScanService(
                windows=self._config.battle.titan_status.check.windows,
                offsets=self._config.battle.titan_status.dead_status.offsets,
                fingerprint=self._config.battle.titan_status.dead_status.fingerprint,
            )

        self._container.register_factory(
            build_dead_scaner, DeadScanService, life_style=ServiceLifeStyle.TRANSIENT
        )

        def build_health_scaner(context: ActivationScope) -> HealthScanerService:
            catalog = context.get(TitanCatalog)
            return HealthScanerService(
                windows=self._config.battle.titan_status.check.windows,
                health_bar=self._config.battle.titan_status.health,
                energy_bar=self._config.battle.titan_status.energy,
                titan_catalog=catalog,
            )

        self._container.register_factory(
            build_health_scaner,
            HealthScanerService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

        def build_replay_service(context: ActivationScope) -> ReplayService:
            timeout = context.get(Timeout)
            clicker = context.get(IMouseClick)
            return ReplayService(
                replay_conditions=self._config.battle.replay.replay_conditions,
                timeout=timeout,
                clicker=clicker,
                replay_buttons=self._config.battle.replay.buttons,
            )

        self._container.register_factory(
            build_replay_service, ReplayService, life_style=ServiceLifeStyle.TRANSIENT
        )

        def build_room_finder_service(context: ActivationScope) -> RoomFinderService:
            timeout = context.get(Timeout)
            room_coordinates = self._config.room.coordinates
            room_fingerprint = self._config.room.fingerprint
            element_coordinates = self._config.selection.coordinates
            element_fingerprint = self._config.selection.fingerprint
            return RoomFinderService(
                timeout=timeout,
                room_coordinates=room_coordinates,
                room_fingerprint=room_fingerprint,
                element_coordinates=element_coordinates,
                element_fingerprints=element_fingerprint,
            )

        def build_select_room_service(context: ActivationScope) -> SelectRoomService:
            click_areas = self._config.room.click_area
            click_service = context.get(IMouseClick)
            return SelectRoomService(
                click_areas=click_areas,
                click_service=click_service,
                element_areas=self._config.selection.click_area,
            )

        def build_titan_catalog_service() -> TitanCatalog:
            titan_catalog_dir = self._config.titan_catalog_dir
            return TitanCatalog(titan_catalog_dir)

        self._container.add_singleton_by_factory(
            build_titan_catalog_service, TitanCatalog
        )

        self._container.register_factory(
            build_room_finder_service,
            RoomFinderService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )
        self._container.register_factory(
            build_select_room_service,
            SelectRoomService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

        def build_health_observe() -> HealthObserveService:
            return HealthObserveService(healing_rules=self._config.battle.healing_rules)

        self._container.register_factory(
            build_health_observe,
            HealthObserveService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

        def build_floor_transit(context: ActivationScope) -> FloorTransitService:
            timeout = context.get(Timeout)
            clicker = context.get(IMouseClick)
            return FloorTransitService(
                buttons_cfg=self._config.floor_transit,
                clicker=clicker,
                timeout=timeout,
            )

        self._container.register_factory(
            build_floor_transit,
            FloorTransitService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

        def build_battle_scaner(context: ActivationScope) -> BattleScannerService:
            catalog = context.get(TitanCatalog)
            timeout = context.get(Timeout)
            team_coords = [cfg.coordinates for cfg in self._config.battle.current_team]
            return BattleScannerService(
                titan_catalog=catalog,
                timeout=timeout,
                analyze_team_coords=team_coords,
                autobattle_coordinates=self._config.battle.autobattle.coordinates,
                autobattle_fingerprint=self._config.battle.autobattle.fingerprint,
                result_coordinates=self._config.battle.battle_result.coordinates,
                result_fingerprints=self._config.battle.battle_result.fingerprints,
            )

        self._container.register_factory(
            build_battle_scaner,
            BattleScannerService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

        def build_team_select(context: ActivationScope) -> TeamSelectService:
            catalog = context.get(TitanCatalog)
            clicker = context.get(IMouseClick)
            team_areas = [cfg.click_area for cfg in self._config.battle.current_team]
            return TeamSelectService(
                titan_catalog=catalog,
                clicker=clicker,
                selected_click_areas=team_areas,
                selection_cfg=self._config.battle.selection,
            )

        self._container.register_factory(
            build_team_select, TeamSelectService, life_style=ServiceLifeStyle.TRANSIENT
        )

        def build_battle_selector(context: ActivationScope) -> BattleSelectorService:
            clicker = context.get(IMouseClick)
            return BattleSelectorService(
                clicker=clicker,
                autobattle_button=self._config.battle.autobattle.click_area,
            )

        self._container.register_factory(
            build_battle_selector,
            BattleSelectorService,
            life_style=ServiceLifeStyle.TRANSIENT,
        )

    def __init_types(self) -> None:
        def build_timeout() -> Timeout:
            return Timeout(30)

        def build_preview_seconds() -> PreviewSeconds:
            return PreviewSeconds(0.5)

        self._container.register_factory(
            build_timeout, Timeout, life_style=ServiceLifeStyle.SINGLETON
        )
        self._container.register_factory(
            build_preview_seconds, PreviewSeconds, life_style=ServiceLifeStyle.SINGLETON
        )
