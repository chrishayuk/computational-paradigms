# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03b (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - generators and yield: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial, "Tuples and Sequences"
#     - a separate function for the splitting direction of conc: METRICS.md,
#       rule 3 (the example of P03b in Python)
#
# P03b. The query conc(a, b, <seq>): every a and b.
# A Python function computes one direction. conc forwards cannot split a
# sequence, so conc is written for the direction the query uses (c known, a
# and b computed), as a generator of every (a, b), by the definition's two
# cases in order: a reformulation (METRICS.md, rule 3).

# CONSTANTS BEGIN
# stage 1
WHOLE = (1, 2)
# CONSTANTS END

known = {}
cp.bindings(known)


def split(c):
    """conc(a, b, c) with c known: every (a, b), by the definition's cases."""
    yield (), c                             # 1. conc(<>, b, b)
    if c:                                   # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)
        for a, b in split(c[1:]):
            yield (c[0],) + a, b


cp.relations(conc=split)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = split(s.constants["WHOLE"])
        cp.pending("splits not yet generated", answers)
        for a, b in answers:
            known["a"], known["b"] = a, b
            if not s.replay:
                cp.answer("a = %s, b = %s" % (show(a), show(b)))
