# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P13d (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"]: harnesses/python/README.md,
#       sections 3 and 8
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as (), so
#       that taking the tail is constant time (problems/13, "Representation"):
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960; the same encoding,
#       and revacc and racc as functions, in systems/python/measurement.md,
#       section 2
#     - each relation a function of its own, by its cases in order, in the
#       direction the query uses, "if not a:" as the dispatch on <>:
#       METRICS.md, rule 3; systems/python/README.md, "Units"
#     - a trailing underscore on a name that would shadow a built-in
#       (range_): PEP 8, "Naming Conventions", "Descriptive: Naming Styles"
#     - tuple unpacking: The Python Tutorial (3.13), "Tuples and Sequences"
#
# P13d. One stage: range(<k>, n, s) and revacc(s, r), in that order, n from
# s.params["n"].
# range, revacc and racc are transcribed forwards, each by its cases in
# order (revacc's one case; racc's cases 2 and 3 of the problem's list).
# racc is linear, but its last call is still a call: Python does not
# eliminate tail calls (The Python Language Reference, "Execution model",
# has none), so at CPython's default recursion limit (1000, not raised:
# harnesses/python/QUESTIONS.md, Q1) the program is expected to end in
# RecursionError from n of about 10^3: that error is the result
# (problems/13, "Representation").

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


def revacc(a):
    """revacc(a, b), forwards: b from a, by its one case."""
    return racc(a, ())                      # 1. revacc(a, b) if racc(a, <>, b)


def racc(a, c):
    """racc(a, c, b), forwards: b from a and c, by the definition's cases."""
    if not a:                               # 2. racc(<>, b, b)
        return c
    h, t = a                                # 3. racc(<h> ++ t, c, b)
    return racc(t, (h, c))                  #    if racc(t, <h> ++ c, b)


cp.relations(range=range_, revacc=revacc, racc=racc)


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
        known["r"] = revacc(known["s"])                                 # and revacc(s, r)
        if not st.replay:
            cp.answer("s = %s, r = %s" % (show(known["s"]), show(known["r"])))
