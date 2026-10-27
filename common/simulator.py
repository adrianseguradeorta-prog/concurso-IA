from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Callable


ACTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "WAIT": (0, 0),
}


@dataclass(frozen=True)
class Scenario:
    seed: int
    size: int
    base: tuple[int, int]
    targets: tuple[tuple[int, int], ...]
    obstacles: frozenset[tuple[int, int]]
    energy: int = 120


def _reachable(start: tuple[int, int], size: int, obstacles: set[tuple[int, int]]) -> set[tuple[int, int]]:
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ACTIONS.values():
            if (dx, dy) == (0, 0):
                continue
            nxt = (x + dx, y + dy)
            if not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                continue
            if nxt in obstacles or nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)
    return seen


def generate_scenario(seed: int, size: int = 20, obstacle_count: int = 28, target_count: int = 3) -> Scenario:
    """Create a deterministic, reachable scenario for a given seed."""
    attempt = 0
    while True:
        rng = random.Random(seed + attempt * 100_003)
        base = (rng.randrange(size), rng.randrange(size))

        cells = [(x, y) for x in range(size) for y in range(size) if (x, y) != base]
        rng.shuffle(cells)
        obstacles = set(cells[:obstacle_count])
        available = [cell for cell in cells[obstacle_count:] if cell not in obstacles]
        targets = tuple(available[:target_count])

        reachable = _reachable(base, size, obstacles)
        if all(target in reachable for target in targets):
            return Scenario(
                seed=seed,
                size=size,
                base=base,
                targets=targets,
                obstacles=frozenset(obstacles),
            )
        attempt += 1


class Simulator:
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.position = scenario.base
        self.targets_remaining = set(scenario.targets)
        self.energy = scenario.energy
        self.steps = 0
        self.invalid_moves = 0
        self.completed = False

    def observation(self) -> dict:
        return {
            "position": self.position,
            "base": self.scenario.base,
            "targets_remaining": tuple(sorted(self.targets_remaining)),
            "obstacles": tuple(sorted(self.scenario.obstacles)),
            "grid_size": self.scenario.size,
            "energy": self.energy,
            "steps": self.steps,
        }

    def step(self, action: str) -> None:
        if self.energy <= 0 or self.completed:
            return

        self.steps += 1
        self.energy -= 1

        if action not in ACTIONS:
            self.invalid_moves += 1
            return

        dx, dy = ACTIONS[action]
        candidate = (self.position[0] + dx, self.position[1] + dy)

        if action != "WAIT":
            outside = not (0 <= candidate[0] < self.scenario.size and 0 <= candidate[1] < self.scenario.size)
            blocked = candidate in self.scenario.obstacles
            if outside or blocked:
                self.invalid_moves += 1
                return

        self.position = candidate
        self.targets_remaining.discard(self.position)

        if not self.targets_remaining and self.position == self.scenario.base:
            self.completed = True

    def score(self) -> int:
        visited = len(self.scenario.targets) - len(self.targets_remaining)
        score = visited * 100
        if self.completed:
            score += 200 + self.energy
        score -= self.invalid_moves * 2
        return score


def run_agent(decide: Callable[[dict], str], scenario: Scenario, max_steps: int = 120) -> dict:
    sim = Simulator(scenario)
    while sim.energy > 0 and sim.steps < max_steps and not sim.completed:
        action = decide(sim.observation())
        sim.step(action)

    return {
        "seed": scenario.seed,
        "score": sim.score(),
        "completed": sim.completed,
        "visited": len(scenario.targets) - len(sim.targets_remaining),
        "energy": sim.energy,
        "steps": sim.steps,
        "invalid_moves": sim.invalid_moves,
    }
