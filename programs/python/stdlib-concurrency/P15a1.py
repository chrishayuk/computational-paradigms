# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P15a1 (one text,
#   the same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation with several solutions as a generator of them, by its
#       cases in order, each case's recursive solutions taken with a for
#       loop; one solution taken with next(), the generator left suspended:
#       The Python Language Reference (3.13), "Yield expressions"; PEP 255,
#       "Simple Generators"; The Python Library Reference, "Built-in
#       Functions" (next with a default); this configuration's P03b and
#       P11a programs
#     - sequences as tuples, indexing and slicing, + on tuples, "if not a:"
#       as the test of <>: The Python Tutorial, "Tuples and Sequences";
#       METRICS.md, rule 3
#
# P15a1. One stage: merge(<seq>, <seq>, m), any one.
# merge is transcribed forwards (m from a and b) as a generator of its
# solutions, by its four cases in order, depth first: case 3 (take a's head)
# before case 4 (take b's head). One solution is taken; the generator is
# left suspended, holding the others, and registered as pending.

# CONSTANTS BEGIN
# stage 1
FIRST = (1, 2)
SECOND = (3, 4)
# CONSTANTS END

known = {}      # the bindings: unknown -> value
cp.bindings(known)


def merge(a, b):
    """merge(a, b, m), forwards: the interleavings m of a and b, by the
    definition's cases in order."""
    if not a:                                   # 1. merge(<>, b, b)
        yield b
    if a and not b:                             # 2. merge(<h> ++ a, <>, <h> ++ a)
        yield a
    if a and b:                                 # 3. merge(<h> ++ a, b, <h> ++ m) if b != <>
        for m in merge(a[1:], b):               #    and merge(a, b, m)
            yield (a[0],) + m
    if b and a:                                 # 4. merge(a, <h> ++ b, <h> ++ m) if a != <>
        for m in merge(a, b[1:]):               #    and merge(a, b, m)
            yield (b[0],) + m


cp.relations(merge=merge)


def show(x):
    """Output adapter: a sequence as the problem writes it."""
    return "⟨" + ",".join(str(e) for e in x) + "⟩"


while (st := cp.stage()) is not None:
    if st.k == 1:
        interleavings = merge(st.constants["FIRST"], st.constants["SECOND"])
        cp.pending("merge's solutions not yet taken", interleavings)
        m = next(interleavings, None)                           # any one
        if m is None:
            if not st.replay:
                print("no solution: merge has no solution for these sequences")
        else:
            known["m"] = m
            if not st.replay:
                cp.answer("m = %s" % show(m))
