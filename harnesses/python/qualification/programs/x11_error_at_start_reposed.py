# CP-POSING: reposed
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up: the program fails before it first asks for a stage (a NameError
# in its set-up), so stage 1 is an error and every later stage's reposed run
# stops before stage 1 is even given to it.

known = {}
cp.bindings(known)
helper = undefined_name

while (s := cp.stage()) is not None:
    cp.answer(len(known))
