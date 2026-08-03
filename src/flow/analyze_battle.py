from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Event
from typing import TypedDict

from exceptions import ApplicationError, BattleResultNotFoundError, TitanCountNotFoundError
from flow.utils import match_fingerprint
from models.dto import State, Titan, TitanElements, TitalRoles
from vision.screen import take_print


logger = logging.getLogger(__name__)

# Larger layouts share center points with smaller ones — check high to low.
_TITAN_COUNTS: tuple[int, ...] = (5, 4, 3)


class BattleResultFingerprints(TypedDict):
    win: list[tuple[int, int, int]]
    lose: list[tuple[int, int, int]]


@dataclass(frozen=True)
class TitanCatalogItem:
    name: str
    element: TitanElements
    role: TitalRoles
    fingerprint: list[tuple[int, int, int]]


@dataclass(frozen=True)
class TitansConfig:
    icon_dx: int
    icon_dy: int
    icon_size: int
    fingerprint_offsets: list[tuple[int, int]]
    health_offset_y: int
    energy_offset_y: int
    bar_half_width: int
    catalog: list[TitanCatalogItem]


def _is_dead_red(rgb: tuple[int, int, int]) -> bool:
    """True if pixel matches the saturated red of the МЁРТВ label."""
    r, g, b = rgb
    return r >= 180 and g <= 80 and b <= 80 and r - max(g, b) >= 90


def _is_health_green(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return g >= 90 and g > r + 15 and g > b


def _is_energy_yellow(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r >= 140 and g >= 90 and b <= 100 and r > b + 40


def _mean_abs_diff(
    a: list[tuple[int, int, int]],
    b: list[tuple[int, int, int]],
) -> float:
    total = 0
    n = 0
    for ca, cb in zip(a, b, strict=True):
        for x, y in zip(ca, cb, strict=True):
            total += abs(x - y)
            n += 1
    return total / n if n else 1e9


class AnalyzeBattleStep:
    """Wait for the battle result screen and run post-battle checks."""

    def __init__(
        self,
        timeout: int,
        coordinates: list[tuple[int, int]],
        fingerprints: BattleResultFingerprints,
        titan_count_coordinates: dict[str, list[tuple[int, int]]],
        titan_count_fingerprints: dict[str, list[tuple[int, int, int]]],
        dead_sample_offsets: list[tuple[int, int]],
        titans: TitansConfig,
    ) -> None:
        self._timeout = timeout
        self._coordinates = coordinates
        self._fingerprints = fingerprints
        self._titan_count_coordinates = titan_count_coordinates
        self._titan_count_fingerprints = titan_count_fingerprints
        self._dead_sample_offsets = dead_sample_offsets
        self._titans = titans

    def execute(self, state: State, stop_event: Event) -> None:
        logger.info("Analyzing battle result")
        self._check_win_lose(state, stop_event)

        if not state.win:
            return

        if stop_event.is_set():
            return

        self._check_titans_count(state)
        self._check_no_dead_titans(state)

        if state.has_dead:
            return

        self._check_titans_resources(state)

    def _check_win_lose(self, state: State, stop_event: Event) -> None:
        start = time.perf_counter()
        logger.info("Waiting for win/lose screen")
        while time.perf_counter() - start < self._timeout:
            if stop_event.is_set():
                return

            scanned = take_print(self._coordinates)
            if match_fingerprint(scanned, self._fingerprints["win"]):
                state.win = True
                logger.info("Battle result: win")
                return
            if match_fingerprint(scanned, self._fingerprints["lose"]):
                state.win = False
                logger.info("Battle result: lose")
                return

            if stop_event.wait(2):
                return

        raise BattleResultNotFoundError("Battle result screen not found")

    def _check_titans_count(self, state: State) -> None:
        state.titan_count = None
        for count in _TITAN_COUNTS:
            key = str(count)
            coordinates = self._titan_count_coordinates[key]
            fingerprint = self._titan_count_fingerprints[key]
            scanned = take_print(coordinates)
            if match_fingerprint(scanned, fingerprint):
                state.titan_count = count
                logger.info("Titans in battle: %s", count)
                return

        raise TitanCountNotFoundError("Could not determine titan count")

    def _check_no_dead_titans(self, state: State) -> None:
        if state.titan_count is None:
            raise ApplicationError("Titan count is unknown; run count check first")

        state.has_dead = False
        icon_points = self._titan_count_coordinates[str(state.titan_count)]
        for left, right in zip(icon_points[::2], icon_points[1::2], strict=True):
            cx = (left[0] + right[0]) // 2
            cy = (left[1] + right[1]) // 2
            sample_points = [
                (cx + dx, cy + dy) for dx, dy in self._dead_sample_offsets
            ]
            scanned = take_print(sample_points)
            if any(_is_dead_red(rgb) for rgb in scanned):
                state.has_dead = True
                logger.info("Dead titan found at (%s, %s)", cx, cy)
                return

        logger.info("No dead titans")

    def _check_titans_resources(self, state: State) -> None:
        if state.titan_count is None:
            raise ApplicationError("Titan count is unknown; run count check first")

        state.titans = []
        icon_points = self._titan_count_coordinates[str(state.titan_count)]
        for left, right in zip(icon_points[::2], icon_points[1::2], strict=True):
            cx = (left[0] + right[0]) // 2
            cy = (left[1] + right[1]) // 2
            titan = self._read_titan_slot(cx, cy)
            state.titans.append(titan)
            logger.info(
                "Titan %s (%s/%s): HP=%.0f%% energy=%.0f%%",
                titan.name,
                titan.element,
                titan.role,
                titan.health_prc,
                titan.energy_prc,
            )

    def _read_titan_slot(self, cx: int, cy: int) -> Titan:
        entry = self._identify_titan(cx, cy)
        health = self._bar_percent(cx, cy, self._titans.health_offset_y, _is_health_green)
        energy = self._bar_percent(cx, cy, self._titans.energy_offset_y, _is_energy_yellow)
        return Titan(
            name=entry.name,
            health_prc=health,
            energy_prc=energy,
            element=entry.element,
            role=entry.role,
        )

    def _identify_titan(self, cx: int, cy: int) -> TitanCatalogItem:
        cfg = self._titans
        icon_cx = cx + cfg.icon_dx + cfg.icon_size // 2
        icon_cy = cy + cfg.icon_dy + cfg.icon_size // 2
        points = [(icon_cx + dx, icon_cy + dy) for dx, dy in cfg.fingerprint_offsets]
        scanned = take_print(points)
        best = min(cfg.catalog, key=lambda item: _mean_abs_diff(scanned, item.fingerprint))
        return best

    def _bar_percent(
        self,
        cx: int,
        cy: int,
        offset_y: int,
        is_filled: Callable[[tuple[int, int, int]], bool],
    ) -> float:
        half = self._titans.bar_half_width
        y = cy + offset_y
        points = [(x, y) for x in range(cx - half, cx + half)]
        colors = take_print(points)
        filled = sum(1 for rgb in colors if is_filled(rgb))
        return round(100.0 * filled / len(colors), 1) if colors else 0.0
