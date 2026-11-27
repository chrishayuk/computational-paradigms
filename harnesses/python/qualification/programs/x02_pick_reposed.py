# CP-POSING: reposed
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X02a: stage 1 chooses p from a set of candidates and emits it; stage 2
# commits to the current p; stage 3 adds p != EXCLUDED.

# CONSTANTS BEGIN
# stage 1
CANDIDATES = [5, 8, 13]
# stage 3
EXCLUDED = 5
# CONSTANTS END

state = {}
candidates = []
cp.bindings(state)

while (s := cp.stage()) is not None:
    if s.k == 1:
        candidates[:] = s.constants["CANDIDATES"]
        state["p"] = candidates[0]
        cp.emit("chose p = %d" % state["p"])
    elif s.k == 2:
        if s.commitment is not None:
            state["p"] = int(s.commitment.split("=")[1])
        state["committed"] = True
    elif s.k == 3:
        excluded = s.constants["EXCLUDED"]
        if state["p"] == excluded:
            if state.get("committed"):
                state["p"] = None
            else:
                state["p"] = [c for c in candidates if c != excluded][0]
    if not s.replay and state.get("p") is not None:
        cp.answer("p = %d" % state["p"])
