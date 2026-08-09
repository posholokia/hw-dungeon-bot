from functools import lru_cache

from rodi import ActivationScope, Container, ServiceLifeStyle, Services

from configs.settings import get_settings
from core.logger.processors.overlay import OverlayProcessor
from domain.types import PreviewSeconds, Timeout
from interfaces.output import IMouseClick
from output.mouse.designation import DesignationClick
from run import BotRunner
from services.select_room.finder import RoomFinderService
from services.select_room.selector import SelectRoomService
from services.titan_catalog import TitanCatalog
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
        self._container.register(BotRunner, BotRunner)
        self._container.register(SelectRoomUseCase, SelectRoomUseCase)

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
            return DesignationClick(marker)

        self._container.register_factory(
            build_designation_click, IMouseClick, life_style=ServiceLifeStyle.TRANSIENT
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
            click_areas = self._config.selection.click_area
            click_service = context.get(IMouseClick)
            preview_seconds = context.get(PreviewSeconds)
            return SelectRoomService(
                click_areas=click_areas,
                click_service=click_service,
                preview_seconds=preview_seconds,
            )

        def build_titan_catalog_service() -> TitanCatalog:
            titan_catalog_dir = self._config.titan_catalog_dir
            return TitanCatalog(titan_catalog_dir)

        self._container.add_singleton_by_factory(build_titan_catalog_service, TitanCatalog)

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

    def __init_types(self) -> None:
        def build_timeout() -> Timeout:
            return Timeout(30)

        def build_preview_seconds() -> PreviewSeconds:
            return PreviewSeconds(0.3)

        self._container.register_factory(
            build_timeout, Timeout, life_style=ServiceLifeStyle.SINGLETON
        )
        self._container.register_factory(
            build_preview_seconds, PreviewSeconds, life_style=ServiceLifeStyle.SINGLETON
        )
