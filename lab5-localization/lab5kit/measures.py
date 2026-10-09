"""Ways of summarizing a belief in one number.
"""

import math


def most_likely(belief):
    """The cell with the highest probability.

    Ties are broken by position, so the answer does not depend on the order
    the dictionary happens to be in.
    """
    return max(sorted(belief), key=lambda cell: belief[cell])


def confidence(belief):
    """The probability the belief puts on its own best guess."""
    return belief[most_likely(belief)]


def entropy(belief):
    """How spread out a belief is, in bits.

    0 bits means certainty. The largest possible value is log2 of the number
    of cells, which a uniform belief achieves: log2(30) is about 4.9 bits.
    """
    total = 0.0
    for probability in belief.values():
        if probability > 0.0:
            total -= probability * math.log2(probability)
    return total


def cells_covering(belief, mass=0.9):
    """How many cells it takes to cover mass of the probability.

    A quick read on ambiguity: 1 means the belief is on a single cell, 8 means
    the robot could be in any of eight places.
    """
    running = 0.0
    for count, probability in enumerate(sorted(belief.values(), reverse=True), 1):
        running += probability
        if running >= mass - 1e-12:
            return count
    return len(belief)


def top_cells(belief, count=5):
    """The count most likely cells, as a list of (cell, probability) pairs."""
    ordered = sorted(belief.items(), key=lambda pair: (-pair[1], pair[0]))
    return ordered[:count]


def total(belief):
    """The sum of a belief's probabilities, which should be 1."""
    return sum(belief.values())
