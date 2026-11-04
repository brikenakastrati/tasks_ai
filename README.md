# AI Tasks

Assignments for the Artificial Intelligence course (University of Prishtina), written in Python 3 using only the standard library.

## Tasks_1 – Uninformed Search Techniques

| Problem | Algorithm | File | Result |
|---|---|---|---|
| Social Golfers (32 golfers, 8 groups of 4) | DFS with backtracking | `social_golfers.py` | 9 valid weeks (upper bound 10) |
| Sudoku (easy, medium, hard) | BFS with backtracking | `sudoku.py` | all three levels solved |
| Latin Square (n × n) | IDDFS with backtracking | `latin_square.py` | n = 5 gives the example square |
| Search Trees: 8-Puzzle, Missionaries and Cannibals, Rotating Workforce Scheduling | tree construction | `search_trees/` | PNG pictures |

Each script starts with a docstring describing the model: variables, domain, constraints, objective function and landscape.

### Running

```bash
cd Tasks_1
python social_golfers.py
python sudoku.py
python latin_square.py 5     # any n
```

### Notes

- **Social Golfers:** golfers are numbered 0–31, and each week is an XOR pattern `{0, a, b, a^b}`. The DFS picks patterns that share no number, so no pair of golfers meets twice. It finds 9 weeks and then checks every combination to confirm a 10th is not possible this way. The known maximum is 10 weeks (Aguado, 2004), but that schedule does not follow this structure.
- **Sudoku:** cells with a single possible digit are filled in automatically, and the search branches on the cell with the fewest options. Grids that reach a contradiction are dropped from the queue.
- **Latin Square:** the first row is fixed to 1..n and the value `(col − row) mod n + 1` is tried first in each cell.
- **Search trees:** the blue node is the initial state and green nodes are goal states.
