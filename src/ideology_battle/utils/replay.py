"""Replay serialization utilities."""

from __future__ import annotations

import json
from typing import Any, Dict, cast

from ideology_battle.engine.battle_engine import BattleState


def dump_replay(state: BattleState) -> str:
    """Serialize battle state to JSON string."""
    data = {
        "winner": state.winner,
        "turn": state.turn,
        "log": state.log.events,
        "history": state.history,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_replay(raw: str) -> Dict[str, Any]:
    """Deserialize battle state from JSON string."""
    return cast(Dict[str, Any], json.loads(raw))
