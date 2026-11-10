"""NEREID-RA: rutas mínimas, planificación global y presupuesto energético.

Usa exclusivamente la biblioteca estándar y no altera el simulador común.
"""
from collections import deque

MOVES = (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0))


def _bfs(start, size, blocked):
    """Devuelve distancias y primera acción para rutas mínimas desde start."""
    distances = {start: 0}
    first = {}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for action, dx, dy in MOVES:
            nxt = (x + dx, y + dy)
            if not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                continue
            if nxt in blocked or nxt in distances:
                continue
            distances[nxt] = distances[(x, y)] + 1
            first[nxt] = action if (x, y) == start else first[(x, y)]
            queue.append(nxt)
    return distances, first


def decide(observation: dict) -> str:
    """Maximiza objetivos y prima de regreso; minimiza energía consumida."""
    position = tuple(observation["position"])
    base = tuple(observation["base"])
    targets = [tuple(t) for t in observation["targets_remaining"]]
    obstacles = {tuple(o) for o in observation["obstacles"]}
    size = int(observation["grid_size"])
    energy = int(observation["energy"])

    from_start, first_action = _bfs(position, size, obstacles)
    if not targets:
        return first_action.get(base, "WAIT")

    # Defensa ante futuras rondas con muchos objetivos.
    if len(targets) > 12:
        reachable = [t for t in targets if from_start.get(t, energy + 1) <= energy]
        goal = min(reachable, key=lambda t: (from_start[t], t), default=None)
        return first_action.get(goal, "WAIT")

    n = len(targets)
    from_target = [_bfs(t, size, obstacles)[0] for t in targets]
    # (máscara, último objetivo) -> (coste, primer objetivo)
    dp = {}
    for j, target in enumerate(targets):
        cost = from_start.get(target)
        if cost is not None and cost <= energy:
            dp[(1 << j, j)] = (cost, j)

    for mask in range(1, 1 << n):
        for last in range(n):
            state = (mask, last)
            if state not in dp:
                continue
            cost, first = dp[state]
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                segment = from_target[last].get(targets[nxt])
                if segment is None or cost + segment > energy:
                    continue
                candidate = (cost + segment, first)
                new_state = (mask | (1 << nxt), nxt)
                if candidate < dp.get(new_state, (float("inf"), n)):
                    dp[new_state] = candidate

    # Completar TODOS y volver siempre supera cualquier misión parcial.
    full = (1 << n) - 1
    complete = []
    for last in range(n):
        state = (full, last)
        if state not in dp:
            continue
        cost, first = dp[state]
        back = from_target[last].get(base)
        if back is not None and cost + back <= energy:
            complete.append((cost + back, first))
    if complete:
        _, first = min(complete)
        return first_action.get(targets[first], "WAIT")

    # Si completar es imposible, rescatar el máximo número de objetivos.
    # Para igual número de objetivos, minimizar el consumo.
    if dp:
        _, _, first = min(
            (-mask.bit_count(), cost, first)
            for (mask, last), (cost, first) in dp.items()
        )
        return first_action.get(targets[first], "WAIT")
    return "WAIT"

