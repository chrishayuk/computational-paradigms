# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Library Reference (iter with a sentinel)
# Made-up X04c: stage 2 loops for ever inside one C call (no Python
# instruction runs, so no budget can see it); stage 3 is reposed after the timeout.

# CONSTANTS BEGIN
# stage 1
R = 1
# stage 3
T = 2
# CONSTANTS END

held = {}
cp.bindings(held)

while (s := cp.stage()) is not None:
    if s.k == 1:
        held["r"] = s.constants["R"]
    elif s.k == 2 and not s.replay:
        any(iter(int, 1))
    elif s.k == 3:
        held["t"] = s.constants["T"]
    if not s.replay:
        cp.answer(", ".join("%s = %s" % kv for kv in sorted(held.items())))
