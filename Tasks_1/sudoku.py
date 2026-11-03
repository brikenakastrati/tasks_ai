"""
Sudoku solver - BFS with backtracking

Model:
    variables:   the 81 cells of the grid
    domain:      {1, ..., 9}
    constraints: no digit repeats in a row, a column or a 3x3 box
    objective:   f = conflicting pairs + empty cells, solved when f = 0
    landscape:   9^(empty cells), or the product of the candidate counts
                 of the empty cells once the clues are taken into account

BFS keeps partial grids in a queue. Before a grid is queued, every cell
that has only one possible digit is filled in. The search then branches on
the cell with the fewest candidates, and grids that reach a contradiction
are thrown away (backtracking) instead of being queued.

Used digits in every row, column and box are stored as 9-bit masks.
"""
import math
from collections import deque

PUZZLES = {
    "easy": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "medium": "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
    "hard": "800000000003600000070090200050007000000045700000100030001000068008500010090000400",
}


def box(cell):
    return (cell // 27) * 3 + (cell % 9) // 3


class Grid:
    def __init__(self, cells):
        self.cells = list(cells)
        self.rows = [0] * 9
        self.cols = [0] * 9
        self.boxes = [0] * 9
        for cell, digit in enumerate(self.cells):
            if digit:
                self.set_bits(cell, digit)

    def copy(self):
        clone = Grid.__new__(Grid)
        clone.cells = self.cells[:]
        clone.rows, clone.cols, clone.boxes = self.rows[:], self.cols[:], self.boxes[:]
        return clone

    def set_bits(self, cell, digit):
        bit = 1 << (digit - 1)
        self.rows[cell // 9] |= bit
        self.cols[cell % 9] |= bit
        self.boxes[box(cell)] |= bit

    def place(self, cell, digit):
        self.cells[cell] = digit
        self.set_bits(cell, digit)

    def candidates(self, cell):
        used = self.rows[cell // 9] | self.cols[cell % 9] | self.boxes[box(cell)]
        return [d for d in range(1, 10) if not used >> (d - 1) & 1]

    def propagate(self):
        # fill cells with a single candidate until nothing changes
        changed = True
        while changed:
            changed = False
            for cell in range(81):
                if self.cells[cell] == 0:
                    options = self.candidates(cell)
                    if not options:
                        return False
                    if len(options) == 1:
                        self.place(cell, options[0])
                        changed = True
        return True

    def solved(self):
        return 0 not in self.cells


def objective(cells):
    conflicts = 0
    for i in range(81):
        for j in range(i + 1, 81):
            same_unit = i // 9 == j // 9 or i % 9 == j % 9 or box(i) == box(j)
            if same_unit and cells[i] and cells[i] == cells[j]:
                conflicts += 1
    return conflicts + cells.count(0)


def bfs(puzzle):
    start = Grid(puzzle)
    if not start.propagate():
        return None, 0

    queue = deque([start])
    expanded = 0
    while queue:
        grid = queue.popleft()
        if grid.solved():
            return grid.cells, expanded
        expanded += 1

        empty = [c for c in range(81) if grid.cells[c] == 0]
        cell = min(empty, key=lambda c: len(grid.candidates(c)))
        for digit in grid.candidates(cell):
            child = grid.copy()
            child.place(cell, digit)
            if child.propagate():
                queue.append(child)
    return None, expanded


if __name__ == "__main__":
    for level, text in PUZZLES.items():
        puzzle = [int(ch) for ch in text]
        grid = Grid(puzzle)
        empty = [c for c in range(81) if puzzle[c] == 0]
        reduced = math.prod(len(grid.candidates(c)) for c in empty)

        solution, expanded = bfs(puzzle)
        print(f"=== {level} ===")
        print(f"landscape: 9^{len(empty)} = 10^{len(empty) * math.log10(9):.1f}, "
              f"with candidates only 10^{math.log10(reduced):.1f}")
        for row in range(9):
            print(" ".join(map(str, solution[row * 9:row * 9 + 9])))
        print(f"f = {objective(solution)}, expanded nodes: {expanded}\n")