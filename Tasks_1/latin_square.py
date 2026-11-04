"""
Latin Square - IDDFS with backtracking

Model:
    variables:   the n*n cells of the grid
    domain:      {1, ..., n}
    constraints: every number appears once in each row and each column
    objective:   f = sum over rows and columns of (n - distinct numbers),
                 the grid is a Latin square when f = 0
    landscape:   n^(n*n) grids in total, (n!)^n when every row is a permutation

Each step of the search fills one cell, so every solution is at depth n*n.
Instead of raising the depth limit by one (and repeating the shallow levels
for nothing), a node is cut when depth + empty cells is over the limit and
the next limit becomes the smallest value that was cut.

The first row is fixed to 1..n: any Latin square can be relabeled so that
it starts like that. In every cell the value (col - row) mod n + 1 is tried
first, which gives the shifted square from the example without backtracking.
Rows and columns keep their used numbers as bitmasks.
"""
import math
import sys


def objective(grid):
    n = len(grid)
    columns = [list(col) for col in zip(*grid)]
    return sum(n - len(set(line)) for line in grid + columns)


class LatinSquare:
    def __init__(self, n):
        self.n = n
        self.grid = [[0] * n for _ in range(n)]
        self.rows = [0] * n
        self.cols = [0] * n
        for col in range(n):
            self.put(0, col, col + 1)

    def put(self, row, col, value):
        self.grid[row][col] = value
        self.rows[row] ^= 1 << value
        self.cols[col] ^= 1 << value

    def remove(self, row, col, value):
        self.grid[row][col] = 0
        self.rows[row] ^= 1 << value
        self.cols[col] ^= 1 << value

    def depth_limited(self, cell, limit):
        """Returns True when solved, otherwise the smallest cut value (None = no solution)."""
        if cell == self.n * self.n:
            return True
        # cell is the depth and n*n - cell the empty cells left
        if self.n * self.n > limit:
            return self.n * self.n

        row, col = divmod(cell, self.n)
        smallest_cut = None
        # try the shifted value first: (col - row) mod n + 1 fits every cell,
        # so the search goes straight down without backtracking
        first = (col - row) % self.n + 1
        order = [first] + [v for v in range(1, self.n + 1) if v != first]
        for value in order:
            if (self.rows[row] | self.cols[col]) >> value & 1:
                continue
            self.put(row, col, value)
            result = self.depth_limited(cell + 1, limit)
            if result is True:
                return True
            self.remove(row, col, value)
            if result is not None and (smallest_cut is None or result < smallest_cut):
                smallest_cut = result
        return smallest_cut

    def iddfs(self):
        limit = 0
        iterations = 0
        while True:
            iterations += 1
            result = self.depth_limited(self.n, limit)
            if result is True:
                return self.grid, iterations
            if result is None:
                return None, iterations
            limit = max(limit + 1, result)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"landscape: n^(n*n) = 10^{n * n * math.log10(n):.1f}, "
          f"(n!)^n = 10^{n * math.log10(math.factorial(n)):.1f}")

    grid, iterations = LatinSquare(n).iddfs()
    for row in grid:
        print(" ".join(map(str, row)))
    print(f"f = {objective(grid)}, iterations: {iterations}")