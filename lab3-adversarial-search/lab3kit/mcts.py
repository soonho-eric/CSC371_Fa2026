r"""Monte Carlo tree search for Connect 4.

Alpha-beta needs somebody to write an evaluation function. MCTS does not. It
estimates how good a position is by playing random games from it to the end
and counting how many it wins.

Four steps, repeated once per rollout:

1. select     walk down the tree, at each step taking the child UCB1 rates
              highest, until reaching a node with a move not yet tried
2. expand     add one new child for one of those untried moves
3. simulate   from that child, play completely at random to the end
4. backprop   add the result to every node on the way back up

UCB1 is what balances the two things the walk wants to do:

    score / visits  +  c * sqrt(ln(parent visits) / visits)
    \_____________/     \_______________________________/
     how good it has     how little we have looked at it
     looked so far

c is the exploration constant. Small c keeps re-checking whatever already
looks best; large c spreads attention evenly.

Positions inside the tree are kept as plain lists rather than the tuples the
rest of the lab uses. Nothing outside this file sees them, and the random
playouts touch millions of positions, so speed matters more than tidiness
here.
"""

import math

import pandas as pd

from .games import COLS, ROWS

DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def wins_after(board, row, col):
    """Did the piece just played at (row, col) complete a line of four?

    Only lines through that one square can be new, so this is much cheaper
    than scanning the whole board.
    """
    player = board[row * COLS + col]
    for dr, dc in DIRECTIONS:
        count = 1
        for sign in (1, -1):
            rr = row + dr * sign
            cc = col + dc * sign
            while 0 <= rr < ROWS and 0 <= cc < COLS and board[rr * COLS + cc] == player:
                count += 1
                if count >= 4:
                    return True
                rr += dr * sign
                cc += dc * sign
    return False


def playout(board, heights, player, rng):
    """Play uniformly random moves to the end. Returns 1, 2, or 0 for a draw.

    board and heights are modified in place, so callers pass in copies.
    """
    for _ in range(ROWS * COLS):
        legal = []
        for col in range(COLS):
            if heights[col] < ROWS:
                legal.append(col)
        if not legal:
            return 0
        col = legal[int(rng.integers(len(legal)))]
        row = heights[col]
        board[row * COLS + col] = player
        heights[col] += 1
        if wins_after(board, row, col):
            return player
        player = 3 - player
    return 0


class Node:
    """One position in the search tree.

    Attributes:
        player: Whose turn it is in this position.
        move: The column played to get here, or None at the root.
        winner: 1 or 2 if the game ended here, else 0.
        children: The positions expanded below this one.
        untried: Moves from here that have not been expanded yet.
        visits: How many rollouts passed through here.
        score: Wins for the player who moved *into* this position, counting a
            draw as half.
    """

    def __init__(self, board, heights, player, parent, move, winner):
        self.board = board
        self.heights = heights
        self.player = player
        self.parent = parent
        self.move = move
        self.winner = winner
        self.children = []
        self.untried = []
        if winner == 0:
            for col in range(COLS):
                if heights[col] < ROWS:
                    self.untried.append(col)
        self.visits = 0
        self.score = 0.0

    def win_rate(self):
        """Share of rollouts through here that the mover won. 0.5 is even."""
        if self.visits == 0:
            return 0.0
        return self.score / self.visits


def ucb1_choice(node, c):
    """Return the child with the highest UCB1 score."""
    best = None
    best_value = None
    for child in node.children:
        exploit = child.score / child.visits
        explore = c * math.sqrt(math.log(node.visits) / child.visits)
        value = exploit + explore
        if best_value is None or value > best_value:
            best_value = value
            best = child
    return best


def to_board(state):
    """Turn one of the lab's (board, player) states into lists MCTS can use."""
    board = list(state[0])
    heights = []
    for col in range(COLS):
        height = 0
        for row in range(ROWS):
            if board[row * COLS + col] != 0:
                height = row + 1
        heights.append(height)
    return board, heights


def mcts_search(state, rollouts, c, rng):
    """Run MCTS from this position and return the root of the tree it built.

    Args:
        state: A Connect 4 (board, player) state.
        rollouts: How many random games to play.
        c: The exploration constant.
        rng: A numpy generator.

    Returns:
        The root Node. Its children carry the visit counts and win rates,
        which is what the demos look at.
    """
    board, heights = to_board(state)
    root = Node(board, heights, state[1], None, None, 0)

    for _ in range(rollouts):
        node = root

        # 1. select
        while not node.untried and node.children:
            node = ucb1_choice(node, c)

        # 2. expand
        if node.untried:
            col = node.untried.pop(int(rng.integers(len(node.untried))))
            child_board = list(node.board)
            child_heights = list(node.heights)
            row = child_heights[col]
            child_board[row * COLS + col] = node.player
            child_heights[col] += 1
            if wins_after(child_board, row, col):
                winner = node.player
            else:
                winner = 0
            child = Node(child_board, child_heights, 3 - node.player,
                         node, col, winner)
            node.children.append(child)
            node = child

        # 3. simulate
        if node.winner != 0:
            result = node.winner
        else:
            result = playout(list(node.board), list(node.heights),
                             node.player, rng)

        # 4. backpropagate
        while node is not None:
            node.visits += 1
            mover = 3 - node.player      # whoever moved into this position
            if result == mover:
                node.score += 1.0
            elif result == 0:
                node.score += 0.5
            node = node.parent

    return root


def best_move(root):
    """The move MCTS would play: the child it spent the most rollouts on."""
    best = None
    for child in root.children:
        if best is None or child.visits > best.visits:
            best = child
    return best.move


def root_table(root):
    """A table of what the root's children look like, one row per column."""
    rows = []
    for child in sorted(root.children, key=lambda child: child.move):
        rows.append({
            "column": child.move,
            "visits": child.visits,
            "share of rollouts": child.visits / root.visits,
            "win rate": child.win_rate(),
        })
    return pd.DataFrame(rows)


class MCTSAgent:
    """An agent that picks its move by running MCTS.

    Args:
        rollouts: How many random games to play per move.
        c: The exploration constant.
        name: Label for this agent in results tables.
    """

    def __init__(self, rollouts, c=1.4, name=None):
        self.rollouts = rollouts
        self.c = c
        if name is None:
            name = "mcts-" + str(rollouts)
        self.name = name

    def choose(self, game, state, rng):
        root = mcts_search(state, self.rollouts, self.c, rng)
        return best_move(root)
