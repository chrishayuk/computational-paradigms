# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03e (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial (3.13), "Tuples and Sequences"; The Python
#       Library Reference, "Sequence Types -- list, tuple, range"
#     - rev and conc by their cases, with "if not a:" as the dispatch on
#       case 1: METRICS.md, rule 3 (the example of conc in Python)
#
# P03e. The query rev(<seq>, b).
# rev and conc are transcribed in the direction the query uses (the first
# place known), each as a function of its own, by their cases in order; rev's
# two conjuncts are evaluated in their order (rev first, then conc).

# CONSTANTS BEGIN
# stage 1
FORWARDS = (1, 2, 3)
# CONSTANTS END

known = {}
cp.bindings(known)


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


def rev(a):
    """rev(a, b), forwards: b from a, by the definition's cases."""
    if not a:                               # 1. rev(<>, <>)
        return ()
    return conc(rev(a[1:]), (a[0],))        # 2. rev(<h> ++ l, r) if rev(l, q) and conc(q, <h>, r)


cp.relations(conc=conc, rev=rev)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        known["b"] = rev(s.constants["FORWARDS"])
        if not s.replay:
            cp.answer("b = %s" % show(known["b"]))
