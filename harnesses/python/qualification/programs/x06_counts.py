# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference (generators)
# Made-up X06a: stage 1 counts the calls of a doubly recursive relation f(n)
# (f(0) = f(1) = 1, f(n) = f(n-1) + f(n-2)), which makes 2 f(n) - 1 calls;
# stage 2 holds nested generators suspended; stage 3 builds and drops a list of
# DROP distinct ints inside a call.

# CONSTANTS BEGIN
# stage 2
DEPTH = 16
# stage 3
DROP = 100000
# CONSTANTS END

held = {}
gens = []
cp.bindings(held)
cp.pending("suspended generators", gens)


def f(n):
    if n < 2:
        return 1
    return f(n - 1) + f(n - 2)


cp.relations(f=f)


def bits(k):
    if k == 0:
        yield ()
        return
    for rest in bits(k - 1):
        for b in (0, 1):
            yield (b,) + rest


def build_and_drop(m):
    xs = [i + 1000 for i in range(m)]
    return len(xs)


while (s := cp.stage()) is not None:
    if s.k == 1:
        held["f"] = f(s.params["n"])
        cp.answer("f = %d" % held["f"])
    elif s.k == 2:
        g = bits(s.constants["DEPTH"])
        held["g"] = next(g)
        gens.append(g)
        cp.answer("g = %r" % (held["g"],))
    elif s.k == 3:
        held["dropped"] = build_and_drop(s.constants["DROP"])
        cp.answer("dropped = %d" % held["dropped"])
