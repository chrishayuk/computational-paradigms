# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Library Reference (iter with a sentinel)
# Made-up X05a: stage 1 loops for ever inside one C call, under a fixed limit.

# CONSTANTS BEGIN
# stage 2
T = 2
# CONSTANTS END

held = {}
cp.bindings(held)

while (s := cp.stage()) is not None:
    if s.k == 1 and not s.replay:
        any(iter(int, 1))
    elif s.k == 2:
        held["t"] = s.constants["T"]
    if not s.replay:
        cp.answer(", ".join("%s = %s" % kv for kv in sorted(held.items())))
