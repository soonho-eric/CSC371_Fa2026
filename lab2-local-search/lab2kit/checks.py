"""Check functions for the Lab 2 tasks.
"""

import itertools
import traceback

import numpy as np


# --------------------------------------------------------------------------
# printing
# --------------------------------------------------------------------------


def passed(name, detail):
    """Print the pass line and return True."""
    print("✅ " + name + ": " + detail)
    return True


def not_written_yet(name):
    """Print the friendly unfinished message and return False."""
    print("⏳ " + name + " is not implemented yet. This is where you start!")
    return False


def failed(name, lines, hint):
    """Print what went wrong and a hint, then return False."""
    print("❌ " + name + ":")
    for line in lines:
        print("   " + line)
    print("   💡 " + hint)
    return False


def crashed(name, error, verbose):
    """Report an exception from student code in one or two readable lines."""
    if verbose:
        traceback.print_exception(type(error), error, error.__traceback__)
    print("❌ " + name + " raised " + type(error).__name__ + ": " + str(error))
    where = student_line(error)
    if where:
        print("   " + where)
    if not verbose:
        print("   💡 Re-run this check with verbose=True for the full traceback.")
    return False


def student_line(error):
    """Return a short pointer to the deepest line of student code, if there is one."""
    frames = []
    for frame in traceback.extract_tb(error.__traceback__):
        if frame.filename and "lab2kit" not in frame.filename:
            frames.append(frame)
    if not frames or not frames[-1].line:
        return ""
    return "your line " + str(frames[-1].lineno) + ": " + frames[-1].line.strip()


def queens_ready(name, problem):
    """Return True if the NQueens problem is usable, else explain and return False."""
    if problem is None:
        print("⏳ " + name + ": the 8-queens problem has not been built yet. "
              "Finish Tasks 1 and 2, run the cell that builds `queens`, then "
              "come back here.")
        return False
    try:
        problem.reset()
        scored = problem.cost((0, 4, 7, 5, 2, 6, 1, 3))
        found = len(problem.all_neighbors((0,) * problem.n))
    except NotImplementedError:
        print("⏳ " + name + ": finish Tasks 1 and 2 first; this check needs them.")
        return False
    wanted = problem.n * (problem.n - 1)
    if scored != 0:
        print("⏳ " + name + ": your NQueens problem scores a known 8-queens "
              "solution as " + str(scored) + " rather than 0, so finish Task 1 "
              "first.")
        return False
    if found != wanted:
        print("⏳ " + name + ": your NQueens problem offers " + str(found) +
              " neighbors where there should be " + str(wanted) + ", so finish "
              "Task 2 first.")
        return False
    problem.reset()
    return True


# --------------------------------------------------------------------------
# small problems built to make one specific mistake visible
#
# --------------------------------------------------------------------------


class Chain:
    """A line of states with costs you choose.

    State (i,) has cost costs[i]. Its neighbors are the next state along the
    line and a "sink" state that is always much worse, so the neighbor list
    is never empty and a climber always has somewhere to stop.
    """

    def __init__(self, costs):
        self.costs = list(costs)
        self.sink = len(self.costs)
        self.n = len(self.costs)
        self.name = "chain"
        self.reset()

    def reset(self):
        self.evaluations = 0
        self.iterations = 0
        self.all_neighbor_calls = 0
        self.best_state = None
        self.best_cost = float("inf")

    def random_state(self, rng):
        return (0,)

    def cost(self, state):
        self.evaluations += 1
        if state[0] == self.sink:
            value = 1e6
        else:
            value = float(self.costs[state[0]])
        if value < self.best_cost:
            self.best_cost = value
            self.best_state = state
        return value

    def neighbor_list(self, state):
        """The neighbors of state, without counting anything."""
        neighbors = []
        if state[0] + 1 < len(self.costs):
            neighbors.append((state[0] + 1,))
        neighbors.append((self.sink,))
        return neighbors

    def all_neighbors(self, state):
        self.iterations += 1
        self.all_neighbor_calls += 1
        return self.neighbor_list(state)

    def random_neighbor(self, state, rng):
        self.iterations += 1
        options = self.neighbor_list(state)
        return options[int(rng.integers(len(options)))]

    def is_goal(self, state):
        return False


class Fork:
    """A landscape where several neighbors tie for best.

    From the start, n_ties different states all share the same, strictly
    lower cost. Which one a climber ends up in shows whether it broke the tie
    at random or simply took the first.
    """

    def __init__(self, n_ties=4):
        self.n_ties = n_ties
        self.n = n_ties + 2
        self.name = "fork"
        self.reset()

    def reset(self):
        self.evaluations = 0
        self.iterations = 0
        self.all_neighbor_calls = 0
        self.best_state = None
        self.best_cost = float("inf")

    def random_state(self, rng):
        return (0,)

    def cost(self, state):
        self.evaluations += 1
        if state == (0,):
            value = 5.0
        elif state[0] == -1:
            value = 100.0
        else:
            value = 1.0
        if value < self.best_cost:
            self.best_cost = value
            self.best_state = state
        return value

    def neighbor_list(self, state):
        """The neighbors of state, without counting anything."""
        if state == (0,):
            return [(index,) for index in range(1, self.n_ties + 1)]
        return [(-1,)]

    def all_neighbors(self, state):
        self.iterations += 1
        self.all_neighbor_calls += 1
        return self.neighbor_list(state)

    def random_neighbor(self, state, rng):
        self.iterations += 1
        options = self.neighbor_list(state)
        return options[int(rng.integers(len(options)))]

    def is_goal(self, state):
        return False


def climb_on(climber, problem, seed, budget):
    """Run a climber on one of the small landscapes and report where it ended."""
    problem.reset()
    rng = np.random.default_rng(seed)
    return climber(problem, rng, budget)


# --------------------------------------------------------------------------
# Task 1
# --------------------------------------------------------------------------

COST_CASES = [
    ((0,), 0, "one queen attacks nobody"),
    ((0, 0), 1, "same row"),
    ((0, 1), 1, "diagonal, going up"),
    ((1, 0), 1, "diagonal, going down"),
    ((1, 3, 0, 2), 0, "a solved 4-queens board"),
    ((2, 0, 3, 1), 0, "another solved 4-queens board"),
    ((0, 0, 0, 0), 6, "all four in row 0"),
    ((0, 1, 2, 3), 6, "all four on one rising diagonal"),
    ((3, 2, 1, 0), 6, "all four on one falling diagonal"),
    ((3, 1, 0, 2), 1, "a mixed board"),
    ((0, 4, 7, 5, 2, 6, 1, 3), 0, "a solved 8-queens board"),
    ((0, 0, 0, 0, 0, 0, 0, 0), 28, "all eight in row 0"),
]


def check_queens_cost(queens_cost, verbose=False):
    """Check a queens_cost(state) implementation."""
    name = "queens_cost"
    try:
        actual = []
        for case in COST_CASES:
            actual.append(queens_cost(case[0]))
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    wrong = []
    for index in range(len(COST_CASES)):
        state, expected, note = COST_CASES[index]
        if actual[index] != expected:
            wrong.append((state, expected, actual[index], note))

    if not wrong:
        return passed(name, "all " + str(len(COST_CASES)) + " cases passed")

    lines = []
    for state, expected, got, note in wrong[:4]:
        lines.append("queens_cost(" + str(state) + ") returned " + str(got) +
                     ", expected " + str(expected) + "  (" + note + ")")
    if len(wrong) > 4:
        lines.append("...and " + str(len(wrong) - 4) + " more case(s) wrong")
    return failed(name, lines, diagnose_cost(actual))


def diagnose_cost(actual):
    """Pick the most specific hint for an observed pattern of answers."""
    by_state = {}
    expected = {}
    for index in range(len(COST_CASES)):
        by_state[COST_CASES[index][0]] = actual[index]
        expected[COST_CASES[index][0]] = COST_CASES[index][1]

    solved_boards = [(1, 3, 0, 2), (0, 4, 7, 5, 2, 6, 1, 3)]
    counts_itself = True
    for state in solved_boards:
        if by_state[state] != len(state):
            counts_itself = False
    if counts_itself:
        return "A queen does not attack itself. Skip the case i == j."

    doubled = True
    for state in expected:
        if expected[state] > 0 and by_state[state] != 2 * expected[state]:
            doubled = False
    if doubled:
        return "Every pair is being counted twice. Loop over pairs with i < j."

    diagonal_only = [(0, 1), (1, 0), (0, 1, 2, 3), (3, 2, 1, 0)]
    misses_diagonals = True
    for state in diagonal_only:
        if by_state[state] != 0:
            misses_diagonals = False
    if misses_diagonals:
        return ("Two queens also attack along a diagonal: compare the "
                "difference in rows with the difference in columns.")

    if by_state[(0, 1)] != 1 or by_state[(1, 0)] != 1:
        return ("Only one diagonal direction is being caught. Use the "
                "absolute value of the row difference, "
                "abs(state[i] - state[j]).")

    return ("Work one failing case out by hand on paper, then step through "
            "your loop on the same board and see where the two disagree.")


# --------------------------------------------------------------------------
# Task 2
# --------------------------------------------------------------------------

NEIGHBOR_CASES = [(0, 0, 0, 0), (1, 3, 0, 2), (0, 1, 2)]


def expected_neighbors(state):
    """The correct neighbor set, found by brute force over every small board.

    This checks all n**n boards and keeps the ones differing from state in
    exactly one column. That is far too slow to be a real implementation,
    which is exactly why it is safe to use as an answer key here.
    """
    n = len(state)
    keep = set()
    for board in itertools.product(range(n), repeat=n):
        differences = 0
        for column in range(n):
            if board[column] != state[column]:
                differences += 1
        if differences == 1:
            keep.add(board)
    return keep


def check_queens_neighbors(queens_neighbors, verbose=False):
    """Check a queens_neighbors(state) implementation."""
    name = "queens_neighbors"
    try:
        for state in NEIGHBOR_CASES:
            got = queens_neighbors(state)
            n = len(state)
            wanted = expected_neighbors(state)

            if not isinstance(got, (list, tuple)):
                return failed(
                    name,
                    ["queens_neighbors(" + str(state) + ") returned a " +
                     type(got).__name__],
                    "Return a list of states.",
                )

            bad = []
            for item in got:
                if not isinstance(item, tuple):
                    bad.append(item)
            if bad:
                return failed(
                    name,
                    ["queens_neighbors(" + str(state) + ") produced " +
                     type(bad[0]).__name__ + " entries such as " + str(bad[0])],
                    "States must be tuples, not lists. Convert with tuple(...).",
                )

            if state in got:
                return failed(
                    name,
                    ["queens_neighbors(" + str(state) + ") includes " +
                     str(state) + " itself"],
                    "Moving a queen to the row it is already in is not a move. "
                    "Skip row == state[col].",
                )

            if len(got) != len(wanted):
                return failed(
                    name,
                    ["queens_neighbors(" + str(state) + ") returned " +
                     str(len(got)) + " neighbors, expected " +
                     str(n * (n - 1))],
                    "For n = " + str(n) + " there are " + str(n) + " columns "
                    "and " + str(n - 1) + " other rows in each, so " + str(n) +
                    " x " + str(n - 1) + " = " + str(n * (n - 1)) + " "
                    "neighbors. Are you looping over every column, or only one?",
                )

            if set(got) != wanted:
                missing = sorted(wanted - set(got))[:2]
                extra = sorted(set(got) - wanted)[:2]
                return failed(
                    name,
                    ["queens_neighbors(" + str(state) + ") has the right "
                     "length but the wrong contents",
                     "missing, for example: " + str(missing),
                     "unexpected, for example: " + str(extra)],
                    "Each neighbor changes exactly one column, and only that "
                    "column's row.",
                )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "all " + str(len(NEIGHBOR_CASES)) + " cases passed")


# --------------------------------------------------------------------------
# Task 3
# --------------------------------------------------------------------------

# A flat stretch: nothing is ever strictly better, so a correct climber stops
# on the spot and a climber that accepts equal-cost moves walks the whole way.
FLAT = [5.0] * 60


def check_hill_climb(hill_climb, problem=None, verbose=False):
    """Check a hill_climb(problem, rng, budget) implementation."""
    name = "hill_climb"
    if not queens_ready(name, problem):
        return False

    try:
        # 1. strict improvement only
        flat = Chain(FLAT)
        state = climb_on(hill_climb, flat, seed=0, budget=300)
        if state[0] > 0 or flat.evaluations >= 300:
            if flat.evaluations >= 300:
                where = "used up its whole budget"
            else:
                where = "ended at step " + str(state[0])
            return failed(
                name,
                ["on a landscape where every neighbor costs exactly the same "
                 "as the current state, your climber " + where,
                 "a hill climber has nowhere to go there and should stop at once"],
                "Move only if the best neighbor is *strictly* better than the "
                "current state. `<=` lets you wander a plateau forever.",
            )

        # 2. random tie-breaking
        endings = set()
        for seed in range(30):
            endings.add(climb_on(hill_climb, Fork(4), seed=seed, budget=200))
        if len(endings) == 1:
            return failed(
                name,
                ["on a landscape where four different neighbors tie for best, "
                 "30 different seeds all ended in the same state " +
                 str(endings.pop())],
                "Break ties uniformly at random with rng: collect every "
                "neighbor that achieves the best cost and choose one with "
                "rng.integers or rng.choice.",
            )

        # 3. climbs all the way to a local minimum
        for seed in (1, 2, 3, 4, 5):
            problem.reset()
            rng = np.random.default_rng(seed)
            result = hill_climb(problem, rng, 200000)
            if result is None:
                return failed(name, ["your hill_climb returned None"],
                              "Return the state you stopped at.")
            here = problem.cost(result)
            better = None
            for neighbor in problem.all_neighbors(result):
                if problem.cost(neighbor) < here:
                    better = neighbor
                    break
            if better is not None:
                return failed(
                    name,
                    ["seed " + str(seed) + ": you stopped at " + str(result) +
                     " with cost " + str(int(here)),
                     "but " + str(better) + " costs " +
                     str(int(problem.cost(better))) + ", which is better"],
                    "Keep stepping in a loop until no neighbor improves on the "
                    "current state. One step is not a climb.",
                )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "plateau, tie-breaking and local-minimum checks passed")


# --------------------------------------------------------------------------
# Task 4
# --------------------------------------------------------------------------

# Cost drops by one every second step, so one sideways move always comes just
# before an improvement. A climber that resets its counter walks the whole
# staircase; one that never resets runs out of allowance after a few steps.
STAIRS = [50.0 - (index // 2) for index in range(80)]

# A completely flat stretch, for spotting an allowance that is never enforced.
LONG_FLAT = [7.0] * 80


def check_hill_climb_sideways(hill_climb_sideways, problem=None, verbose=False):
    """Check a hill_climb_sideways(problem, rng, budget, max_sideways) implementation."""
    name = "hill_climb_sideways"
    if not queens_ready(name, problem):
        return False

    try:
        # 1. the allowance is enforced at all
        flat = Chain(LONG_FLAT)
        flat.reset()
        rng = np.random.default_rng(0)
        state = hill_climb_sideways(flat, rng, 2000, max_sideways=3)
        if state[0] > 8:
            return failed(
                name,
                ["with max_sideways=3 on a completely flat landscape, your "
                 "climber took " + str(state[0]) + " sideways steps",
                 "after 3 sideways moves in a row it should give up"],
                "Count consecutive sideways moves and stop once the count "
                "reaches max_sideways.",
            )

        # 2. the allowance is refreshed by a strict improvement
        stairs = Chain(STAIRS)
        stairs.reset()
        rng = np.random.default_rng(0)
        state = hill_climb_sideways(stairs, rng, 4000, max_sideways=3)
        if state[0] < 60:
            return failed(
                name,
                ["on a staircase where one sideways move always leads to a "
                 "strict improvement, your climber stopped at step " +
                 str(state[0]) + " of 79",
                 "it never used more than one sideways move in a row, so the "
                 "allowance of 3 should never have run out"],
                "Reset the consecutive-sideways counter to zero after every "
                "strictly improving move.",
            )

        # 3. it still behaves like a hill climber on the real problem
        solved = 0
        for seed in range(12):
            problem.reset()
            rng = np.random.default_rng(seed)
            result = hill_climb_sideways(problem, rng, 200000, max_sideways=100)
            if result is None:
                return failed(name, ["your hill_climb_sideways returned None"],
                              "Return the state you stopped at.")
            if problem.is_goal(result):
                solved += 1
        if solved < 4:
            return failed(
                name,
                ["on 8-queens with max_sideways=100, only " + str(solved) +
                 " of 12 runs reached a solution",
                 "allowing sideways moves should do considerably better"],
                "Check that a sideways move actually moves you: the current "
                "state has to become the equal-cost neighbor.",
            )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "allowance, reset and 8-queens behaviour checks passed")


# --------------------------------------------------------------------------
# Task 5
# --------------------------------------------------------------------------


def check_random_restart(random_restart, problem=None, verbose=False):
    """Check a random_restart(problem, rng, budget, climber) implementation."""
    name = "random_restart"
    if not queens_ready(name, problem):
        return False

    calls = []
    starts = []

    def stub_climber(inner_problem, rng, budget):
        """A climber that always fails, so restarting is the only way on."""
        calls.append(1)
        start = inner_problem.random_state(rng)
        starts.append(start)
        inner_problem.cost(start)
        return start

    try:
        problem.reset()
        rng = np.random.default_rng(0)
        random_restart(problem, rng, 400, climber=stub_climber)

        if len(calls) == 0:
            return failed(
                name,
                ["the climber passed in as the `climber` argument was never called"],
                "Call climber(problem, rng, budget), not hill_climb directly, "
                "so that the same function works with any climber.",
            )
        if len(calls) == 1:
            return failed(
                name,
                ["the climber ran once and then random_restart returned",
                 "the climber it was given never reaches a goal state, so a "
                 "correct random_restart would have tried again"],
                "Loop while problem.evaluations < budget, restarting until "
                "problem.is_goal(state) is true.",
            )
        if len(set(starts)) == 1:
            return failed(
                name,
                ["the climber ran " + str(len(calls)) + " times but every "
                 "restart began from the same state " + str(starts[0])],
                "Each restart needs a fresh problem.random_state(rng). Pass "
                "the same rng through rather than making a new one.",
            )

        # It actually solves 8-queens when given a real climber and budget.
        solved = 0
        for seed in range(5):
            problem.reset()
            rng = np.random.default_rng(seed)
            result = random_restart(problem, rng, 60000)
            if result is not None and problem.is_goal(result):
                solved += 1
        if solved < 4:
            return failed(
                name,
                ["with the default climber and a generous budget, only " +
                 str(solved) + " of 5 runs reached a solved board"],
                "Restarting plain hill climbing should solve 8-queens reliably "
                "given enough restarts. Check that the loop keeps going until "
                "problem.is_goal(state) or the budget runs out.",
            )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "restart, fresh-start and 8-queens checks passed")


# --------------------------------------------------------------------------
# Task 6a
# --------------------------------------------------------------------------

ACCEPT_RATES = [
    (1.0, 1.0, 0.3679),
    (0.1, 1.0, 0.9048),
    (2.0, 1.0, 0.1353),
    (1.0, 0.25, 0.0183),
]

FROZEN_HINT = ("Treat T at or below 1e-12 as frozen: accept improvements "
               "only, and never compute exp(-delta / T) there.")


def check_accept(accept, verbose=False):
    """Check an accept(delta, T, rng) implementation."""
    name = "accept"
    draws = 4000

    try:
        # 1. improvements and equal moves are always taken
        for delta in (-5.0, -1.0, -0.001, 0.0):
            for temperature in (10.0, 1.0, 0.01, 0.0):
                rng = np.random.default_rng(7)
                for _ in range(50):
                    if not accept(delta, temperature, rng):
                        return failed(
                            name,
                            ["accept(delta=" + str(delta) + ", T=" +
                             str(temperature) + ", rng) returned False at "
                             "least once"],
                            "A move with delta <= 0 is never worse than where "
                            "you are, so it is always accepted, whatever T is.",
                        )

        # 2. very small T behaves greedily instead of dividing by zero
        for temperature in (0.0, 1e-15, 1e-13):
            rng = np.random.default_rng(3)
            taken = 0
            try:
                for _ in range(200):
                    if accept(1.0, temperature, rng):
                        taken += 1
            except (ZeroDivisionError, OverflowError, FloatingPointError) as error:
                return failed(
                    name,
                    ["accept(delta=1.0, T=" + str(temperature) + ", rng) "
                     "raised " + type(error).__name__ + ": " + str(error)],
                    FROZEN_HINT,
                )
            if taken > 0:
                return failed(
                    name,
                    ["accept(delta=1.0, T=" + str(temperature) + ", rng) "
                     "accepted an uphill move " + str(taken) +
                     " time(s) out of 200"],
                    FROZEN_HINT,
                )

        # 3. uphill moves follow the Metropolis rate
        measured = []
        for delta, temperature, wanted in ACCEPT_RATES:
            rng = np.random.default_rng(12345)
            taken = 0
            for _ in range(draws):
                if accept(delta, temperature, rng):
                    taken += 1
            measured.append((delta, temperature, taken / draws, wanted))
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    wrong = []
    for row in measured:
        if abs(row[2] - row[3]) > 0.035:
            wrong.append(row)

    if wrong:
        delta, temperature, got, wanted = wrong[0]
        always_accepts = True
        for row in measured:
            if row[2] <= 0.98:
                always_accepts = False
        if always_accepts:
            hint = ("The sign in the exponent is flipped. A bigger delta "
                    "means a worse move, so it should be accepted *less* "
                    "often: use exp(-delta / T).")
        elif got < wanted:
            hint = ("Compare your probability against a fresh random number, "
                    "for example rng.random() < math.exp(-delta / T).")
        else:
            hint = ("Uphill moves are being accepted too often. Check that "
                    "you divide delta by T and negate it.")
        return failed(
            name,
            ["with delta=" + str(delta) + " and T=" + str(temperature) +
             ", you accepted " + f"{got:.1%}" + " of 4000 uphill moves",
             "the Metropolis rule accepts exp(-delta/T) = " + f"{wanted:.1%}"],
            hint,
        )

    return passed(name, "all 4 rate cases and the frozen-T case passed")


# --------------------------------------------------------------------------
# Task 6b
# --------------------------------------------------------------------------


def check_simulated_annealing(simulated_annealing, problem=None, verbose=False):
    """Check a simulated_annealing(problem, rng, budget, ...) implementation."""
    name = "simulated_annealing"
    if not queens_ready(name, problem):
        return False

    try:
        # 1. one random neighbor per step, not the whole neighborhood
        problem.reset()
        simulated_annealing(problem, np.random.default_rng(0), 600)
        if problem.all_neighbor_calls > 0:
            return failed(
                name,
                ["your loop called problem.all_neighbors() " +
                 str(problem.all_neighbor_calls) + " time(s)"],
                "Annealing looks at one random neighbor per step: use "
                "problem.random_neighbor(state, rng).",
            )
        if problem.iterations > 0:
            per_step = problem.evaluations / problem.iterations
            if per_step > 4:
                return failed(
                    name,
                    ["you spent " + str(problem.evaluations) + " evaluations "
                     "over " + str(problem.iterations) + " steps (" +
                     f"{per_step:.1f}" + " per step)"],
                    "One step should cost about one evaluation. Remember the "
                    "current cost instead of recomputing it every time.",
                )

        # 2. the walk actually moves
        problem.reset()
        problem.record_visits = True
        simulated_annealing(problem, np.random.default_rng(1), 1500,
                            T0=5.0, alpha=0.99, T_min=1e-3)
        walk = list(problem.visited)
        problem.record_visits = False
        moves = 0
        for index in range(len(walk) - 1):
            if walk[index] != walk[index + 1]:
                moves += 1
        if len(walk) > 50 and moves < 5:
            return failed(
                name,
                ["over " + str(len(walk)) + " steps the current state changed "
                 "only " + str(moves) + " time(s)"],
                "When a move is accepted, the accepted neighbor has to become "
                "the current state for the next step.",
            )

        # 3. the temperature comes down
        # T_min is tiny here so the schedule never resets inside the window.
        problem.reset()
        problem.record_visits = True
        simulated_annealing(problem, np.random.default_rng(2), 900,
                            T0=20.0, alpha=0.97, T_min=1e-300)
        walk = list(problem.visited)
        problem.record_visits = False
        if len(walk) >= 200:
            third = len(walk) // 3
            early = uphill_rate(problem, walk[:third])
            late = uphill_rate(problem, walk[-third:])
            if late > 0.25 and late > early - 0.1:
                return failed(
                    name,
                    ["early in the run you accepted " + f"{early:.0%}" +
                     " of uphill moves; near the end, still " + f"{late:.0%}",
                     "with alpha = 0.97 the temperature should have fallen far "
                     "enough by then that uphill moves are rare"],
                    "Multiply T by alpha once per step, and use the current T "
                    "in accept(...).",
                )

        # 4. it works
        solved = 0
        for seed in range(10):
            problem.reset()
            simulated_annealing(problem, np.random.default_rng(seed), 20000)
            if problem.best_state is not None and problem.is_goal(problem.best_state):
                solved += 1
        if solved < 6:
            return failed(
                name,
                ["with a budget of 20,000 evaluations, only " + str(solved) +
                 " of 10 runs found a solved 8-queens board"],
                "Check the order of a step: draw a neighbor, compute delta as "
                "(neighbor cost - current cost), call accept, move if "
                "accepted, then cool. And make sure T is reset to T0 once it "
                "drops below T_min, so the search never stalls at zero "
                "temperature.",
            )
    except NotImplementedError:
        problem.record_visits = False
        return not_written_yet(name)
    except Exception as error:
        problem.record_visits = False
        return crashed(name, error, verbose)

    return passed(name, "neighbor use, movement, cooling and 8-queens checks "
                        "passed (" + str(solved) + "/10 solved)")


def uphill_rate(problem, walk):
    """Fraction of consecutive steps in walk that moved to a worse state."""
    if len(walk) < 2:
        return 0.0
    uphill = 0
    for index in range(len(walk) - 1):
        before = problem.cost_fn(walk[index])
        after = problem.cost_fn(walk[index + 1])
        if after > before:
            uphill += 1
    return uphill / (len(walk) - 1)
