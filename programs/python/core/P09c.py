# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P09c, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - relations transcribed in the direction the query uses (gen: s from n;
#       sum3: total from s), one branch per case, a case's guard as an if:
#       METRICS.md, rules 2, 3 and 8 (the example of conc in Python)
#     - sequences as tuples, + on tuples, len, indexing: The Python Tutorial
#       (3.13), "Tuples and Sequences"; The Python Library Reference,
#       "Sequence Types -- list, tuple, range"
#
# P09c. One computation: gen(<k>, s) and sum3(s, total), in that order.
# gen and sum3 are functions of their own, by their cases in order; the
# conjunction is evaluated in its order: gen gives s, then sum3 gives total
# from s. gen's last element (5 in the problem file) is part of gen's
# definition, kept in the constants block with the stage that poses it.

# CONSTANTS BEGIN
# stage 1
GEN_FROM = 1
GEN_LAST = 5
# CONSTANTS END

known = {}
cp.bindings(known)
definition = {}     # gen's last element, as stage 1 gives the definition


def gen(n):
    """gen(n, s), forwards: s from n, by the definition's cases."""
    if n > definition["last"]:              # 1. gen(n, <>) if n > 5
        return ()
    if n <= definition["last"]:             # 2. gen(n, <n> ++ rest) if n <= 5 and gen(n + 1, rest)
        return (n,) + gen(n + 1)


def sum3(s):
    """sum3(s, total), forwards: total from s, by its one case; None if no
    case applies (s has fewer than three elements)."""
    if len(s) >= 3:                         # 1. sum3(<p, q, r> ++ m, total) if p + q + r = total
        p, q, r = s[0], s[1], s[2]
        return p + q + r


cp.relations(gen=gen, sum3=sum3)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        definition["last"] = s.constants["GEN_LAST"]
        seq = gen(s.constants["GEN_FROM"])          # gen(<k>, s)
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
