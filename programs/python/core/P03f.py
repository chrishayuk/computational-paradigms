# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03f (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - generators and yield: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#     - sequences as tuples, indexing and slicing, len and + on tuples:
#       The Python Tutorial, "Tuples and Sequences"
#     - separate functions for the directions of rev and conc: METRICS.md,
#       rule 3 (the example of P03b in Python)
#
# P03f. The query rev(a, <seq>): exactly one a.
# rev is written for the direction the query uses (b known, a computed), as a
# generator of every a, by the definition's two cases in order. In case 2 the
# second place r is known, so conc(q, <h>, r) is the conjunct that can be
# computed first: it is taken first (a move of a conjunct), in conc's
# splitting direction (c known, every a and b), keeping the splits whose
# second part is one element <h>; then rev(l, q) in its backward direction.
# Both are reformulations (METRICS.md, rules 3 and 4).

# CONSTANTS BEGIN
# stage 1
BACKWARDS = (1, 2, 3)
# CONSTANTS END

known = {}
cp.bindings(known)


def split(c):
    """conc(a, b, c) with c known: every (a, b), by the definition's cases."""
    yield (), c                             # 1. conc(<>, b, b)
    if c:                                   # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)
        for a, b in split(c[1:]):
            yield (c[0],) + a, b


def unrev(r):
    """rev(a, r) with r known: every a, by the definition's cases."""
    if not r:                               # 1. rev(<>, <>)
        yield ()
    for q, last in split(r):                # 2. rev(<h> ++ l, r) if rev(l, q) and conc(q, <h>, r)
        if len(last) == 1:
            for l in unrev(q):
                yield (last[0],) + l


cp.relations(conc=split, rev=unrev)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = unrev(s.constants["BACKWARDS"])
        cp.pending("answers not yet generated", answers)
        for a in answers:
            known["a"] = a
            if not s.replay:
                cp.answer("a = %s" % show(a))
