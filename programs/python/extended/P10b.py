# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of extended for P10b (one text, the same
#   file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a relation held in a list and taken up
#       again after each stage: harnesses/python/README.md, sections 3 and 8
#       (x01_total.py); the holding loop of this configuration's P02 programs
#     - a named quantity as an entry of a dict, replaced by assignment: The
#       Python Language Reference (3.13), "Assignment statements"
#     - the relation d = k * b evaluated in the direction it is used (d from
#       b): METRICS.md, rule 8; "Binary arithmetic operations"
#
# P10b. Stage 1: d = <k> * b, at all times; stages 2-4: b becomes <k>, b
# becomes b + <k>, b becomes <k>.
# b is a named quantity, replaced by assignment. The standing relation is
# held, as (factor, source, target), for as long as the program runs: after
# every stage, each standing relation whose source has a value gives its
# target the value the relation defines from the source's current value.
# The relation is never removed: it holds at all times.

# CONSTANTS BEGIN
# stage 1
D_FACTOR = 2
# stage 2
B_FIRST = 10
# stage 3
B_ADDEND = 5
# stage 4
B_THIRD = 7
# CONSTANTS END

NAMES = ("b", "d")

quantities = {}     # the named quantities: name -> current value
standing = []       # standing relations, target = factor * source: (factor, source, target)

cp.bindings(quantities)
cp.suspended("standing relations, taken up again after every stage", standing)


def times(a, b):
    """The relation a * b = c, c from a and b."""
    return a * b


cp.relations(times=times)


def maintain():
    """Give each standing relation's target the value it defines, from its
    source's current value, where the source has one."""
    for factor, source, target in standing:
        if source in quantities:
            quantities[target] = times(factor, quantities[source])


while (s := cp.stage()) is not None:
    if s.k == 1:
        standing.append((s.constants["D_FACTOR"], "b", "d"))           # d = <k> * b, at all times
    elif s.k == 2:
        quantities["b"] = s.constants["B_FIRST"]                        # b becomes <k>
    elif s.k == 3:
        quantities["b"] = quantities["b"] + s.constants["B_ADDEND"]     # b becomes b + <k>
    elif s.k == 4:
        quantities["b"] = s.constants["B_THIRD"]                        # b becomes <k>
    maintain()
    if not s.replay and quantities:
        cp.answer(", ".join("%s = %s" % (n, quantities[n]) for n in NAMES if n in quantities))
