# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P03c (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - generators, yield and yield from: The Python Language Reference
#       (3.13), "Yield expressions"; PEP 255, "Simple Generators"; PEP 380,
#       "Syntax for Delegating to a Subgenerator"
#     - sequences as tuples, indexing and slicing: The Python Tutorial,
#       "Tuples and Sequences"
#     - a separate function for a direction of conc: METRICS.md, rule 3
#
# P03c. The query conc(<seq>, b, <seq>).
# conc is written for the direction the query uses (a and c known, b
# computed), as a generator of every b, by the definition's two cases in
# order: a reformulation (METRICS.md, rule 3). It yields none if no b exists.

# CONSTANTS BEGIN
# stage 1
FIRST = (1,)
WHOLE = (1, 2, 3)
# CONSTANTS END

known = {}
cp.bindings(known)


def rest(a, c):
    """conc(a, b, c) with a and c known: every b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        yield c
    if a and c and a[0] == c[0]:            # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)
        yield from rest(a[1:], c[1:])


cp.relations(conc=rest)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = rest(s.constants["FIRST"], s.constants["WHOLE"])
        cp.pending("answers not yet generated", answers)
        for b in answers:
            known["b"] = b
            if not s.replay:
                cp.answer("b = %s" % show(b))
