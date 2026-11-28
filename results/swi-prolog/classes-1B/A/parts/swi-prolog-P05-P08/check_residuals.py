"""Check, by enumeration over a box of integers, that each residual reported in
P05-P07 denotes the same set as the valid outcomes there (a check, not a proof;
the hand reasoning is in swi-prolog.json, residual_equivalence)."""
R = range(-60, 61)
cases = {
  "P05b st1 clpfd 'X in 2..sup' vs x > 1": (lambda x: x >= 2, lambda x: x > 1, 1),
  "P05b st1 freeze(X, X>1) vs x > 1": (lambda x: x > 1, lambda x: x > 1, 1),
  "P07b clpfd '4+Y#=X, X+Y#=10' vs {(7,3)}": (lambda x, y: 4 + y == x and x + y == 10, lambda x, y: (x, y) == (7, 3), 2),
  "P07b when sum_known(X,Y,10), diff_known(X,Y,4) vs {(7,3)}": (lambda x, y: x + y == 10 and x - y == 4, lambda x, y: (x, y) == (7, 3), 2),
  "P07c 'X+Y#=10' vs x + y = 10": (lambda x, y: x + y == 10, lambda x, y: x + y == 10, 2),
  "P07f 'X+Y#=11, X+Y#=10' vs empty": (lambda x, y: x + y == 11 and x + y == 10, lambda x, y: False, 2),
  "P07g 'X in -3\\/3' vs {3,-3}": (lambda x: x in (-3, 3), lambda x: x * x == 9, 1),
  "P07g when product_known(X,X,9) (9 is X*X) vs {3,-3}": (lambda x: 9 == x * x, lambda x: x in (3, -3), 1),
}
import itertools
for name, (res, valid, n) in cases.items():
    bad = [v for v in itertools.product(R, repeat=n) if bool(res(*v)) != bool(valid(*v))]
    print(("OK  " if not bad else "DIFF"), name, bad[:5])
# P06a/P06c: dif(X, 1) over values: checked over integers, atoms and a sequence sample
vals = list(R) + ["a", "brown", (), (1, 2)]
print("OK  " if all((v != 1) == (not (v == 1)) for v in vals) else "DIFF", "P06a/c dif(X,1) vs not (x = 1)")
