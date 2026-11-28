# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P12b (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, s.params (n, answers), a generator
#       registered as pending, accept registered as the relation whose
#       applications are the candidates examined: harnesses/python/README.md,
#       sections 3 and 8
#     - a relation as a generator of the values that satisfy it, by its
#       cases in order (case 1's sequence first, then case 2's, e = 'l before
#       e = 'r); the conjunction as a generator over the first conjunct's
#       solutions, testing the second: The Python Language Reference (3.13),
#       "Yield expressions"; PEP 255, "Simple Generators"; this
#       configuration's P04 programs (alist-right)
#     - one answer taken with next(), every answer with a for loop: The
#       Python Library Reference, "Built-in Functions" (next, with a default)
#     - a closed world of facts as a tuple, tested with in: The Python
#       Library Reference, "Common Sequence Operations"; METRICS.md, rule 9
#     - atoms as strings: The Python Library Reference, "Text Sequence Type
#       -- str"
#
# P12b. One stage: choice(n, s) and accept(s), in that order, for all
# solutions or for any one (s.params["answers"]), n from s.params["n"].
# accept: <R> only (a closed world).
# The same text as this configuration's P12a, with P12b's facts.
# choice is a generator of the sequences s it holds of, by its cases in
# order, depth first: case 1 gives <>, then case 2 gives <e> ++ t for e = 'l,
# then e = 'r, each with every t of choice(n - 1, t) in its order. accept is a
# test of s against the closed world's facts. The search is Python's own
# evaluation of nested generators. The closed world depends on n, so the
# constants block gives the facts for each n the problem poses.

# CONSTANTS BEGIN
# stage 1
ACCEPT_FACTS = {
    8: (("r",),),
    12: (("r",),),
    16: (("r",),),
}
# CONSTANTS END

facts = []          # accept's closed world, as stage 1 gives it for this n


def choice(n):
    """choice(n, s), s unknown: yields each s for which it holds, by the
    definition's cases in order."""
    yield ()                                # 1. choice(n, <>)
    if n > 0:                               # 2. choice(n, <e> ++ t) if n > 0 and
        for e in ("l", "r"):                #    (e = 'l or e = 'r, in that order) and
            for t in choice(n - 1):         #    choice(n - 1, t)
                yield (e,) + t


def accept(s):
    """accept(s): s is one of the facts."""
    return s in facts


cp.relations(choice=choice, accept=accept)


def conjunction(n):
    """choice(n, s) and accept(s), in that order: yields each solution s."""
    for s in choice(n):
        if accept(s):
            yield s


def show(x):
    """Output adapter: a sequence as the problem writes it, an atom with a
    leading quote."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    if isinstance(x, str):
        return "'" + x
    return str(x)


while (st := cp.stage()) is not None:
    if st.k == 1:
        n = st.params["n"]
        facts[:] = st.constants["ACCEPT_FACTS"][n]
        answers = conjunction(n)
        cp.pending("the conjunction's untried alternatives", answers)
        if st.params["answers"] == "any-one":
            found = next(answers, None)             # any one
            if found is not None and not st.replay:
                cp.answer("s = %s" % show(found))
        else:
            found = None
            for found in answers:                   # all
                if not st.replay:
                    cp.answer("s = %s" % show(found))
        if found is None and not st.replay:
            print("no solution: no s of choice(%d, s) is accepted" % n)
