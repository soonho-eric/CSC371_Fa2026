"""Check functions for the Lab 3 tasks.
Pass verbose=True to any check to see the full traceback of an error inside
your code. The checks only look at what your functions do.
"""

import math
import traceback

import numpy as np

from .games import COLS, ROWS, Connect4, TicTacToe
from .evaluation import centre_first, windowed_eval


# --------------------------------------------------------------------------
# printing
# --------------------------------------------------------------------------


def passed(name, detail):
    print("✅ " + name + ": " + detail)
    return True


def not_written_yet(name):
    print("⏳ " + name + " is not implemented yet. This is where you start!")
    return False


def failed(name, lines, hint):
    print("❌ " + name + ":")
    for line in lines:
        print("   " + line)
    print("   💡 " + hint)
    return False


def crashed(name, error, verbose):
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
    """A short pointer to the deepest line of student code, if there is one."""
    frames = []
    for frame in traceback.extract_tb(error.__traceback__):
        if frame.filename and "lab3kit" not in frame.filename:
            frames.append(frame)
    if not frames or not frames[-1].line:
        return ""
    return "your line " + str(frames[-1].lineno) + ": " + frames[-1].line.strip()


# --------------------------------------------------------------------------
# positions the checks use
# --------------------------------------------------------------------------


def build(game, moves):
    """Play a list of moves from the start and return the position reached."""
    state = game.initial_state()
    for move in moves:
        state = game.result(state, move)
    return state


def connect4(order=False):
    """A Connect 4 game wired up with the provided evaluation."""
    if order:
        return Connect4(windowed_eval, order_fn=centre_first)
    return Connect4(windowed_eval)


# Player 1 can win at once by completing the bottom row.
WIN_IN_ONE = (0, 0, 1, 1, 2, 2)


def random_positions(count, plies, seed):
    """A list of Connect 4 positions reached by random play."""
    rng = np.random.default_rng(seed)
    game = connect4()
    out = []
    while len(out) < count:
        state = game.initial_state()
        for _ in range(int(rng.integers(1, plies + 1))):
            if game.is_terminal(state):
                break
            moves = game.actions(state)
            state = game.result(state, moves[int(rng.integers(len(moves)))])
        if not game.is_terminal(state):
            out.append(state)
    return out


# --------------------------------------------------------------------------
# Task 1: minimax with no depth limit
# --------------------------------------------------------------------------


def check_minimax_value(minimax_value, verbose=False):
    """Check a minimax_value(game, state, player) implementation."""
    name = "minimax_value"
    try:
        tic = TicTacToe()

        # tic-tac-toe is a draw when nobody blunders
        tic.reset()
        value = minimax_value(tic, tic.initial_state(), 1)
        if value != 0:
            return failed(
                name,
                ["searching tic-tac-toe to the end from an empty board gave " +
                 format(value, "+.0f") + ", expected 0"],
                "Perfect play draws tic-tac-toe. A value of +1 usually means "
                "the search maximises at every node instead of alternating; "
                "check that you only take the max when "
                "game.to_move(state) == player.",
            )

        # a finished game is worth its utility, from either side
        won = build(tic, [0, 3, 1, 4, 2])          # player 1 holds the top row
        tic.reset()
        value = minimax_value(tic, won, 1)
        if value != 1:
            lines = ["a position player 1 has already won scored " +
                     format(value, "+.0f") + ", expected +1"]
            if value == -1:
                hint = ("The value came back with the wrong sign. Two things "
                        "cause that: negating game.utility(...), which already "
                        "reports from player's point of view, or handing it "
                        "game.to_move(state) instead of player. The player "
                        "argument is fixed for the whole search; only whose "
                        "turn it is changes.")
            else:
                hint = ("When game.is_terminal(state) is true, return "
                        "game.utility(state, player).")
            return failed(name, lines, hint)
        tic.reset()
        value = minimax_value(tic, won, 2)
        if value != -1:
            return failed(
                name,
                ["the same finished position scored " + format(value, "+.0f") +
                 " for the losing player, expected -1"],
                "utility is measured from the point of view of the player "
                "argument, so pass player through unchanged.",
            )

        # the opponent gets to reply: player 1 to move here still cannot win
        tic.reset()
        threat = build(tic, [4, 0, 8])   # player 2 must block, and does
        value = minimax_value(tic, threat, 2)
        if value > 0:
            return failed(
                name,
                ["a position where player 2 is under pressure scored " +
                 format(value, "+.0f") + " for player 2"],
                "At a node where it is the opponent's turn you must take the "
                "minimum, not the maximum. Otherwise you are assuming they "
                "help you.",
            )

    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "draw, terminal and opponent-reply checks passed")


# --------------------------------------------------------------------------
# Task 2: minimax with a depth cutoff
# --------------------------------------------------------------------------


def check_minimax_cutoff(minimax_cutoff, minimax_value=None, verbose=False):
    """Check a minimax_cutoff(game, state, depth, player) implementation.

    Args:
        minimax_cutoff: Your Task 2 function.
        minimax_value: Your Task 1 function, used as the answer key on
            tic-tac-toe.
        verbose: Show the full traceback for an error inside your code.
    """
    name = "minimax_cutoff"
    try:
        tic = TicTacToe()

        # given depth to spare, it must agree with the search that runs to the end
        tic.reset()
        value = minimax_cutoff(tic, tic.initial_state(), 9, 1)
        if value != 0:
            return failed(
                name,
                ["searching tic-tac-toe nine plies deep gave " +
                 format(value, "+.0f") + ", expected 0"],
                "With enough depth to reach the end of every line this should "
                "give exactly what Task 1 gave. Check that the recursive call "
                "passes depth - 1 and keeps the same player.",
            )

        # a finished game is worth its utility, even with depth left over
        won = build(tic, [0, 3, 1, 4, 2])
        for depth in (0, 1, 5):
            tic.reset()
            value = minimax_cutoff(tic, won, depth, 1)
            if value != 1:
                return failed(
                    name,
                    ["a position player 1 has already won scored " +
                     format(value, "+.0f") + " at depth " + str(depth) +
                     ", expected +1"],
                    "Test game.is_terminal(state) before you test the depth. A "
                    "finished game is finished however much depth is left, and "
                    "asking the evaluation function about it gives a guess "
                    "where you already have the answer.",
                )

        # depth 0 on an unfinished position hands over to the evaluation
        game = connect4()
        game.reset()
        state = build(game, [3, 3, 4])
        value = minimax_cutoff(game, state, 0, 1)
        if game.evaluations == 0:
            return failed(
                name,
                ["at depth 0 your search never called game.evaluate(...)"],
                "When the depth runs out on a position that is not over, "
                "return game.evaluate(state, player).",
            )
        if abs(value - windowed_eval(game, state, 1)) > 1e-9:
            return failed(
                name,
                ["at depth 0 you returned " + format(value, ".4f") + " but "
                 "game.evaluate gives " +
                 format(windowed_eval(game, state, 1), ".4f")],
                "Return the evaluation unchanged at depth 0.",
            )

        # deeper search must actually look at more positions. This runs on
        # tic-tac-toe, which is finite: a cutoff that never decrements would
        # search all of Connect 4 and never come back.
        shallow = TicTacToe()
        shallow.reset()
        minimax_cutoff(shallow, shallow.initial_state(), 2, 1)
        deep = TicTacToe()
        deep.reset()
        minimax_cutoff(deep, deep.initial_state(), 4, 1)
        if deep.nodes <= shallow.nodes:
            return failed(
                name,
                ["depth 2 searched " + f"{shallow.nodes:,}" + " positions and "
                 "depth 4 searched " + f"{deep.nodes:,}"],
                "The depth is not reaching the recursion. Each recursive call "
                "should get depth - 1.",
            )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "agreement, terminal, depth-0 and depth-growth checks passed")


# --------------------------------------------------------------------------
# Task 3: alpha-beta
# --------------------------------------------------------------------------


def check_alphabeta_value(alphabeta_value, minimax_cutoff=None, verbose=False):
    """Check an alphabeta_value(game, state, depth, player, alpha, beta) implementation.

    Args:
        alphabeta_value: Your function.
        minimax_cutoff: Your Task 2 function, used as the answer key.
        verbose: Show the full traceback for an error inside your code.
    """
    name = "alphabeta_value"
    if minimax_cutoff is None:
        print("⏳ " + name + ": this check needs your minimax_cutoff from "
              "Task 2. Pass it in as the second argument.")
        return False
    try:
        # same answer as minimax, on tic-tac-toe and on Connect 4
        tic = TicTacToe()
        tic.reset()
        value = alphabeta_value(tic, tic.initial_state(), 9, 1)
        if value != 0:
            return failed(
                name,
                ["searching tic-tac-toe to the end gave " + format(value, "+.0f") +
                 ", expected 0"],
                "Alpha-beta must return exactly what minimax returns. If it "
                "does not, a cutoff is firing when it should not: check that "
                "you compare against beta at maximising nodes and against "
                "alpha at minimising nodes.",
            )

        plain = connect4()
        for state in random_positions(8, 10, seed=3):
            player = plain.to_move(state)
            reference = connect4()
            reference.reset()
            wanted = minimax_cutoff(reference, state, 4, player)
            plain.reset()
            got = alphabeta_value(plain, state, 4, player)
            if abs(got - wanted) > 1e-9:
                return failed(
                    name,
                    ["on a Connect 4 position at depth 4 your alpha-beta "
                     "returned " + format(got, ".4f"),
                     "your own minimax returns " + format(wanted, ".4f") +
                     " on the same position"],
                    "Alpha-beta is an optimisation, not an approximation: it "
                    "has to agree with minimax everywhere. A swapped alpha "
                    "and beta update is the usual cause.",
                )

        # it has to actually prune
        state = build(connect4(), [3, 3])
        reference = connect4()
        reference.reset()
        minimax_cutoff(reference, state, 5, reference.to_move(state))
        plain.reset()
        alphabeta_value(plain, state, 5, plain.to_move(state))
        if plain.nodes >= reference.nodes:
            return failed(
                name,
                ["at depth 5 your alpha-beta searched " + f"{plain.nodes:,}" +
                 " positions and plain minimax searched " +
                 f"{reference.nodes:,}",
                 "alpha-beta should search far fewer"],
                "Nothing is being cut off. After updating the value at a "
                "node, compare it against beta (maximising) or alpha "
                "(minimising) and return early when the branch cannot matter.",
            )

        # and ordering has to reach it, which means calling game.order
        ordered = connect4(order=True)
        ordered.reset()
        alphabeta_value(ordered, state, 5, ordered.to_move(state))
        if ordered.nodes >= plain.nodes:
            return failed(
                name,
                ["searching with the centre-first ordering took " +
                 f"{ordered.nodes:,}" + " positions, against " +
                 f"{plain.nodes:,}" + " with no ordering",
                 "trying good moves first should prune more, not less"],
                "Get your moves from game.order(state, game.actions(state)) "
                "rather than from game.actions(state) alone.",
            )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "agreement, pruning and move-ordering checks passed")


# --------------------------------------------------------------------------
# Task 4: expectimax
# --------------------------------------------------------------------------


def check_expectimax_value(expectimax_value, minimax_cutoff=None, verbose=False):
    """Check an expectimax_value(game, state, depth, player) implementation."""
    name = "expectimax_value"
    try:
        tic = TicTacToe()

        # finished games still score their utility
        won = build(tic, [0, 3, 1, 4, 2])
        tic.reset()
        if expectimax_value(tic, won, 4, 1) != 1:
            return failed(
                name,
                ["a position player 1 has already won did not score +1"],
                "Test game.is_terminal(state) first and return "
                "game.utility(state, player), exactly as in minimax.",
            )

        # at the player's own nodes it still maximises
        game = connect4()
        state = build(game, WIN_IN_ONE)
        player = game.to_move(state)
        game.reset()
        value = expectimax_value(game, state, 2, player)
        if value < 1:
            return failed(
                name,
                ["from a position where " + str(player) + " can win at once, "
                 "expectimax scored " + format(value, ".3f") + ", expected +1"],
                "At nodes where it is your turn you still take the best move. "
                "Only the opponent's nodes change.",
            )

        # the opponent's nodes must average, not minimise
        positions = random_positions(10, 8, seed=5)
        differs = 0
        for state in positions:
            player = game.to_move(state)
            a = connect4()
            a.reset()
            expect = expectimax_value(a, state, 3, player)
            b = connect4()
            b.reset()
            worst = None
            if minimax_cutoff is not None:
                worst = minimax_cutoff(b, state, 3, player)
            if worst is not None and abs(expect - worst) > 1e-9:
                differs += 1
        if minimax_cutoff is not None and differs == 0:
            return failed(
                name,
                ["expectimax agreed with minimax on all 10 test positions"],
                "Those two should disagree: minimax assumes the opponent "
                "picks their best move, expectimax assumes they pick at "
                "random. At an opponent node, average the children instead "
                "of taking the minimum.",
            )

        # averaging, not summing: values must stay inside the utility range
        for state in positions:
            player = game.to_move(state)
            fresh = connect4()
            fresh.reset()
            value = expectimax_value(fresh, state, 3, player)
            if abs(value) > 5:
                return failed(
                    name,
                    ["a position scored " + format(value, ".2f"),
                     "scores should stay near the -1 to +1 range the "
                     "evaluation uses"],
                    "Divide the total by the number of moves. Adding the "
                    "children without averaging makes the value grow with "
                    "the branching factor.",
                )
    except NotImplementedError:
        return not_written_yet(name)
    except Exception as error:
        return crashed(name, error, verbose)

    return passed(name, "terminal, maximising, averaging and range checks passed")
