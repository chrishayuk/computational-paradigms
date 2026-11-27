# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03d (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - generators and yield: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#     - sequences as tuples, indexing and slicing, == and + on tuples:
#       The Python Tutorial, "Tuples and Sequences"; The Python Language
#       Reference, "Value comparisons"
#     - a separate function for a direction of conc: METRICS.md, rule 3
#
# P03d. The query conc(a, <seq>, <seq>).
# conc is written for the direction the query uses (b and c known, a
# computed), as a generator of every a, by the definition's two cases in
# order: a reformulation (METRICS.md, rule 3).

# CONSTANTS BEGIN
# stage 1
SECOND = (3,)
WHOLE = (1, 2, 3)
# CONSTANTS END

known = {}
cp.bindings(known)


def front(b, c):
    """conc(a, b, c) with b and c known: every a, by the definition's cases."""
    if b == c:                              # 1. conc(<>, b, b)
        yield ()
    if c:                                   # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)
        for a in front(b, c[1:]):
            yield (c[0],) + a


cp.relations(conc=front)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = front(s.constants["SECOND"], s.constants["WHOLE"])
        cp.pending("answers not yet generated", answers)
        for a in answers:
            known["a"] = a
            if not s.replay:
                cp.answer("a = %s" % show(a))
