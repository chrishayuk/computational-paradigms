# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core, of stdlib-concurrency and of extended for P10c
#   (one text, the same file in all three folders), written before any
#   program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a named quantity as an entry of a dict, replaced by assignment; the
#       right-hand side evaluated once, when the assignment is executed:
#       The Python Language Reference (3.13), "Assignment statements";
#       "Binary arithmetic operations"
#
# P10c. Stage 1: b becomes <k>; stage 2: d becomes <k> * b; stage 3: b
# becomes b + <k>; stage 4: b becomes <k>.
# Every stage is a replacement, by Python's own assignment. d is given a
# value once, from b's value at stage 2, and keeps it.

# CONSTANTS BEGIN
# stage 1
B_FIRST = 10
# stage 2
D_FACTOR = 2
# stage 3
B_ADDEND = 5
# stage 4
B_THIRD = 7
# CONSTANTS END

NAMES = ("b", "d")

quantities = {}     # the named quantities: name -> current value
cp.bindings(quantities)


def times(a, b):
    """The relation a * b = c, c from a and b."""
    return a * b


cp.relations(times=times)

while (s := cp.stage()) is not None:
    if s.k == 1:
        quantities["b"] = s.constants["B_FIRST"]                        # b becomes <k>
    elif s.k == 2:
        quantities["d"] = times(s.constants["D_FACTOR"], quantities["b"])   # d becomes <k> * b
    elif s.k == 3:
        quantities["b"] = quantities["b"] + s.constants["B_ADDEND"]     # b becomes b + <k>
    elif s.k == 4:
        quantities["b"] = s.constants["B_THIRD"]                        # b becomes <k>
    if not s.replay:
        cp.answer(", ".join("%s = %s" % (n, quantities[n]) for n in NAMES if n in quantities))
