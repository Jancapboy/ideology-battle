"""AI controller for unit decision making."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ideology_battle.core.constants import GRID_SIZE
from ideology_battle.core.skill import Event
from ideology_battle.core.unit import Position, Unit


@dataclass
class Action:
    type: str
    unit: Unit
    target: Optional[Unit] = None
    destination: Optional[Position] = None


def find_nearest_enemy(unit: Unit, enemies: List[Unit]) -> Optional[Unit]:
    if not unit.position or not enemies:
        return None
    alive = [e for e in enemies if e.is_alive and e.position]
    if not alive:
        return None
    return min(alive, key=lambda e: unit.position.distance_to(e.position))  # type: ignore[union-attr]


def move_towards(unit: Unit, target: Unit) -> Optional[Position]:
    if not unit.position or not target.position:
        return None
    ux, uy = unit.position.x, unit.position.y
    tx, ty = target.position.x, target.position.y
    best: Optional[Position] = None
    best_dist = unit.position.distance_to(target.position)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = ux + dx, uy + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            p = Position(nx, ny)
            d = p.distance_to(target.position)
            if d < best_dist:
                best_dist = d
                best = p
    return best


def decide_action(unit: Unit, allies: List[Unit], enemies: List[Unit]) -> Action:
    target = find_nearest_enemy(unit, enemies)
    if not target or not unit.position or not target.position:
        return Action("idle", unit)

    dist = unit.position.distance_to(target.position)

    # Cast skill if available and cooldown is 0
    if unit.skill and unit.cooldown_remaining <= 0:
        unit.cooldown_remaining = unit.skill.cooldown
        return Action("cast", unit, target=target)

    # Attack if adjacent
    if dist <= 1:
        return Action("attack", unit, target=target)

    # Move towards target
    dest = move_towards(unit, target)
    if dest:
        return Action("move", unit, destination=dest)

    return Action("idle", unit)
