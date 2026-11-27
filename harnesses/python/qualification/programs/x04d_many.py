# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X04d: more answers than the cap, with a pending stack.

# CONSTANTS BEGIN
# stage 1
HIGH = 25
# CONSTANTS END

stack = []
high = []
cp.pending("stack of unvisited values", stack)

while (s := cp.stage()) is not None:
    if s.k == 1:
        high.append(s.constants["HIGH"])
    stack[:] = list(range(high[0], 0, -1))
    while stack:
        cp.answer("r = %d" % stack.pop())
        if s.k == 2:
            break
