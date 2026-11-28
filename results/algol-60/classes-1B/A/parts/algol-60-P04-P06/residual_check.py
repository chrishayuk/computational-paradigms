"""Checks the residuals of this batch against the valid outcomes over a test range of
integers (the reasoning for values that are not integers is in the notes)."""
R = range(-1000, 1001)
# P05b stage 1: held x > 1 (c1 = 1 from P05b.constants); valid: every integer x > 1.
held = {x for x in R if x > 1}
valid = {x for x in R if x > 1}
print('P05b stage 1: held x > 1 equals valid over', R, held == valid)
# P05b stage 2: held relation decided on pick's facts {1,2,3}: {2,3}.
print('P05b stage 2:', {x for x in (1, 2, 3) if x > 1} == {2, 3})
# P06a/P06c stage 1: held not (x = 1); valid: every value other than 1.
held = {x for x in R if not x == 1}
valid = {x for x in R if x != 1}
print('P06a/P06c stage 1: held not (x = 1) equals valid over', R, held == valid)
