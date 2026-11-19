"""
play.py
-------
Play the multi-agent Maze Runner: Thomas against the Grievers.

Examples
    python play.py                                    # you play (arrow keys) on arena_small
    python play.py -a beeline                         # the worked example
    python play.py -a reflex -l arena_small -n 10 -q  # 10 games, numbers only
    python play.py -a minimax -l duel -d 3
    python play.py -a alphabeta -l arena_medium -d 2
    python play.py -a expectimax -l dead_end -d 3 -n 10 -q
    python play.py -a expectimax -e better -l arena_medium
    python play.py -a minimax -l duel -d 2 --first-move   # one decision, then stop
    python play.py -l arena_small -g hunter           # Grievers that chase you
    python play.py -a reflex -t                       # text output, no window
    python play.py --list                             # list all mazes

Run 'python play.py -h' for all options.
"""

import argparse
import random
import sys
import time

import maze as mazeModule
from game import Agent, Game, GameState
from grievers import GRIEVERS

sys.setrecursionlimit(20000)

AGENTS = {
    'keyboard': 'you, with the arrow keys (or WASD; space = Stop)',
    'beeline': 'BeelineAgent: the worked example (Q0)',
    'reflex': 'ReflexAgent (Q1)',
    'minimax': 'MinimaxAgent (Q2)',
    'alphabeta': 'AlphaBetaAgent (Q3)',
    'expectimax': 'ExpectimaxAgent (Q4)',
}
SEARCH_AGENTS = ('minimax', 'alphabeta', 'expectimax')
EVAL_FUNCTIONS = {'score': 'scoreEvaluationFunction', 'better': 'betterEvaluationFunction'}


def grieverCount(maze):
    n = len(maze.grieverStarts)
    return "%d Griever%s" % (n, '' if n == 1 else 's')


class KeyboardAgent(Agent):
    def __init__(self, display):
        Agent.__init__(self, 0)
        self.display = display

    def getAction(self, gameState):
        return self.display.waitForKey(gameState.getLegalActions(0))


def makeRunner(name, depth, evalName, display=None):
    import multi_agents
    if name == 'keyboard':
        return KeyboardAgent(display)
    if name == 'beeline':
        return multi_agents.BeelineAgent(0)
    if name == 'reflex':
        return multi_agents.ReflexAgent(0)
    cls = {'minimax': multi_agents.MinimaxAgent, 'alphabeta': multi_agents.AlphaBetaAgent,
           'expectimax': multi_agents.ExpectimaxAgent}[name]
    return cls(evalFn=EVAL_FUNCTIONS[evalName], depth=str(depth))


def makeGrievers(maze, kind, seed):
    cls = GRIEVERS[kind]
    return [cls(i, seed=None if seed is None else seed * 1000 + i)
            for i in range(1, 1 + len(maze.grieverStarts))]


class TimedAgent(Agent):
    """Wraps Thomas's agent to measure how long its decisions take."""

    def __init__(self, agent):
        Agent.__init__(self, 0)
        self.agent = agent
        self.moveTimes = []

    def registerInitialState(self, state):
        self.agent.registerInitialState(state)

    def getAction(self, state):
        start = time.perf_counter()
        action = self.agent.getAction(state)
        self.moveTimes.append(time.perf_counter() - start)
        return action


def playGames(maze, runnerName, depth=2, evalName='score', grieverKind='random', numGames=1,
              seed=0, display=None, verbose=True):
    """Plays numGames games. Returns a list of dicts, one per game."""
    results = []
    for g in range(numGames):
        gameSeed = None if seed is None else seed + g
        random.seed(gameSeed)
        runner = TimedAgent(makeRunner(runnerName, depth, evalName, display))
        agents = [runner] + makeGrievers(maze, grieverKind, gameSeed)
        GameState.generated = 0
        state, moves = Game(maze, agents, display).run()
        res = {'win': state.isWin(), 'score': state.getScore(), 'moves': moves,
               'reason': state.reason, 'generated': GameState.generated,
               'time': sum(runner.moveTimes),
               'maxMoveTime': max(runner.moveTimes) if runner.moveTimes else 0.0}
        results.append(res)
        if verbose:
            print("Game %2d (seed %s): %-8s score %5d  after %3d moves  (%s)"
                  % (g + 1, gameSeed, 'ESCAPED' if res['win'] else 'LOST', res['score'],
                     moves, res['reason']))
    return results


def summarize(results):
    n = len(results)
    wins = sum(r['win'] for r in results)
    avg = sum(r['score'] for r in results) / float(n)
    moves = sum(r['moves'] for r in results)
    lines = ["Escaped:        %d/%d (%.0f%%)" % (wins, n, 100.0 * wins / n),
             "Average score:  %.1f" % avg,
             "Scores:         %s" % ', '.join(str(r['score']) for r in results),
             "States generated per move: %.0f" % (sum(r['generated'] for r in results) / max(1, moves)),
             "Time per move:  %.3f s (slowest %.3f s)"
             % (sum(r['time'] for r in results) / max(1, moves),
                max(r['maxMoveTime'] for r in results))]
    return '\n'.join(lines)


def firstMove(maze, runnerName, depth, evalName):
    """Runs one decision from the start state and reports it."""
    agent = makeRunner(runnerName, depth, evalName)
    state = GameState(maze)
    agent.registerInitialState(state)
    GameState.generated = 0
    start = time.perf_counter()
    action = agent.getAction(state)
    elapsed = time.perf_counter() - start
    print("Maze:             %s (%s)" % (maze.title, grieverCount(maze)))
    print("Agent:            %s, depth %s, evaluation %s" % (runnerName, depth, evalName))
    print("First action:     %s" % action)
    print("States generated: %d" % GameState.generated)
    print("Time:             %.3f s" % elapsed)


def main(argv=None):
    parser = argparse.ArgumentParser(description="The Maze Runner: adversarial search.")
    parser.add_argument('-l', '--maze', default='arena_small', help="maze name or path (default: arena_small)")
    parser.add_argument('-a', '--agent', default='keyboard', choices=list(AGENTS),
                        help="Thomas's agent (default: keyboard)")
    parser.add_argument('-d', '--depth', type=int, default=2, help="search depth in plies (default: 2)")
    parser.add_argument('-e', '--eval', default='score', choices=list(EVAL_FUNCTIONS),
                        help="evaluation function for the search agents (default: score)")
    parser.add_argument('-g', '--grievers', default='random', choices=list(GRIEVERS),
                        help="Griever behaviour (default: random)")
    parser.add_argument('-n', '--num-games', type=int, default=1, help="number of games")
    parser.add_argument('-s', '--seed', type=int, default=0,
                        help="random seed (default 0); game i uses seed + i")
    parser.add_argument('-t', '--text', action='store_true', help="text output instead of a window")
    parser.add_argument('-q', '--quiet', action='store_true', help="no display, only results")
    parser.add_argument('-z', '--zoom', type=float, default=1.0, help="zoom the window")
    parser.add_argument('-f', '--frame-time', type=float, default=None,
                        help="seconds to pause after each ply (default: 0.08 in a window, 0 in text)")
    parser.add_argument('--first-move', action='store_true',
                        help="make one decision from the start state, print it and stop")
    parser.add_argument('--list', action='store_true', help="list available mazes and exit")
    args = parser.parse_args(argv)

    if args.list:
        for name in mazeModule.availableMazes():
            m = mazeModule.loadMaze(name)
            print("%-14s %3dx%-3d %-11s %d code pieces, sunset %3d   %s"
                  % (name, m.height, m.width, grieverCount(m) + ',', len(m.keys), m.sunset, m.title))
        return

    maze = mazeModule.loadMaze(args.maze)
    if args.first_move:
        if args.agent == 'keyboard':
            parser.error("--first-move needs an agent other than keyboard (use -a)")
        firstMove(maze, args.agent, args.depth, args.eval)
        return

    if args.agent == 'keyboard' and (args.quiet or args.text):
        parser.error("the keyboard agent needs the window (drop -q / -t, or choose an agent with -a)")

    display = None
    from display import NullDisplay, TextDisplay
    if args.quiet:
        display = NullDisplay()
    elif args.text:
        display = TextDisplay(args.frame_time or 0.0)
    else:
        try:
            from display import TkDisplay
            display = TkDisplay(args.zoom, 0.08 if args.frame_time is None else args.frame_time)
        except Exception as e:   # no tkinter / no display (e.g. over SSH)
            if args.agent == 'keyboard':
                print("Could not open a window (%s). Choose an agent with -a and use -t." % e)
                return
            print("(could not open a window: %s; showing text instead)" % e)
            display = TextDisplay(args.frame_time or 0.0)

    from display import WindowClosed
    name = AGENTS[args.agent]
    if args.agent in SEARCH_AGENTS:
        name += ", depth %d, evaluation: %s" % (args.depth, args.eval)
    print("Maze:    %s (%s, %s)" % (maze.title, grieverCount(maze), args.grievers))
    print("Thomas:  %s" % name)
    try:
        results = playGames(maze, args.agent, args.depth, args.eval, args.grievers,
                            args.num_games, args.seed, display)
    except WindowClosed:
        print("Window closed.")
        return
    print(summarize(results))
    if hasattr(display, 'waitForClose'):
        display.waitForClose()


if __name__ == '__main__':
    import util
    try:
        main()
    except util.NotImplementedYet as e:
        print("ERROR - %s" % e)
