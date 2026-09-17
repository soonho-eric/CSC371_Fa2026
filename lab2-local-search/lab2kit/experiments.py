"""Running experiments and collecting the results.

run_one resets a problem, builds a generator from a seed, calls your algorithm, and reports
what the problem recorded. run_all does that over a grid of algorithms and
seeds and hands back a table.

The budget itself is not enforced here. Your algorithms enforce it, by
checking problem.evaluations against the budget they were given. That is why
every algorithm in this lab takes a budget argument.
"""

import numpy as np
import pandas as pd


def run_one(algorithm, problem, budget, seed, name):
    """Run one algorithm once on one problem.

    Args:
        algorithm: A function taking (problem, rng, budget).
        problem: An NQueens or TSP instance.
        budget: How many cost evaluations the algorithm may spend.
        seed: Seed for this run's generator.
        name: Label for this algorithm in the results table.

    Returns:
        A dictionary describing the run. The interesting keys are 'solved',
        'evaluations', 'final_cost' and 'best_state'; 'trace' and 'snapshots'
        are what the plots are drawn from.
    """
    problem.reset()
    rng = np.random.default_rng(seed)
    algorithm(problem, rng, budget)

    if problem.best_state is None:
        solved = False
    else:
        solved = problem.is_goal(problem.best_state)

    return {
        "problem": problem.name,
        "n": problem.n,
        "algorithm": name,
        "seed": seed,
        "solved": solved,
        "evaluations": problem.evaluations,
        "final_cost": problem.best_cost,
        "trace": problem.trace,
        "best_state": problem.best_state,
        "snapshots": problem.best_states,
    }


def run_all(algorithms, make_problem, seeds, budget):
    """Run every algorithm on every seed and collect the results in a table.

    Args:
        algorithms: A dictionary mapping a display name to a function taking
            (problem, rng, budget).
        make_problem: A function taking a seed and returning a problem. It is
            called once per run, so each seed can get its own instance.
        seeds: A list of seeds. Every algorithm sees every seed.
        budget: The evaluation budget for each individual run.

    Returns:
        A pandas DataFrame with one row per run.
    """
    rows = []
    total = len(algorithms) * len(seeds)
    report_every = max(1, total // 20)
    done = 0

    for name in algorithms:
        for seed in seeds:
            problem = make_problem(seed)
            rows.append(run_one(algorithms[name], problem, budget, seed, name))
            done = done + 1
            if done % report_every == 0 or done == total:
                print(f"\r  {done}/{total} runs done ({name})   ", end="", flush=True)

    print()
    return pd.DataFrame(rows)
