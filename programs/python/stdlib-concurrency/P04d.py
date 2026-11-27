# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P04d (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of the values that satisfy it, by its
#       cases in order: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#     - sequences as tuples, + and slicing on tuples, atoms as strings:
#       The Python Tutorial, "Tuples and Sequences"; The Python Library
#       Reference, "Sequence Types -- list, tuple, range"
#     - None for a place that has no value: The Python Library Reference,
#       "Built-in Constants" (None)
#
# P04d. The query alist(s), with alist-left.
# alist is a generator of the values of s that satisfy it, s given as None
# while it is unknown, by alist-left's cases in their order, and case 1's
# conjuncts in theirs: alist(m), with m unknown, first; then s = <A> ++ m.
# The atom A is the string "a". Every value of s found is reported, in the
# order found. The sub-problem has no constants.

A = "a"

known = {}
cp.bindings(known)


def alist(s):
    """alist-left: yields each value of s for which alist(s) holds."""
    for m in alist(None):                   # 1. alist(s) if alist(m)
        if s is None or s == (A,) + m:      #    and s = <A> ++ m
            yield (A,) + m
    if s is None or s == ():                # 2. alist(<>)
        yield ()


cp.relations(alist=alist)


def show(x):
    """Output adapter: a sequence as the problem writes it, an atom with a
    leading quote (SPECIFICATION.md, "Values and names")."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    if isinstance(x, str):
        return "'" + x
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = alist(None)
        cp.pending("the query, not yet exhausted", answers)
        for value in answers:
            known["s"] = value
            if not s.replay:
                cp.answer("s = %s" % show(value))
