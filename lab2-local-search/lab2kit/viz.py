"""Plotting helpers for Lab 2.

Contains plotting code in this lab. Everything here is called for you
from provided cells. The colours come from the Okabe-Ito colourblind-safe
palette, and every series is also given its own marker and line style so the
figures stay readable in grayscale. Written with help from Claude.
"""

import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Okabe-Ito, a colourblind-safe qualitative palette.
PALETTE = [
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#009E73",  # bluish green
    "#CC79A7",  # reddish purple
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
]
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":"]

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.dpi": 110,
    }
)


def _style(index):
    """Return colour, marker and line style for series number ``index``."""
    return {
        "color": PALETTE[index % len(PALETTE)],
        "marker": MARKERS[index % len(MARKERS)],
        "linestyle": LINESTYLES[index % len(LINESTYLES)],
    }


def _attacking_pairs(state):
    """Return the column pairs that attack each other, for drawing only.

    Drawing the attack lines means knowing which pairs attack, so this
    function has to apply the rule. The rule is given to you in Part 2
    anyway; turning it into a cost function is still Task 1.
    """
    return [
        (i, j)
        for i, j in itertools.combinations(range(len(state)), 2)
        if state[i] == state[j] or abs(state[i] - state[j]) == j - i
    ]


def reference_cost(state):
    """Count attacking pairs, so that Part 0 has something to plot.

    Part 0 needs a working cost before you have written one, and the figures
    need one to put in their titles. It counts by histogram rather than by
    examining pairs: every row, every rising diagonal (``row + col``) and
    every falling diagonal (``row - col``) that holds k queens contributes
    k(k-1)/2 attacking pairs.

    This is not the shape of the answer to Task 1, and it is not a substitute
    for writing it: the point of Task 1 is to express the attack rule
    directly, which is what the rest of the lab builds on.
    """
    lines = {}
    for col, row in enumerate(state):
        for key in (("row", row), ("up", row + col), ("down", row - col)):
            lines[key] = lines.get(key, 0) + 1
    return sum(k * (k - 1) // 2 for k in lines.values())


def show_board(state, ax=None):
    """Draw an n-queens board with attacking pairs joined by thin lines.

    Args:
        state: Board state, ``state[col]`` is the row of that column's queen.
        ax: Optional axes to draw on. A new figure is made if omitted.

    Returns:
        The axes that were drawn on.
    """
    n = len(state)
    if ax is None:
        _, ax = plt.subplots(figsize=(4.2, 4.2))

    squares = np.indices((n, n)).sum(axis=0) % 2
    ax.imshow(squares, cmap="binary", vmin=0, vmax=4, origin="lower")

    for col, row in enumerate(state):
        ax.text(col, row, "♛", ha="center", va="center", fontsize=220 / n)

    pairs = _attacking_pairs(state)
    for i, j in pairs:
        ax.plot(
            [i, j],
            [state[i], state[j]],
            color=PALETTE[1],
            linewidth=1.2,
            alpha=0.9,
            zorder=3,
        )

    count = len(pairs)
    ax.set_title(f"{n}-queens, {count} attacking pair{'s' if count != 1 else ''}")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xlabel("column")
    ax.set_ylabel("row")
    return ax


def show_neighbor_costs(problem, state, ax=None):
    """Draw the cost of every one-queen move as a heat map.

    Cell (row, col) shows the cost of moving column ``col``'s queen to
    ``row``. The queens' current squares are marked. This is a picture of the
    search landscape one step around ``state``.

    Args:
        problem: An NQueens instance.
        state: The state to look around.
        ax: Optional axes to draw on.

    Returns:
        The axes that were drawn on.
    """
    n = len(state)
    if ax is None:
        _, ax = plt.subplots(figsize=(5.0, 4.2))

    grid = np.full((n, n), np.nan)
    here = problem.cost(state)
    for col in range(n):
        for row in range(n):
            moved = state[:col] + (row,) + state[col + 1 :]
            grid[row, col] = problem.cost(moved)

    image = ax.imshow(grid, cmap="viridis_r", origin="lower")
    plt.colorbar(image, ax=ax, label="attacking pairs after the move")
    for col, row in enumerate(state):
        ax.plot(col, row, marker="o", markersize=9, markerfacecolor="none",
                markeredgecolor=PALETTE[1], markeredgewidth=2)
    for col in range(n):
        for row in range(n):
            ax.text(col, row, f"{int(grid[row, col])}", ha="center", va="center",
                    fontsize=9, color="white")

    ax.set_title(f"cost of each single move (current cost {int(here)})")
    ax.set_xlabel("column of the queen we move")
    ax.set_ylabel("row we move it to")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    return ax


def show_tour(tsp, tour, ax=None, title=None):
    """Draw a TSP tour as a closed path through the cities.

    Args:
        tsp: The problem instance the tour belongs to.
        tour: A permutation tuple.
        ax: Optional axes to draw on.
        title: Optional title. Defaults to the tour length.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(4.2, 4.2))
    order = list(tour) + [tour[0]]
    points = tsp.points[order]
    ax.plot(points[:, 0], points[:, 1], color=PALETTE[0], linewidth=1.2, zorder=1)
    ax.scatter(tsp.points[:, 0], tsp.points[:, 1], s=18, color=PALETTE[1], zorder=2)
    ax.set_title(title or f"tour length {tsp.cost(tour):.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    return ax


def show_tour_progress(tsp, result, n_panels=4):
    """Show the best tour at evenly spaced points along a run.

    Args:
        tsp: The problem instance that was searched.
        result: The dictionary that run_one returned for that search.
        n_panels: How many snapshots to draw.

    Returns:
        The matplotlib figure.
    """
    trace = result["trace"]
    snapshots = result["snapshots"]
    if not trace:
        raise ValueError("this run recorded no improvements, so there is nothing to show")

    indices = np.unique(np.linspace(0, len(trace) - 1, n_panels).astype(int))
    fig, axes = plt.subplots(1, len(indices), figsize=(3.3 * len(indices), 3.6))
    axes = np.atleast_1d(axes)
    for ax, index in zip(axes, indices):
        evaluations = trace[index][0]
        cost = trace[index][2]
        show_tour(
            tsp,
            snapshots[index],
            ax=ax,
            title=f"after {evaluations} evaluations\nlength {cost:.2f}",
        )
    fig.tight_layout()
    return fig


def plot_success_rates(df, reference=None):
    """Bar chart of the fraction of runs that reached a goal state.

    """
    rates = df.groupby("algorithm")["solved"].mean()
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    positions = np.arange(len(rates))
    ax.bar(positions, rates.to_numpy(), color=PALETTE[: len(rates)], width=0.6)
    for x, value in zip(positions, rates.to_numpy()):
        ax.text(x, value + 0.02, f"{value:.0%}", ha="center", fontsize=11)

    if reference:
        for index, (label, value) in enumerate(reference.items()):
            ax.axhline(
                value,
                linestyle=LINESTYLES[1 + index % 3],
                color="0.35",
                linewidth=1.3,
                label=f"{label} (reference {value:.0%})",
            )
        ax.legend(loc="upper left", framealpha=0.9)

    ax.set_xticks(positions)
    ax.set_xticklabels(rates.index, rotation=12, ha="right")
    ax.set_ylabel("fraction of runs solved")
    ax.set_ylim(0, 1.4)
    ax.set_title("success rate by algorithm")
    fig.tight_layout()
    return ax


def _median_band(df, x, grid):
    """Return per-algorithm median and quartile curves of best cost over ``grid``."""
    column = 0 if x == "evaluations" else 1
    curves = {}
    for algorithm, group in df.groupby("algorithm"):
        stacked = []
        for trace in group["trace"]:
            if not trace:
                continue
            xs = np.array([point[column] for point in trace], dtype=float)
            ys = np.array([point[2] for point in trace], dtype=float)
            # Step function: best cost so far at each grid point.
            positions = np.searchsorted(xs, grid, side="right") - 1
            values = np.where(positions >= 0, ys[np.clip(positions, 0, None)], np.nan)
            stacked.append(values)
        if stacked:
            curves[algorithm] = np.vstack(stacked)
    return curves


def plot_cost_vs_budget(df, x="evaluations", ax=None):
    """Plot median best cost against spent budget, with an interquartile band.

    Args:
        df: Results frame with ``algorithm`` and ``trace`` columns.
        x: Either ``"evaluations"`` or ``"iterations"``.
        ax: Optional axes to draw on.

    Returns:
        The axes that were drawn on.
    """
    if x not in ("evaluations", "iterations"):
        raise ValueError('x must be "evaluations" or "iterations"')
    if ax is None:
        _, ax = plt.subplots(figsize=(6.0, 4.2))

    column = 0 if x == "evaluations" else 1
    largest = max(
        (point[column] for trace in df["trace"] for point in trace), default=1
    )
    grid = np.geomspace(1, max(largest, 2), 200)
    curves = _median_band(df, x, grid)
    floor = min(np.nanmin(stacked) for stacked in curves.values()) if curves else 0.0

    for index, (algorithm, stacked) in enumerate(sorted(curves.items())):
        style = _style(index)
        median = np.nanmedian(stacked, axis=0)
        low = np.nanpercentile(stacked, 25, axis=0)
        high = np.nanpercentile(stacked, 75, axis=0)
        ax.plot(grid, median, label=algorithm, linewidth=1.8,
                markevery=25, markersize=5, **style)
        ax.fill_between(grid, low, high, color=style["color"], alpha=0.18, linewidth=0)

    unit = "cost evaluations" if x == "evaluations" else "neighbor-generation calls"
    ax.set_xlabel(f"budget spent ({unit})")
    ax.set_ylabel("best tour length (units of the unit square)")
    ax.set_xscale("log")
    if curves and floor > 0:
        # Every run starts from a random state whose cost dwarfs anything the
        # search reaches, so zoom in on the range where the curves separate,
        # and drop the leading stretch where nothing is in view yet.
        top = floor * 1.6
        visible = np.flatnonzero(
            np.nanmin(
                [np.nanmedian(stacked, axis=0) for stacked in curves.values()], axis=0
            )
            <= top
        )
        ax.set_ylim(floor * 0.97, top)
        if len(visible):
            ax.set_xlim(grid[max(0, visible[0] - 8)], grid[-1])
    ax.legend(framealpha=0.9)
    return ax


def plot_budget_reversal(df):
    """Draw best cost against each budget unit, side by side on a shared y-axis.

    Args:
        df: Results frame with ``algorithm`` and ``trace`` columns.

    Returns:
        The matplotlib figure.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=True)
    plot_cost_vs_budget(df, x="iterations", ax=axes[0])
    plot_cost_vs_budget(df, x="evaluations", ax=axes[1])
    axes[0].set_title("budget measured in iterations")
    axes[1].set_title("budget measured in cost evaluations")
    axes[1].set_ylabel("")
    fig.tight_layout()
    return fig
