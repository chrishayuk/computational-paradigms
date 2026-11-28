# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P15c, written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation given by facts as a generator of them, in order; one
#       solution taken with next(), the generator left suspended: The Python
#       Language Reference (3.13), "Yield expressions"; PEP 255, "Simple
#       Generators"; The Python Library Reference, "Built-in Functions"
#       (next with a default); this configuration's P11a and P12a programs
#     - atoms as strings, shown with a leading quote: this configuration's
#       earlier programs (programs/python/README.md, batch 1B)
#
# P15c. One stage: grant(<atom>, <atom>, g), any one.
# grant is transcribed forwards (g from p and q) as a generator of its two
# facts, in order. One solution is taken with next(); the choice is the
# first fact's. The generator is left suspended, holding the other, and is
# registered as pending: nothing in the program asks it again.

# CONSTANTS BEGIN
# stage 1
FIRST = "a"
SECOND = "b"
# CONSTANTS END

known = {}      # the bindings: unknown -> value
cp.bindings(known)


def grant(p, q):
    """grant(p, q, g), forwards: the requests g that may be granted, by the
    definition's facts in order."""
    yield p                                     # 1. grant(p, q, p)
    yield q                                     # 2. grant(p, q, q)


cp.relations(grant=grant)

while (st := cp.stage()) is not None:
    if st.k == 1:
        grants = grant(st.constants["FIRST"], st.constants["SECOND"])
        cp.pending("grant's solutions not yet taken", grants)
        known["g"] = next(grants)                               # any one
        if not st.replay:
            cp.answer("g = '%s" % known["g"])
