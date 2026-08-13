from structlog import getLogger

from configs.settings import HealingRulesConfig
from services.battle.dto import BattleState, TitanStatus

logger = getLogger(__name__)


class HealthObserveService:
    def __init__(self, healing_rules: HealingRulesConfig) -> None:
        self._healing_rules = healing_rules

    def observe(
        self, health_list: list[TitanStatus], battle_state: BattleState
    ) -> None:
        healing_list = set()
        for titan in health_list:
            if titan.name not in self._healing_rules.titans:
                continue

            if titan.health >= self._healing_rules.heal_below:
                continue

            healing_list.add(titan.name)

        battle_state.need_healing = healing_list
        logger.info(f"Требуется лечение: {healing_list}")
