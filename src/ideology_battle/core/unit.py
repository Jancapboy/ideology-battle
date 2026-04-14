"""Core data models for units, positions, and events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from ideology_battle.core.constants import GRID_SIZE


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def distance_to(self, other: Position) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def is_valid(self) -> bool:
        return 0 <= self.x < GRID_SIZE and 0 <= self.y < GRID_SIZE


@dataclass
class Buff:
    name: str
    stat: str
    value: float
    duration: int
    source: str = ""


@dataclass
class Unit:
    id: str
    name: str
    faction_tags: List[str]
    hp: float
    max_hp: float
    atk: float
    spd: float
    skill: Optional[Any] = None
    buffs: List[Buff] = field(default_factory=list)
    position: Optional[Position] = None
    level: int = 1
    team: int = 0
    cooldown_remaining: int = 0

    @property
    def current_atk(self) -> float:
        base = self.atk * (1 + 0.5 * (self.level - 1))
        bonus = sum(b.value for b in self.buffs if b.stat == "atk")
        return max(1.0, base + bonus)

    @property
    def current_spd(self) -> float:
        base = self.spd * (1 + 0.3 * (self.level - 1))
        bonus = sum(b.value for b in self.buffs if b.stat == "spd")
        return max(0.1, base + bonus)

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: float) -> None:
        self.hp = max(0.0, self.hp - damage)

    def heal(self, amount: float) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def tick_buffs(self) -> None:
        remaining: List[Buff] = []
        for b in self.buffs:
            b.duration -= 1
            if b.duration > 0:
                remaining.append(b)
        self.buffs = remaining
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

    def clone(self) -> Unit:
        return Unit(
            id=self.id,
            name=self.name,
            faction_tags=list(self.faction_tags),
            hp=self.hp,
            max_hp=self.max_hp,
            atk=self.atk,
            spd=self.spd,
            skill=self.skill,
            buffs=[Buff(b.name, b.stat, b.value, b.duration, b.source) for b in self.buffs],
            position=self.position,
            level=self.level,
            team=self.team,
            cooldown_remaining=self.cooldown_remaining,
        )
