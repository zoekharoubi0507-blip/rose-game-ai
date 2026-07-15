"""Self-contained IENO Safe Competition v5 submission driver.

Generated from ``ieno/core/planner.py`` and
``ieno/drivers/competition.py`` by ``tools/build_single_driver.py``.
The generated submission has no dependency on the local ``ieno`` package.
"""

from __future__ import annotations

import math
import random
import time
import hashlib
from typing import NamedTuple
from functools import lru_cache

from rose.common import actions, obstacles

ACTIONS = actions.ALL
HEIGHT = 9
CELLS_PER_LANE = 3
BLOCKING = {obstacles.CRACK, obstacles.TRASH, obstacles.BIKE,
            obstacles.WATER, obstacles.BARRIER}

STAY_ACTION = {
    obstacles.PENGUIN: actions.PICKUP,
    obstacles.CRACK: actions.JUMP,
    obstacles.WATER: actions.BRAKE,
}


class State(NamedTuple):
    x: int
    y: int
    track: tuple[tuple[str, ...], ...]


def from_world(world):
    width = 0
    while True:
        try:
            world.get((width, 0))
            width += 1
        except IndexError:
            break
    track = tuple(
        tuple(world.get((x, y)) for x in range(width))
        for y in range(HEIGHT)
    )
    return State(world.car.x, world.car.y, track)


def obstacle_reward(obstacle, action):
    if obstacle == obstacles.NONE:
        return 10, False
    if obstacle == obstacles.PENGUIN:
        return (20 if action == actions.PICKUP else 10), False
    if obstacle == obstacles.CRACK and action == actions.JUMP:
        return 15, False
    if obstacle == obstacles.WATER and action == actions.BRAKE:
        return 14, False
    return -10, True


def next_state(state, action, generated_row):
    """Reproduce engine order: shift, steer, score obstacle, push back."""
    track = [list(generated_row)] + [list(row) for row in state.track[:-1]]
    x = state.x
    if action == actions.LEFT and x > 0:
        x -= 1
    elif action == actions.RIGHT and x < len(track[0]) - 1:
        x += 1
    reward, hit = obstacle_reward(track[state.y][x], action)
    y = state.y
    if hit:
        track[y][x] = obstacles.NONE
        y = min(HEIGHT - 1, y + 1)
    return State(x, y, tuple(tuple(row) for row in track)), reward, hit


def possible_rows(width, lane, random_lanes=False):
    """Exact row distribution relevant to one driver's lane."""
    start = lane * CELLS_PER_LANE
    outcomes = []
    for obstacle in obstacles.ALL:
        for offset in range(CELLS_PER_LANE):
            row = [obstacles.NONE] * width
            row[start + offset] = obstacle
            outcomes.append((tuple(row), 1.0 / (len(obstacles.ALL) * 3)))
    return outcomes


def random_row(rng, width, lanes, track_mode="same"):
    obstacle = rng.choice(obstacles.ALL)
    row = [obstacles.NONE] * width
    if track_mode == "same":
        offset = rng.randrange(CELLS_PER_LANE)
        for lane in range(lanes):
            row[lane * CELLS_PER_LANE + offset] = obstacle
    else:
        for lane in range(lanes):
            offset = rng.randrange(CELLS_PER_LANE)
            row[lane * CELLS_PER_LANE + offset] = obstacle
    return tuple(row)


def terminal_value(state, lane=None):
    lane = state.x // CELLS_PER_LANE if lane is None else lane
    center = lane * CELLS_PER_LANE + 1
    mobility = int(state.x > lane * 3) + int(state.x < lane * 3 + 2)
    return -0.35 * abs(state.x - center) + 0.15 * mobility - 0.1 * max(0, state.y - 6)


def legal_actions(state, lane):
    start = lane * CELLS_PER_LANE
    end = start + CELLS_PER_LANE - 1
    return tuple(action for action in ACTIONS
                 if not (action == actions.LEFT and state.x <= start)
                 and not (action == actions.RIGHT and state.x >= end))


def visible_dp_action(state, time_budget=0.08, lane=None):
    deadline = time.perf_counter() + time_budget
    lane = state.x // 3 if lane is None else lane
    blank = (obstacles.NONE,) * len(state.track[0])

    @lru_cache(maxsize=None)
    def value(s, depth):
        if depth <= 0 or time.perf_counter() >= deadline:
            return terminal_value(s, lane)
        return max(next_state(s, a, blank)[1] + value(next_state(s, a, blank)[0], depth - 1)
                   for a in legal_actions(s, lane))

    depth = min(state.y + 1, 8)
    scored = []
    for action in legal_actions(state, lane):
        nxt, reward, _ = next_state(state, action, blank)
        scored.append((reward + value(nxt, depth - 1), -ACTIONS.index(action), action))
    return max(scored)[2]


def visible_route_dp_action(state, lane=None, max_depth=8):
    """Plan the best stable route through all currently visible rows.

    Equal-scoring routes prefer staying in the current column, then moving
    left, then moving right.  This is the useful behavior learned from the
    Group 9 driver, generalized to every three-column lane in a five-player
    game.  The route model is intentionally simple and is recalculated after
    every turn, so any hit displacement is incorporated on the next request.
    """
    lane = state.x // CELLS_PER_LANE if lane is None else lane
    lane_start = lane * CELLS_PER_LANE
    lane_end = lane_start + CELLS_PER_LANE - 1

    # A temporary defensive crossing can leave the car outside its assigned
    # lane.  Use the exact planner until it has recovered instead of treating
    # the new lane as its assignment.
    if not lane_start <= state.x <= lane_end:
        return visible_dp_action(state, lane=lane)

    rows = []
    for offset in range(max_depth):
        row_index = state.y - 1 - offset
        if row_index < 0:
            break
        rows.append(state.track[row_index])
    if not rows:
        return actions.NONE

    future = {column: 0 for column in range(lane_start, lane_end + 1)}
    choice = {}
    for row in reversed(rows):
        current = {}
        choice = {}
        for column in range(lane_start, lane_end + 1):
            stay_action = STAY_ACTION.get(row[column], actions.NONE)
            stay_reward, _ = obstacle_reward(row[column], stay_action)
            options = [(stay_reward + future[column], stay_action, column)]

            if column > lane_start:
                move_reward, _ = obstacle_reward(row[column - 1], actions.LEFT)
                options.append((move_reward + future[column - 1],
                                actions.LEFT, column - 1))
            if column < lane_end:
                move_reward, _ = obstacle_reward(row[column + 1], actions.RIGHT)
                options.append((move_reward + future[column + 1],
                                actions.RIGHT, column + 1))

            best = max(options, key=lambda option: option[0])
            current[column] = best[0]
            choice[column] = (best[1], best[2])
        future = current

    return choice[state.x][0]


def finite_horizon_action(state, turns_remaining, lane=None):
    """Maximize the exact score over a fully visible remaining game horizon.

    The result is exact when ``turns_remaining <= state.y`` because every row
    that can reach the car before the game ends is already visible.  Keeping
    this separate from the normal route planner prevents an end-of-game move
    from sacrificing points for obstacles that arrive after turn 60.
    """
    if turns_remaining < 1:
        raise ValueError("turns_remaining must be positive")
    if turns_remaining > state.y:
        raise ValueError("the remaining horizon includes unseen rows")

    lane = state.x // CELLS_PER_LANE if lane is None else lane
    blank = (obstacles.NONE,) * len(state.track[0])
    depth = min(turns_remaining, 8)

    @lru_cache(maxsize=None)
    def value(current, remaining):
        if remaining == 0:
            return 0
        scores = []
        for action in legal_actions(current, lane):
            nxt, reward, _ = next_state(current, action, blank)
            scores.append(reward + value(nxt, remaining - 1))
        return max(scores)

    scored = []
    for action in legal_actions(state, lane):
        nxt, reward, _ = next_state(state, action, blank)
        scored.append((reward + value(nxt, depth - 1),
                       -ACTIONS.index(action), action))
    return max(scored)[2]


def expectimax_action(state, depth=2, time_budget=0.12):
    deadline = time.perf_counter() + time_budget
    lane = state.x // 3
    rows = possible_rows(len(state.track[0]), lane)

    @lru_cache(maxsize=30000)
    def value(s, d):
        if d == 0 or time.perf_counter() >= deadline:
            return terminal_value(s, lane)
        best = -math.inf
        for action in legal_actions(s, lane):
            expected = 0.0
            for row, probability in rows:
                nxt, reward, _ = next_state(s, action, row)
                expected += probability * (reward + value(nxt, d - 1))
            best = max(best, expected)
        return best

    values = []
    for action in legal_actions(state, lane):
        expected = 0.0
        for row, probability in rows:
            nxt, reward, _ = next_state(state, action, row)
            expected += probability * (reward + value(nxt, depth - 1))
        values.append((expected, -ACTIONS.index(action), action))
    return max(values)[2]


def rollout_action(state, *, robust=False, simulations=24, horizon=12, seed=0):
    lane = state.x // 3
    width = len(state.track[0])
    payload = repr((seed, state.x, state.y, state.track)).encode("utf-8")
    stable_seed = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")
    rng = random.Random(stable_seed)
    samples = {action: [] for action in legal_actions(state, lane)}
    for action in legal_actions(state, lane):
        for _ in range(simulations):
            current = state
            total = 0
            first = action
            for step in range(horizon):
                row = random_row(rng, width, width // 3)
                candidate = first if step == 0 else heuristic_action(current, lane)
                current, reward, _ = next_state(current, candidate, row)
                total += reward
            samples[action].append(total + terminal_value(current, lane))
    ranked = []
    for action, values in samples.items():
        values.sort()
        mean = sum(values) / len(values)
        tail_n = max(1, len(values) // 10)
        cvar = sum(values[:tail_n]) / tail_n
        score = 0.8 * mean + 0.2 * cvar if robust else mean
        ranked.append((score, -ACTIONS.index(action), action))
    return max(ranked)[2]


def heuristic_action(state, lane=None):
    lane = state.x // 3 if lane is None else lane
    blank = (obstacles.NONE,) * len(state.track[0])
    best = []
    for action in legal_actions(state, lane):
        nxt, reward, hit = next_state(state, action, blank)
        best.append((reward - 3 * hit + terminal_value(nxt, lane), -ACTIONS.index(action), action))
    return max(best)[2]


def hybrid_action(state):
    """Short exact search with a compact learned-style linear leaf value."""
    lane = state.x // 3
    blank = (obstacles.NONE,) * len(state.track[0])

    def learned_value(s):
        center = lane * 3 + 1
        danger = sum(1 for y in range(min(s.y + 1, HEIGHT))
                     if s.track[y][s.x] in BLOCKING)
        return 0.42 - 0.61 * abs(s.x - center) - 0.74 * max(0, s.y - 6) - 0.18 * danger

    @lru_cache(maxsize=None)
    def value(s, depth):
        if depth == 0:
            return learned_value(s)
        choices = []
        for action in legal_actions(s, lane):
            nxt, reward, _ = next_state(s, action, blank)
            choices.append(reward + value(nxt, depth - 1))
        return max(choices)

    return max((next_state(state, a, blank)[1] + value(next_state(state, a, blank)[0], 3),
                -ACTIONS.index(a), a) for a in legal_actions(state, lane))[2]


from collections import defaultdict

from rose.common import actions, obstacles

driver_name = "IENO Competition Driver_claude"

GAME_DURATION_TURNS = 60
TRACK_SCORE_WEIGHT = 1.0
COLLISION_RISK_COST = 15.0
CROSS_LANE_COST = 6.0
BOUNDARY_COST = 0.5
OWN_LANE_CENTER_BONUS = 0.2

# Shield: catch PENGUINS_FOR_SHIELD penguins in a row, with no bump into a
# score-lowering obstacle in between, and the car earns SHIELD_DURATION
# steps of invincibility. While shielded it stops dodging bad obstacles
# (no jump/brake/avoidance steering) and just drives straight, still
# picking up any penguin directly in front of it.
PENGUINS_FOR_SHIELD = 3
SHIELD_DURATION = 5


class OpponentModel:
    def __init__(self):
        self.previous_track = None
        self.previous_position = None
        self.previous_action = None
        self.tick = 0
        self.belief = {}
        self.boundary_activity = 0
        self.pickups = 0
        self.blocker_clears = 0

    def reset(self):
        self.__init__()

    def update(self, state):
        width = len(state.track[0])
        own_lane = state.x // 3
        evidence = defaultdict(float)
        if self.previous_track is not None:
            own_clear_position = None
            if self.previous_position is not None:
                own_x, own_y = self.previous_position
                if self.previous_action == actions.LEFT:
                    own_x = max(0, own_x - 1)
                elif self.previous_action == actions.RIGHT:
                    own_x = min(width - 1, own_x + 1)
                own_clear_position = (own_x, own_y)
            shifted = self.previous_track[:-1]
            for y in range(1, len(state.track)):
                old_row = shifted[y - 1]
                for x, old_obstacle in enumerate(old_row):
                    if old_obstacle == obstacles.NONE:
                        continue
                    if state.track[y][x] == obstacles.NONE:
                        # Attribute our previous target before looking for an
                        # invader. After a hit the car is pushed back one row,
                        # so its current position is not the cleared tile.
                        if (x, y) == own_clear_position:
                            continue
                        evidence[(x, y)] += 1.0
                        if old_obstacle == obstacles.PENGUIN:
                            self.pickups += 1
                        elif old_obstacle in {
                            obstacles.CRACK,
                            obstacles.TRASH,
                            obstacles.BIKE,
                            obstacles.WATER,
                            obstacles.BARRIER,
                        }:
                            self.blocker_clears += 1
                        if x // 3 == own_lane:
                            self.boundary_activity += 1

        if evidence:
            total = sum(evidence.values())
            observed = {position: weight / total for position, weight in evidence.items()}
            carried = {(x, min(8, y + 1)): probability * 0.35
                       for (x, y), probability in self.belief.items()}
            combined = defaultdict(float, carried)
            for position, probability in observed.items():
                combined[position] += probability
            norm = sum(combined.values()) or 1.0
            self.belief = {position: probability / norm
                           for position, probability in combined.items()}
        elif self.belief:
            carried = {(x, min(8, y + 1)): probability
                       for (x, y), probability in self.belief.items()}
            self.belief = carried
        else:
            other_centers = [lane * 3 + 1 for lane in range(width // 3)
                             if lane != own_lane]
            if other_centers:
                probability = 1.0 / len(other_centers)
                self.belief = {(x, 6): probability for x in other_centers}

        self.previous_track = state.track
        self.previous_position = (state.x, state.y)
        self.tick += 1

    def classify(self):
        if self.tick < 10:
            return "unknown"
        if self.boundary_activity >= 3:
            return "aggressive"
        if self.pickups >= 4 and self.pickups > self.blocker_clears:
            return "penguin_hunter"
        if self.blocker_clears >= 4:
            return "weak_reactive"
        return "passive"

    def collision_risk(self, x, y):
        risk = 0.0
        for (opponent_x, opponent_y), probability in self.belief.items():
            if opponent_y == y and abs(opponent_x - x) <= 1:
                risk += probability
            elif abs(opponent_y - y) == 1 and opponent_x == x:
                risk += probability * 0.4
        return min(1.0, risk)


class CompetitionPolicy:
    def __init__(self, *, inference=True, collision_penalty=True,
                 classification=True, lane_bonus=True, soft_crossing=True):
        self.model = OpponentModel()
        self.inference = inference
        self.collision_penalty = collision_penalty
        self.classification = classification
        self.lane_bonus = lane_bonus
        self.soft_crossing = soft_crossing
        self.assigned_lane = None
        self.turn = 0
        self.last_state = None
        self.penguin_streak = 0
        self.shield_steps_remaining = 0

    def reset(self):
        self.model.reset()
        self.assigned_lane = None
        self.turn = 0
        self.last_state = None
        self.penguin_streak = 0
        self.shield_steps_remaining = 0

    def _is_new_game(self, state):
        if self.turn == 0 or state.y != 6 or state.x % 3 != 1:
            return False
        if any(obstacle != obstacles.NONE
               for row in state.track for obstacle in row):
            return False

        previous_had_obstacles = (
            self.last_state is not None
            and any(
                obstacle != obstacles.NONE
                for row in self.last_state.track
                for obstacle in row
            )
        )
        previous_was_not_start = (
            self.last_state is not None
            and (self.last_state.y != 6 or self.last_state.x % 3 != 1)
        )
        return (
            self.turn >= GAME_DURATION_TURNS
            or previous_had_obstacles
            or previous_was_not_start
        )

    def choose(self, state):
        if self._is_new_game(state):
            self.reset()
        self.turn += 1
        if self.inference:
            self.model.update(state)
        else:
            self.model.tick += 1

        front = (
            state.track[state.y - 1][state.x] if state.y > 0 else obstacles.NONE
        )

        if self.shield_steps_remaining > 0:
            self.shield_steps_remaining -= 1
            selected = actions.PICKUP if front == obstacles.PENGUIN else actions.NONE
            self.model.previous_action = selected
            self.last_state = state
            return selected

        if self.assigned_lane is None:
            self.assigned_lane = state.x // 3
        own_lane = self.assigned_lane
        lane_start = own_lane * 3
        lane_end = lane_start + 2
        center = lane_start + 1
        turns_remaining = GAME_DURATION_TURNS - self.turn + 1
        if 0 < turns_remaining <= state.y:
            baseline = finite_horizon_action(
                state, turns_remaining, lane=own_lane)
        else:
            baseline = visible_route_dp_action(state, lane=own_lane)
        opponent_type = (
            self.model.classify() if self.classification else "unknown"
        )
        collision_cost = COLLISION_RISK_COST * (
            1.5 if opponent_type == "aggressive" else 1.0
        )
        blank = (obstacles.NONE,) * len(state.track[0])
        baseline_next, baseline_reward, _ = next_state(state, baseline, blank)
        baseline_risk = (
            self.model.collision_risk(baseline_next.x, baseline_next.y)
            if self.inference else 0.0
        )
        own_lane_probability = sum(
            probability for (x, _), probability in self.model.belief.items()
            if x // 3 == own_lane
        ) if self.inference else 0.0
        credible_opponent_threat = (
            own_lane_probability >= 0.10
            or (
                baseline_risk >= 0.10
                and opponent_type in {"unknown", "aggressive"}
            )
        )
        if not credible_opponent_threat:
            selected = baseline
        else:
            candidates = []
            baseline_value = None

            for action in ACTIONS:
                nxt, reward, _ = next_state(state, action, blank)
                in_lane = lane_start <= nxt.x <= lane_end
                risk = self.model.collision_risk(nxt.x, nxt.y) if self.inference else 0.0
                if not in_lane:
                    expected_gain = reward - baseline_reward
                    allow_crossing = (self.soft_crossing and expected_gain > CROSS_LANE_COST
                                      and risk < 0.15)
                    if not allow_crossing:
                        continue
                boundary = int(nxt.x in (lane_start, lane_end))
                score = TRACK_SCORE_WEIGHT * reward
                if self.collision_penalty:
                    score -= risk * collision_cost
                score -= (0 if in_lane else CROSS_LANE_COST)
                score -= boundary * BOUNDARY_COST
                if self.lane_bonus:
                    score += int(nxt.x == center) * OWN_LANE_CENTER_BONUS
                score += terminal_value(nxt, own_lane)
                score += 1.0 if action == baseline else 0.0
                if self.classification and opponent_type == "aggressive" and boundary:
                    score -= 1.5
                candidates.append((score, -ACTIONS.index(action), action))
                if action == baseline:
                    baseline_value = score

            best = max(candidates) if candidates else None
            selected = (
                best[2]
                if (
                    best is not None
                    and baseline_value is not None
                    and best[0] > baseline_value + 1.0
                )
                else baseline
            )

        _, _, hit = next_state(state, selected, blank)
        if hit:
            self.penguin_streak = 0
        elif front == obstacles.PENGUIN and selected == actions.PICKUP:
            self.penguin_streak += 1
            if self.penguin_streak >= PENGUINS_FOR_SHIELD:
                self.penguin_streak = 0
                self.shield_steps_remaining = SHIELD_DURATION

        self.model.previous_action = selected
        self.last_state = state
        return selected


_policy = CompetitionPolicy()
_model = _policy.model


def reset_state():
    """Public test hook and game-reset hook."""
    _policy.reset()


def drive(world):
    return _policy.choose(from_world(world))
