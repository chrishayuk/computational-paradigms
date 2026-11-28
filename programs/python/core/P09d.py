# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P09d, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - relations transcribed in the direction the query uses (genu: s from
#       n; sum3: total from s), one branch per case: METRICS.md, rules 2, 3
#       and 8 (the example of conc in Python)
#     - sequences as tuples, + on tuples, len, indexing: The Python Tutorial
#       (3.13), "Tuples and Sequences"; The Python Library Reference,
#       "Sequence Types -- list, tuple, range"
#
# P09d. One computation: genu(<k>, s) and sum3(s, total), in that order.
# The same text as this configuration's P09c, with genu in place of gen:
# genu, by its one case, gives s from n; then sum3 gives total from s. A
# sequence is a tuple, which is finite: genu calls itself without end, so
# the conjunction's first part never returns (expected: RecursionError).

# CONSTANTS BEGIN
# stage 1
GENU_FROM = 1
# CONSTANTS END

known = {}
cp.bindings(known)


def genu(n):
    """genu(n, s), forwards: s from n, by its one case."""
    return (n,) + genu(n + 1)               # 1. genu(n, <n> ++ rest) if genu(n + 1, rest)


def sum3(s):
    """sum3(s, total), forwards: total from s, by its one case; None if no
    case applies (s has fewer than three elements)."""
    if len(s) >= 3:                         # 1. sum3(<p, q, r> ++ m, total) if p + q + r = total
        p, q, r = s[0], s[1], s[2]
        return p + q + r


cp.relations(genu=genu, sum3=sum3)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        seq = genu(s.constants["GENU_FROM"])        # genu(<k>, s)
        known["s"] = seq
        total = sum3(seq)                           # and sum3(s, total)
        if total is None:
            del known["s"]
            if not s.replay:
                print("no solution: sum3 does not hold of s = %s" % show(seq))
        else:
            known["total"] = total
            if not s.replay:
                cp.answer("s = %s, total = %s" % (show(seq), total))
