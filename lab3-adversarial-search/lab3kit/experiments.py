"""Playing games and collecting the results.

An agent is anything with a choose(game, state, rng) method that returns a
legal move. Three are provided:

    SearchAgent   picks the move your value function scores highest
    GreedyAgent   picks the best move one ply ahead, with no search
    RandomAgent   picks uniformly at random
    MixedAgent    random with probability epsilon, otherwise the wrapped agent

random_position builds a position partway through a game
run_search measures one search -> nodes and evaluations it spent
play_game   plays one game     -> who won and how long it took
run_matches plays many games   -> a table
"""

import pandas as pd


def random_position(game, pieces, seed):
    """A position reached by playing that many random moves, not yet over.

    Retries until it finds one, so the caller always gets a live position.
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    for attempt in range(4000):
        state = game.initial_state()
        finished_early = False
        for _ in range(pieces):
            if game.is_terminal(state):
                finished_early = True
                break
            moves = game.actions(state)
            state = game.result(state, moves[int(rng.integers(len(moves)))])
        if not finished_early and not game.is_terminal(state):
            return state
    raise ValueError("could not build a live position with " + str(pieces) + " pieces")


def run_search(game, state, depth, value_fn):
    """Run one search and report what it cost.

    Args:
        game: The game to search. Its counters are cleared first.
        state: The position to search from.
        depth: How many plies to look ahead.
        value_fn: One of your value functions, taking
            (game, state, depth, player).

    Returns:
        A dictionary with the value found and the work it took.
    """
    game.reset()
    value = value_fn(game, state, depth, game.to_move(state))
    return {
        "game": game.name,
        "depth": depth,
        "value": value,
        "nodes": game.nodes,
        "evaluations": game.evaluations,
    }


class SearchAgent:
    """Plays the move whose resulting position scores highest.

    Args:
        value_fn: One of your value functions.
        depth: How many plies to look ahead.
        name: Label for this agent in results tables.
    """

    def __init__(self, value_fn, depth, name):
        self.value_fn = value_fn
        self.depth = depth
        self.name = name

    def choose(self, game, state, rng):
        """Return the best move, breaking ties at random."""
        player = game.to_move(state)
        best_value = None
        best_moves = []
        for move in game.actions(state):
            child = game.result(state, move)
            value = self.value_fn(game, child, self.depth - 1, player)
            if best_value is None or value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
        return best_moves[int(rng.integers(len(best_moves)))]


class GreedyAgent:
    """Plays the move that looks best right now, with no search at all.

    It scores each position one move ahead with the game's evaluation
    function and takes the highest. That is a one-ply search, which is the
    least lookahead there is.
    """

    def __init__(self, name="greedy"):
        self.name = name

    def choose(self, game, state, rng):
        player = game.to_move(state)
        best_value = None
        best_moves = []
        for move in game.actions(state):
            child = game.result(state, move)
            if game.is_terminal(child):
                value = game.utility(child, player)
            else:
                value = game.evaluate(child, player)
            if best_value is None or value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
        return best_moves[int(rng.integers(len(best_moves)))]


class RandomAgent:
    """Plays a uniformly random legal move."""

    def __init__(self, name="random"):
        self.name = name

    def choose(self, game, state, rng):
        moves = game.actions(state)
        return moves[int(rng.integers(len(moves)))]


class MixedAgent:
    """Plays randomly with probability epsilon, otherwise like the agent given.

    epsilon = 0 is the wrapped agent unchanged; epsilon = 1 is pure noise.
    Turning this dial is how the experiments vary how good the opponent is.

    Args:
        agent: The agent to fall back on.
        epsilon: Chance of playing at random instead.
        name: Label for this agent in results tables.
    """

    def __init__(self, agent, epsilon, name=None):
        self.agent = agent
        self.epsilon = epsilon
        if name is None:
            name = agent.name + " (eps=" + str(epsilon) + ")"
        self.name = name

    def choose(self, game, state, rng):
        if rng.random() < self.epsilon:
            moves = game.actions(state)
            return moves[int(rng.integers(len(moves)))]
        return self.agent.choose(game, state, rng)


def play_game(game, first, second, rng):
    """Play one game through to the end.

    Args:
        game: The game to play. Its counters are cleared first.
        first: The agent moving first.
        second: The agent moving second.
        rng: The generator both agents draw from.

    Returns:
        A dictionary holding the result from first's point of view, the
        number of plies, and the work first's searches cost.
    """
    game.reset()
    state = game.initial_state()
    plies = 0
    while not game.is_terminal(state):
        if game.to_move(state) == 1:
            move = first.choose(game, state, rng)
        else:
            move = second.choose(game, state, rng)
        state = game.result(state, move)
        plies += 1
    return {
        "result": game.utility(state, 1),
        "plies": plies,
        "nodes": game.nodes,
        "evaluations": game.evaluations,
    }


def run_matches(agents, opponent, make_game, seeds):
    """Play every agent against the opponent over every seed.

    Each agent plays half the seeds first and half second, so nobody gets an
    advantage from moving first.

    Args:
        agents: A dictionary mapping a display name to an agent.
        opponent: The agent everyone plays against.
        make_game: A function taking a seed and returning a game.
        seeds: A list of seeds.

    Returns:
        A pandas DataFrame with one row per game.
    """
    import numpy as np

    rows = []
    total = len(agents) * len(seeds)
    report_every = max(1, total // 20)
    done = 0

    for name in agents:
        agent = agents[name]
        for seed in seeds:
            game = make_game(seed)
            rng = np.random.default_rng(seed)
            agent_first = (seed % 2 == 0)
            if agent_first:
                outcome = play_game(game, agent, opponent, rng)
                result = outcome["result"]
            else:
                outcome = play_game(game, opponent, agent, rng)
                result = -outcome["result"]
            rows.append({
                "game": game.name,
                "agent": name,
                "opponent": opponent.name,
                "seed": seed,
                "agent_first": agent_first,
                "result": result,
                "plies": outcome["plies"],
                "nodes": outcome["nodes"],
                "evaluations": outcome["evaluations"],
            })
            done = done + 1
            if done % report_every == 0 or done == total:
                print(f"\r  {done}/{total} games done ({name})   ", end="", flush=True)

    print()
    return pd.DataFrame(rows)
