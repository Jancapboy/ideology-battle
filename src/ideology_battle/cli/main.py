"""Command-line interface for Ideology Battle Royale."""

from __future__ import annotations

import argparse
import random
import time
from typing import List

from ideology_battle.data import get_demo_teams, get_random_team, load_all_units
from ideology_battle.engine.battle_engine import BattleEngine


def render_grid(engine: BattleEngine) -> str:
    from ideology_battle.core.constants import GRID_SIZE
    from ideology_battle.core.unit import Position

    lines: List[str] = []
    pos_map = {}
    for u in engine.state.units:
        if u.is_alive and u.position:
            pos_map[(u.position.x, u.position.y)] = u

    header = "   " + " ".join(str(x) for x in range(GRID_SIZE))
    lines.append(header)
    for y in range(GRID_SIZE):
        row = [str(y) + "  "]
        for x in range(GRID_SIZE):
            if (x, y) in pos_map:
                u = pos_map[(x, y)]
                symbol = u.name[0] if u.team == 0 else u.name[0].lower()
                row.append(symbol)
            else:
                row.append(".")
        lines.append(" ".join(row))
    return "\n".join(lines)


def run_demo(slow: bool = False) -> None:
    units = load_all_units()
    team0, team1 = get_demo_teams(units)
    engine = BattleEngine(team0, team1)

    print("=== Ideology Battle Royale ===")
    print(f"Team 0 (红方): {', '.join(u.name for u in engine.state.team0)}")
    print(f"Team 1 (蓝方): {', '.join(u.name for u in engine.state.team1)}")
    print()

    for _ in range(100):
        done = engine.step()
        print(render_grid(engine))
        # Print recent log events
        recent = engine.state.log.events[-5:]
        for ev in recent:
            print(ev)
        print()
        if slow:
            time.sleep(0.5)
        if done:
            break

    winner = engine.state.winner
    print(f"🏆 获胜方: Team {winner}")
    print("\n存活单位:")
    for u in engine.state.units:
        if u.is_alive:
            print(f"  {u.name}: {u.hp:.1f}/{u.max_hp:.1f} HP")


def run_quick(slow: bool = False) -> None:
    units = load_all_units()
    team0 = get_random_team(units, 5)
    team1 = get_random_team(units, 5)
    engine = BattleEngine(team0, team1)

    print("=== Ideology Battle Royale (随机对战) ===")
    print(f"Team 0: {', '.join(u.name for u in engine.state.team0)}")
    print(f"Team 1: {', '.join(u.name for u in engine.state.team1)}")
    print()

    for _ in range(100):
        done = engine.step()
        print(render_grid(engine))
        recent = engine.state.log.events[-5:]
        for ev in recent:
            print(ev)
        print()
        if slow:
            time.sleep(0.5)
        if done:
            break

    winner = engine.state.winner
    print(f"🏆 获胜方: Team {winner}")
    print("\n存活单位:")
    for u in engine.state.units:
        if u.is_alive:
            print(f"  {u.name}: {u.hp:.1f}/{u.max_hp:.1f} HP")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ideology Battle Royale")
    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser("demo", help="Run a themed demo battle")
    demo_parser.add_argument("--slow", action="store_true", help="Pause between turns")

    quick_parser = subparsers.add_parser("quick", help="Run a random quick battle")
    quick_parser.add_argument("--slow", action="store_true", help="Pause between turns")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(slow=args.slow)
    elif args.command == "quick":
        run_quick(slow=args.slow)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
