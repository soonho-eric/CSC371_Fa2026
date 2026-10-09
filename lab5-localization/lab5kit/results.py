"""Saving results in a pre-defined format.

Lab 5 produces two tables:

    TRACE_COLUMNS   one row per time step of a filter run
    RUN_COLUMNS     one row per whole run, for the model-mismatch sweep

save_results checks both and writes results_trace.csv and results_runs.csv.
"""

TRACE_COLUMNS = [
    "run",
    "t",
    "action",
    "reading",
    "true_cell",
    "map_cell",
    "p_truth",
    "confidence",
    "entropy",
    "cells90",
    "correct",
]

RUN_COLUMNS = [
    "experiment",
    "assumed_epsilon",
    "true_epsilon",
    "p_move",
    "seed",
    "steps",
    "accuracy",
    "mean_p_truth",
    "mean_confidence",
    "mean_entropy",
    "final_correct",
]

# What each column should hold. The letters are how pandas labels a column's
# type: 'O' for text, 'i' for whole numbers, 'f' for ordinary numbers.
EXPECTED_KIND = {
    "run": "O",
    "experiment": "O",
    "action": "O",
    "reading": "O",
    "true_cell": "O",
    "map_cell": "O",
    "t": "i",
    "seed": "i",
    "steps": "i",
    "cells90": "i",
    "correct": "i",
    "final_correct": "i",
    "p_truth": "f",
    "confidence": "f",
    "entropy": "f",
    "accuracy": "f",
    "mean_p_truth": "f",
    "mean_confidence": "f",
    "mean_entropy": "f",
    "assumed_epsilon": "f",
    "true_epsilon": "f",
    "p_move": "f",
}

KIND_NAME = {"O": "text", "i": "whole number", "f": "number"}


def check_table(df, columns, label):
    """Return the table trimmed to columns, or raise if it does not fit."""
    missing = []
    for column in columns:
        if column not in df.columns:
            missing.append(column)
    if missing:
        raise ValueError(
            f"the {label} table needs the columns {columns}, but these are "
            f"missing: {missing}. Pass the table the experiment cell built."
        )

    trimmed = df[columns].copy()
    for column in columns:
        expected = EXPECTED_KIND[column]
        actual = trimmed[column].dtype.kind
        if actual == expected:
            continue
        if expected == "f" and actual in "iu":
            continue  # whole numbers are fine where a number is wanted
        if expected == "i" and actual in "ub":
            continue
        raise ValueError(
            f"in the {label} table, column '{column}' should hold "
            f"{KIND_NAME[expected]} values, but it holds "
            f"{trimmed[column].dtype}."
        )
    return trimmed


def save_results(df_trace, df_runs, prefix="results"):
    """Check both tables against their schema and write them out.

    Args:
        df_trace: The table of filter runs, step by step.
        df_runs: The table from the model-mismatch sweep.
        prefix: Files are written as <prefix>_trace.csv and <prefix>_runs.csv.
    """
    trace = check_table(df_trace, TRACE_COLUMNS, "trace")
    runs = check_table(df_runs, RUN_COLUMNS, "run")

    trace.to_csv(prefix + "_trace.csv", index=False)
    runs.to_csv(prefix + "_runs.csv", index=False)
    print(f"✅ wrote {len(trace)} rows to {prefix}_trace.csv")
    print(f"✅ wrote {len(runs)} rows to {prefix}_runs.csv")
