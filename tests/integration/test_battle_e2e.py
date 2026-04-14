"""End-to-end integration tests for full battles."""

import subprocess
import sys
from pathlib import Path

from ideology_battle.data import get_demo_teams, load_all_units
from ideology_battle.engine.battle_engine import BattleEngine
from ideology_battle.utils.replay import dump_replay, load_replay


class TestBattleE2E:
    def test_demo_teams_produce_winner(self) -> None:
        units = load_all_units()
        team0, team1 = get_demo_teams(units)
        engine = BattleEngine(team0, team1)
        state = engine.run()
        assert state.winner in (0, 1)
        alive0 = len(state.alive(0))
        alive1 = len(state.alive(1))
        assert alive0 == 0 or alive1 == 0 or state.turn >= 100

    def test_replay_serialization(self) -> None:
        units = load_all_units()
        team0, team1 = get_demo_teams(units)
        engine = BattleEngine(team0, team1)
        engine.run()
        raw = dump_replay(engine.state)
        restored = load_replay(raw)
        assert restored["winner"] == engine.state.winner
        assert len(restored["log"]) == len(engine.state.log.events)

    def test_cli_demo_runs(self) -> None:
        import os

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
        result = subprocess.run(
            [sys.executable, "-m", "ideology_battle.cli.main", "demo"],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert "获胜方" in result.stdout or "Team" in result.stdout

    def test_cli_quick_runs(self) -> None:
        import os

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
        result = subprocess.run(
            [sys.executable, "-m", "ideology_battle.cli.main", "quick"],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert "获胜方" in result.stdout or "Team" in result.stdout
