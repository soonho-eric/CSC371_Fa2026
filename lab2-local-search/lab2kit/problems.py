"""Local search problems for Lab 2.

A problem class in local search does three things:

1. a way to make a random state -> problem.random_state(rng)
2. a cost to minimize -> problem.cost(state)
3. a way to list (or sample) the neighbors of a state. 
        -> problem.all_neighbors(state) or problem.random_neighbor(state, rng)

Both classes use the same method name, so your code can interact with both.

Each class also counts its own work:

    problem.evaluations   how many times cost() has been called
    problem.iterations    how many times you asked for neighbors

"""

import numpy as np


class NQueens:
    """Place n queens on an n x n board, one per column, with no attacks.

    A state is a tuple of length n where state[col] is the row of the queen
    standing in column col. Because there is exactly one queen per column, no
    two queens can ever share a column, and the only thing left to fix is
    rows and diagonals.

    The cost function and the neighbor functions need to be supplied by the user.

    Args:
        n: Board size (an int).
        cost_fn: A funciton that takes a state, returns the number of
            attacking pairs.
        neighbors_fn: A function that takes a state, returns every
            state reachable by moving one queen within its own column.
    """

    def __init__(self, n, cost_fn, neighbors_fn):
        self.n = n
        self.name = str(n) + "-queens"
        self.cost_fn = cost_fn
        self.neighbors_fn = neighbors_fn
        # The check functions turn this on to watch how your search moves.
        # It stays off during experiments, where the list would grow huge.
        self.record_visits = False
        self.reset()

    def reset(self):
        """Clear the counters and the best-so-far record, ready for a new run."""
        self.evaluations = 0
        self.iterations = 0
        self.all_neighbor_calls = 0
        self.best_state = None
        self.best_cost = float("inf")
        self.trace = []
        self.best_states = []
        self.visited = []

    def random_state(self, rng):
        """Return a board with each queen in a random row. Costs nothing."""
        return tuple(int(row) for row in rng.integers(0, self.n, size=self.n))

    def cost(self, state):
        """Return the number of attacking pairs, using queens_cost provided.
        """
        self.evaluations += 1
        value = float(self.cost_fn(state))
        if value < self.best_cost:
            self.best_cost = value
            self.best_state = state
            self.trace.append((self.evaluations, self.iterations, value))
            self.best_states.append(state)
        return value

    def all_neighbors(self, state):
        """Return every one-queen move, using your queens_neighbors."""
        self.iterations += 1
        self.all_neighbor_calls += 1
        return self.neighbors_fn(state)

    def random_neighbor(self, state, rng):
        """Move one random queen to a different random row in its column."""
        self.iterations += 1
        if self.record_visits:
            self.visited.append(state)
        col = int(rng.integers(self.n))
        row = int(rng.integers(self.n - 1))
        if row >= state[col]:
            row = row + 1  # skip the row the queen is already in
        return state[:col] + (row,) + state[col + 1:]

    def is_goal(self, state):
        """Return True when no two queens attack each other.

        A board is safe exactly when all n rows differ, all n values of
        row + col differ, and all n values of row - col differ.

        Does not spend on budget.
        """
        rows = set(state)
        up = set()
        down = set()
        for col in range(len(state)):
            up.add(state[col] + col)
            down.add(state[col] - col)
        return len(rows) == self.n and len(up) == self.n and len(down) == self.n


class TSP:
    """The traveling salesperson problem on random points in the unit square.

    A state is a permutation tuple: state[k] is the city visited k-th. The
    cost is the length of the closed tour, which returns to the start.

    Neighbors come from the 2-opt move (swapping destinations of two edges), 
    which is done by taking a segment and reversing.

    Args:
        n: How many cities.
        seed: rng seed for city position
    """

    def __init__(self, n, seed):
        rng = np.random.default_rng(seed)
        self.points = rng.random((n, 2))
        self.n = n
        self.name = "tsp-" + str(n)
        difference = self.points[:, None, :] - self.points[None, :, :]
        self.distances = np.sqrt((difference ** 2).sum(axis=-1))
        self.record_visits = False
        self.reset()

    def reset(self):
        """Clear the counters and the best-so-far record, ready for a new run."""
        self.evaluations = 0
        self.iterations = 0
        self.all_neighbor_calls = 0
        self.best_state = None
        self.best_cost = float("inf")
        self.trace = []
        self.best_states = []
        self.visited = []

    def random_state(self, rng):
        """Return a random tour visiting every city once. Costs nothing."""
        return tuple(int(city) for city in rng.permutation(self.n))

    def cost(self, state):
        """Return the total length of the closed tour, and count the call."""
        self.evaluations += 1
        tour = np.asarray(state)
        value = float(self.distances[tour, np.roll(tour, -1)].sum())
        if value < self.best_cost:
            self.best_cost = value
            self.best_state = state
            self.trace.append((self.evaluations, self.iterations, value))
            self.best_states.append(state)
        return value

    def all_neighbors(self, state):
        """Return every distinct 2-opt move from this tour."""
        self.iterations += 1
        neighbors = []
        for i in range(self.n - 1):
            for j in range(i + 1, self.n):
                if i == 0 and j == self.n - 1:
                    continue  # reversing the whole tour gives the same cycle
                neighbors.append(two_opt(state, i, j))
        return neighbors

    def random_neighbor(self, state, rng):
        """Return the result of one random 2-opt move."""
        self.iterations += 1
        if self.record_visits:
            self.visited.append(state)
        while True:
            # pick two random numbers from 0 - n with i < j
            i, j = sorted(int(x) for x in rng.choice(self.n, size=2, replace=False))
            if not (i == 0 and j == self.n - 1):
                return two_opt(state, i, j) # reverse segment

    def is_goal(self, state):
        """Always False: there is no known perfect tour to recognise."""
        return False

def two_opt(state, i, j):
     return state[:i] + state[i:j + 1][::-1] + state[j + 1:]