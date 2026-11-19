"""
grievers.py
-----------
The Griever agents. You do NOT need to edit this file.

    RandomGriever   picks one of its legal moves uniformly at random.
                    This is exactly the model ExpectimaxAgent assumes.
    HunterGriever   moves towards Thomas (along the maze) with probability
                    0.8, and makes a random legal move otherwise.

Each Griever has its own random number generator, seeded from the game seed,
so a game with a given --seed is always the same game.
"""

import random

import maze as mazeModule
from game import Agent


class GrieverAgent(Agent):
    def __init__(self, index, seed=None):
        Agent.__init__(self, index)
        self.rng = random.Random(seed)

    def getDistribution(self, state):
        """A list of (action, probability) pairs."""
        raise NotImplementedError

    def getAction(self, state):
        dist = self.getDistribution(state)
        x = self.rng.random()
        total = 0.0
        for action, p in dist:
            total += p
            if x < total:
                return action
        return dist[-1][0]


class RandomGriever(GrieverAgent):
    def getDistribution(self, state):
        actions = state.getLegalActions(self.index)
        return [(a, 1.0 / len(actions)) for a in actions]


class HunterGriever(GrieverAgent):
    def __init__(self, index, seed=None, chaseProbability=0.8):
        GrieverAgent.__init__(self, index, seed)
        self.chaseProbability = chaseProbability

    def getDistribution(self, state):
        actions = state.getLegalActions(self.index)
        pos = state.getGrieverPosition(self.index)
        target = state.getRunnerPosition()
        maze = state.getMaze()
        dists = []
        for a in actions:
            dr, dc = mazeModule.DELTA[a]
            dists.append(maze.distance((pos[0] + dr, pos[1] + dc), target))
        best = min(dists)
        bestActions = [a for a, d in zip(actions, dists) if d == best]
        dist = {a: (1 - self.chaseProbability) / len(actions) for a in actions}
        for a in bestActions:
            dist[a] += self.chaseProbability / len(bestActions)
        return [(a, dist[a]) for a in actions]


GRIEVERS = {'random': RandomGriever, 'hunter': HunterGriever}
