"""Recording predictions before the experiments, and revealing them after."""

import json

import pandas as pd

WINNERS = ("minimax", "expectimax", "tie")


def record_predictions(alphabeta_node_fraction,
                       ordering_speedup,
                       random_opponent_winner,
                       why,
                       path="predictions.json"):
    """Check the four predictions over, save them, and hand them back.

    Args:
        alphabeta_node_fraction: At depth 6, what fraction of minimax's
            positions will alpha-beta look at? A number between 0 and 1.
        ordering_speedup: At depth 8, how many times fewer positions does
            alpha-beta search with centre-first ordering than without?
            A number of 1 or more.
        random_opponent_winner: Against an opponent that moves completely at
            random, which agent wins more games? "minimax", "expectimax" or
            "tie".
        why: A sentence or two explaining your reasoning.
        path: Where to save the predictions.

    Returns:
        A dictionary of the four predictions.
    """
    if alphabeta_node_fraction is not None:
        value = alphabeta_node_fraction
        if not isinstance(value, (int, float)) or value < 0.0 or value > 1.0:
            raise ValueError(
                "alphabeta_node_fraction should be a fraction between 0 and 1 "
                f'(0.25 means "a quarter as many positions"), not {value!r}'
            )

    if ordering_speedup is not None:
        value = ordering_speedup
        if not isinstance(value, (int, float)) or value < 1.0:
            raise ValueError(
                "ordering_speedup should be 1 or more (2 means \"half as many "
                f'positions"), not {value!r}'
            )

    if random_opponent_winner is not None:
        if random_opponent_winner not in WINNERS:
            raise ValueError(
                f"random_opponent_winner should be one of {WINNERS}, "
                f"not {random_opponent_winner!r}"
            )

    predictions = {
        "alphabeta_node_fraction": alphabeta_node_fraction,
        "ordering_speedup": ordering_speedup,
        "random_opponent_winner": random_opponent_winner,
        "why": why,
    }

    blank = []
    for key in predictions:
        if predictions[key] is None:
            blank.append(key)
    if blank:
        print(f"⚠️  {', '.join(blank)} left as None. ")

    handle = open(path, "w")
    json.dump(predictions, handle, indent=2)
    handle.close()
    print(f"✅ predictions recorded in {path}. Now go find out.")
    return predictions


def reveal(predictions, df_search, df_matches):
    """Return a table putting each prediction next to what actually happened.

    Args:
        predictions: The dictionary record_predictions returned.
        df_search: The search-cost table.
        df_matches: The tournament table.

    Returns:
        A pandas DataFrame with one row per prediction.
    """
    fraction = nodes_ratio(df_search, "alpha-beta", "minimax", 6)
    speedup = nodes_ratio(df_search, "alpha-beta", "alpha-beta + ordering", 8)

    random_games = df_matches[df_matches["epsilon"] == 1.0]
    winner = None
    note = ""
    if len(random_games) > 0:
        scores = random_games.groupby("agent")["result"].mean()
        best = scores.max()
        leaders = []
        for name in scores.index:
            if abs(scores[name] - best) < 1e-9:
                leaders.append(name)
        if len(leaders) == 1:
            winner = leaders[0]
        else:
            winner = "tie"
        parts = []
        for name in scores.index:
            parts.append(f"{name}: {scores[name]:+.2f}")
        note = ", ".join(parts)

    rows = [
        {
            "question": "alpha-beta's share of minimax's positions, depth 6",
            "you predicted": as_fraction(predictions["alphabeta_node_fraction"]),
            "actual": as_fraction(fraction),
            "note": "",
        },
        {
            "question": "positions saved by centre-first ordering, depth 8",
            "you predicted": as_times(predictions["ordering_speedup"]),
            "actual": as_times(speedup),
            "note": "",
        },
        {
            "question": "wins more against a fully random opponent",
            "you predicted": str(predictions["random_opponent_winner"]),
            "actual": str(winner),
            "note": note,
        },
        {
            "question": "your reasoning",
            "you predicted": str(predictions["why"]),
            "actual": "",
            "note": "Part 6 asks you to revisit this.",
        },
    ]
    return pd.DataFrame(rows)


def nodes_ratio(df_search, numerator, denominator, depth):
    """Nodes for one search divided by nodes for another, at a given depth."""
    rows = df_search[df_search["depth"] == depth]
    top = rows[rows["search"] == numerator]
    bottom = rows[rows["search"] == denominator]
    if len(top) == 0 or len(bottom) == 0:
        return None
    return float(top["nodes"].iloc[0]) / float(bottom["nodes"].iloc[0])


def as_fraction(value):
    """Format a fraction, or a dash when it is missing."""
    if value is None:
        return "—"
    return f"{value:.1%}"


def as_times(value):
    """Format a speedup, or a dash when it is missing."""
    if value is None:
        return "—"
    return f"{value:.1f}x"
