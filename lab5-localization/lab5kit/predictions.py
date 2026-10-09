"""Recording predictions before the experiments, and revealing them after."""

import json

import pandas as pd

from .experiments import localization_times

ANSWERS = ("yes", "no", "same")


def record_predictions(readings_to_localize,
                       best_assumed_epsilon,
                       overconfident_is_surer,
                       why,
                       path="predictions.json"):
    """Check the four predictions over, save them, and hand them back.

    Args:
        readings_to_localize: Starting from no idea where it is, how many
            readings does the filter need before it puts at least half its
            probability on the cell the robot is really in? A whole number,
            typical over many runs.
        best_assumed_epsilon: The sonar really lies 30% of the time. Of the
            noise levels the sweep tries, which one should the filter be told
            to make its best guesses most often? A number between 0 and 0.5.
        overconfident_is_surer: A filter told the sonar hardly ever lies,
            fed readings from a sonar that lies 30% of the time. Will its
            average probability on its own best guess be higher than that of
            a filter told the truth? Answer "yes", "no" or "same".
        why: A sentence or two explaining your reasoning.
        path: Where to save the predictions.

    Returns:
        A dictionary of the four predictions.
    """
    if readings_to_localize is not None:
        value = readings_to_localize
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(
                "readings_to_localize should be a whole number of readings, "
                f"1 or more, not {value!r}"
            )

    if best_assumed_epsilon is not None:
        value = best_assumed_epsilon
        if not isinstance(value, (int, float)) or value < 0.0 or value > 0.5:
            raise ValueError(
                "best_assumed_epsilon should be a sonar noise level between "
                f"0 and 0.5, not {value!r}"
            )

    if overconfident_is_surer is not None:
        if overconfident_is_surer not in ANSWERS:
            raise ValueError(
                f"overconfident_is_surer should be one of {ANSWERS}, "
                f"not {overconfident_is_surer!r}"
            )

    predictions = {
        "readings_to_localize": readings_to_localize,
        "best_assumed_epsilon": best_assumed_epsilon,
        "overconfident_is_surer": overconfident_is_surer,
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


def reveal(predictions, df_trace, df_runs, threshold=0.5):
    """Return a table putting each prediction next to what actually happened.

    Args:
        predictions: The dictionary record_predictions returned.
        df_trace: The trace table from the many-runs experiment.
        df_runs: The sweep table.
        threshold: How much probability on the true cell counts as localized.

    Returns:
        A pandas DataFrame with one row per prediction.
    """
    many = df_trace[df_trace["run"].str.startswith("run")]
    if len(many) == 0:
        many = df_trace
    times = localization_times(many, threshold)
    median_time = times.median()
    never = int(times.isna().sum())

    by_epsilon = df_runs.groupby("assumed_epsilon")
    accuracy = by_epsilon["accuracy"].mean()
    confidence = by_epsilon["mean_confidence"].mean()
    best = accuracy.idxmax()
    true_epsilon = float(df_runs["true_epsilon"].iloc[0])

    surer = None
    note_confidence = ""
    lowest = confidence.index.min()
    if lowest < true_epsilon and true_epsilon in confidence.index:
        overconfident = confidence[lowest]
        honest = confidence[true_epsilon]
        if abs(overconfident - honest) < 0.01:
            surer = "same"
        else:
            surer = "yes" if overconfident > honest else "no"
        note_confidence = (f"assuming {lowest:g}: {overconfident:.2f} sure and "
                           f"{accuracy[lowest]:.0%} right; "
                           f"assuming {true_epsilon:g}: {honest:.2f} sure and "
                           f"{accuracy[true_epsilon]:.0%} right")

    rows = [
        {
            "question": f"readings until p(true cell) >= {threshold}",
            "you predicted": _whole(predictions["readings_to_localize"]),
            "actual": _whole(median_time) + " (median)",
            "note": (f"{len(times)} runs; {never} never got there"
                     if never else f"{len(times)} runs"),
        },
        {
            "question": "assumed sonar noise with the best accuracy",
            "you predicted": _number(predictions["best_assumed_epsilon"]),
            "actual": _number(best),
            "note": "accuracy " + ", ".join(
                f"{value:g}: {accuracy[value]:.0%}" for value in accuracy.index),
        },
        {
            "question": "an overconfident filter is surer of itself",
            "you predicted": str(predictions["overconfident_is_surer"]),
            "actual": str(surer),
            "note": note_confidence,
        },
        {
            "question": "your reasoning",
            "you predicted": str(predictions["why"]),
            "actual": "",
            "note": "Part 7 asks you to revisit this.",
        },
    ]
    return pd.DataFrame(rows)


def _whole(value):
    """Format a count, or say so when it is missing."""
    if value is None or value != value:  # None or NaN
        return "not given"
    return f"{value:.0f}"


def _number(value):
    """Format a noise level, or say so when it is missing."""
    if value is None:
        return "not given"
    return f"{value:g}"
