"""
Saving results in a pre-defined format.
"""

RESULTS_COLUMNS = [
    "problem",
    "n",
    "algorithm",
    "seed",
    "solved",
    "evaluations",
    "final_cost",
]

# What each column should hold. The letters are how pandas labels a column's
# type: 'O' for text, 'i' for whole numbers, 'b' for True/False, 'f' for
# ordinary numbers.
EXPECTED_KIND = {
    "problem": "O",
    "n": "i",
    "algorithm": "O",
    "seed": "i",
    "solved": "b",
    "evaluations": "i",
    "final_cost": "f",
}

KIND_NAME = {
    "O": "text",
    "i": "whole number",
    "b": "True/False",
    "f": "number",
}


def save_results(df, path="results.csv"):
    """Check a results table against the fixed schema and write it out.

    Extra columns such as 'trace' are dropped rather than rejected, so you
    can pass the tables that run_all returned straight in.

    Args:
        df: The results table to save.
        path: Where to write the CSV.

    Raises:
        ValueError: If a required column is missing or holds the wrong type.
    """
    missing = []
    for column in RESULTS_COLUMNS:
        if column not in df.columns:
            missing.append(column)
    if missing:
        raise ValueError(
            f"results.csv needs the columns {RESULTS_COLUMNS}, but these are "
            f"missing: {missing}. Pass the table that run_all returned, or "
            "join several of them with pd.concat(...)."
        )

    trimmed = df[RESULTS_COLUMNS].copy()
    for column in RESULTS_COLUMNS:
        expected = EXPECTED_KIND[column]
        actual = trimmed[column].dtype.kind
        if actual == expected:
            continue
        if expected == "f" and actual in "iu":
            continue  # whole numbers are fine where a number is wanted
        if expected == "i" and actual == "u":
            continue
        raise ValueError(
            f"column '{column}' should hold {KIND_NAME[expected]} values, but "
            f"it holds {trimmed[column].dtype}. Did a row get built by hand "
            "instead of by run_all?"
        )

    trimmed.to_csv(path, index=False)
    print(f"✅ wrote {len(trimmed)} rows to {path}")
