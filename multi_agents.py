"""
multi_agents.py
---------------
THE MAZE RUNNER - Mini Project 2: Adversarial Search

This is where you write Thomas's agents (Questions 1-5).

An agent has a method getAction(gameState) that returns one of
gameState.getLegalActions(0): 'North', 'South', 'East', 'West' or 'Stop'.
Read the GameState methods in game.py before you start.

  * Thomas is agent 0. The Grievers are agents 1, 2, ..., n-1, where
    n = gameState.getNumAgents(). They move in that order.
  * ONE PLY is one move by every agent: Thomas, then each Griever. A search
    of depth 2 looks two plies ahead (Thomas, every Griever, Thomas, every
    Griever) and then calls self.evaluationFunction on the states it reaches.
  * Stop expanding at the depth limit OR when the game is over
    (state.isWin() or state.isLose()), and evaluate that state with
    self.evaluationFunction.
  * Generate successors with state.generateSuccessor(agentIndex, action),
    taking the actions in the order getLegalActions returns them. 
  * If several actions at the root tie for the best value, return the FIRST
    of them.
"""

import random

import util
from game import Agent
from maze import STOP


# ----------------------------------------------------------------------
# Q0 (worked example, not graded): the beeline
# ----------------------------------------------------------------------
class BeelineAgent(Agent):
    """
    Not a real game-playing agent: Thomas runs straight for the nearest code
    piece (or for the exit once it is open) and ignores the Grievers
    completely. It shows you how to read a GameState and how to look one move
    ahead. Try it:
        python play.py -a beeline -l duel            (often escapes)
        python play.py -a beeline -l arena_medium    (runs into a Griever)
    """

    def getAction(self, gameState):
        pos = gameState.getRunnerPosition()
        targets = list(gameState.getKeys()) or [gameState.getExit()]
        best, bestDistance = STOP, float('inf')
        for action in gameState.getLegalActions(self.index):
            nextState = gameState.generateRunnerSuccessor(action)
            nextPos = nextState.getRunnerPosition()
            d = min(gameState.mazeDistance(nextPos, t) for t in targets)
            if d < bestDistance:
                best, bestDistance = action, d
        return best


# ----------------------------------------------------------------------
# Q1: Reflex agent
# ----------------------------------------------------------------------
class ReflexAgent(Agent):
    """
    A reflex agent looks at the moves available right now and picks the one
    that leads to the best-looking state, according to evaluationFunction.
    It does not look further ahead.

    getAction is written for you. Your job is evaluationFunction.
    """

    def getAction(self, gameState):
        legalMoves = gameState.getLegalActions()

        # Score every move and pick one of the best (ties broken at random).
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Q1: return a number that is HIGHER for better moves.

        The code below pulls some useful information out of the state that
        'action' leads to. Things worth thinking about: how far away is the
        next code piece (or the exit, once it is open)? How close are the
        Grievers? Is standing still ever a good idea?

        gameState.mazeDistance(pos1, pos2) gives the real distance through
        the maze, and util.manhattanDistance(pos1, pos2) the straight-line
        grid distance.
        """
        successorGameState = currentGameState.generateRunnerSuccessor(action)
        newPos = successorGameState.getRunnerPosition()
        newKeys = successorGameState.getKeys()
        newGrieverPositions = successorGameState.getGrieverPositions()

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()


def scoreEvaluationFunction(currentGameState):
    """
    The default evaluation function for the search agents: just the score.
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    Common parent of MinimaxAgent, AlphaBetaAgent and ExpectimaxAgent.
    You do not need to change anything here, but you will use
    self.depth and self.evaluationFunction.

    Do NOT change this class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        Agent.__init__(self, 0)     # Thomas is always agent 0
        self.evaluationFunction = globals()[evalFn] if isinstance(evalFn, str) else evalFn
        self.depth = int(depth)


# ----------------------------------------------------------------------
# Q2: Minimax
# ----------------------------------------------------------------------
class MinimaxAgent(MultiAgentSearchAgent):
    """
    Q2: Thomas maximises, every Griever minimises.
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from gameState, searching self.depth plies
        and evaluating the states at the bottom with self.evaluationFunction.

        Useful methods:
            gameState.getLegalActions(agentIndex)
            gameState.generateSuccessor(agentIndex, action)
            gameState.getNumAgents()
            gameState.isWin(), gameState.isLose()

        Hint: a recursive helper value(state, agentIndex, depth) is the most
        natural way to write this. Work out which agent moves next, and when
        the depth goes up.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


# ----------------------------------------------------------------------
# Q3: Alpha-beta pruning
# ----------------------------------------------------------------------
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Q3: minimax with alpha-beta pruning.
    """

    def getAction(self, gameState):
        """
        Returns the same action as MinimaxAgent, but skips the parts of the
        tree that cannot change the decision.

        Do NOT prune on equality: prune only when a value is STRICTLY better
        than the bound (v > beta at Thomas's levels, v < alpha at a
        Griever's levels). Remember to update alpha at the root as well.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


# ----------------------------------------------------------------------
# Q4: Expectimax
# ----------------------------------------------------------------------
class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Q4: Thomas maximises; every Griever is a chance node.
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action from gameState, searching self.depth
        plies. Model every Griever as choosing uniformly at random among its
        legal actions, so a Griever's value is the AVERAGE of its children.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


# ----------------------------------------------------------------------
# Q5: Evaluation function
# ----------------------------------------------------------------------
def betterEvaluationFunction(currentGameState):
    """
    Q5: a much better evaluation function for the search agents.

    Unlike the Q1 evaluation function, this one scores a STATE, not an
    action. Describe what it does here and in your report:

    DESCRIPTION: <write something here>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction
