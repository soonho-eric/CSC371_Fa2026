"""Figures for Lab 3.
"""

import matplotlib.pyplot as plt
import numpy as np

from .games import COLS, ROWS

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":"]

PIECE_COLOURS = {1: "#D55E00", 2: "#0072B2"}

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


def show_board(game, state, ax=None, title=None):
    """Draw a Connect 4 or tic-tac-toe position.

    Args:
        game: The game the state belongs to.
        state: The position to draw.
        ax: Optional axes to draw on.
        title: Optional title.

    Returns:
        The axes that were drawn on.
    """
    board = state[0]
    if game.name == "connect4":
        rows, cols = ROWS, COLS
    else:
        rows, cols = 3, 3

    if ax is None:
        _, ax = plt.subplots(figsize=(0.65 * cols + 1, 0.65 * rows + 1))

    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(-0.5, rows - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    for edge in range(cols + 1):
        ax.axvline(edge - 0.5, color="0.7", linewidth=1)
    for edge in range(rows + 1):
        ax.axhline(edge - 0.5, color="0.7", linewidth=1)

    for index in range(rows * cols):
        piece = board[index]
        if piece == 0:
            continue
        if game.name == "connect4":
            row = index // cols
            col = index % cols
        else:
            # tic-tac-toe reads top to bottom, so flip it for drawing
            row = rows - 1 - index // cols
            col = index % cols
        ax.plot(col, row, marker="o", markersize=18,
                color=PIECE_COLOURS[piece], linestyle="none")

    if title is None:
        winner = game.winner(state)
        if winner != 0:
            title = "player " + str(winner) + " has won"
        elif game.is_terminal(state):
            title = "drawn"
        else:
            title = "player " + str(game.to_move(state)) + " to move"
    ax.set_title(title)
    ax.set_xlabel("column")
    return ax


def plot_nodes_by_depth(df, ax=None):
    """Plot nodes searched against depth, one line per search method.

    Args:
        df: A table with columns 'search', 'depth' and 'nodes'.
        ax: Optional axes to draw on.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.4, 4.4))
    for index, name in enumerate(sorted(df["search"].unique())):
        sub = df[df["search"] == name].sort_values("depth")
        ax.plot(sub["depth"], sub["nodes"], label=name, linewidth=1.8,
                markersize=6, **style(index))
    ax.set_yscale("log")
    ax.set_xlabel("search depth (plies)")
    ax.set_ylabel("positions searched")
    ax.set_title("how much work each search does")
    ax.grid(True, which="both", axis="y", color="0.9")
    ax.set_axisbelow(True)
    ax.legend(framealpha=0.9)
    return ax


def plot_branching(df, reference=None, ax=None):
    """Plot the measured branching factor against depth.

    The branching factor is nodes ** (1 / depth): the average number of moves
    the search really had to consider at each ply.

    Args:
        df: A table with columns 'search', 'depth' and 'nodes'.
        reference: Optional mapping from label to a theoretical value, drawn
            as a dashed horizontal line.
        ax: Optional axes to draw on.

    Returns:
        The axes that were drawn on.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6.4, 4.4))
    for index, name in enumerate(sorted(df["search"].unique())):
        sub = df[df["search"] == name].sort_values("depth")
        factor = sub["nodes"] ** (1.0 / sub["depth"])
        ax.plot(sub["depth"], factor, label=name, linewidth=1.8,
                markersize=6, **style(index))
    if reference:
        for offset, label in enumerate(reference):
            ax.axhline(reference[label], color="0.35", linewidth=1.3,
                       linestyle=LINESTYLES[1 + offset % 3],
                       label=label + " = " + format(reference[label], ".2f"))
    ax.set_xlabel("search depth (plies)")
    ax.set_ylabel("effective branching factor")
    ax.set_title("moves actually considered per ply")
    ax.legend(fontsize=9, framealpha=0.9)
    return ax


def plot_visits(tables, labels, title="where the rollouts went"):
    """Grouped bars of how many rollouts each column received.

    Args:
        tables: A list of tables from lab3kit.mcts.root_table.
        labels: One label per table, used in the legend.
        title: Title for the plot.

    Returns:
        The axes that were drawn on.
    """
    _, ax = plt.subplots(figsize=(7.0, 4.2))
    width = 0.8 / len(tables)
    for index in range(len(tables)):
        table = tables[index]
        offset = (index - (len(tables) - 1) / 2) * width
        ax.bar(table["column"] + offset, table["share of rollouts"],
               width=width, label=labels[index],
               color=PALETTE[index % len(PALETTE)])
    ax.set_xlabel("column")
    ax.set_ylabel("share of all rollouts")
    ax.set_title(title)
    ax.set_xticks(range(COLS))
    ax.legend(framealpha=0.9)
    return ax


def plot_opponent_sweep(df):
    """Plot score and speed against how random the opponent is.

    Args:
        df: A table with columns 'epsilon', 'agent', 'result' and 'plies'.

    Returns:
        The matplotlib figure.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    names = sorted(df["agent"].unique())

    for index, name in enumerate(names):
        sub = df[df["agent"] == name]
        scores = sub.groupby("epsilon")["result"].mean()
        axes[0].plot(scores.index, scores.to_numpy(), label=name,
                     linewidth=1.8, markersize=6, **style(index))

        wins = sub[sub["result"] > 0]
        speed = wins.groupby("epsilon")["plies"].mean()
        axes[1].plot(speed.index, speed.to_numpy(), label=name,
                     linewidth=1.8, markersize=6, **style(index))

    axes[0].set_ylabel("average score  (+1 win, 0 draw, -1 loss)")
    axes[0].set_title("who wins more")
    axes[0].axhline(0, color="0.7", linewidth=1)
    axes[1].set_ylabel("plies taken, in games that were won")
    axes[1].set_title("who wins faster")
    for ax in axes:
        ax.set_xlabel("epsilon  (how often the opponent moves at random)")
        ax.legend(framealpha=0.9)
    fig.tight_layout()
    return fig
