"""
maze.py
-------
Loads maze layouts (mazes/*.maze) and answers questions about them.

You do NOT need to edit this file.

Layout characters
    %          wall (ivy-covered stone, impassable)
    ' ' or .   open corridor
    S          Thomas's starting cell (the Glade door)
    E          the exit (the Griever Hole). It only opens once every code
               piece has been collected.
    K          a piece of the escape code
    G          the starting cell of a Griever (one G per Griever)

Lines at the top of a file that start with '#' are comments. The first one is
the maze's title. A comment of the form '# sunset: 300' sets the number of
moves Thomas has before the walls close (default: 300).

Positions are (row, col) tuples. Row 0 is the top of the maze, so moving
North decreases the row and moving East increases the column.

Every move costs the same in this project, so there is no ivy and no
Griever territory: the Grievers themselves are the danger now.
"""

import os
import re
from collections import deque

WALL = '%'
START = 'S'
EXIT = 'E'
KEY = 'K'
GRIEVER = 'G'
OPEN = (' ', '.', START, EXIT, KEY, GRIEVER)

DEFAULT_SUNSET = 300

# The order in which moves are generated. Keep it fixed.
NORTH, SOUTH, EAST, WEST, STOP = 'North', 'South', 'East', 'West', 'Stop'
DIRECTIONS = [
    (NORTH, (-1, 0)),
    (SOUTH, (1, 0)),
    (EAST, (0, 1)),
    (WEST, (0, -1)),
]
DELTA = dict(DIRECTIONS)
DELTA[STOP] = (0, 0)
REVERSE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST, STOP: STOP}

MAZE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mazes')


class Maze:
    """The fixed part of the world: walls, the exit, and where everything starts."""

    def __init__(self, lines, name='maze', title=None, sunset=DEFAULT_SUNSET):
        width = max(len(line) for line in lines)
        # Pad ragged lines with walls so the grid is rectangular.
        self.grid = [line.ljust(width, WALL) for line in lines]
        self.height = len(self.grid)
        self.width = width
        self.name = name
        self.title = title or name
        self.sunset = sunset

        self.start = None
        self.exit = None
        self.keys = []
        self.grieverStarts = []
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                if ch not in OPEN and ch != WALL:
                    raise ValueError("Unknown character %r at %s in maze %s" % (ch, (r, c), name))
                if ch == START:
                    if self.start is not None:
                        raise ValueError("Maze %s has more than one S" % name)
                    self.start = (r, c)
                elif ch == EXIT:
                    if self.exit is not None:
                        raise ValueError("Maze %s has more than one E" % name)
                    self.exit = (r, c)
                elif ch == KEY:
                    self.keys.append((r, c))
                elif ch == GRIEVER:
                    self.grieverStarts.append((r, c))
        if self.start is None or self.exit is None:
            raise ValueError("Maze %s needs exactly one S and one E" % name)
        self._distances = {}

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def inBounds(self, pos):
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def terrain(self, pos):
        """The layout character at pos."""
        r, c = pos
        return self.grid[r][c]

    def isWall(self, pos):
        return (not self.inBounds(pos)) or self.terrain(pos) == WALL

    def neighbors(self, pos):
        """
        Legal moves from pos, as a list of (action, nextPosition) pairs,
        always in the order North, South, East, West. ('Stop' is not included.)
        """
        r, c = pos
        result = []
        for action, (dr, dc) in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if not self.isWall(nxt):
                result.append((action, nxt))
        return result

    def openCells(self):
        return [(r, c) for r in range(self.height) for c in range(self.width)
                if self.grid[r][c] != WALL]

    def distance(self, pos1, pos2):
        """
        The number of steps on the shortest path between pos1 and pos2
        (walls block, Grievers do not). Returns float('inf') if pos2 cannot be
        reached. One breadth-first search is run per source cell and the
        results are cached, so calling this many times is cheap.
        """
        table = self._distances.get(pos1)
        if table is None:
            table = {pos1: 0}
            frontier = deque([pos1])
            while frontier:
                cur = frontier.popleft()
                for _, nxt in self.neighbors(cur):
                    if nxt not in table:
                        table[nxt] = table[cur] + 1
                        frontier.append(nxt)
            self._distances[pos1] = table
        return table.get(pos2, float('inf'))

    def __str__(self):
        return '\n'.join(self.grid)


def mazePath(name):
    """Resolve a maze name ('arena_small') or a file path to a file path."""
    if os.path.exists(name):
        return name
    candidate = os.path.join(MAZE_DIR, name)
    if not candidate.endswith('.maze'):
        candidate += '.maze'
    if os.path.exists(candidate):
        return candidate
    raise FileNotFoundError("Could not find maze '%s' (looked in %s)" % (name, MAZE_DIR))


def parseMaze(text, name='maze'):
    raw = text.splitlines()
    comments = []
    while raw and raw[0].startswith('#'):
        comments.append(raw.pop(0).lstrip('#').strip())
    while raw and not raw[-1].strip():
        raw.pop()
    title = name
    sunset = DEFAULT_SUNSET
    for i, comment in enumerate(comments):
        match = re.match(r'sunset\s*:\s*(\d+)$', comment, re.IGNORECASE)
        if match:
            sunset = int(match.group(1))
        elif i == 0:
            title = comment
    return Maze(raw, name=name, title=title, sunset=sunset)


def loadMaze(name):
    path = mazePath(name)
    with open(path) as f:
        text = f.read()
    return parseMaze(text, os.path.splitext(os.path.basename(path))[0])


def availableMazes():
    return sorted(f[:-5] for f in os.listdir(MAZE_DIR) if f.endswith('.maze'))
