"""Faction synergy system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ideology_battle.core.buff import Buff
from ideology_battle.core.unit import Unit


@dataclass
class SynergyEffect:
    threshold: int
    buff_name: str
    stat: str
    value: float
    duration: int


@dataclass
class Faction:
    name: str
    effects: List[SynergyEffect]

    def apply(self, units: List[Unit]) -> List[str]:
        """Apply synergy buffs to eligible units and return log messages."""
        messages: List[str] = []
        counts: Dict[str, int] = {}
        for u in units:
            if self.name in u.faction_tags:
                counts[u.team] = counts.get(u.team, 0) + 1

        for team, count in counts.items():
            team_units = [u for u in units if u.team == team and self.name in u.faction_tags]
            for effect in sorted(self.effects, key=lambda e: e.threshold, reverse=True):
                if count >= effect.threshold:
                    for u in team_units:
                        u.buffs.append(
                            Buff(
                                effect.buff_name,
                                effect.stat,
                                effect.value,
                                effect.duration,
                                self.name,
                            )
                        )
                    messages.append(f"Team {team} 触发 {self.name} {effect.threshold} 人羁绊")
                    break
        return messages


FACTION_REGISTRY = {
    "经济系": Faction(
        "经济系",
        [
            SynergyEffect(2, "eco_2", "atk", 5.0, 999),
            SynergyEffect(4, "eco_4", "atk", 15.0, 999),
        ],
    ),
    "技术系": Faction(
        "技术系",
        [
            SynergyEffect(2, "tech_2", "spd", 0.2, 999),
            SynergyEffect(4, "tech_4", "spd", 0.5, 999),
        ],
    ),
    "社会系": Faction(
        "社会系",
        [
            SynergyEffect(2, "social_2", "max_hp", 20.0, 999),
            SynergyEffect(4, "social_4", "max_hp", 50.0, 999),
        ],
    ),
    "反乌托邦系": Faction(
        "反乌托邦系",
        [
            SynergyEffect(2, "dystopia_2", "atk", 8.0, 999),
            SynergyEffect(4, "dystopia_4", "atk", 25.0, 999),
        ],
    ),
}
