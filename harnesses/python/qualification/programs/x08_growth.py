# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X08a: one stage, a sum over 1..n (for the CPU time and resident set fields).

while (s := cp.stage()) is not None:
    t = 0
    for i in range(1, s.params["n"] + 1):
        t += i
    cp.answer("s = %d" % t)
