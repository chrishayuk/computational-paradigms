# Checks, over a box of integers, that each P02 residual or solved form the programs reported denotes the same set
# as the problem's valid outcomes. The box check is a test, not a proof; the argument by hand is in the notes:
# every residual here is the posed relations themselves, or the posed relations with u = 2 substituted, so the
# equivalence holds on all integers (substitution of a determined value preserves the solution set).
B = range(-60, 61)
R1 = lambda u, v, w: u + v == 16
R2 = lambda u, v, w: w * u == v
R3 = lambda u, v, w: u + 10 == 12
TEN = {(1, 15, 15), (2, 14, 7), (4, 12, 3), (8, 8, 1), (16, 0, 0), (-1, 17, -17), (-2, 18, -9), (-4, 20, -5), (-8, 24, -3), (-16, 32, -2)}
valid = {  # the problem file's table for P02b, by the relations that have arrived
    "R1": lambda u, v, w: u + v == 16,
    "R2": lambda u, v, w: v == w * u,
    "R3": lambda u, v, w: u == 2,
    "R1R2": lambda u, v, w: (u, v, w) in TEN,
    "R1R3": lambda u, v, w: u == 2 and v == 14,
    "R2R3": lambda u, v, w: u == 2 and v == 2 * w,
    "R1R2R3": lambda u, v, w: (u, v, w) == (2, 14, 7),
}
reported = {  # what the programs reported, read as conditions (the answer's 'where' part and its bindings)
    "R1": ("u + v = 16, w free", lambda u, v, w: u + v == 16),
    "R2": ("w . u = v", lambda u, v, w: w * u == v),
    "R3": ("u = 2, v free, w free", lambda u, v, w: u == 2),
    "R1R2": ("u + v = 16, w . u = v", lambda u, v, w: u + v == 16 and w * u == v),
    "R1R3": ("u = 2, v = 14, w free", lambda u, v, w: u == 2 and v == 14),
    "R2R3": ("u = 2, where w . 2 = v", lambda u, v, w: u == 2 and w * 2 == v),
    "R1R2R3": ("u = 2, v = 14, w = 7", lambda u, v, w: (u, v, w) == (2, 14, 7)),
}
for k, (text, f) in reported.items():
    a = {(u, v, w) for u in B for v in B for w in B if f(u, v, w)}
    b = {(u, v, w) for u in B for v in B for w in B if valid[k](u, v, w)}
    print(f"{k:7} reported '{text}': {'equivalent' if a == b else 'DIFFERENT'} on the box [-60, 60]^3 ({len(a)} points)")
# the ten triples of R1, R2 are exactly the box solutions (all lie inside it)
print("ten triples inside the box:", all(max(map(abs, t)) <= 60 for t in TEN))
# P01: by enumeration over small sequences of small integers
import itertools
seqs = [tuple(s) for n in range(0, 4) for s in itertools.product(range(0, 4), repeat=n)]
conc = lambda a, b: a + b
# P01b stage 1: conc(<1,2>, s, t) held  vs  t = <1,2> ++ s
ok = all((conc((1, 2), s) == t) == (t == (1, 2) + s) for s in seqs for t in seqs + [(1, 2) + s for s in seqs])
print("P01b stage 1: conc(<1,2>, s, t) equivalent to t = <1,2> ++ s on sequences up to length 5:", ok)
# P01c finite reading: x = <1> ++ x has no finite solution (length would satisfy n = n + 1)
print("P01c finite: solutions among sequences up to length 3:", [x for x in seqs if x == (1,) + x])
