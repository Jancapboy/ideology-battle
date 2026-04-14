"""Unit tests for skills."""

import pytest

from ideology_battle.core.skill import (
    AlgorithmicOppression,
    ConsumerismFrenzy,
    InvisibleHand,
    PopulistRhetoric,
    ZeroSumGame,
)
from ideology_battle.core.unit import Unit


class TestInvisibleHand:
    def test_buffs_ally(self) -> None:
        skill = InvisibleHand()
        caster = Unit(id="cap", name=" capitalism", faction_tags=["经济系"], hp=100, max_hp=100, atk=10, spd=1.0, skill=skill)
        ally = Unit(id="ally", name="Ally", faction_tags=["经济系"], hp=50, max_hp=100, atk=10, spd=1.0)
        events = skill.apply(caster, [caster, ally], [])
        assert any(e.type == "buff" for e in events)


class TestZeroSumGame:
    def test_steals_spd(self) -> None:
        skill = ZeroSumGame()
        caster = Unit(id="nei", name="内卷", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0, skill=skill)
        enemy = Unit(id="en", name="Enemy", faction_tags=["技术系"], hp=100, max_hp=100, atk=10, spd=1.0)
        skill.apply(caster, [caster], [enemy])
        assert any(b.name == "spd_gain" for b in caster.buffs)
        assert any(b.name == "spd_steal" for b in enemy.buffs)


class TestPopulistRhetoric:
    def test_heals_all_allies(self) -> None:
        skill = PopulistRhetoric()
        caster = Unit(id="dem", name="民主", faction_tags=["政治系"], hp=100, max_hp=100, atk=10, spd=1.0)
        ally = Unit(id="a1", name="A1", faction_tags=["政治系"], hp=50, max_hp=100, atk=10, spd=1.0)
        events = skill.apply(caster, [caster, ally], [])
        assert len([e for e in events if e.type == "heal"]) == 2


class TestAlgorithmicOppression:
    def test_aoe_damage(self) -> None:
        skill = AlgorithmicOppression()
        caster = Unit(id="alg", name="算法推荐", faction_tags=["技术系"], hp=100, max_hp=100, atk=10, spd=1.0)
        enemies = [
            Unit(id="e1", name="E1", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0),
            Unit(id="e2", name="E2", faction_tags=["社会系"], hp=100, max_hp=100, atk=10, spd=1.0),
        ]
        events = skill.apply(caster, [], enemies)
        assert len(events) == 2
        assert events[0].type == "damage"


class TestConsumerismFrenzy:
    def test_damage_and_heal(self) -> None:
        skill = ConsumerismFrenzy()
        caster = Unit(id="con", name="消费主义", faction_tags=["经济系"], hp=80, max_hp=100, atk=10, spd=1.0)
        enemy = Unit(id="en", name="Enemy", faction_tags=["技术系"], hp=100, max_hp=100, atk=20, spd=1.0)
        events = skill.apply(caster, [], [enemy])
        types = [e.type for e in events]
        assert "damage" in types
        assert "heal" in types
