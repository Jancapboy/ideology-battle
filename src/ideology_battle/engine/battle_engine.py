"""Battle engine core."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ideology_battle.core.constants import GRID_SIZE, MAX_TURNS
from ideology_battle.core.faction import FACTION_REGISTRY
from ideology_battle.core.skill import Event
from ideology_battle.core.unit import Position, Unit
from ideology_battle.engine.ai_controller import Action, decide_action


@dataclass
class BattleLog:
    events: List[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.events.append(message)


@dataclass
class BattleState:
    units: List[Unit]
    turn: int = 0
    log: BattleLog = field(default_factory=BattleLog)
    winner: Optional[int] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def team0(self) -> List[Unit]:
        return [u for u in self.units if u.team == 0]

    @property
    def team1(self) -> List[Unit]:
        return [u for u in self.units if u.team == 1]

    def alive(self, team: int) -> List[Unit]:
        return [u for u in self.units if u.team == team and u.is_alive]

    def check_winner(self) -> Optional[int]:
        t0_alive = len(self.alive(0))
        t1_alive = len(self.alive(1))
        if t0_alive == 0:
            return 1
        if t1_alive == 0:
            return 0
        return None

    def _snapshot(self) -> Dict[str, any]:
        return {
            "turn": self.turn,
            "units": [
                {
                    "name": u.name,
                    "team": u.team,
                    "hp": u.hp,
                    "position": (u.position.x, u.position.y) if u.position else None,
                }
                for u in self.units
            ],
        }


class BattleEngine:
    """Runs a battle between two teams."""

    def __init__(self, team0: List[Unit], team1: List[Unit]) -> None:
        self.state = BattleState(units=[])
        for u in team0:
            nu = u.clone()
            nu.team = 0
            self.state.units.append(nu)
        for u in team1:
            nu = u.clone()
            nu.team = 1
            self.state.units.append(nu)
        self._place_units()
        self._apply_synergies()
        self.state.history.append(self.state._snapshot())

    def _place_units(self) -> None:
        t0 = [u for u in self.state.units if u.team == 0]
        t1 = [u for u in self.state.units if u.team == 1]
        for i, u in enumerate(t0):
            u.position = Position(i % 2, i // 2)
        for i, u in enumerate(t1):
            u.position = Position(GRID_SIZE - 1 - (i % 2), i // 2)

    def _apply_synergies(self) -> None:
        for faction in FACTION_REGISTRY.values():
            msgs = faction.apply(self.state.units)
            for m in msgs:
                self.state.log.add(m)

    def _position_map(self) -> Dict[Tuple[int, int], Unit]:
        pos_map: Dict[Tuple[int, int], Unit] = {}
        for u in self.state.units:
            if u.is_alive and u.position:
                pos_map[(u.position.x, u.position.y)] = u
        return pos_map

    def _resolve_action(self, action: Action) -> None:
        unit = action.unit
        if not unit.is_alive:
            return

        if action.type == "move" and action.destination:
            pos_map = self._position_map()
            dest = action.destination
            if (dest.x, dest.y) not in pos_map:
                unit.position = dest
                self.state.log.add(f"[{unit.name}] 移动到 ({dest.x}, {dest.y})")

        elif action.type == "attack" and action.target:
            target = action.target
            if target.is_alive:
                damage = unit.current_atk
                # 996 overdraft: 2x damage every 2 turns for first 10 turns
                if unit.id == "996" and self.state.turn <= 10 and self.state.turn % 2 == 1:
                    damage *= 2.0
                    self.state.log.add(f"[{unit.name}] 透支爆发!")
                # remote work aoe reduction
                if any(u.id == "remote_work" for u in self.state.alive(target.team)):
                    damage *= 0.5
                    self.state.log.add(f"[{target.name}] 分布式抗性减免伤害")
                target.take_damage(damage)
                self.state.log.add(f"[{unit.name}] 攻击 [{target.name}] 造成 {damage:.1f} 伤害")
                if not target.is_alive:
                    self.state.log.add(f"[{target.name}] 被击败!")
                    # AI exponential growth on kill
                    if unit.id == "ai":
                        unit.atk *= 1.15
                        unit.max_hp *= 1.15
                        unit.heal(unit.max_hp * 0.15)
                        self.state.log.add(f"[{unit.name}] 指数增长! ATK/HP 提升")

        elif action.type == "cast" and unit.skill:
            allies = self.state.alive(unit.team)
            enemies = self.state.alive(1 - unit.team)
            events = unit.skill.apply(unit, allies, enemies)
            self.state.log.add(f"[{unit.name}] 释放技能: {unit.skill.name}")
            for ev in events:
                if ev.type == "damage" and ev.target:
                    ev.target.take_damage(ev.value)
                    self.state.log.add(f"  → {ev.message} ({ev.value:.1f})")
                    if not ev.target.is_alive:
                        self.state.log.add(f"  → [{ev.target.name}] 被击败!")
                        if unit.id == "ai":
                            unit.atk *= 1.15
                            unit.max_hp *= 1.15
                            unit.heal(unit.max_hp * 0.15)
                            self.state.log.add(f"[{unit.name}] 指数增长! ATK/HP 提升")
                elif ev.type == "buff":
                    self.state.log.add(f"  → {ev.message}")
                elif ev.type == "heal":
                    self.state.log.add(f"  → {ev.message}")
                elif ev.type == "death":
                    if ev.target:
                        ev.target.take_damage(ev.target.hp)
                        self.state.log.add(f"  → {ev.message}")

    def _passive_effects(self) -> None:
        # 996 overdraft self-damage every 10 turns
        for u in self.state.units:
            if u.is_alive and u.id == "996" and self.state.turn > 0 and self.state.turn % 10 == 0:
                dmg = u.max_hp * 0.1
                u.take_damage(dmg)
                self.state.log.add(f"[{u.name}] 透支反噬，损失 {dmg:.1f} HP")
                if not u.is_alive:
                    self.state.log.add(f"[{u.name}] 过劳死!")

    def step(self) -> bool:
        """Execute one turn. Returns True if battle is over."""
        self.state.turn += 1
        self.state.log.add(f"=== Turn {self.state.turn} ===")

        # Tick buffs and cooldowns
        for u in self.state.units:
            u.tick_buffs()

        # Passive effects
        self._passive_effects()
        if self.state.check_winner() is not None:
            return True

        # Determine turn order by current SPD descending
        actors = [u for u in self.state.units if u.is_alive]
        actors.sort(key=lambda u: u.current_spd, reverse=True)

        for unit in actors:
            if not unit.is_alive:
                continue
            allies = self.state.alive(unit.team)
            enemies = self.state.alive(1 - unit.team)
            if not enemies:
                break
            action = decide_action(unit, allies, enemies)
            self._resolve_action(action)
            # Check winner after each action
            if self.state.check_winner() is not None:
                return True

        self.state.history.append(self.state._snapshot())
        return self.state.check_winner() is not None or self.state.turn >= MAX_TURNS

    def run(self) -> BattleState:
        """Run the full battle until completion."""
        for _ in range(MAX_TURNS):
            if self.step():
                break
        self.state.winner = self.state.check_winner()
        if self.state.winner is None:
            # If max turns reached, team with more total HP wins
            hp0 = sum(u.hp for u in self.state.alive(0))
            hp1 = sum(u.hp for u in self.state.alive(1))
            self.state.winner = 0 if hp0 >= hp1 else 1
            self.state.log.add(f"回合上限到达，按剩余血量判定: Team {self.state.winner} 获胜")
        else:
            self.state.log.add(f"Team {self.state.winner} 获胜!")
        return self.state
