"""
display.py
----------
Text and graphical (Tkinter) displays for the multi-agent Maze Runner.

You do NOT need to edit or read this file.
"""

import time

import maze as mazeModule


class NullDisplay:
    def initialize(self, state):
        pass

    def update(self, state, agentIndex):
        pass

    def finish(self, state):
        pass


# ----------------------------------------------------------------------
# Text display
# ----------------------------------------------------------------------
class TextDisplay(NullDisplay):
    """
    Prints the maze after every ply.
        T  Thomas      1 2 3  Grievers      K  code piece
        E  the Griever Hole (closed)        O  the Griever Hole (open)
    """

    def __init__(self, frameTime=0.0, everyMove=True):
        self.frameTime = frameTime
        self.everyMove = everyMove

    def initialize(self, state):
        print(state.getMaze().title)
        print(state)

    def update(self, state, agentIndex):
        lastAgent = state.getNumAgents() - 1
        if self.everyMove and (agentIndex == lastAgent or state.isOver()):
            print()
            print(state)
            if self.frameTime:
                time.sleep(self.frameTime)

    def finish(self, state):
        if not self.everyMove:
            print(state)


# ----------------------------------------------------------------------
# Graphical display
# ----------------------------------------------------------------------
COLORS = {
    mazeModule.WALL: '#34403a',
    'floor': '#ece2c6',
    'exit_closed': '#9a8a63',
    'exit_open': '#e0a526',
    'start': '#3fa34d',
}
RUNNER = '#1d5f9e'
KEY_COLOR = '#2f7fd8'
GRIEVER_COLORS = ['#8e2c38', '#6b3f8e', '#a0522d', '#2e6b5e', '#7a7a2a']
BACKGROUND = '#1f2622'


class WindowClosed(Exception):
    pass


class TkDisplay(NullDisplay):
    def __init__(self, zoom=1.0, frameTime=0.08):
        import tkinter as tk
        self.tk = tk
        self.zoom = zoom
        self.frameTime = frameTime
        self.root = None
        self.closed = False
        self.keysDown = []      # for KeyboardAgent

    # -- window --------------------------------------------------------
    def _open(self, maze):
        tk = self.tk
        root = tk.Tk()
        root.title("Maze Runner - " + maze.title)
        root.configure(bg=BACKGROUND)
        self.root = root
        size = int(max(10, min(40, 900 / max(maze.width, maze.height * 1.4))) * self.zoom)
        self.size = size
        self.pad = 10
        self.canvas = tk.Canvas(root, width=maze.width * size + 2 * self.pad,
                                height=maze.height * size + 2 * self.pad,
                                bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(padx=6, pady=(6, 0))
        self.status = tk.Label(root, text='', justify='left', font=('Menlo', 12),
                               fg='#e8e8e8', bg=BACKGROUND, anchor='w')
        self.status.pack(fill='x', padx=12, pady=6)
        tk.Label(root, text="Arrow keys / WASD: move Thomas (keyboard agent)    Q / Esc: quit",
                 font=('Helvetica', 10), fg='#9aa59e', bg=BACKGROUND).pack(pady=(0, 6))
        root.bind('<Escape>', lambda e: self._close())
        root.bind('q', lambda e: self._close())
        root.bind('<KeyPress>', self._keyPress)
        root.protocol('WM_DELETE_WINDOW', self._close)
        self.mazeKey = maze.name

    def _close(self):
        self.closed = True
        try:
            self.root.destroy()
        except Exception:
            pass

    def _keyPress(self, event):
        self.keysDown.append(event.keysym)

    def pump(self):
        """Process window events. Raises WindowClosed if the window was closed."""
        if self.closed:
            raise WindowClosed()
        try:
            self.root.update()
        except self.tk.TclError:
            self.closed = True
        if self.closed:
            raise WindowClosed()

    def _box(self, pos, inset=0):
        r, c = pos
        s, p = self.size, self.pad
        return (p + c * s + inset, p + r * s + inset,
                p + (c + 1) * s - inset, p + (r + 1) * s - inset)

    # -- drawing ---------------------------------------------------------
    def initialize(self, state):
        maze = state.getMaze()
        if self.root is None or self.closed:
            self._open(maze)
        cv = self.canvas
        cv.delete('all')
        for r in range(maze.height):
            for c in range(maze.width):
                ch = maze.grid[r][c]
                color = COLORS[mazeModule.WALL] if ch == mazeModule.WALL else COLORS['floor']
                if ch == mazeModule.START:
                    color = COLORS['start']
                cv.create_rectangle(*self._box((r, c)), fill=color, outline=color)
                if ch == mazeModule.WALL and self.size >= 12 and (r * 7 + c * 3) % 5 == 0:
                    cv.create_oval(*self._box((r, c), self.size // 3), fill='#46594a', outline='')
        self.exitItem = cv.create_rectangle(*self._box(maze.exit), fill=COLORS['exit_closed'],
                                            outline=COLORS['exit_closed'])
        x0, y0, x1, y1 = self._box(maze.exit)
        font = ('Helvetica', max(7, int(self.size * 0.55)), 'bold')
        cv.create_text((x0 + x1) / 2, (y0 + y1) / 2, text='E', fill='white', font=font)
        self.keyItems = {}
        for pos in maze.keys:
            x0, y0, x1, y1 = self._box(pos, max(2, self.size // 5))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            self.keyItems[pos] = cv.create_polygon(cx, y0, x1, cy, cx, y1, x0, cy,
                                                   fill=KEY_COLOR, outline='white')
        self.runnerItem = cv.create_oval(*self._box(state.getRunnerPosition(), self.size // 6),
                                         fill=RUNNER, outline='white', width=2)
        self.grieverItems = []
        for i, pos in enumerate(state.getGrieverPositions()):
            self.grieverItems.append(self._drawGriever(pos, GRIEVER_COLORS[i % len(GRIEVER_COLORS)]))
        self._status(state)
        self.pump()
        time.sleep(min(0.4, 4 * (self.frameTime or 0)))

    def _grieverShape(self, pos):
        x0, y0, x1, y1 = self._box(pos, max(1, self.size // 8))
        w, h = x1 - x0, y1 - y0
        # A spiky blob: a body with legs underneath.
        pts = [x0 + w * 0.15, y0 + h * 0.35, x0 + w * 0.5, y0, x1 - w * 0.15, y0 + h * 0.35,
               x1, y1, x1 - w * 0.25, y1 - h * 0.2, x0 + w * 0.5, y1, x0 + w * 0.25, y1 - h * 0.2,
               x0, y1]
        return pts

    def _drawGriever(self, pos, color):
        body = self.canvas.create_polygon(*self._grieverShape(pos), fill=color, outline='#f0d0d0',
                                          width=1, smooth=False)
        x0, y0, x1, y1 = self._box(pos, max(1, self.size // 8))
        w = x1 - x0
        eye = self.canvas.create_oval(x0 + w * 0.4, y0 + w * 0.3, x0 + w * 0.6, y0 + w * 0.5,
                                      fill='#ffd84a', outline='')
        return (body, eye)

    def _status(self, state):
        text = "Score: %d    Code pieces left: %d    Moves before sunset: %d" % (
            state.getScore(), state.getNumKeys(), state.getTimeLeft())
        if state.isOver():
            text += "\n%s - %s" % ('ESCAPED!' if state.isWin() else 'LOST', state.reason)
        self.status.config(text=text)

    def update(self, state, agentIndex):
        cv = self.canvas
        if agentIndex == 0:
            cv.coords(self.runnerItem, *self._box(state.getRunnerPosition(), self.size // 6))
            for pos, item in list(self.keyItems.items()):
                if pos not in state.getKeys():
                    cv.delete(item)
                    del self.keyItems[pos]
            if state.isExitOpen():
                cv.itemconfig(self.exitItem, fill=COLORS['exit_open'], outline=COLORS['exit_open'])
        else:
            body, eye = self.grieverItems[agentIndex - 1]
            pos = state.getGrieverPosition(agentIndex)
            cv.coords(body, *self._grieverShape(pos))
            x0, y0, x1, y1 = self._box(pos, max(1, self.size // 8))
            w = x1 - x0
            cv.coords(eye, x0 + w * 0.4, y0 + w * 0.3, x0 + w * 0.6, y0 + w * 0.5)
        self._status(state)
        lastAgent = state.getNumAgents() - 1
        self.pump()
        if self.frameTime and (agentIndex == lastAgent or state.isOver()):
            time.sleep(self.frameTime)

    def finish(self, state):
        self._status(state)
        self.pump()
        time.sleep(0.6)

    def waitForClose(self):
        if self.closed:
            return
        self.status.config(text=self.status.cget('text') + "\n(press Q to close)")
        try:
            self.root.mainloop()
        except Exception:
            pass

    def waitForKey(self, legal):
        """Used by KeyboardAgent: block until a movement key is pressed."""
        mapping = {'Up': 'North', 'w': 'North', 'Down': 'South', 's': 'South',
                   'Right': 'East', 'd': 'East', 'Left': 'West', 'a': 'West',
                   'space': 'Stop'}
        self.keysDown = []
        while True:
            self.pump()
            while self.keysDown:
                action = mapping.get(self.keysDown.pop(0))
                if action in legal:
                    return action
            time.sleep(0.02)
