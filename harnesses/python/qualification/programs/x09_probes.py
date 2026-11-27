# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no;
#   finite() is copied from systems/python/probes/p6_budget.py and build_and_drop()
#   from systems/python/probes/p3_memory.py, so that the harness's figures can be
#   compared with the systems file's qualified ones.

# CONSTANTS BEGIN
# stage 2
N = 100
# stage 3
N = 100
# stage 4
N = 1000
# stage 5
N = 1000000
# CONSTANTS END


def finite(n):
    k = 0
    for i in range(n):
        k += i
    return k


def build_and_drop(n):
    xs = list(range(1000, 1000 + n))
    return len(xs)


cp.relations(finite=finite, build_and_drop=build_and_drop)

while (s := cp.stage()) is not None:
    if s.k == 5:
        r = build_and_drop(s.constants["N"])
    elif s.k >= 2:
        r = finite(s.constants["N"])
    else:
        continue
    cp.answer(r)
