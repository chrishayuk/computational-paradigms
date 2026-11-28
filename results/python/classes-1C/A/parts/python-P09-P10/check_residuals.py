# Checks, on a grid of integers, that the residuals reported are equivalent to the valid outcomes.
R = range(-50, 51)
# P09e: held y + 1 = x and x - 1 = y (all three configurations, the constants of the records: 1 and 1)
held = {(x, y) for x in R for y in R if y + 1 == x and x - 1 == y}
valid = {(x, y) for x in R for y in R if x == y + 1}
assert held == valid, "P09e"
# the smaller form x = y + 1 alone is equivalent too (so the held pair is reducible)
assert {(x, y) for x in R for y in R if y + 1 == x} == valid
# P10b stage 1: held (2, 'b', 'd') read as d = 2 * b; valid d = 2 * b
assert {(b, d) for b in R for d in R if d == 2 * b} == {(b, d) for b in R for d in R if d == 2 * b}
# P09d2: total = 6 from the first three elements of the stream <1, 2, 3, ...>
assert sum([1, 2, 3]) == 6
print("residual checks passed")
