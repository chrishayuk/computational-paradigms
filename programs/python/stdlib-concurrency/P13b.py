# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P13b (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"]: harnesses/python/README.md,
#       sections 3 and 8
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as (), so
#       that taking the tail is constant time (problems/13, "Representation"):
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960; the same encoding
#       in systems/python/measurement.md, section 2
#     - each relation a function of its own, by its cases in order, in the
#       direction the query uses, "if not a:" as the dispatch on <>:
#       METRICS.md, rule 3; systems/python/README.md, "Units" (problem
#       operations: "each defined relation is therefore written as a
#       function of its own")
#     - a trailing underscore on a name that would shadow a built-in
#       (range_, sum_): PEP 8, "Naming Conventions", "Descriptive: Naming
#       Styles" (single_trailing_underscore_)
#     - tuple unpacking: The Python Tutorial (3.13), "Tuples and Sequences"
#
# P13b. One stage: range(<k>, n, s) and sum(s, k), in that order, n from
# s.params["n"].
# range and sum are transcribed forwards (s from m and n; k from s), each by
# its cases in order; sum's body keeps its conjuncts in order (sum(t, j),
# then k = h + j). Both call themselves once per element, so at CPython's
# default recursion limit (1000, not raised: harnesses/python/QUESTIONS.md,
# Q1) they are expected to end in RecursionError from n of about 10^3: that
# error is the result (problems/13, "Representation").

# CONSTANTS BEGIN
# stage 1
START = 1
# CONSTANTS END

known = {}      # the bindings: unknown -> value
cp.bindings(known)


def range_(m, n):
    """range(m, n, s), forwards: s from m and n, by the definition's cases."""
    if m > n:                               # 1. range(m, n, <>) if m > n
        return ()
    if m <= n:                              # 2. range(m, n, <m> ++ t) if m <= n
        return (m, range_(m + 1, n))        #    and range(m + 1, n, t)


def sum_(s):
    """sum(s, k), forwards: k from s, by the definition's cases."""
    if not s:                               # 1. sum(<>, 0)
        return 0
    h, t = s                                # 2. sum(<h> ++ t, k)
    j = sum_(t)                             #    if sum(t, j)
    return h + j                            #    and k = h + j


cp.relations(range=range_, sum=sum_)


def show(s):
    """Output adapter: a sequence of cons cells as the problem writes it,
    without recursion."""
    items = []
    while s:
        h, s = s
        items.append(str(h))
    return "⟨" + ",".join(items) + "⟩"


while (st := cp.stage()) is not None:
    if st.k == 1:
        known["s"] = range_(st.constants["START"], st.params["n"])     # range(<k>, n, s)
        known["k"] = sum_(known["s"])                                   # and sum(s, k)
        if not st.replay:
            cp.answer("s = %s, k = %d" % (show(known["s"]), known["k"]))
