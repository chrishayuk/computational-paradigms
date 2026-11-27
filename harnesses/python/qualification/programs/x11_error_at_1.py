# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up: the program raises at stage 1, every time stage 1 is run (posed or
# replayed), so every later stage's reposed replay stops at stage 1.

# CONSTANTS BEGIN
# stage 2
A_VALUE = 3
# CONSTANTS END

known = {}
cp.bindings(known)

while (s := cp.stage()) is not None:
    if s.k == 1:
        known["x"] = 1 // 0
    elif s.k == 2:
        known["a"] = s.constants["A_VALUE"]
    cp.answer(len(known))
