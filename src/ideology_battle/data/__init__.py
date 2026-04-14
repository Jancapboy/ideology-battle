"""Data loading utilities."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

from ideology_battle.core.skill import SKILL_REGISTRY
from ideology_battle.core.unit import Unit


_DATA_DIR = Path(__file__).resolve().parent


def load_all_units() -> Dict[str, Unit]:
    with open(_DATA_DIR / "units.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    units: Dict[str, Unit] = {}
    for uid, info in data.items():
        skill = None
        if info.get("skill_id"):
            skill_cls = SKILL_REGISTRY.get(info["skill_id"])
            if skill_cls:
                skill = skill_cls()
        units[uid] = Unit(
            id=uid,
            name=info["name"],
            faction_tags=info["faction_tags"],
            hp=info["base_hp"],
            max_hp=info["base_hp"],
            atk=info["base_atk"],
            spd=info["base_spd"],
            skill=skill,
        )
    return units


def get_random_team(units: Dict[str, Unit], size: int = 5) -> List[Unit]:
    pool = list(units.values())
    return [random.choice(pool).clone() for _ in range(size)]


def get_demo_teams(units: Dict[str, Unit]) -> tuple[List[Unit], List[Unit]]:
    """Return two themed demo teams."""
    team0_ids = ["capitalism", "consumerism", "996", "blockchain", "ai"]
    team1_ids = ["socialism", "tang_ping", "remote_work", "democracy", "climate_crisis"]
    team0 = [units[i].clone() for i in team0_ids if i in units]
    team1 = [units[i].clone() for i in team1_ids if i in units]
    return team0, team1
