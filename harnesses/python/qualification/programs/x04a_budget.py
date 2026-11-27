# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X04a: stage 1 is a sum long enough to spend the budget of 10^6
# instructions and finish within 2 x 10^6; continued after its budget, it ends
# within stage 2, then reads stage 2.

# CONSTANTS BEGIN
# stage 1
N = 200000
# stage 2
T = 1
# CONSTANTS END

held = {}
cp.bindings(held)


def total(n):
    k = 0
    for i in range(n):
        k += i
    return k


while (s := cp.stage()) is not None:
    if s.k == 1:
        held["r"] = total(s.constants["N"])
        cp.answer("r = %d" % held["r"])
    elif s.k == 2:
        held["t"] = s.constants["T"]
        cp.answer("t = %d" % held["t"])
