# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core, of stdlib-concurrency and of extended for P13e
#   (one text, the same file in the three folders), written before any
#   program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"]: harnesses/python/README.md,
#       sections 3 and 8
#     - the native idiom: a list built from range() and summed with the
#       built-in sum(): The Python Library Reference (3.13), "Built-in
#       Functions" (sum), "Built-in Types", "Ranges" and "Lists"; The Python
#       Tutorial, "The range() Function" (list(range(...)))
#
# P13e. One stage, native: build <1, ..., n> and sum it, n from
# s.params["n"].
# Algorithm: the sequence is built as a Python list by list(range(...))
# (a loop inside the built-ins, which no step counts), held in `xs` until the
# answer is given, and summed by the built-in sum() (also a loop inside a
# built-in). Built-ins used in place of the problem's relations (METRICS.md,
# rule 9): range() for building the sequence, sum() for sum. Neither
# recurses, so no recursion limit is reached.

# CONSTANTS BEGIN
# stage 1
START = 1
# CONSTANTS END

known = {}      # the bindings: unknown -> value
cp.bindings(known)

while (st := cp.stage()) is not None:
    if st.k == 1:
        xs = list(range(st.constants["START"], st.params["n"] + 1))    # build <1, ..., n>, held
        known["k"] = sum(xs)                                            # and sum it
        if not st.replay:
            cp.answer("k = %d" % known["k"])
