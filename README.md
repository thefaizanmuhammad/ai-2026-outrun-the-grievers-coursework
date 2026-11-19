# AI Mini Project 02 — Outrun the Grievers

AI coursework project implementing reflex agents, minimax, alpha-beta pruning, expectimax, and evaluation functions in a multi-agent maze environment. Thomas must collect every escape-code piece and reach the exit before sunset while avoiding moving Grievers.

**Course:** Artificial Intelligence, Fall 2026

**Technologies:** Python and the instructor-provided starter framework.

**Status:** Starter framework only; Q1–Q5 remain to be implemented and verified.

## Project structure

```text
ai-2026-outrun-the-grievers-coursework/
├── mazes/
│   ├── arena_big.maze
│   ├── arena_medium.maze
│   ├── arena_small.maze
│   ├── dead_end.maze
│   ├── duel.maze
│   └── open_glade.maze
├── .gitignore
├── display.py
├── game.py
├── gametrees.py
├── grievers.py
├── maze.py
├── multi_agents.py
├── play.py
├── README.md
└── util.py
```

All Q1–Q5 implementations belong in `multi_agents.py`. Do not split agents into additional modules or modify the other instructor-provided Python files.

## Team and task allocation

| Member | GitHub |
| --- | --- |
| Faizan Muhammad | [thefaizanmuhammad](https://github.com/thefaizanmuhammad) |
| Abdul Kareem | Username to be provided |

| Question | Topic | Marks | Assigned To |
| --- | --- | --- | --- |
| Q1 | Reflex Agent | 4 | Abdul Kareem |
| Q2 | Minimax Agent | 5 | Faizan Muhammad |
| Q3 | Alpha-Beta Pruning | 5 | Faizan Muhammad |
| Q4 | Expectimax Agent | 5 | Both (Shared) |
| Q5 | Better Evaluation Function | 6 | Abdul Kareem |

Splitting Q4 equally gives each member **12.5 out of 25 code marks**. Both members will complete the **5-mark report** together.

### Shared Q4 responsibilities

- **Faizan:** Maximizing-player logic, recursive search, agent switching, and depth management.
- **Abdul Kareem:** Griever chance-node logic, uniform floating-point averaging of successor values, and validation of the example game trees.
- **Both:** Integrate Q4, verify expected actions and generated-state counts, review each other's contributions, and understand the complete algorithm for the viva.

Only one member should edit the shared function at a time. Agree on a handoff and synchronize the latest changes before the other member continues.

## Development workflow

The planned branches are:

| Branch | Purpose |
| --- | --- |
| `main` | Stable, integrated project |
| `faizan` | Faizan's assigned work |
| `abdul-kareem` | Abdul Kareem's assigned work |

Both members must work on their respective branches and keep edits limited to assigned functions. Make focused commits and push completed, tested work to the appropriate branch, then open a pull request into `main` for the other member to review. Coordinate Q4 edits rather than modifying the same function simultaneously.

After each merge, synchronize with `main`. Resolve conflicts by preserving both members' assigned implementations, then rerun the relevant checks. Verify that the final `main` contains all five implementations. Branch creation and any branch protection changes remain pending explicit authorization.

### Implementation order

1. **Independent work:** Faizan implements Q2; Abdul Kareem implements Q1.
2. **Independent work:** Faizan implements Q3; Abdul Kareem implements Q5.
3. **Shared work:** Both implement and integrate Q4 through coordinated handoffs.
4. **Integration and validation:** Merge both members' work, test all five questions, compare with the instructor's expected results, and run the required performance experiments.
5. **Final submission:** Complete the report together, verify the final submitted Python file, and prepare the required ZIP.

## Running and testing

Run these verified starter commands from the repository root with Python 3:

```powershell
python play.py --list
python play.py -a beeline -l duel -q
python play.py -a beeline -l arena_medium -q
python gametrees.py
```

`--list` loads and lists all six supplied mazes. `beeline` is the instructor's worked example; `-q` runs without graphics. The baseline was checked with Python 3.14.3, and all eight Python files passed syntax compilation.

The starter `gametrees.py` currently reports **not implemented yet** for the search agents. This is expected and does not count as passing those checks. After implementation, verify the exact actions and generated-state counts in the manual's **Checking your work** table. Use the prescribed `-n 10 -q` experiments for the report and the specified 20-game `dead_end` comparison.

## Submission requirements

Submit one ZIP on GCR containing only:

- `multi_agents.py`
- `report.pdf` — a 2–4 page report based on actual experimental results, completed by both members.

The manual specifies **`<group_number>_project1.zip`**, despite this being Project 2. Clarify this discrepancy with the instructor before final submission. Only one member needs to submit. Run the manual's final checks using exactly the Python file being submitted.

**Deadline: November 29, 2026, 11:59 PM.**
