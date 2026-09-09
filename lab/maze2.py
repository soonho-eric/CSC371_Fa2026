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
'#G.....#....#',
'#############']

maze3 = [
'#############',
'#S....#.....#',
'#.##.##.###.#',
'#..#.#....#.#',
'##.###.##.#.#',
'#......#..#G#',
'#############']


maze3 = [
'#############',
'#S....#.....#',
'#.##.##.#####',
'#..#.#....#.#',
'##.###.##.#.#',
'#......#..#G#',
'#############']


maze11 = [
'#######################################',
'##.####.#####..########################',
'##............#########.....###########',
'##.###.################.###.###########',
'##.###..........#######G###.###########',
'##.####.#######...#########.###########',
'##.#.##.#####.#########.###.###########',
'##...##.###S.....####................##',
'####.###########.###################.##',
'####.####.##..##.###################.##',
'#.........###.##..................##.##',
'#########.....########.###.######.##.##',
'#############..........###.######....##',
'#######################################',]

maze12 = [
'#######################################',
'##.####.#####..########################',
'##............#########.....###########',
'##.###.################.###.###########',
'##.###..........###....G###.###########',
'##.####.#######.....#######.###########',
'##.#.##.#####.##.######.###.###########',
'##...##.###S.....####................##',
'####.###########.###################.##',
'####.####.##..##.###################.##',
'#.........###.##..................##.##',
'#########.....########.###.######.##.##',
'#############..........###.######....##',
'#######################################',]


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



# Plotting functions

import numpy as np
import matplotlib.pyplot as plt


def plot_maze(maze):
    """ Visualize the maze."""
    rows = len(maze)
    cols = len(maze[0])
    
    values = np.full((rows, cols), np.nan)
        
    # Use -1 for walls
    for row in range(rows):
        for col in range(cols):
            if maze[row][col] == "#":
                values[row, col] = -1
                
    plt.figure(figsize=(6/rows*cols, 6))
    plt.imshow(values)
    
    start = find_symbol(maze, "S")
    goal = find_symbol(maze, "G")
    plt.scatter(start[1], start[0], s=200, marker="o")
    plt.scatter(goal[1], goal[0], s=200, marker="*")
    plt.xticks([])
    plt.yticks([])
    plt.show()


def plot_search(maze, expanded, path=None):
    """ Visualize the searched states.
        Draw the final path if provided."""
    rows = len(maze)
    cols = len(maze[0])
    # NaN = unexpanded open cell
    values = np.full((rows, cols), np.nan)
    
    # Record expansion order
    for step, (row, col) in enumerate(expanded):
        values[row, col] = step
        
    # Use -1 for walls
    for row in range(rows):
        for col in range(cols):
            if maze[row][col] == "#":
                values[row, col] = -1
                
    plt.figure(figsize=(6/rows*cols, 6))
    plt.imshow(values)
    
    if path is not None:
        path_rows = [state[0] for state in path]
        path_cols = [state[1] for state in path]
        plt.plot(path_cols, path_rows, linewidth=3)
        
    start = find_symbol(maze, "S")
    goal = find_symbol(maze, "G")
    plt.scatter(start[1], start[0], s=200, marker="o")
    plt.scatter(goal[1], goal[0], s=200, marker="*")
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=12)          # adjust tick font size
    cbar.set_label("Expansion order", fontsize=12)  # add label
    plt.xticks([])
    plt.yticks([])
    plt.show()

from collections import deque

def reconstruct_path(parent, goal):
    """ Backtrack from goal to start and return path. """
    path = []
    state = goal

    # keep looping until None which means state is start
    while state is not None: 
        path.append(state)
        state = parent[state]

    path.reverse()
    return path


from collections import deque

def reconstruct_path(parent, goal):
    """ Backtrack from goal to start and return path. """
    path = []
    state = goal

    # keep looping until None which means state is start
    while state is not None: 
        path.append(state)
        state = parent[state]

    path.reverse()
    return path
    

def bfs(problem):
    """
    breadth-first search

    Parameters
    -----------
    problem : problem class
    
    Returns
    -------
    goal, path, expanded
    Or, if fails: None, None, expanded
    
    """
    start = problem.start
    frontier = deque([start])

    parent = {start: None}
    expanded = []

    while frontier: # keep going while any nodes in frontier
        state = frontier.popleft()
        expanded.append(state)

        if problem.goal_test(state):
            path = reconstruct_path(parent, state)
            return state, path, expanded
            
        for next_state in problem.neighbors(state):
            if next_state not in parent:
                parent[next_state] = state
                frontier.append(next_state)

    return None, None, expanded

    
def dfs(problem):
    """
    depth-first search

    Parameters
    -----------
    problem : problem class
    
    Returns
    -------
    goal, path, expanded
    Or, if fails: None, None, expanded
    
    """
    start = problem.start
    frontier = deque([start])

    parent = {start: None}
    expanded = []

    while frontier: # keep going while any nodes in frontier
        state = frontier.pop()
        expanded.append(state)

        if problem.goal_test(state):
            path = reconstruct_path(parent, state)
            return state, path, expanded
            
        for next_state in problem.neighbors(state):
            if next_state not in parent:
                parent[next_state] = state
                frontier.append(next_state)

    return None, None, expanded