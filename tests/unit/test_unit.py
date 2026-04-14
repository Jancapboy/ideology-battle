"""Unit tests for core unit model."""

import pytest

from ideology_battle.core.unit import Buff, Position, Unit


class TestPosition:
    def test_distance_to(self) -> None:
        p1 = Position(0, 0)
        p2 = Position(3, 4)
        assert p1.distance_to(p2) == 7

    def test_is_valid(self) -> None:
        assert Position(0, 0).is_valid() is True
        assert Position(7, 7).is_valid() is True
        assert Position(8, 0).is_valid() is False


class TestUnit:
    def test_unit_alive(self) -> None:
        u = Unit(id="test", name="Test", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0)
        assert u.is_alive is True
        u.take_damage(100)
        assert u.is_alive is False

    def test_unit_heal(self) -> None:
        u = Unit(id="test", name="Test", faction_tags=["社会系"], hp=50, max_hp=100, atk=10, spd=1.0)
        u.heal(30)
        assert u.hp == 80
        u.heal(100)
        assert u.hp == 100

    def test_current_atk_with_buff(self) -> None:
        u = Unit(id="test", name="Test", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.buffs.append(Buff("rage", "atk", 5.0, 2))
        assert u.current_atk == 15.0

    def test_clone(self) -> None:
        u = Unit(id="test", name="Test", faction_tags=["社会系"], hp=80, max_hp=100, atk=10, spd=1.0)
        u2 = u.clone()
        assert u2.hp == u.hp
        u2.take_damage(10)
        assert u.hp == 80

    def test_tick_buffs(self) -> None:
        u = Unit(id="test", name="Test", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0)
        u.buffs.append(Buff("tmp", "atk", 5.0, 1))
        u.tick_buffs()
        assert len(u.buffs) == 0
