"""
gametrees.py
------------
Small, explicit game trees with the same methods as a GameState, so you can
check your agents on examples you can work out by hand.

You do NOT need to edit this file. Run it to try your agents on the
examples from the handout:

    python gametrees.py

Build your own tree like this:

    from gametrees import GameTree
    tree = GameTree(numAgents=2,
                    edges=[('A', 'Left', 'B'), ('A', 'Right', 'C'),
                           ('B', 'Left', 'B1'), ('B', 'Right', 'B2'),
                           ('C', 'Left', 'C1'), ('C', 'Right', 'C2')],
                    scores={'B1': 3, 'B2': 5, 'C1': 1, 'C2': 9})
    agent = multi_agents.MinimaxAgent(depth='1')
    print(agent.getAction(tree.root()), tree.generated)

Each edge is (parentState, action, childState). The root is the parent of
the first edge, and agent 0 moves there; the agents then take turns level by
level (with numAgents=3: Thomas, Griever 1, Griever 2, Thomas, ...).
'scores' gives the value of the states where the search should stop. 'wins'
and 'loses' list states where the game is over (they also need a score).
tree.generated lists the states you generated, in order.
"""


class TreeError(Exception):
    """Raised when an agent uses a tree in a way that cannot be right."""


class GameTree:
    def __init__(self, numAgents, edges, scores, wins=(), loses=(), root=None):
        self.numAgents = numAgents
        self.children = {}
        for (parent, action, child) in edges:
            self.children.setdefault(parent, []).append((action, child))
        self.start = root if root is not None else edges[0][0]
        self.scores = dict(scores)
        self.wins = set(wins)
        self.loses = set(loses)
        # Which agent moves in each state.
        self.agentOf = {self.start: 0}
        stack = [self.start]
        while stack:
            s = stack.pop()
            for _, c in self.children.get(s, []):
                self.agentOf[c] = (self.agentOf[s] + 1) % numAgents
                stack.append(c)
        self.generated = []
        self.evaluated = []

    @classmethod
    def fromDict(cls, d):
        return cls(d['numAgents'], [tuple(e) for e in d['edges']], d['scores'],
                   d.get('wins', ()), d.get('loses', ()), d.get('root'))

    def root(self):
        self.generated = []
        self.evaluated = []
        return TreeGameState(self, self.start)


class TreeGameState:
    """A state in a GameTree. It has the GameState methods the search agents need."""

    def __init__(self, tree, name):
        self.tree = tree
        self.name = name

    def getNumAgents(self):
        return self.tree.numAgents

    def isWin(self):
        return self.name in self.tree.wins

    def isLose(self):
        return self.name in self.tree.loses

    def isOver(self):
        return self.isWin() or self.isLose()

    def _checkAgent(self, agentIndex):
        expected = self.tree.agentOf[self.name]
        if agentIndex != expected:
            raise TreeError("state %s is a move for agent %d, but you asked about agent %d "
                            "(check which agent moves next)" % (self.name, expected, agentIndex))

    def getLegalActions(self, agentIndex=0):
        if self.isOver():
            return []
        self._checkAgent(agentIndex)
        return [a for a, _ in self.tree.children.get(self.name, [])]

    def generateSuccessor(self, agentIndex, action):
        if self.isOver():
            raise TreeError("state %s is a terminal state (isWin/isLose): it has no successors"
                            % self.name)
        self._checkAgent(agentIndex)
        for a, child in self.tree.children.get(self.name, []):
            if a == action:
                self.tree.generated.append(child)
                return TreeGameState(self.tree, child)
        raise TreeError("%r is not a legal action in state %s" % (action, self.name))

    def generateRunnerSuccessor(self, action):
        return self.generateSuccessor(0, action)

    def getScore(self):
        if self.name not in self.tree.scores:
            raise TreeError("your agent evaluated state %s, where the search should not stop "
                            "(check your depth counting and your terminal test)" % self.name)
        self.tree.evaluated.append(self.name)
        return self.tree.scores[self.name]

    def __repr__(self):
        return 'TreeGameState(%s)' % self.name


# ----------------------------------------------------------------------
# The examples from the handout
# ----------------------------------------------------------------------
def handoutTree():
    """One Griever, depth 1: the tree from the 'Checking your work' section."""
    return GameTree(
        numAgents=2,
        edges=[('A', 'Left', 'B'), ('A', 'Middle', 'C'), ('A', 'Right', 'D'),
               ('B', 'Left', 'B1'), ('B', 'Middle', 'B2'), ('B', 'Right', 'B3'),
               ('C', 'Left', 'C1'), ('C', 'Middle', 'C2'), ('C', 'Right', 'C3'),
               ('D', 'Left', 'D1'), ('D', 'Middle', 'D2'), ('D', 'Right', 'D3')],
        scores={'B1': 3, 'B2': 12, 'B3': 8, 'C1': 2, 'C2': 4, 'C3': 6,
                'D1': 14, 'D2': 2, 'D3': 15})


def twoGrieversTree():
    """Two Grievers, depth 1: Thomas, then Griever 1, then Griever 2."""
    return GameTree(
        numAgents=3,
        edges=[('A', 'Left', 'B'), ('A', 'Right', 'C'),
               ('B', 'Left', 'B1'), ('B', 'Right', 'B2'),
               ('C', 'Left', 'C1'), ('C', 'Right', 'C2'),
               ('B1', 'Left', 'B1a'), ('B1', 'Right', 'B1b'),
               ('B2', 'Left', 'B2a'), ('B2', 'Right', 'B2b'),
               ('C1', 'Left', 'C1a'), ('C1', 'Right', 'C1b'),
               ('C2', 'Left', 'C2a'), ('C2', 'Right', 'C2b')],
        scores={'B1a': 6, 'B1b': 8, 'B2a': 4, 'B2b': 9,
                'C1a': 5, 'C1b': 7, 'C2a': 2, 'C2b': 30})


EXAMPLES = [
    # (title, tree builder, agent, depth, expected action, expected generated states)
    ('handout tree', handoutTree, 'MinimaxAgent', 1, 'Left',
     ['B', 'B1', 'B2', 'B3', 'C', 'C1', 'C2', 'C3', 'D', 'D1', 'D2', 'D3']),
    ('handout tree', handoutTree, 'AlphaBetaAgent', 1, 'Left',
     ['B', 'B1', 'B2', 'B3', 'C', 'C1', 'D', 'D1', 'D2']),
    ('handout tree', handoutTree, 'ExpectimaxAgent', 1, 'Right',
     ['B', 'B1', 'B2', 'B3', 'C', 'C1', 'C2', 'C3', 'D', 'D1', 'D2', 'D3']),
    ('two Grievers', twoGrieversTree, 'MinimaxAgent', 1, 'Left',
     ['B', 'B1', 'B1a', 'B1b', 'B2', 'B2a', 'B2b', 'C', 'C1', 'C1a', 'C1b', 'C2', 'C2a', 'C2b']),
    ('two Grievers', twoGrieversTree, 'AlphaBetaAgent', 1, 'Left',
     ['B', 'B1', 'B1a', 'B1b', 'B2', 'B2a', 'B2b', 'C', 'C1', 'C1a', 'C1b', 'C2', 'C2a']),
    ('two Grievers', twoGrieversTree, 'ExpectimaxAgent', 1, 'Right',
     ['B', 'B1', 'B1a', 'B1b', 'B2', 'B2a', 'B2b', 'C', 'C1', 'C1a', 'C1b', 'C2', 'C2a', 'C2b']),
]


def main():
    import multi_agents
    import util
    for title, build, agentName, depth, action, generated in EXAMPLES:
        tree = build()
        agent = getattr(multi_agents, agentName)(depth=str(depth))
        print("%s on the %s (depth %d)" % (agentName, title, depth))
        try:
            got = agent.getAction(tree.root())
        except util.NotImplementedYet as e:
            print("    not implemented yet (%s)\n" % e)
            continue
        except TreeError as e:
            print("    ERROR: %s\n" % e)
            continue
        sameStates = sorted(tree.generated) == sorted(generated)
        print("    your action:      %-8s expected: %s" % (got, action))
        print("    you generated:    %s" % ' '.join(tree.generated))
        print("    expected:         %s" % ' '.join(generated))
        if got == action and tree.generated == generated:
            print("    OK\n")
        elif got == action and sameStates:
            print("    OK (same states in a different order, which is fine)\n")
        else:
            print("    DIFFERENT\n")


if __name__ == '__main__':
    main()
