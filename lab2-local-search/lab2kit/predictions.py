"""Recording predictions before the experiments, and revealing them after."""

import json

import pandas as pd


def record_predictions(hc_success_rate_8queens,
                       sideways_success_rate_8queens,
                       tsp_winner_equal_evaluations,
                       why,
                       path="predictions.json"):
    """Check the four predictions over, save them, and hand them back.

    Args:
        hc_success_rate_8queens: A fraction between 0 and 1, or None.
        sideways_success_rate_8queens: A fraction between 0 and 1, or None.
        tsp_winner_equal_evaluations: "annealing" or "restarts", or None.
        why: A sentence or two explaining your reasoning.
        path: Where to save the predictions.

    Returns:
        A dictionary of the four predictions.
    """
    check_rate("hc_success_rate_8queens", hc_success_rate_8queens)
    check_rate("sideways_success_rate_8queens", sideways_success_rate_8queens)

    if tsp_winner_equal_evaluations is not None:
        if tsp_winner_equal_evaluations not in ("annealing", "restarts"):
            raise ValueError(
                'tsp_winner_equal_evaluations should be "annealing" or '
                f'"restarts", not {tsp_winner_equal_evaluations!r}'
            )

    predictions = {
        "hc_success_rate_8queens": hc_success_rate_8queens,
        "sideways_success_rate_8queens": sideways_success_rate_8queens,
        "tsp_winner_equal_evaluations": tsp_winner_equal_evaluations,
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


def check_rate(name, value):
    """Complain if value is not a fraction between 0 and 1 (None is allowed)."""
    if value is None:
        return
    if not isinstance(value, (int, float)) or value < 0.0 or value > 1.0:
        raise ValueError(
            f'{name} should be a fraction between 0 and 1 '
            f'(0.25 means "a quarter of runs"), not {value!r}'
        )


def reveal(predictions, df_queens, df_tsp):
    """Return a table putting each prediction next to what actually happened.

    Args:
        predictions: The dictionary record_predictions returned.
        df_queens: The Experiment 1 results table.
        df_tsp: The Experiment 2 results table.

    Returns:
        A pandas DataFrame with one row per prediction.
    """
    rates = df_queens.groupby("algorithm")["solved"].mean()
    finals = df_tsp.groupby("algorithm")["final_cost"].median()

    actual_hc = rate_for(rates, "hill climbing")
    actual_sideways = rate_for(rates, "sideways")

    if len(finals) > 0:
        best = finals.idxmin()
        if "anneal" in best.lower():
            actual_winner = "annealing"
        else:
            actual_winner = "restarts"
        notes = []
        for name in finals.index:
            notes.append(f"{name}: {finals[name]:.2f}")
        winner_note = ", ".join(notes)
    else:
        actual_winner = None
        winner_note = ""

    rows = [
        {
            "question": "hill climbing success rate, 8-queens",
            "you predicted": as_percent(predictions["hc_success_rate_8queens"]),
            "actual": as_percent(actual_hc),
            "note": "",
        },
        {
            "question": "with sideways moves, 8-queens",
            "you predicted": as_percent(predictions["sideways_success_rate_8queens"]),
            "actual": as_percent(actual_sideways),
            "note": "",
        },
        {
            "question": "better median TSP tour at equal evaluations",
            "you predicted": str(predictions["tsp_winner_equal_evaluations"]),
            "actual": str(actual_winner),
            "note": winner_note,
        },
        {
            "question": "your reasoning",
            "you predicted": str(predictions["why"]),
            "actual": "",
            "note": "Part 6 asks you to revisit this.",
        },
    ]
    return pd.DataFrame(rows)


def rate_for(rates, fragment):
    """Return the success rate of the first algorithm whose name contains fragment."""
    for name in rates.index:
        if fragment in name:
            return float(rates[name])
    return None


def as_percent(value):
    """Format a fraction as a percentage, or a dash when it is missing."""
    if value is None:
        return "—"
    return f"{value:.0%}"
