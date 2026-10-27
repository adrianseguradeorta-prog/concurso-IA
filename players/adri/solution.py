from __future__ import annotations

from collections import deque


MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


def _next_step(start, goal, size, obstacles):
    """Baseline BFS. Replace or improve this however you want."""
    if start == goal:
        return "WAIT"

    queue = deque([start])
    previous = {start: None}
    previous_action = {}

    while queue:
        current = queue.popleft()
        for action, (dx, dy) in MOVES.items():
            nxt = (current[0] + dx, current[1] + dy)
            if not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                continue
            if nxt in obstacles or nxt in previous:
                continue
            previous[nxt] = current
            previous_action[nxt] = action
            if nxt == goal:
                node = nxt
                while previous[node] != start:
                    node = previous[node]
                return previous_action[node]
            queue.append(nxt)

    return "WAIT"


def decide(observation: dict) -> str:
    """Starter agent for Adri.

    It simply travels to the nearest remaining target by Manhattan distance and,
    once all targets have been visited, returns to base. This is intentionally
    only a baseline: Adri's competition code starts here.
    """
    position = tuple(observation["position"])
    base = tuple(observation["base"])
    targets = [tuple(t) for t in observation["targets_remaining"]]
    obstacles = {tuple(o) for o in observation["obstacles"]}
    size = observation["grid_size"]

    if targets:
        goal = min(targets, key=lambda t: abs(t[0] - position[0]) + abs(t[1] - position[1]))
    else:
        goal = base

    return _next_step(position, goal, size, obstacles)
