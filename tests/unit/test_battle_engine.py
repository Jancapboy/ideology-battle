"""Unit tests for battle engine."""

import pytest

from ideology_battle.core.unit import Unit
from ideology_battle.engine.battle_engine import BattleEngine


def make_unit(uid: str, name: str, team: int = 0) -> Unit:
    return Unit(id=uid, name=name, faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0, team=team)


class TestBattleEngine:
    def test_places_units(self) -> None:
        t0 = [make_unit("a", "A")]
        t1 = [make_unit("b", "B")]
        engine = BattleEngine(t0, t1)
        assert engine.state.team0[0].position is not None
        assert engine.state.team1[0].position is not None

    def test_battle_ends(self) -> None:
        t0 = [make_unit("a", "A")]
        t1 = [make_unit("b", "B", team=1)]
        engine = BattleEngine(t0, t1)
        state = engine.run()
        assert state.winner in (0, 1)

    def test_turn_increments(self) -> None:
        t0 = [make_unit("a", "A")]
        t1 = [make_unit("b", "B", team=1)]
        engine = BattleEngine(t0, t1)
        engine.step()
        assert engine.state.turn == 1

    def test_log_not_empty(self) -> None:
        t0 = [make_unit("a", "A")]
        t1 = [make_unit("b", "B", team=1)]
        engine = BattleEngine(t0, t1)
        engine.run()
        assert len(engine.state.log.events) > 0

    def test_max_turns_cap(self) -> None:
        t0 = [make_unit("a", "A")]
        t1 = [make_unit("b", "B", team=1)]
        engine = BattleEngine(t0, t1)
        for _ in range(200):
            if engine.step():
                break
        assert engine.state.turn <= 100 or engine.state.winner is not None
