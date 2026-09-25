"""The provided evaluation function and move ordering for Connect 4.

windowed_eval scores a position -> pass it to Connect4(windowed_eval)
centre_first reorders the legal moves -> pass it to your alpha-beta
"""

from .games import COLS, ROWS

# Every set of four cells in a line. A player wins by filling one of these.
WINDOWS = []
for _row in range(ROWS):
    for _col in range(COLS):
        for _dr, _dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            _cells = []
            for _step in range(4):
                _rr = _row + _dr * _step
                _cc = _col + _dc * _step
                if 0 <= _rr < ROWS and 0 <= _cc < COLS:
                    _cells.append(_rr * COLS + _cc)
            if len(_cells) == 4:
                WINDOWS.append(tuple(_cells))

# What a window is worth, by how many of the four cells one player holds.
WINDOW_SCORE = (0, 1, 4, 20)

# Search the middle columns first: they take part in the most windows, so
# they are the moves most likely to be good, and trying good moves early is
# what lets alpha-beta prune.
CENTRE_FIRST = (3, 2, 4, 1, 5, 0, 6)


def windowed_eval(game, state, player):
    """Score a Connect 4 position by counting windows only one player holds.

    A window with three of my pieces and no opponent piece is close to a win,
    so it scores much more than a window with one. Windows both players
    occupy are dead and score nothing.

    Args:
        game: The Connect4 instance.
        state: The position to score.
        player: Score from this player's point of view.

    Returns:
        A number, positive when the position favours player.
    """
    board = state[0]
    opponent = 3 - player
    score = 0
    for window in WINDOWS:
        mine = 0
        theirs = 0
        for index in window:
            if board[index] == player:
                mine += 1
            elif board[index] == opponent:
                theirs += 1
        if theirs == 0:
            score += WINDOW_SCORE[mine]
        elif mine == 0:
            score -= WINDOW_SCORE[theirs]
    # Holding the centre column is worth a little on its own.
    for row in range(ROWS):
        piece = board[row * COLS + 3]
        if piece == player:
            score += 3
        elif piece == opponent:
            score -= 3
    return score / 1000.0


def centre_first(game, state, moves):
    """Return the same moves, middle columns first.

    Args:
        game: The game instance.
        state: The position the moves apply to.
        moves: The list game.actions(state) returned.

    Returns:
        A reordered list holding exactly the same moves.
    """
    ordered = []
    for col in CENTRE_FIRST:
        if col in moves:
            ordered.append(col)
    return ordered
