"""
Social Golfers Problem - DFS with backtracking

32 golfers play once a week in 8 groups of 4. For how many weeks can they
play so that no two golfers are in the same group more than once?

Model:
    variables:   one variable per week, the way the 32 golfers are split
                 into 8 groups of 4
    domain:      all splits of {0, ..., 31} into 8 groups of 4
    constraints: two golfers can share a group in at most one week
    objective:   f(S) = sum over all pairs of max(0, times_together - 1)
                 a schedule is valid when f(S) = 0, and we want as many
                 weeks as possible with f(S) = 0
    landscape:   32! / ((4!)^8 * 8!) ~ 2.4 * 10^19 splits for one week,
                 about 10^178 schedules for 10 weeks with week 1 fixed.
                 Upper bound: every week a golfer meets 3 new people and
                 there are 31 others, so at most floor(31 / 3) = 10 weeks.

Representation used by the search:
    Every golfer is a 5-bit number (0..31). A pattern is a set of 4 numbers
    {0, a, b, a ^ b}. XOR-ing all golfers with a pattern splits them into
    8 groups of 4, so one pattern is one week:
        golfer x plays with x ^ a, x ^ b and x ^ a ^ b
    Golfers x and y meet in that week exactly when x ^ y is in the pattern,
    so two weeks repeat a pair only if their patterns share a nonzero number.
    The search therefore picks patterns that do not overlap. There are only
    155 patterns, compared to 10^19 possible weeks.

DFS with backtracking:
    Each of the numbers 1..31 can be used by at most one week, and w weeks
    use 3w of them. The DFS always takes the smallest number that no week
    uses yet and either picks a week (pattern) containing it, or leaves it
    unused if the target still allows that. When no choice works, the last
    week is removed again and the next one is tried (backtracking).
    Going through the numbers in order means every set of weeks is built
    only once.
"""
import math
import time
from itertools import combinations

GOLFERS = 32
GROUP_SIZE = 4
GROUPS = GOLFERS // GROUP_SIZE


def objective(schedule):
    pair_count = {}
    for week in schedule:
        for group in week:
            for pair in combinations(sorted(group), 2):
                pair_count[pair] = pair_count.get(pair, 0) + 1
    return sum(count - 1 for count in pair_count.values())


def landscape(weeks):
    one_week = math.factorial(GOLFERS) // (math.factorial(GROUP_SIZE) ** GROUPS * math.factorial(GROUPS))
    return one_week, one_week ** (weeks - 1)


def all_patterns():
    patterns = set()
    for a, b in combinations(range(1, GOLFERS), 2):
        patterns.add(frozenset({a, b, a ^ b}))
    return sorted(patterns, key=sorted)


def week_from_pattern(pattern):
    week, placed = [], set()
    for golfer in range(GOLFERS):
        if golfer not in placed:
            group = sorted([golfer] + [golfer ^ value for value in pattern])
            placed.update(group)
            week.append(group)
    return week


class SocialGolfersDFS:
    def __init__(self):
        self.patterns = all_patterns()
        # patterns_with[v] = the patterns (weeks) that use the number v
        self.patterns_with = {v: [] for v in range(1, GOLFERS)}
        for pattern in self.patterns:
            mask = sum(1 << v for v in pattern)
            for v in pattern:
                self.patterns_with[v].append((pattern, mask))
        self.nodes = 0

    def solve(self, weeks):
        """Returns `weeks` non-overlapping patterns, or None if they do not exist."""
        first = frozenset({1, 2, 3})               # week 1: 0-3, 4-7, ..., 28-31
        used = sum(1 << v for v in first)
        unused_allowed = (GOLFERS - 1) - 3 * weeks
        if unused_allowed < 0:
            return None
        chosen = [first]
        if self.dfs(chosen, used, unused_allowed, weeks):
            return chosen
        return None

    def dfs(self, chosen, used, unused_allowed, weeks):
        self.nodes += 1
        if len(chosen) == weeks:
            return True

        # smallest number no week uses yet
        v = 1
        while used >> v & 1:
            v += 1

        for pattern, mask in self.patterns_with[v]:
            if mask & used == 0:
                chosen.append(pattern)
                if self.dfs(chosen, used | mask, unused_allowed, weeks):
                    return True
                chosen.pop()                         # backtrack

        # or no week will ever use v
        if unused_allowed > 0:
            return self.dfs(chosen, used | (1 << v), unused_allowed - 1, weeks)
        return False

    def max_weeks(self):
        best = None
        for weeks in range(1, (GOLFERS - 1) // (GROUP_SIZE - 1) + 1):
            found = self.solve(weeks)
            if found is None:
                return best, weeks
            best = found
        return best, None


if __name__ == "__main__":
    upper_bound = (GOLFERS - 1) // (GROUP_SIZE - 1)
    one_week, schedules = landscape(upper_bound)
    print(f"{GOLFERS} golfers, {GROUPS} groups of {GROUP_SIZE}")
    print(f"landscape: 10^{math.log10(one_week):.1f} possible weeks, "
          f"10^{math.log10(schedules):.1f} schedules for {upper_bound} weeks")
    print(f"upper bound: floor(31 / 3) = {upper_bound} weeks\n")

    start = time.time()
    solver = SocialGolfersDFS()
    patterns, failed_at = solver.max_weeks()
    schedule = [week_from_pattern(p) for p in patterns]

    for number, week in enumerate(schedule, 1):
        print(f"Week {number:2}: " + " | ".join(",".join(map(str, group)) for group in week))
    print(f"\nweeks: {len(schedule)}, f = {objective(schedule)}")
    if failed_at:
        print(f"DFS searched every pattern combination: {failed_at} weeks are not possible this way")
    print(f"nodes: {solver.nodes}, time: {time.time() - start:.3f}s")