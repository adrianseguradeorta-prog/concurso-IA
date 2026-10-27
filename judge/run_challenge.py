from __future__ import annotations

import argparse
from importlib import import_module

from common.simulator import generate_scenario, run_agent


OFFICIAL_SEEDS = (7, 19, 31, 43, 59, 71, 83, 97, 109, 127)
PLAYERS = {
    "adri": "players.adri.solution",
    "raquel": "players.raquel.solution",
}


def evaluate(player: str) -> dict:
    module = import_module(PLAYERS[player])
    decide = module.decide

    results = []
    for seed in OFFICIAL_SEEDS:
        scenario = generate_scenario(seed)
        results.append(run_agent(decide, scenario))

    return {
        "player": player,
        "score": sum(r["score"] for r in results),
        "completed": sum(1 for r in results if r["completed"]),
        "invalid_moves": sum(r["invalid_moves"] for r in results),
        "results": results,
    }


def print_report(reports: list[dict]) -> None:
    print("\nNEREID — RONDA 1")
    print("=" * 58)
    print(f"{'Jugador':<12} {'Puntos':>10} {'Misiones':>12} {'Inválidos':>12}")
    print("-" * 58)

    ordered = sorted(reports, key=lambda r: (-r["score"], r["invalid_moves"], r["player"]))
    for report in ordered:
        print(
            f"{report['player'].capitalize():<12} "
            f"{report['score']:>10} "
            f"{report['completed']:>9}/{len(OFFICIAL_SEEDS):<2} "
            f"{report['invalid_moves']:>12}"
        )

    print("=" * 58)
    if len(ordered) > 1:
        if ordered[0]["score"] == ordered[1]["score"]:
            print("Resultado: empate")
        else:
            print(f"Ganador provisional: {ordered[0]['player'].capitalize()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta el benchmark oficial de NEREID.")
    parser.add_argument("--player", choices=PLAYERS.keys(), help="Evalúa solo un competidor.")
    parser.add_argument("--details", action="store_true", help="Muestra el resultado de cada misión.")
    args = parser.parse_args()

    selected = [args.player] if args.player else list(PLAYERS)
    reports = [evaluate(player) for player in selected]
    print_report(reports)

    if args.details:
        for report in reports:
            print(f"\n{report['player'].upper()}")
            for result in report["results"]:
                print(
                    f"seed={result['seed']:>3} score={result['score']:>3} "
                    f"completed={str(result['completed']):<5} "
                    f"energy={result['energy']:>3} invalid={result['invalid_moves']}"
                )


if __name__ == "__main__":
    main()
