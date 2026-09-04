maze1 = [
'#############',
'#S....#.....#',
'#.##..#.###.#',
'#..#......#.#',
'##.#####.##.#',
'#......#...G#',
'#############']

maze2 = [
'#############',
'#S....#.....#',
'#.##..#.###.#',
'#..#......#.#',
'##.########.#',
'#......#...G#',
'#############']

maze3 = [
'#############',
'#S....#.....#',
'#.##.##.###.#',
'#..#.#....#.#',
'##.###.##.#.#',
'#......#..#G#',
'#############']


def find_symbol(maze, symbol):
    """Return row and column of a symbol in the maze."""
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == symbol:
                return (row, col)


def get_neighbors(maze, state):
    """Return all valid neighboring states."""
    row, col = state

    possible_neighbors = [
        (row - 1, col),  # up
        (row + 1, col),  # down
        (row, col - 1),  # left
        (row, col + 1),  # right
    ]

    neighbors = []

    for next_row, next_col in possible_neighbors:
        if maze[next_row][next_col] != "#":
            neighbors.append((next_row, next_col))

    return neighbors


def print_maze(maze, path=None):
    """Print maze. if path given, it is marked with *."""

    if path is None:
        path = []

    path = set(path)

    for row in range(len(maze)):
        line = ""

        for col in range(len(maze[row])):
            cell = maze[row][col]

            if (row, col) in path and cell == ".":
                line += "*"
            else:
                line += cell

        print(line)
