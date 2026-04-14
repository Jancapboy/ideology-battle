"""Unit tests for AI controller."""

from ideology_battle.core.unit import Position, Unit
from ideology_battle.engine.ai_controller import decide_action, find_nearest_enemy, move_towards


class TestFindNearestEnemy:
    def test_finds_closest(self) -> None:
        u = Unit(id="a", name="A", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.position = Position(0, 0)
        e1 = Unit(id="b", name="B", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        e1.position = Position(5, 0)
        e2 = Unit(id="c", name="C", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        e2.position = Position(1, 0)
        result = find_nearest_enemy(u, [e1, e2])
        assert result == e2


class TestMoveTowards:
    def test_moves_closer(self) -> None:
        u = Unit(id="a", name="A", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.position = Position(0, 0)
        t = Unit(id="b", name="B", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        t.position = Position(2, 0)
        dest = move_towards(u, t)
        assert dest is not None
        assert dest.x == 1


class TestDecideAction:
    def test_attacks_when_adjacent(self) -> None:
        u = Unit(id="a", name="A", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.position = Position(0, 0)
        e = Unit(id="b", name="B", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        e.position = Position(1, 0)
        action = decide_action(u, [], [e])
        assert action.type == "attack"

    def test_moves_when_far(self) -> None:
        u = Unit(id="a", name="A", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.position = Position(0, 0)
        e = Unit(id="b", name="B", faction_tags=["测试系"], hp=100, max_hp=100, atk=10, spd=1.0)
        e.position = Position(3, 0)
        action = decide_action(u, [], [e])
        assert action.type == "move"
