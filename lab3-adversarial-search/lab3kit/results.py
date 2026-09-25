"""Saving results in a pre-defined format.

Lab 3 produces two different tables, so there are two schemas:

    SEARCH_COLUMNS   one row per search: how much work it took
    MATCH_COLUMNS    one row per game played: who won and how fast

save_results checks both and writes results_search.csv and results_matches.csv.
"""

SEARCH_COLUMNS = [
    "game",
    "search",
    "depth",
    "nodes",
    "evaluations",
]

MATCH_COLUMNS = [
    "game",
    "agent",
    "opponent",
    "epsilon",
    "seed",
    "result",
    "plies",
    "nodes",
]

# What each column should hold. The letters are how pandas labels a column's
# type: 'O' for text, 'i' for whole numbers, 'f' for ordinary numbers.
EXPECTED_KIND = {
    "game": "O",
    "search": "O",
    "agent": "O",
    "opponent": "O",
    "depth": "i",
    "epsilon": "f",
    "seed": "i",
    "result": "i",
    "plies": "i",
    "nodes": "i",
    "evaluations": "i",
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


def save_results(df_search, df_matches, prefix="results"):
    """Check both tables against their schema and write them out.

    Args:
        df_search: The table from the search-cost experiment.
        df_matches: The table from the tournament.
        prefix: Files are written as <prefix>_search.csv and
            <prefix>_matches.csv.
    """
    search = check_table(df_search, SEARCH_COLUMNS, "search")
    matches = check_table(df_matches, MATCH_COLUMNS, "match")

    search.to_csv(prefix + "_search.csv", index=False)
    matches.to_csv(prefix + "_matches.csv", index=False)
    print(f"✅ wrote {len(search)} rows to {prefix}_search.csv")
    print(f"✅ wrote {len(matches)} rows to {prefix}_matches.csv")
