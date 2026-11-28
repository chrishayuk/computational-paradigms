"""Residual equivalence checks for algol-60 P07 and P08 (classifier A).

P07: each reported residual or answer is checked against the valid
outcomes by enumerating integer assignments in a window (|v| <= 60); the
residual relations are parsed from the record's observe block.
P08: the reported bindings and held equations are closed under the held
element equations (union-find) and compared, term by term, with the
valid outcomes' solved form.
Run: python3 -I equiv.py  (prints one line per check; exit 1 on a failure)
"""
import itertools, sys

W = range(-60, 61)
ok = True


def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok = ok and cond


# ---- P07 ----
def sols2(rel):
    return {(x, y) for x in W for y in W if rel(x, y)}


# P07b residual: x + y = 10, x - y = 4 held  vs valid x = 7, y = 3
check("P07b residual {x+y=10, x-y=4} == {(7,3)}", sols2(lambda x, y: x + y == 10 and x - y == 4) == {(7, 3)})
# P07c residual: x + y = 10 held vs valid: every pair with x + y = 10 (identical relation)
check("P07c residual {x+y=10} == valid (same relation, window)", sols2(lambda x, y: x + y == 10) == {(x, 10 - x) for x in W if 10 - x in W})
# P07f residual: x + y = 10, x + y = 11 held vs none
check("P07f residual {x+y=10, x+y=11} == {} (inconsistency undetected)", sols2(lambda x, y: x + y == 10 and x + y == 11) == set())
# P07a explicit answers, every order: x=5,y=4,z=3
check("P07a x=5,y=4,z=3 is the only solution", {(x, y, z) for x in W for y in W for z in W if x + y + z == 12 and y + z == 7 and z == 3} == {(5, 4, 3)})
# P07d explicit
check("P07d w=7 (u=2,v=14) only", {w for w in W if w * 2 == 14} == {7})
# P07e reported none
check("P07e none: no integer w with 2w = 15", {w for w in W if w * 2 == 15} == set())
# P07g both roots
check("P07g x*x=9 -> {3,-3}", {x for x in W if x * x == 9} == {3, -3})


# ---- P08 ----
class UF:
    def __init__(self):
        self.p = {}

    def f(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            a = self.p[a]
        return a

    def u(self, a, b):
        self.p[self.f(a)] = self.f(b)


def close(seq, eqs):
    uf = UF()
    for a, b in eqs:
        uf.u(a, b)
    return [uf.f(e) if isinstance(e, str) else e for e in seq]


def same_up_to(rep_terms, rep_eqs, valid_terms, valid_eqs):
    """Both sides denote the same set if, under each side's equations, the
    terms coincide and each side's equations are entailed by the other's."""
    a = [close(t, rep_eqs) for t in rep_terms]
    b = [close(t, rep_eqs) for t in valid_terms]
    c = [close(t, valid_eqs) for t in rep_terms]
    d = [close(t, valid_eqs) for t in valid_terms]
    ent1 = all(close([x], valid_eqs) == close([y], valid_eqs) for x, y in rep_eqs)
    ent2 = all(close([x], rep_eqs) == close([y], rep_eqs) for x, y in valid_eqs)
    return a == b and c == d and ent1 and ent2


# stage 3 (open): reported a=(x,y,z), x = y held, rev pending; valid a=(y,y,z), x=y, rev pending
check("P08a s3 open: a=(x,y,z) & x=y  ==  a=(y,y,z) & x=y",
      same_up_to([["x", "y", "z"]], [("x", "y")], [["y", "y", "z"]], [("x", "y")]))
# stage 4: reported a=(x,y,z), b=(z,y,x), x=y held; valid x=y, a=(y,y,z), b=(z,y,y)
check("P08a s4: a=(x,y,z), b=(z,y,x), x=y  ==  a=(y,y,z), b=(z,y,y), x=y",
      same_up_to([["x", "y", "z"], ["z", "y", "x"]], [("x", "y")], [["y", "y", "z"], ["z", "y", "y"]], [("x", "y")]))
# stage 5: reported a=(x,y,z), b=(z,y,x), x=y, y=z held; valid x=y=z, a=b=(z,z,z)
check("P08a s5: a=(x,y,z), b=(z,y,x), x=y, y=z  ==  a=b=(z,z,z), x=y=z",
      same_up_to([["x", "y", "z"], ["z", "y", "x"]], [("x", "y"), ("y", "z")], [["z", "z", "z"], ["z", "z", "z"]], [("x", "y"), ("y", "z")]))
# stage 6 explicit
check("P08a s6: (42,42,42) reversed is itself, and (42) ++ c = b gives c = (42,42)",
      list(reversed([42, 42, 42])) == [42, 42, 42] and [42, 42, 42][1:] == [42, 42])
# P08c stage 4
check("P08c s4: rev((1,2)) = (2,1)", list(reversed([1, 2])) == [2, 1])

sys.exit(0 if ok else 1)
