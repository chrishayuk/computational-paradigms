# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core, of stdlib-concurrency and of extended for P10a
#   (one text, the same file in all three folders), written before any
#   program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a named quantity as an entry of a dict, replaced by assignment; the
#       right-hand side evaluated before the assignment, so b + <k> takes b
#       at its value before the stage: The Python Language Reference
#       (3.13), "Assignment statements" ("An assignment statement evaluates
#       the expression list ... and assigns the single resulting object"),
#       "Mapping Types -- dict" (The Python Library Reference)
#
# P10a. Stage 1: b becomes <k>; stage 2: b becomes b + <k>; stage 3: b
# becomes <k>. Replacement is Python's own assignment: b holds one value at
# a time, and the value it replaces is not kept.

# CONSTANTS BEGIN
# stage 1
B_FIRST = 10
# stage 2
B_ADDEND = 5
# stage 3
B_THIRD = 7
# CONSTANTS END

quantities = {}     # the named quantities: name -> current value
cp.bindings(quantities)

while (s := cp.stage()) is not None:
    if s.k == 1:
        quantities["b"] = s.constants["B_FIRST"]                        # b becomes <k>
    elif s.k == 2:
        quantities["b"] = quantities["b"] + s.constants["B_ADDEND"]     # b becomes b + <k>
    elif s.k == 3:
        quantities["b"] = s.constants["B_THIRD"]                        # b becomes <k>
    if not s.replay:
        cp.answer("b = %s" % quantities["b"])
