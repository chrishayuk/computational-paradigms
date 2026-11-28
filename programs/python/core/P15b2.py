# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P15b2, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a stream, a sequence that may be infinite, as () or a pair of its
#       head and its delayed rest (a function of no arguments that gives the
#       rest when it is called): Abelson and Sussman, *Structure and
#       Interpretation of Computer Programs*, MIT Press, 1985, section 3.4
#       ("Streams": cons-stream, delay and force); Friedman and Wise, "CONS
#       should not evaluate its arguments", Automata, Languages and
#       Programming, 1976; in Python, lambda for the delay: The Python
#       Language Reference (3.13), "Lambdas"
#     - each relation a function of its own, by its cases in order, in the
#       direction the query uses: METRICS.md, rule 3
#
# P15b2. One stage: zeros(z) and merge(<seq>, z, m) and position(<k>, m, i),
# in that order, any one, under the stream reading: P15b with the arguments
# of merge swapped. The same text as this configuration's P15b, but for that.
# Python's tuples are finite, so the stream reading is taken with streams
# whose rest is delayed (a reformulation of the representation). zeros, read
# as the greatest relation, is the stream <0> ++ zeros. merge gives one
# interleaving, as a stream: its head by the first of the definition's cases
# that applies, in their order, its rest delayed (the merge of the case's
# body). position is transcribed forwards (i from e and m), forcing m's rest
# only as far as it reads. With <9> first, case 3 takes its head first.

# CONSTANTS BEGIN
# stage 1
OTHER = (9,)
SOUGHT = 9
# CONSTANTS END

NIL = ()
known = {}      # the bindings: unknown -> value
cp.bindings(known)


def stream(seq):
    """The encoding of a given finite sequence as a stream: () or a pair of
    its head and its delayed rest."""
    t = NIL
    for e in reversed(seq):
        t = (e, lambda rest=t: rest)
    return t


def zeros():
    """zeros(s), read as the greatest relation: s as a stream, its rest the
    stream of the case's body, delayed."""
    return (0, zeros)                           # 1. zeros(<0> ++ s) if zeros(s)


def merge(a, b):
    """merge(a, b, m), forwards, for any one m: m as a stream, its head by
    the first case that applies, in the definition's order, its rest the
    merge of that case's body, delayed."""
    if a == NIL:                                # 1. merge(<>, b, b)
        return b
    if b == NIL:                                # 2. merge(<h> ++ a, <>, <h> ++ a)
        return a
    h, rest = a
    if b != NIL:                                # 3. merge(<h> ++ a, b, <h> ++ m) if b != <>
        return (h, lambda: merge(rest(), b))    #    and merge(a, b, m)
    k, rest_b = b                               # 4. merge(a, <h> ++ b, <h> ++ m) if a != <>
    return (k, lambda: merge(a, rest_b()))      #    and merge(a, b, m)


def position(e, m):
    """position(e, m, i), forwards: i from e and m, by the definition's
    cases in order; None where no case holds."""
    if m == NIL:                                # no case holds of <>
        return None
    h, rest = m
    if h == e:                                  # 1. position(e, <e> ++ t, 1)
        return 1
    if h != e:                                  # 2. position(e, <h> ++ t, i) if h != e
        j = position(e, rest())                 #    and position(e, t, j)
        if j is not None:
            return j + 1                        #    and i = j + 1


cp.relations(zeros=zeros, merge=merge, position=position)


while (st := cp.stage()) is not None:
    if st.k == 1:
        z = zeros()                                             # zeros(z)
        m = merge(stream(st.constants["OTHER"]), z)             # and merge(<9>, z, m)
        i = position(st.constants["SOUGHT"], m)                 # and position(9, m, i)
        if i is None:
            if not st.replay:
                print("no solution: no position of %r in m" % st.constants["SOUGHT"])
        else:
            known["i"] = i
            if not st.replay:
                cp.answer("i = %d" % i)
