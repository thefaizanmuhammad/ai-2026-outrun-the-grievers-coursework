"""
game.py
-------
The rules of the game and the GameState your agents reason about.

You do NOT need to edit this file, but read the GameState methods carefully:
they are the only way your agents see and simulate the world.

The game
    Thomas (agent 0) has to pick up every piece of the escape code (K) and
    then step onto the Griever Hole (E). The Grievers (agents 1, 2, ...) are
    hunting him. Agents move one at a time: Thomas, then Griever 1, then
    Griever 2, ..., then Thomas again. One such round is called a PLY.

    Thomas may move North, South, East, West or Stop. A Griever must move if
    it can: it never chooses 'Stop'.

Scoring (the score is from Thomas's point of view)
    every move Thomas makes (including Stop)        -1
    picking up a code piece                        +50
    escaping through the Griever Hole             +500   -> win
    sharing a cell with a Griever                 -500   -> lose
    the walls close (Thomas runs out of moves)    -500   -> lose
"""

import maze as mazeModule
from maze import STOP

STEP_SCORE = -1
KEY_SCORE = 50
ESCAPE_SCORE = 500
CAUGHT_SCORE = -500
SUNSET_SCORE = -500

RUNNER_INDEX = 0


class IllegalAction(Exception):
    pass


class GameState:
    """
    A snapshot of the game. A GameState is never changed in place:
    generateSuccessor returns a NEW state.

    Calling generateSuccessor counts as GENERATING a state. 
    """

    # Number of generateSuccessor calls so far .
    generated = 0

    def __init__(self, maze):
        """The initial state of a game on 'maze' (a maze.Maze)."""
        self.maze = maze
        self.runnerPosition = maze.start
        self.grieverPositions = tuple(maze.grieverStarts)
        self.keys = frozenset(maze.keys)
        self.score = 0
        self.timeLeft = maze.sunset
        self.result = None       # None while playing, then 'win' or 'lose'
        self.reason = None       # why the game ended

    # ------------------------------------------------------------------
    # Asking about the state
    # ------------------------------------------------------------------
    def getNumAgents(self):
        """Thomas plus the number of Grievers."""
        return 1 + len(self.grieverPositions)

    def getRunnerPosition(self):
        """Thomas's (row, col)."""
        return self.runnerPosition

    def getGrieverPositions(self):
        """A tuple with the (row, col) of each Griever: Griever i is at index i - 1."""
        return self.grieverPositions

    def getGrieverPosition(self, agentIndex):
        """The (row, col) of Griever 'agentIndex' (1, 2, ...)."""
        if agentIndex < 1 or agentIndex > len(self.grieverPositions):
            raise ValueError("there is no Griever with index %s" % agentIndex)
        return self.grieverPositions[agentIndex - 1]

    def getKeys(self):
        """A frozenset with the positions of the code pieces still in the maze."""
        return self.keys

    def getNumKeys(self):
        return len(self.keys)

    def getExit(self):
        """The (row, col) of the Griever Hole."""
        return self.maze.exit

    def isExitOpen(self):
        """True once every code piece has been collected."""
        return not self.keys

    def getScore(self):
        return self.score

    def getTimeLeft(self):
        """How many more moves Thomas can make before the walls close."""
        return self.timeLeft

    def getMaze(self):
        """The maze.Maze (walls, size, ...). It never changes during a game."""
        return self.maze

    def hasWall(self, pos):
        return self.maze.isWall(pos)

    def mazeDistance(self, pos1, pos2):
        """
        The true number of steps between two cells, going around walls (but
        ignoring Grievers). Cached, so it is cheap after the first call from
        a given cell. Use it in your evaluation functions.
        """
        return self.maze.distance(pos1, pos2)

    def isWin(self):
        return self.result == 'win'

    def isLose(self):
        return self.result == 'lose'

    def isOver(self):
        return self.result is not None

    # ------------------------------------------------------------------
    # Moves
    # ------------------------------------------------------------------
    def getLegalActions(self, agentIndex=RUNNER_INDEX):
        """
        The legal actions of agent 'agentIndex', always in the order
        North, South, East, West (then Stop for Thomas). There are no legal
        actions once the game is over.
        """
        if self.result is not None:
            return []
        if agentIndex == RUNNER_INDEX:
            pos = self.runnerPosition
            return [a for a, _ in self.maze.neighbors(pos)] + [STOP]
        pos = self.getGrieverPosition(agentIndex)
        actions = [a for a, _ in self.maze.neighbors(pos)]
        return actions or [STOP]   # a walled-in Griever can only wait

    def generateSuccessor(self, agentIndex, action):
        """The state after agent 'agentIndex' takes 'action'."""
        if self.result is not None:
            raise IllegalAction("the game is already over: cannot generate a successor "
                                "of a state where isWin() or isLose() is True")
        if action not in self.getLegalActions(agentIndex):
            raise IllegalAction("%r is not a legal action for agent %d in this state"
                                % (action, agentIndex))
        GameState.generated += 1
        s = self._copy()
        dr, dc = mazeModule.DELTA[action]
        if agentIndex == RUNNER_INDEX:
            r, c = s.runnerPosition
            pos = (r + dr, c + dc)
            s.runnerPosition = pos
            s.score += STEP_SCORE
            s.timeLeft -= 1
            if pos in s.keys:
                s.keys = s.keys - {pos}
                s.score += KEY_SCORE
            if pos in s.grieverPositions:
                s._end('lose', CAUGHT_SCORE, 'caught by a Griever')
            elif pos == s.maze.exit and not s.keys:
                s._end('win', ESCAPE_SCORE, 'escaped through the Griever Hole')
            elif s.timeLeft <= 0:
                s._end('lose', SUNSET_SCORE, 'the walls closed')
        else:
            positions = list(s.grieverPositions)
            r, c = positions[agentIndex - 1]
            positions[agentIndex - 1] = (r + dr, c + dc)
            s.grieverPositions = tuple(positions)
            if s.runnerPosition == positions[agentIndex - 1]:
                s._end('lose', CAUGHT_SCORE, 'caught by a Griever')
        return s

    def generateRunnerSuccessor(self, action):
        """Shorthand for generateSuccessor(0, action)."""
        return self.generateSuccessor(RUNNER_INDEX, action)

    # ------------------------------------------------------------------
    def _copy(self):
        s = GameState.__new__(GameState)
        s.__dict__.update(self.__dict__)
        return s

    def _end(self, result, bonus, reason):
        self.result = result
        self.score += bonus
        self.reason = reason

    def __eq__(self, other):
        return (isinstance(other, GameState) and self._key() == other._key())

    def __hash__(self):
        return hash(self._key())

    def _key(self):
        return (self.runnerPosition, self.grieverPositions, self.keys, self.score,
                self.timeLeft, self.result)

    def __str__(self):
        grid = [list(row) for row in self.maze.grid]
        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch in (mazeModule.START, mazeModule.GRIEVER, mazeModule.KEY, '.'):
                    grid[r][c] = ' '
        for (r, c) in self.keys:
            grid[r][c] = mazeModule.KEY
        er, ec = self.maze.exit
        grid[er][ec] = mazeModule.EXIT if self.keys else 'O'
        r, c = self.runnerPosition
        grid[r][c] = 'T'
        for i, (r, c) in enumerate(self.grieverPositions):
            grid[r][c] = 'X' if (r, c) == self.runnerPosition else str(i + 1)[-1]
        lines = [''.join(row) for row in grid]
        lines.append("Score: %d   Keys left: %d   Moves left: %d%s"
                     % (self.score, len(self.keys), self.timeLeft,
                        ("   " + self.reason.upper()) if self.reason else ''))
        return '\n'.join(lines)


class Agent:
    """
    An agent must define getAction(gameState), which returns one of
    gameState.getLegalActions(self.index).
    """

    def __init__(self, index=0):
        self.index = index

    def getAction(self, gameState):
        raise NotImplementedError

    def registerInitialState(self, gameState):
        """Called once at the start of each game. Override if you need it."""
        pass


class Game:
    """Plays one game: Thomas, then each Griever in turn, until it is over."""

    def __init__(self, maze, agents, display=None):
        self.maze = maze
        self.agents = agents
        self.display = display
        if len(agents) != 1 + len(maze.grieverStarts):
            raise ValueError("maze %s needs %d agents but got %d"
                             % (maze.name, 1 + len(maze.grieverStarts), len(agents)))

    def run(self):
        state = GameState(self.maze)
        for agent in self.agents:
            agent.registerInitialState(state)
        if self.display:
            self.display.initialize(state)
        moves = 0
        while not state.isOver():
            for i, agent in enumerate(self.agents):
                action = agent.getAction(state)
                state = state.generateSuccessor(i, action)
                if i == RUNNER_INDEX:
                    moves += 1
                if self.display:
                    self.display.update(state, i)
                if state.isOver():
                    break
        if self.display:
            self.display.finish(state)
        return state, moves
