# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core, of stdlib-concurrency and of extended for P13f
#   (one text, the same file in the three folders), written before any
#   program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"]: harnesses/python/README.md,
#       sections 3 and 8
#     - the native idiom: a list built from range() and reversed by a slice
#       with step -1: The Python Library Reference (3.13), "Built-in Types",
#       "Common Sequence Operations" (s[i:j:k]), "Ranges" and "Lists"; The
#       Python Tutorial, "The range() Function"
#     - an answer rendered with str.join and map: The Python Library
#       Reference, "str.join", "Built-in Functions" (map, str)
#
# P13f. One stage, native: build <1, ..., n> and reverse it, n from
# s.params["n"].
# Algorithm: the sequence is built as a Python list by list(range(...)),
# held in `xs` until the answer is given, and reversed into a new list r by
# the slice xs[::-1] (a copy in reverse order, made inside the built-in
# slicing, which no step counts). Built-ins used in place of the problem's
# relations (METRICS.md, rule 9): range() for building the sequence, the
# slice with step -1 for rev. Neither recurses.

# CONSTANTS BEGIN
# stage 1
START = 1
# CONSTANTS END

known = {}      # the bindings: unknown -> value
cp.bindings(known)

while (st := cp.stage()) is not None:
    if st.k == 1:
        xs = list(range(st.constants["START"], st.params["n"] + 1))    # build <1, ..., n>, held
        known["r"] = xs[::-1]                                           # and reverse it
        if not st.replay:
            cp.answer("r = ⟨%s⟩" % ",".join(map(str, known["r"])))
