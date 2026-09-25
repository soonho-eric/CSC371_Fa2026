"""Two-player games for Lab 3.

A game class gives a search algorithm six things:

1. the starting position       -> game.initial_state()
2. whose turn it is            -> game.to_move(state)
3. the legal moves             -> game.actions(state)
4. the position after a move   -> game.result(state, move)
5. whether the game is over    -> game.is_terminal(state)
6. who won, once it is over    -> game.utility(state, player)

Depth-limited search needs one more: a guess at the value of a position that
is not over yet -> game.evaluate(state, player).

Alpha-beta prunes more when good moves are tried first, so there is also
   the moves, reordered  -> game.order(state, moves)

Both of those come from functions supplied when the game is built, the same
way NQueens took a cost function in Lab 2.

Both classes use the same method names, so your code runs on either.

Each class counts its own work:

    game.nodes         how many positions result() has built
    game.evaluations   how many times evaluate() has been called

A state is a tuple (board, player).
"""

ROWS = 6
COLS = 7
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


class Connect4:
    """Connect 4 on a 6-row, 7-column board.

    The board is a tuple of 42 ints, 0 for empty and 1 or 2 for a player.
    Cell (row, col) lives at index row * COLS + col, with row 0 at the bottom.

    Args:
        evaluate_fn: A function taking (game, state, player) and returning a
            number. Positive means good for player. Only called on positions
            that are not over.
        order_fn: A function taking (game, state, moves) and returning the
            same moves in a different order, or None to leave them alone.
    """

    def __init__(self, evaluate_fn=None, order_fn=None):
        self.name = "connect4"
        self.n = ROWS * COLS
        self.evaluate_fn = evaluate_fn
        self.order_fn = order_fn
        self.reset()

    def reset(self):
        """Clear the counters, ready for a new measurement."""
        self.nodes = 0
        self.evaluations = 0

    def initial_state(self):
        """An empty board, player 1 to move."""
        return ((0,) * (ROWS * COLS), 1)

    def to_move(self, state):
        return state[1]

    def actions(self, state):
        """The columns that are not yet full."""
        board = state[0]
        moves = []
        for col in range(COLS):
            if board[(ROWS - 1) * COLS + col] == 0:  # top cell still empty
                moves.append(col)
        return moves

    def result(self, state, col):
        """Drop a piece into this column and hand the turn over."""
        self.nodes += 1
        board, player = state
        for row in range(ROWS):
            if board[row * COLS + col] == 0:  # lowest empty cell in the column
                index = row * COLS + col
                return (board[:index] + (player,) + board[index + 1:], 3 - player)
        raise ValueError("column " + str(col) + " is full")

    def winner(self, state):
        """Return 1 or 2 if that player has four in a row, else 0."""
        board = state[0]
        for row in range(ROWS):
            for col in range(COLS):
                player = board[row * COLS + col]
                if player == 0:
                    continue
                for dr, dc in DIRECTIONS:
                    count = 1
                    rr = row + dr
                    cc = col + dc
                    while 0 <= rr < ROWS and 0 <= cc < COLS and board[rr * COLS + cc] == player:
                        count += 1
                        if count == 4:
                            return player
                        rr += dr
                        cc += dc
        return 0

    def is_terminal(self, state):
        """True when somebody has won or the board is full."""
        return self.winner(state) != 0 or len(self.actions(state)) == 0

    def utility(self, state, player):
        """+1 win, -1 loss, 0 draw. Only meaningful on a finished game."""
        won = self.winner(state)
        if won == 0:
            return 0
        if won == player:
            return 1
        return -1

    def evaluate(self, state, player):
        """Guess the value of an unfinished position, using the supplied function."""
        self.evaluations += 1
        return self.evaluate_fn(self, state, player)

    def order(self, state, moves):
        """Return the moves in the order search should try them."""
        if self.order_fn is None:
            return moves
        return self.order_fn(self, state, moves)


class TicTacToe:
    """Tic-tac-toe on the usual 3 by 3 board.

    The board is a tuple of 9 ints, 0 for empty and 1 or 2 for a player,
    read left to right and top to bottom.

    Small enough that search can reach the end of every line, so no
    evaluation function is needed. One is accepted anyway so that the same
    code runs on both games.
    """

    LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
             (0, 3, 6), (1, 4, 7), (2, 5, 8),
             (0, 4, 8), (2, 4, 6))

    def __init__(self, evaluate_fn=None, order_fn=None):
        self.name = "tictactoe"
        self.n = 9
        self.evaluate_fn = evaluate_fn
        self.order_fn = order_fn
        self.reset()

    def reset(self):
        """Clear the counters, ready for a new measurement."""
        self.nodes = 0
        self.evaluations = 0

    def initial_state(self):
        """An empty board, player 1 to move."""
        return ((0,) * 9, 1)

    def to_move(self, state):
        return state[1]

    def actions(self, state):
        """The empty squares."""
        board = state[0]
        moves = []
        for square in range(9):
            if board[square] == 0:
                moves.append(square)
        return moves

    def result(self, state, square):
        """Put a mark on this square and hand the turn over."""
        self.nodes += 1
        board, player = state
        return (board[:square] + (player,) + board[square + 1:], 3 - player)

    def winner(self, state):
        """Return 1 or 2 if that player holds a line, else 0."""
        board = state[0]
        for a, b, c in self.LINES:
            if board[a] != 0 and board[a] == board[b] and board[b] == board[c]:
                return board[a]
        return 0

    def is_terminal(self, state):
        """True when somebody has won or the board is full."""
        return self.winner(state) != 0 or len(self.actions(state)) == 0

    def utility(self, state, player):
        """+1 win, -1 loss, 0 draw. Only meaningful on a finished game."""
        won = self.winner(state)
        if won == 0:
            return 0
        if won == player:
            return 1
        return -1

    def evaluate(self, state, player):
        """Guess the value of an unfinished position, using the supplied function."""
        self.evaluations += 1
        if self.evaluate_fn is None:
            return 0.0
        return self.evaluate_fn(self, state, player)

    def order(self, state, moves):
        """Return the moves in the order search should try them."""
        if self.order_fn is None:
            return moves
        return self.order_fn(self, state, moves)
