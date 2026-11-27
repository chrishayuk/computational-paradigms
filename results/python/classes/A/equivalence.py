# Classifier A's checking script for residual and solved-form equivalence (P01, P02).
# Brute force over a finite box of integers (P02) and of short sequences (P01b);
# it supports, and does not replace, the reasoning written in python.json.
import itertools

B = range(-60, 61)

def ten():
    return {(1, 15, 15), (2, 14, 7), (4, 12, 3), (8, 8, 1), (16, 0, 0), (-1, 17, -17),
            (-2, 18, -9), (-4, 20, -5), (-8, 24, -3), (-16, 32, -2)}

R1 = lambda u, v, w: u + v == 16
R2 = lambda u, v, w: w * u == v
R3 = lambda u, v, w: u + 10 == 12

def sols(*rels):
    return {(u, v, w) for u in B for v in B for w in B if all(r(u, v, w) for r in rels)}

checks = []
# R1 and R2 held (core/stdlib/extended, every order where both arrived before R3): ten triples
s = sols(R1, R2); checks.append(("R1,R2 held = the ten triples (in the box)", s == ten()))
# R2 held with u = 2 bound (R2R3 stage 2): u = 2, v = 2w
s = sols(R2, R3); checks.append(("R2,R3 = {u=2, v=2w}", s == {(2, 2 * w, w) for w in B if -60 <= 2 * w <= 60}))
s2 = {(u, v, w) for (u, v, w) in itertools.product(B, B, B) if u == 2 and w * 2 == v}
checks.append(("held w*2=v with binding u=2 = R2,R3", s2 == s))
# R1, R3 decided into u = 2, v = 14, w free
s = sols(R1, R3); checks.append(("R1,R3 = {u=2, v=14, w free}", s == {(2, 14, w) for w in B}))
s = sols(R3); checks.append(("R3 = {u=2, v, w free}", s == {(2, v, w) for v in B for w in B}))
s = sols(R1, R2, R3); checks.append(("R1,R2,R3 = {(2,14,7)}", s == {(2, 14, 7)}))
# times evaluator's zero case: 0 * b = 0 holds for every b (relation dropped, b left free)
checks.append(("0*b=0 for every b", all(0 * b == 0 for b in B)))

# P01b: conc(<1,2>, s, t) held = {t = <1,2> ++ s} over sequences of length <= 3 of {1,2,3}
def conc_rel(a, b, c):
    return tuple(a) + tuple(b) == tuple(c)
seqs = [tuple(p) for n in range(4) for p in itertools.product((1, 2, 3), repeat=n)]
held = {(s_, t) for s_ in seqs for t in [tuple(x) for n in range(6) for x in itertools.product((1, 2, 3), repeat=n)] if conc_rel((1, 2), s_, t)}
checks.append(("conc(<1,2>,s,t) = {t = <1,2>++s}", held == {(s_, (1, 2) + s_) for s_ in seqs}))
# P01c: no finite sequence x (length <= 8) with x = <1> ++ x
checks.append(("x = <1>++x has no finite solution (len<=8)",
               not any((1,) + x == x for n in range(9) for x in itertools.product((1, 2), repeat=n))))
# P01a: the held equations {x=y, y=z} and the identification x=y=z have the same solutions
dom = range(-3, 4)
checks.append(("{x=y,y=z} = {x=y=z}", {(x, y, z) for x in dom for y in dom for z in dom if x == y and y == z}
               == {(x, x, x) for x in dom}))

for name, ok in checks:
    print("ok  " if ok else "FAIL", name)
