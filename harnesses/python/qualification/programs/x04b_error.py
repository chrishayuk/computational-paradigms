# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X04b: stage 2 raises an exception, so stage 3 is reposed.

# CONSTANTS BEGIN
# stage 1
R = 2
# stage 3
T = 9
# CONSTANTS END

held = {}
cp.bindings(held)


def deep(n):
    return 0 if n == 0 else 1 + deep(n - 1)


while (s := cp.stage()) is not None:
    if s.k == 1:
        held["r"] = s.constants["R"]
    elif s.k == 2 and not s.replay:
        held["d"] = deep(10 ** 5)
    elif s.k == 3:
        held["t"] = s.constants["T"]
    if not s.replay:
        cp.answer(", ".join("%s = %s" % kv for kv in sorted(held.items())))
