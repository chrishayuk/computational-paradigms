# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03a (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial (3.13), "Tuples and Sequences"; The Python
#       Library Reference, "Sequence Types -- list, tuple, range"
#     - conc by its two cases, with "if not a:" as the dispatch on case 1:
#       METRICS.md, rule 3 (the example of conc in Python)
#
# P03a. The query conc(<seq>, <seq>, c).
# conc is transcribed in the direction the query uses (a and b known, c
# computed), as a function of its own, by its two cases in order.

# CONSTANTS BEGIN
# stage 1
FIRST = (1, 2)
SECOND = (3,)
# CONSTANTS END

known = {}
cp.bindings(known)


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


cp.relations(conc=conc)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        known["c"] = conc(s.constants["FIRST"], s.constants["SECOND"])
        if not s.replay:
            cp.answer("c = %s" % show(known["c"]))
