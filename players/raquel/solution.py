"""NEREID-RA3: planificador exacto y beam search con heurística aprendida."""
from __future__ import annotations
from collections import deque
from functools import lru_cache

MOVES = (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0))
MAX_STEPS = 120
EXACT_LIMIT = 12
BEAM_WIDTH = 96
INF = 10**8
_CURRENT_MAP = None
LEARNED_WEIGHTS = (0.889664, 1.0895102, 0.8707107, 0.4839643, 2.9991982)


@lru_cache(maxsize=512)
def _bfs(start, size, blocked_key):
    blocked = set(blocked_key)
    dist = {start: 0}
    first = {}
    q = deque([start])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)] + 1
        for action, dx, dy in MOVES:
            nxt = (x + dx, y + dy)
            if (not (0 <= nxt[0] < size and 0 <= nxt[1] < size)
                    or nxt in blocked or nxt in dist):
                continue
            dist[nxt] = d
            first[nxt] = action if (x, y) == start else first[(x, y)]
            q.append(nxt)
    return dist, first


def _exact(targets, budget, from_start, from_target, base):
    n = len(targets)
    full = (1 << n) - 1
    dp = {}
    for j, t in enumerate(targets):
        cost = from_start.get(t, INF)
        if cost <= budget:
            dp[(1 << j, j)] = (cost, j)
    for mask in range(1, full + 1):
        for last in range(n):
            state = (mask, last)
            item = dp.get(state)
            if item is None:
                continue
            cost, first = item
            remaining = full ^ mask
            while remaining:
                bit = remaining & -remaining
                nxt = bit.bit_length() - 1
                remaining ^= bit
                segment = from_target[last].get(targets[nxt], INF)
                new_cost = cost + segment
                if new_cost > budget:
                    continue
                key = (mask | bit, nxt)
                candidate = (new_cost, first)
                if candidate < dp.get(key, (INF, n)):
                    dp[key] = candidate
    complete = []
    for j in range(n):
        item = dp.get((full, j))
        if item is None:
            continue
        cost, first = item
        total = cost + from_target[j].get(base, INF)
        if total <= budget:
            complete.append((total, first))
    if complete:
        return min(complete)[1]
    if dp:
        return min((-mask.bit_count(), cost, first)
                   for (mask, last), (cost, first) in dp.items())[2]
    return None


def _beam(targets, budget, from_start, from_target, base, use_ml=True):
    n = len(targets)
    full = (1 << n) - 1
    D = [[from_target[i].get(t, INF) for t in targets] for i in range(n)]
    Dbase = [from_target[i].get(base, INF) for i in range(n)]
    start_dist = [from_start.get(t, INF) for t in targets]

    @lru_cache(maxsize=65536)
    def mst(mask):
        bits = [i for i in range(n) if mask & (1 << i)]
        if len(bits) <= 1:
            return 0
        active = {bits[0]}
        remaining = set(bits[1:])
        total = 0
        while remaining:
            cost, nxt = min((D[i][j], j) for i in active for j in remaining)
            if cost >= INF:
                return INF
            total += cost
            active.add(nxt)
            remaining.remove(nxt)
        return total

    def estimate(last, visited):
        remaining = full ^ visited
        if not remaining:
            return Dbase[last]
        ids = [j for j in range(n) if remaining & (1 << j)]
        near = min(D[last][j] for j in ids)
        span = mst(remaining)
        home = min(Dbase[j] for j in ids)
        if use_ml:
            w0, w1, w2, w3, w4 = LEARNED_WEIGHTS
            return w0 * near + w1 * span + w2 * home + w3 * len(ids) + w4
        return near + span + home

    beam = [(start_dist[j], 1 << j, j, j)
            for j in range(n) if start_dist[j] <= budget]
    if not beam:
        return None
    best_partial = None
    best_complete = None
    for depth in range(1, n + 1):
        beam.sort(key=lambda s: (s[0] + estimate(s[2], s[1]), s[0], s[3], s[2]))
        beam = beam[:BEAM_WIDTH]
        new_states = {}
        for cost, mask, last, first in beam:
            candidate = (-depth, cost, first)
            if best_partial is None or candidate < best_partial:
                best_partial = candidate
            if mask == full:
                back = Dbase[last]
                if cost + back <= budget:
                    complete = (cost + back, first)
                    if best_complete is None or complete < best_complete:
                        best_complete = complete
                continue
            rem = full ^ mask
            while rem:
                bit = rem & -rem
                nxt = bit.bit_length() - 1
                rem ^= bit
                new_cost = cost + D[last][nxt]
                if new_cost > budget:
                    continue
                key = (mask | bit, nxt)
                value = (new_cost, key[0], nxt, first)
                old = new_states.get(key)
                if old is None or (new_cost, first) < (old[0], old[3]):
                    new_states[key] = value
        if not new_states:
            break
        beam = list(new_states.values())
    if best_complete is not None:
        return best_complete[1]
    return best_partial[2] if best_partial is not None else None


def _decide(observation: dict, use_ml=True) -> str:
    position = tuple(observation["position"])
    base = tuple(observation["base"])
    targets = tuple(sorted({tuple(t) for t in observation["targets_remaining"]}))
    blocked = tuple(sorted({tuple(o) for o in observation["obstacles"]}))
    size = int(observation["grid_size"])
    energy = int(observation["energy"])
    steps = int(observation["steps"])
    global _CURRENT_MAP
    map_key = (size, blocked)
    if map_key != _CURRENT_MAP:
        _bfs.cache_clear()
        _CURRENT_MAP = map_key
    budget = min(energy, max(0, MAX_STEPS - steps))
    if budget <= 0:
        return "WAIT"
    if position in targets:
        return "WAIT"
    from_start, first_action = _bfs(position, size, blocked)
    if not targets:
        return first_action.get(base, "WAIT")
    from_target = [_bfs(t, size, blocked)[0] for t in targets]
    if len(targets) <= EXACT_LIMIT:
        first = _exact(targets, budget, from_start, from_target, base)
    else:
        first = _beam(targets, budget, from_start, from_target, base, use_ml=use_ml)
    if first is None:
        return "WAIT"
    action = first_action.get(targets[first], "WAIT")
    for name, dx, dy in MOVES:
        if name == action:
            nxt = (position[0] + dx, position[1] + dy)
            return action if (0 <= nxt[0] < size and 0 <= nxt[1] < size
                              and nxt not in blocked) else "WAIT"
    return "WAIT"


def decide(observation: dict) -> str:
    return _decide(observation, use_ml=True)
