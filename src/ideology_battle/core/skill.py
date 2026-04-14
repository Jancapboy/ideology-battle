"""Skill system for units."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ideology_battle.core.buff import Buff
from ideology_battle.core.unit import Unit


@dataclass
class Event:
    type: str
    source: Unit
    target: Optional[Unit]
    value: float
    message: str = ""


class Skill(ABC):
    """Abstract base class for all skills."""

    name: str = ""
    cooldown: int = 0

    @abstractmethod
    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        """Apply skill effect and return list of events."""
        ...


class InvisibleHand(Skill):
    """Capitalism: market invisible hand."""

    name = "市场无形之手"
    cooldown = 4

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        events: List[Event] = []
        if allies:
            target = max(allies, key=lambda u: u.current_atk)
            buff = Buff("market_boost", "atk", target.atk * 0.3, 3, self.name)
            target.buffs.append(buff)
            events.append(Event("buff", caster, target, buff.value, f"{target.name} 获得市场 boost"))
            # 20% chance to bankrupt lowest HP ally
            victim = min(allies, key=lambda u: u.hp)
            if random.random() < 0.2:
                victim.take_damage(victim.hp)
                events.append(
                    Event("death", caster, victim, victim.hp, f"{victim.name} 被市场无情淘汰")
                )
        return events


class LowDesireShield(Skill):
    """Tang ping: low desire shield."""

    name = "低欲望护盾"
    cooldown = 0

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        return []


class ZeroSumGame(Skill):
    """Nei juan: zero sum game."""

    name = "零和博弈"
    cooldown = 3

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        events: List[Event] = []
        if enemies:
            target = min(enemies, key=lambda u: u.hp)
            steal = target.spd * 0.2
            target.buffs.append(Buff("spd_steal", "spd", -steal, 3, self.name))
            caster.buffs.append(Buff("spd_gain", "spd", steal, 3, self.name))
            events.append(
                Event("buff", caster, target, steal, f"{caster.name} 从 {target.name} 偷取速度")
            )
        return events


class ExponentialGrowth(Skill):
    """AI: exponential growth."""

    name = "指数增长"
    cooldown = 0

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        return []


class Overdraft(Skill):
    """996: overdraft."""

    name = "透支"
    cooldown = 0

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        return []


class DistributedResistance(Skill):
    """Remote work: distributed resistance."""

    name = "分布式抗性"
    cooldown = 0

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        return []


class PopulistRhetoric(Skill):
    """Min zhu: populist rhetoric."""

    name = "民粹 rhetoric"
    cooldown = 5

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        events: List[Event] = []
        for ally in allies:
            ally.heal(ally.max_hp * 0.15)
            events.append(Event("heal", caster, ally, ally.max_hp * 0.15, f"{ally.name} 被民意治愈"))
        return events


class AlgorithmicOppression(Skill):
    """Algorithm recommendation: algorithmic oppression."""

    name = "算法压迫"
    cooldown = 4

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        events: List[Event] = []
        for enemy in enemies[:3]:
            damage = caster.current_atk * 0.5
            enemy.take_damage(damage)
            events.append(Event("damage", caster, enemy, damage, f"{enemy.name} 被算法推送伤害"))
        return events


class ConsumerismFrenzy(Skill):
    """Consumerism: consumption frenzy."""

    name = "消费狂热"
    cooldown = 4

    def apply(self, caster: Unit, allies: List[Unit], enemies: List[Unit]) -> List[Event]:
        events: List[Event] = []
        if enemies:
            target = max(enemies, key=lambda u: u.current_atk)
            damage = caster.current_atk * 1.2
            target.take_damage(damage)
            caster.heal(damage * 0.3)
            events.append(
                Event("damage", caster, target, damage, f"{target.name} 被消费主义吞噬")
            )
            events.append(Event("heal", caster, caster, damage * 0.3, f"{caster.name} 回血"))
        return events


SKILL_REGISTRY = {
    "invisible_hand": InvisibleHand,
    "low_desire_shield": LowDesireShield,
    "zero_sum_game": ZeroSumGame,
    "exponential_growth": ExponentialGrowth,
    "overdraft": Overdraft,
    "distributed_resistance": DistributedResistance,
    "populist_rhetoric": PopulistRhetoric,
    "algorithmic_oppression": AlgorithmicOppression,
    "consumerism_frenzy": ConsumerismFrenzy,
}
