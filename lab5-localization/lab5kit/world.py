"""The world Lab 5 localizes in: a maze, a motion model and a sonar.
"""

import collections

MAZE = """
##########
#........#
#.##..##.#
#.#....#.#
#.##..##.#
#........#
##########
"""

DIRECTIONS = ("north", "east", "south", "west")

STEP = {
    "north": (-1, 0),
    "east": (0, 1),
    "south": (1, 0),
    "west": (0, -1),
}

# Drifting sideways is the only way a move goes wrong: the robot never ends up
# behind where it started.
SIDEWAYS = {
    "north": ("east", "west"),
    "east": ("north", "south"),
    "south": ("east", "west"),
    "west": ("north", "south"),
}

Trajectory = collections.namedtuple("Trajectory", "cells actions readings")
Trajectory.__doc__ = """One run of the robot through the maze.

cells: the true cell at each time step, length T + 1.
actions: the action taken between time steps, length T.
readings: the sonar reading at each time step, length T + 1.

Time 0 is the robot sitting at its starting cell having taken one reading.
From then on each step is one action followed by one reading, so there is
always one more reading than there are actions.
"""


class Maze:
    """A grid maze, a noisy motion model and a noisy sonar.

    Attributes:
        rows: Number of rows, walls included.
        cols: Number of columns, walls included.
        cells: Every free cell, as a sorted tuple. The robot is in one of
            these and a belief has one entry per cell.
        walls: The wall cells, as a frozenset.
        epsilon: The chance that any one sonar beam reports the opposite of
            the truth. 0 is a perfect sonar, 0.5 is a useless one.
        p_move: The chance that a move goes the way it was asked to. The rest
            of the probability is split between the two sideways directions.
    """

    def __init__(self, maze=MAZE, epsilon=0.1, p_move=0.8):
        lines = [line for line in maze.strip().splitlines()]
        self.rows = len(lines)
        self.cols = len(lines[0])
        if any(len(line) != self.cols for line in lines):
            raise ValueError("every row of the maze must be the same width")

        walls = set()
        cells = []
        for row, line in enumerate(lines):
            for col, character in enumerate(line):
                if character == "#":
                    walls.add((row, col))
                else:
                    cells.append((row, col))
        self.walls = frozenset(walls)
        self.cells = tuple(sorted(cells))

        if not 0.0 <= epsilon <= 1.0:
            raise ValueError(f"epsilon must be between 0 and 1, not {epsilon!r}")
        if not 0.0 <= p_move <= 1.0:
            raise ValueError(f"p_move must be between 0 and 1, not {p_move!r}")
        self.epsilon = float(epsilon)
        self.p_move = float(p_move)

        self._signatures = {cell: self._compute_signature(cell) for cell in self.cells}

    # ------------------------------------------------------------------
    # the maze itself
    # ------------------------------------------------------------------

    def is_wall(self, cell):
        """True when cell is a wall or outside the maze."""
        row, col = cell
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        return cell in self.walls

    def neighbor(self, cell, direction):
        """The cell one step in direction, or cell itself if that is a wall."""
        row, col = cell
        d_row, d_col = STEP[direction]
        ahead = (row + d_row, col + d_col)
        if self.is_wall(ahead):
            return cell
        return ahead

    # ------------------------------------------------------------------
    # the motion model
    # ------------------------------------------------------------------

    def transition(self, cell, action):
        """P(next cell | cell, action), as a dictionary over the cells it can reach.

        The robot goes the way it was asked with probability ``p_move`` and
        drifts to one of the two sideways directions otherwise. Whichever
        direction it ends up going, driving into a wall leaves it where it
        started, so a cell facing a wall keeps some probability of staying put.

        Args:
            cell: The cell the robot is in.
            action: One of ``DIRECTIONS``.

        Returns:
            A dictionary mapping each reachable cell to its probability. The
            values sum to 1.
        """
        if action not in STEP:
            raise ValueError(f"{action!r} is not one of {DIRECTIONS}")
        if self.is_wall(cell):
            raise ValueError(f"{cell} is a wall, so the robot cannot be there")

        drift = (1.0 - self.p_move) / 2.0
        outcomes = [(action, self.p_move)]
        for sideways in SIDEWAYS[action]:
            outcomes.append((sideways, drift))

        result = {}
        for direction, probability in outcomes:
            if probability == 0.0:
                continue
            landing = self.neighbor(cell, direction)
            result[landing] = result.get(landing, 0.0) + probability
        return result

    # ------------------------------------------------------------------
    # the sonar
    # ------------------------------------------------------------------

    def _compute_signature(self, cell):
        return tuple(
            1 if self.is_wall((cell[0] + STEP[d][0], cell[1] + STEP[d][1])) else 0
            for d in DIRECTIONS
        )

    def signature(self, cell):
        """What a perfect sonar would read in cell.

        Args:
            cell: A free cell.

        Returns:
            A 4-tuple of 0s and 1s in the order of ``DIRECTIONS``, where 1
            means there is a wall on that side.
        """
        if cell not in self._signatures:
            raise ValueError(f"{cell} is not a free cell of this maze")
        return self._signatures[cell]

    def matching_cells(self, reading):
        """Every cell whose perfect reading is exactly reading.

        Useful for seeing how ambiguous a reading is before any noise: in a
        symmetric maze, several cells look identical to a perfect sonar.
        """
        return tuple(c for c in self.cells if self.signature(c) == tuple(reading))

    # ------------------------------------------------------------------
    # beliefs
    # ------------------------------------------------------------------

    def uniform_belief(self):
        """A belief that gives every free cell the same probability."""
        share = 1.0 / len(self.cells)
        return {cell: share for cell in self.cells}

    def point_belief(self, cell):
        """A belief that is certain the robot is in cell."""
        if cell not in self._signatures:
            raise ValueError(f"{cell} is not a free cell of this maze")
        belief = {c: 0.0 for c in self.cells}
        belief[cell] = 1.0
        return belief

    # ------------------------------------------------------------------
    # variants: the same maze, believed to behave differently
    # ------------------------------------------------------------------

    def variant(self, epsilon=None, p_move=None):
        """The same maze with different noise, as a new Maze.

        Part 6 generates a trajectory in one maze and filters it with another.
        This is how you make the second one.

        Args:
            epsilon: Sonar noise for the copy. None keeps this maze's.
            p_move: Motion reliability for the copy. None keeps this maze's.

        Returns:
            A new Maze with the same layout.
        """
        copy = object.__new__(Maze)
        copy.rows = self.rows
        copy.cols = self.cols
        copy.walls = self.walls
        copy.cells = self.cells
        copy._signatures = self._signatures
        copy.epsilon = self.epsilon if epsilon is None else float(epsilon)
        copy.p_move = self.p_move if p_move is None else float(p_move)
        if not 0.0 <= copy.epsilon <= 1.0:
            raise ValueError(f"epsilon must be between 0 and 1, not {copy.epsilon!r}")
        if not 0.0 <= copy.p_move <= 1.0:
            raise ValueError(f"p_move must be between 0 and 1, not {copy.p_move!r}")
        return copy

    # ------------------------------------------------------------------
    # generating data
    # ------------------------------------------------------------------

    def sample_reading(self, cell, rng):
        """One noisy sonar reading from cell.

        Each of the four beams independently reports the opposite of the truth
        with probability ``epsilon``.
        """
        truth = self.signature(cell)
        return tuple(
            1 - bit if rng.random() < self.epsilon else bit for bit in truth
        )

    def sample_move(self, cell, action, rng):
        """Where the robot actually ends up when it tries action from cell."""
        outcomes = sorted(self.transition(cell, action).items())
        draw = rng.random()
        total = 0.0
        for landing, probability in outcomes:
            total += probability
            if draw < total:
                return landing
        return outcomes[-1][0]

    def simulate(self, steps, rng, start=None, actions=None):
        """Drive the robot around and record what happened.

        The noise comes from this maze's own ``epsilon`` and ``p_move``, which
        is what makes it the *true* world: a filter that is given different
        numbers is a filter working from the wrong model.

        Args:
            steps: How many actions to take.
            rng: A ``numpy.random.Generator``.
            start: Starting cell. None picks one uniformly at random.
            actions: The actions to take. None picks each one at random.

        Returns:
            A Trajectory. ``cells`` and ``readings`` have ``steps + 1``
            entries; ``actions`` has ``steps``.
        """
        if start is None:
            start = self.cells[int(rng.integers(len(self.cells)))]
        if actions is None:
            actions = [DIRECTIONS[int(rng.integers(4))] for _ in range(steps)]
        actions = list(actions)
        if len(actions) != steps:
            raise ValueError(f"got {len(actions)} actions for {steps} steps")

        cell = start
        cells = [cell]
        readings = [self.sample_reading(cell, rng)]
        for action in actions:
            cell = self.sample_move(cell, action, rng)
            cells.append(cell)
            readings.append(self.sample_reading(cell, rng))
        return Trajectory(cells=cells, actions=actions, readings=readings)

    def __repr__(self):
        return (f"Maze({len(self.cells)} free cells, "
                f"epsilon={self.epsilon}, p_move={self.p_move})")

    def render(self, highlight=()):
        """The maze as text, with any highlighted cells marked with an R."""
        highlight = set(highlight)
        lines = []
        for row in range(self.rows):
            line = ""
            for col in range(self.cols):
                if (row, col) in highlight:
                    line += "R"
                elif (row, col) in self.walls:
                    line += "#"
                else:
                    line += "."
            lines.append(line)
        return "\n".join(lines)
