# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P04f (one text, the
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
# P04f. The query alist(s), with alist-right.
# alist is a generator of the values of s that satisfy it, s given as None
# while it is unknown, by alist-right's cases in their order. Case 2's head
# <A> ++ m, with s known, gives m as the rest of s when s begins with A;
# with s unknown, m is unknown too. The atom A is the string "a". Every value
# of s found is reported, in the order found. The sub-problem has no constants.

A = "a"

known = {}
cp.bindings(known)


def alist(s):
    """alist-right: yields each value of s for which alist(s) holds."""
    if s is None or s == ():                # 1. alist(<>)
        yield ()
    if s is None or s[:1] == (A,):          # 2. alist(<A> ++ m)
        for m in alist(None if s is None else s[1:]):   # if alist(m)
            yield (A,) + m


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
