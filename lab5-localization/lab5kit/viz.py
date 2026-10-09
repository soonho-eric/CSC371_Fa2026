"""Figures for Lab 5.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from . import measures
from .world import DIRECTIONS

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":"]

WALL_COLOR = "#3F3F3F"
BELIEF_CMAP = LinearSegmentedColormap.from_list(
    "belief", ["#FFFFFF", "#AED6EC", "#0072B2", "#073B5A"]
)

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.dpi": 110,
})


def style(index):
    """Colour, marker and dash pattern for series number index."""
    return {
        "color": PALETTE[index % len(PALETTE)],
        "marker": MARKERS[index % len(MARKERS)],
        "linestyle": LINESTYLES[index % len(LINESTYLES)],
    }


# ----------------------------------------------------------------------
# the maze and a belief over it
# ----------------------------------------------------------------------


def _grid(world, values, fill=np.nan):
    """Lay a cell -> number mapping back out as a rows x cols array."""
    array = np.full((world.rows, world.cols), fill, dtype=float)
    for cell, value in values.items():
        array[cell] = value
    return np.ma.masked_invalid(array)


def _frame(world, ax):
    """Grid lines, ticks and aspect ratio, shared by every maze figure."""
    ax.set_aspect("equal")
    ax.set_xticks(range(world.cols))
    ax.set_yticks(range(world.rows))
    ax.set_xticks(np.arange(-0.5, world.cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, world.rows, 1), minor=True)
    ax.grid(which="minor", color="0.85", linewidth=0.8)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(labelsize=8)
    for cell in world.walls:
        ax.add_patch(plt.Rectangle((cell[1] - 0.5, cell[0] - 0.5), 1, 1,
                                   color=WALL_COLOR, linewidth=0))


def show_maze(world, ax=None, cells=(), path=None, title=None):
    """Draw the maze, optionally marking some cells and a path through it.

    Args:
        world: The Maze.
        ax: Optional axes to draw on.
        cells: Cells to mark with a dot.
        path: A list of cells to join with a line.
        title: Optional title.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(0.52 * world.cols + 1,
                                      0.52 * world.rows + 1))
    ax.imshow(_grid(world, {c: 0.0 for c in world.cells}),
              cmap=BELIEF_CMAP, vmin=0, vmax=1)
    _frame(world, ax)

    if path:
        rows = [cell[0] for cell in path]
        cols = [cell[1] for cell in path]
        ax.plot(cols, rows, color=PALETTE[1], linewidth=1.8, alpha=0.9,
                zorder=3)
        ax.plot(cols[0], rows[0], marker="o", markersize=7, color=PALETTE[1],
                zorder=4)
        ax.plot(cols[-1], rows[-1], marker="s", markersize=7,
                color=PALETTE[1], zorder=4)
    for cell in cells:
        ax.plot(cell[1], cell[0], marker="o", markersize=8, color=PALETTE[0],
                zorder=4)

    ax.set_title(title if title is not None else
                 f"{len(world.cells)} free cells")
    return ax


def show_belief(world, belief, ax=None, truth=None, title=None,
                annotate=None, vmax=None, colorbar=False):
    """Draw a belief as a heat map over the maze.

    Args:
        world: The Maze.
        belief: A cell -> probability dictionary.
        ax: Optional axes to draw on.
        truth: The cell the robot is really in, marked with a cross.
        title: Optional title. The default names the best guess.
        annotate: Write each probability in its cell. The default does this
            for mazes small enough to read.
        vmax: Top of the colour scale. The default is the belief's own
            maximum, which makes a flat belief visible; pass 1.0 to compare
            panels on one scale.
        colorbar: Add a colour bar.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(0.52 * world.cols + 1,
                                      0.52 * world.rows + 1))
    if annotate is None:
        annotate = len(world.cells) <= 40

    top = max(belief.values()) if vmax is None else vmax
    top = max(top, 1e-9)
    image = ax.imshow(_grid(world, belief), cmap=BELIEF_CMAP, vmin=0.0,
                      vmax=top)
    _frame(world, ax)

    if annotate:
        for cell, probability in belief.items():
            if probability < 0.005:
                continue
            shade = "white" if probability > 0.55 * top else "0.15"
            ax.text(cell[1], cell[0], f"{probability:.2f}"[1:],
                    ha="center", va="center", fontsize=7.5, color=shade)

    if truth is not None:
        ax.plot(truth[1], truth[0], marker="x", markersize=11,
                markeredgewidth=3, color="white", zorder=4)
        ax.plot(truth[1], truth[0], marker="x", markersize=9,
                markeredgewidth=1.8, color=PALETTE[1], zorder=5)

    if title is None:
        guess = measures.most_likely(belief)
        title = f"best guess {guess}, p = {belief[guess]:.2f}"
    ax.set_title(title)
    if colorbar:
        ax.figure.colorbar(image, ax=ax, shrink=0.8, label="probability")
    return ax


def show_filter_steps(world, beliefs, trajectory, times=None, shared=True):
    """A row of belief panels at selected time steps.

    Args:
        world: The Maze.
        beliefs: The list your filter returned.
        trajectory: The Trajectory it was filtering.
        times: Which time steps to draw. The default spreads five across the
            run.
        shared: Put every panel on one colour scale, so that a belief
            spreading out or sharpening up is visible across the row.

    Returns:
        The figure.
    """
    if times is None:
        last = len(beliefs) - 1
        times = sorted({0, 1, 2, last // 2, last})
    times = [t for t in times if 0 <= t < len(beliefs)]

    top = max(max(beliefs[t].values()) for t in times) if shared else None
    figure, axes = plt.subplots(
        1, len(times), figsize=(2.5 * len(times) + 0.6, 2.9))
    if len(times) == 1:
        axes = [axes]
    for ax, t in zip(axes, times):
        show_belief(world, beliefs[t], ax=ax, truth=trajectory.cells[t],
                    vmax=top,
                    title=f"t = {t}\np(truth) = {beliefs[t][trajectory.cells[t]]:.2f}")
        ax.set_xticks([])
        ax.set_yticks([])
    figure.suptitle("the cross is where the robot really is", fontsize=10,
                    color="0.3")
    figure.tight_layout()
    return figure


def show_ambiguity(world, ax=None):
    """Shade each cell by how many cells share its perfect sonar reading.

    1 means a cell a noiseless sonar could pin down from a standstill. The
    darker cells are the ones that look exactly like somewhere else.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(0.52 * world.cols + 1.6,
                                      0.52 * world.rows + 1))
    counts = {}
    for cell in world.cells:
        counts[cell] = len(world.matching_cells(world.signature(cell)))
    image = ax.imshow(_grid(world, counts), cmap="YlOrBr",
                      vmin=1, vmax=max(counts.values()))
    _frame(world, ax)
    for cell, count in counts.items():
        ax.text(cell[1], cell[0], str(count), ha="center", va="center",
                fontsize=8, color="0.1")
    ax.set_title("cells sharing each sonar signature")
    ax.figure.colorbar(image, ax=ax, shrink=0.8, label="look-alike cells")
    return ax


def show_paths(world, trajectory, paths, labels, ax=None):
    """Draw the true route and one or more estimated routes over the maze.

    Args:
        world: The Maze.
        trajectory: The Trajectory, for the true cells.
        paths: A list of paths, each a list of cells.
        labels: One label per path.
        ax: Optional axes.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(0.62 * world.cols + 1.4,
                                      0.62 * world.rows + 1))
    ax.imshow(_grid(world, {c: 0.0 for c in world.cells}),
              cmap=BELIEF_CMAP, vmin=0, vmax=1)
    _frame(world, ax)

    series = [(list(trajectory.cells), "the truth")] + list(zip(paths, labels))
    for index, (path, label) in enumerate(series):
        jitter = 0.10 * (index - (len(series) - 1) / 2)
        rows = [cell[0] + jitter for cell in path]
        cols = [cell[1] + jitter for cell in path]
        ax.plot(cols, rows, label=label, linewidth=2.0, alpha=0.85,
                zorder=3 + index, **style(index))
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax.set_title("where the robot went, and where each method says it went")
    return ax


# ----------------------------------------------------------------------
# experiment figures
# ----------------------------------------------------------------------


def _median_band(frame, value):
    """Median and quartiles of value at each time step."""
    grouped = frame.groupby("t")[value]
    return (grouped.median(), grouped.quantile(0.25), grouped.quantile(0.75))


def plot_convergence(df_trace, value="p_truth", ax=None):
    """How fast the belief closes in on the truth, over many runs.

    Args:
        df_trace: A trace table holding several runs.
        value: The column to plot. ``p_truth``, ``entropy`` and ``cells90``
            all tell the same story from different angles.
        ax: Optional axes.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.2, 4.0))

    median, low, high = _median_band(df_trace, value)
    for _, frame in df_trace.groupby("run"):
        ordered = frame.sort_values("t")
        ax.plot(ordered["t"], ordered[value], color=PALETTE[0], alpha=0.10,
                linewidth=1.0)
    ax.fill_between(median.index, low, high, color=PALETTE[0], alpha=0.22,
                    linewidth=0, label="middle half of runs")
    ax.plot(median.index, median, color=PALETTE[0], linewidth=2.2,
            marker="o", markersize=4, label="median run")

    labels = {
        "p_truth": "probability on the true cell",
        "entropy": "entropy of the belief (bits)",
        "cells90": "cells needed to cover 90%",
        "confidence": "probability on the best guess",
    }
    ax.set_xlabel("readings taken (t)")
    ax.set_ylabel(labels.get(value, value))
    if value == "p_truth":
        ax.axhline(0.5, color="0.35", linewidth=1.2, linestyle="--",
                   label="half the belief on the truth")
        ax.set_ylim(0, 1)
    ax.grid(True, color="0.92")
    ax.legend(frameon=False)
    ax.set_title(f"{df_trace['run'].nunique()} runs, same filter, fresh maze each time")
    return ax


def plot_mismatch(df_runs, true_epsilon=None):
    """Accuracy, confidence and entropy against the sonar noise the filter assumed.

    Args:
        df_runs: The sweep table.
        true_epsilon: The real noise, drawn as a vertical line. The default
            reads it out of the table.

    Returns:
        The figure.
    """
    if true_epsilon is None:
        true_epsilon = float(df_runs["true_epsilon"].iloc[0])

    panels = [
        ("accuracy", "share of steps where the best guess is right"),
        ("mean_confidence", "probability it put on its own best guess"),
        ("mean_entropy", "entropy of the belief (bits)"),
    ]
    figure, axes = plt.subplots(1, 3, figsize=(13.0, 4.0))
    grouped = df_runs.groupby("assumed_epsilon")

    for index, ((column, label), ax) in enumerate(zip(panels, axes)):
        median = grouped[column].median()
        low = grouped[column].quantile(0.25)
        high = grouped[column].quantile(0.75)
        ax.fill_between(median.index, low, high, color=PALETTE[index],
                        alpha=0.20, linewidth=0)
        ax.plot(median.index, median, linewidth=2.0, markersize=5,
                **style(index))
        ax.axvline(true_epsilon, color="0.35", linewidth=1.3, linestyle="--")
        ax.annotate("the truth", xy=(true_epsilon, median.max()),
                    xytext=(4, -2), textcoords="offset points",
                    fontsize=9, color="0.35")
        ax.set_xlabel("sonar noise the filter assumed")
        ax.set_ylabel(label)
        ax.grid(True, color="0.92")
        if column in ("accuracy", "mean_confidence"):
            ax.set_ylim(0, 1)

    figure.suptitle(
        f"one sonar that really lies {true_epsilon:.0%} of the time, "
        f"{df_runs['seed'].nunique()} trajectories, "
        f"{df_runs['assumed_epsilon'].nunique()} filters",
        fontsize=11)
    figure.tight_layout()
    return figure


def plot_calibration(df_runs, ax=None):
    """Confidence against accuracy, one point per filter.

    A filter on the diagonal is honest: when it says 0.7 it is right about
    70% of the time. Above the line it is overconfident.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(5.2, 4.6))
    grouped = df_runs.groupby("assumed_epsilon")
    accuracy = grouped["accuracy"].mean()
    confidence = grouped["mean_confidence"].mean()

    ax.plot([0, 1], [0, 1], color="0.5", linewidth=1.2, linestyle="--",
            label="honest: as sure as it is right")
    ax.plot(accuracy, confidence, color=PALETTE[0], marker="o", markersize=6,
            linewidth=1.4, label="your filters")
    for assumed in accuracy.index:
        ax.annotate(f"ε={assumed:g}", (accuracy[assumed], confidence[assumed]),
                    xytext=(6, -3), textcoords="offset points", fontsize=9,
                    color="0.25")
    ax.set_xlabel("accuracy")
    ax.set_ylabel("confidence")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(True, color="0.92")
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("sure of itself, or right?")
    return ax
