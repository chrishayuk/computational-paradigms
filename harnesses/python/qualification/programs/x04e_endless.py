# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X04e: an endless Python loop: budget at stage 1, continued at stage 2, budget again.

# CONSTANTS BEGIN
# stage 2
T = 3
# CONSTANTS END

frontier = [0]
cp.pending("frontier", frontier)

while (s := cp.stage()) is not None:
    while True:
        frontier.append(frontier[-1] + 1)
        if len(frontier) > 50:
            del frontier[:-50]
