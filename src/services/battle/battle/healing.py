from structlog import getLogger

from configs.settings import HealingRulesConfig
from services.battle.dto import BattleState, TitanHealth, TitanStatus

logger = getLogger(__name__)


class HealthObserveService:
    def __init__(self, healing_rules: HealingRulesConfig) -> None:
        self._healing_rules = healing_rules

    def observe(
        self, health_list: list[TitanStatus], battle_state: BattleState
    ) -> bool:
        """
        Наблюдение за лечением титанов.
        Если это обычный бой, не с целью лечения - очередь на лечение резолвится только по условию уровня хп.
        Если бой для отлечивания - то проверяется что хп титана стало больше.
        Если хп уменьшилось - то требуется переигровка с обычной командой.

        Args:
            health_list: Список состояний титанов после боя.
            battle_state: Состояние боя.
        Returns:
            Требуется переигровка или нет.
        """
        if not battle_state.is_healing_try:
            for titan_after_battle in health_list:
                self.__resolve_heal(titan_after_battle, battle_state)
            return False
        else:
            need_healing_names: set[str] = set()
            need_healing_map: dict[str, TitanHealth] = {}

            for titan in battle_state.need_healing:
                need_healing_names.add(titan.name)
                need_healing_map[titan.name] = titan

            for titan_after_battle in health_list:
                if titan_after_battle.name in need_healing_names:
                    titan_before_battle = need_healing_map[titan_after_battle.name]
                    if titan_after_battle.health < titan_before_battle.health:
                        logger.debug(
                            f"Не удалось вылечить титана: {titan_after_battle.name}, "
                            f"до={titan_before_battle.health}, после={titan_after_battle.health}"
                        )
                        return True
                    self.__resolve_heal(titan_after_battle, battle_state)
                else:
                    self.__resolve_heal(titan_after_battle, battle_state)
            return False

    def __resolve_heal(self, titan: TitanStatus, battle_state: BattleState) -> None:
        if titan.name not in self._healing_rules.titans:
            return
        elif titan.health >= self._healing_rules.heal_below:
            battle_state.remove_from_heal_list(
                TitanHealth(name=titan.name, health=titan.health)
            )
        else:
            battle_state.add_to_leal_list(
                TitanHealth(name=titan.name, health=titan.health)
            )
            logger.info(f"Требуется лечение: {titan.name}")
