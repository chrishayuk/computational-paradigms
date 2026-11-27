# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Library Reference (os.abort)
# Made-up X04b, another way: stage 2 aborts the interpreter process (SIGABRT).
import os

# CONSTANTS BEGIN
# stage 1
R = 2
# stage 3
T = 9
# CONSTANTS END

held = {}
cp.bindings(held)

while (s := cp.stage()) is not None:
    if s.k == 1:
        held["r"] = s.constants["R"]
    elif s.k == 2 and not s.replay:
        os.abort()
    elif s.k == 3:
        held["t"] = s.constants["T"]
    if not s.replay:
        cp.answer(", ".join("%s = %s" % kv for kv in sorted(held.items())))
