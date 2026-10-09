"""Running a filter over trajectories and collecting what happened.
"""

import numpy as np
import pandas as pd

from . import measures


def _row(run, t, action, reading, truth, belief):
    """One line of a trace table."""
    guess = measures.most_likely(belief)
    return {
        "run": run,
        "t": int(t),
        "action": "none" if action is None else action,
        "reading": "".join(str(bit) for bit in reading),
        "true_cell": str(truth),
        "map_cell": str(guess),
        "p_truth": float(belief[truth]),
        "confidence": float(belief[guess]),
        "entropy": float(measures.entropy(belief)),
        "cells90": int(measures.cells_covering(belief, 0.9)),
        "correct": int(guess == truth),
    }


def run_filter(world, trajectory, filter_sequence, belief=None, run="showcase"):
    """Filter one trajectory and tabulate every step.

    Args:
        world: The maze the filter believes in. Its ``epsilon`` and ``p_move``
            are the filter's model, which need not match the world the
            trajectory came from.
        trajectory: A Trajectory from ``Maze.simulate``.
        filter_sequence: Your ``filter_sequence`` function.
        belief: The belief to start from. None means uniform.
        run: The label to put in the table's ``run`` column.

    Returns:
        ``(beliefs, df)`` where ``beliefs`` is the list your filter returned
        and ``df`` has one row per time step.
    """
    if belief is None:
        belief = world.uniform_belief()
    beliefs = filter_sequence(world, belief, trajectory.actions,
                              trajectory.readings)
    if len(beliefs) != len(trajectory.readings):
        raise ValueError(
            f"filter_sequence returned {len(beliefs)} beliefs for "
            f"{len(trajectory.readings)} readings. It should return one "
            "belief per reading, starting with the belief after reading 0."
        )

    actions = [None] + list(trajectory.actions)
    rows = [
        _row(run, t, actions[t], trajectory.readings[t], trajectory.cells[t],
             beliefs[t])
        for t in range(len(beliefs))
    ]
    return beliefs, pd.DataFrame(rows)


def run_many(world, filter_sequence, seeds=range(50), steps=20,
             start=None, label="run"):
    """Filter one fresh trajectory per seed and stack the traces.

    The trajectories come from ``world`` itself, so the filter is working from
    the right model here. This is the baseline everything else is measured
    against.

    Returns:
        One DataFrame with one row per (seed, time step).
    """
    frames = []
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        trajectory = world.simulate(steps, rng, start=start)
        _, frame = run_filter(world, trajectory, filter_sequence,
                              run=f"{label}{int(seed)}")
        frame["seed"] = int(seed)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def localization_times(df_trace, threshold=0.5):
    """For each run, the first time step whose belief passes threshold.

    "Passes" means the belief puts at least ``threshold`` on the cell the
    robot is really in. A run that never gets there is left as NaN.

    Returns:
        A pandas Series indexed by run label.
    """
    found = {}
    for run, frame in df_trace.groupby("run", sort=True):
        passed = frame[frame["p_truth"] >= threshold]
        found[run] = float(passed["t"].min()) if len(passed) else float("nan")
    return pd.Series(found, name=f"first t with p_truth >= {threshold}")


def summarize(df_trace, **extra):
    """Collapse one run's trace into the single row the sweep table wants."""
    row = {
        "steps": int(df_trace["t"].max()),
        "accuracy": float(df_trace["correct"].mean()),
        "mean_p_truth": float(df_trace["p_truth"].mean()),
        "mean_confidence": float(df_trace["confidence"].mean()),
        "mean_entropy": float(df_trace["entropy"].mean()),
        "final_correct": int(df_trace.sort_values("t")["correct"].iloc[-1]),
    }
    row.update(extra)
    return row


def run_mismatch_sweep(truth, filter_sequence, assumed_epsilons,
                       seeds=range(20), steps=20):
    """Filter the same trajectories with a range of assumed sonar noises.

    For each seed, one trajectory is generated from ``truth``, which is the
    world as it really is. Every value in ``assumed_epsilons`` then filters
    that same trajectory, so the comparison is not affected by the filters
    seeing different data.

    Args:
        truth: The maze the data comes from. Its ``epsilon`` is the real one.
        filter_sequence: Your ``filter_sequence`` function.
        assumed_epsilons: The epsilons to hand the filter.
        seeds: One trajectory per seed.
        steps: Actions per trajectory.

    Returns:
        A DataFrame with one row per (assumed epsilon, seed).

    Raises:
        ValueError: If an assumed epsilon of exactly 0 rules out every cell
            at once. A filter that believes its sonar is perfect eventually
            concludes the robot is nowhere, which is worth seeing on its own
            rather than in the middle of a sweep.
    """
    rows = []
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        trajectory = truth.simulate(steps, rng)
        for assumed in assumed_epsilons:
            model = truth.variant(epsilon=assumed)
            _, frame = run_filter(model, trajectory, filter_sequence,
                                  run=f"eps{assumed}_seed{seed}")
            rows.append(summarize(
                frame,
                experiment="sonar mismatch",
                assumed_epsilon=float(assumed),
                true_epsilon=float(truth.epsilon),
                p_move=float(truth.p_move),
                seed=int(seed),
            ))
    return pd.DataFrame(rows)


def agreement(path_a, path_b):
    """The fraction of time steps on which two paths name the same cell."""
    if len(path_a) != len(path_b):
        raise ValueError(f"paths are {len(path_a)} and {len(path_b)} long")
    same = sum(1 for a, b in zip(path_a, path_b) if a == b)
    return same / len(path_a)


def illegal_steps(world, path):
    """The steps of a path that no single action could have produced.

    Returns a list of ``(t, cell, next_cell)`` for each move from one cell to
    another that is not reachable in one step. A path with any of these is not
    something the robot could actually have done.
    """
    broken = []
    for t in range(len(path) - 1):
        here, there = path[t], path[t + 1]
        reachable = {here}
        for direction in ("north", "east", "south", "west"):
            reachable |= set(world.transition(here, direction))
        if there not in reachable:
            broken.append((t, here, there))
    return broken
