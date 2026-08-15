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
        for titan in health_list:
            if titan.name not in self._healing_rules.titans:
                continue
            elif titan.health >= self._healing_rules.heal_below:
                battle_state.remove_from_heal_list(titan.name)
            else:
                battle_state.add_to_leal_list(titan.name)
                logger.info(f"Требуется лечение: {titan.name}")
