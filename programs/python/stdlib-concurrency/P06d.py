# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P06d (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial (3.13), "Tuples and Sequences"
#     - relations by their cases, with "if not s:" as the dispatch on the
#       empty sequence: METRICS.md, rule 3 (the example of conc in Python)
#     - negation as Python's "not" on a decided test: The Python Language
#       Reference, "Boolean operations"
#
# P06d. The query setdiff(<seq>, <seq>, d).
# mem and setdiff are transcribed in the direction the query uses, each as a
# function of its own, by their cases in order: mem as a test (e and s
# known: true or false, no case for the empty sequence, so false there);
# setdiff computing d from s1 and s2. Case 3's guard, not mem(h, s2), is
# written as it is stated, so mem is applied again there.

# CONSTANTS BEGIN
# stage 1
FIRST = (1, 2, 3, 4)
SECOND = (2, 4, 6)
# CONSTANTS END

known = {}
cp.bindings(known)


def mem(e, s):
    """mem(e, s), e and s known: whether e is an element of s."""
    if s and s[0] == e:                     # 1. mem(e, <e> ++ t)
        return True
    if s:                                   # 2. mem(e, <h> ++ t) if mem(e, t)
        return mem(e, s[1:])
    return False


def setdiff(s1, s2):
    """setdiff(s1, s2, d), forwards: d from s1 and s2, by the cases."""
    if not s1:                              # 1. setdiff(<>, s2, <>)
        return ()
    h, t = s1[0], s1[1:]
    if mem(h, s2):                          # 2. setdiff(<h> ++ t, s2, d) if mem(h, s2)
        return setdiff(t, s2)               #    and setdiff(t, s2, d)
    if not mem(h, s2):                      # 3. setdiff(<h> ++ t, s2, <h> ++ d) if not mem(h, s2)
        return (h,) + setdiff(t, s2)        #    and setdiff(t, s2, d)


cp.relations(mem=mem, setdiff=setdiff)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        known["d"] = setdiff(s.constants["FIRST"], s.constants["SECOND"])
        if not s.replay:
            cp.answer("d = %s" % show(known["d"]))
