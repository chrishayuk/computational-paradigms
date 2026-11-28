#!/usr/bin/env python3
"""Compare two classifiers' stage outcomes for one system.

    tools/outcome-agreement.py A.json B.json

Each file is a classifier's output (sandbox/briefs/classifier.md). Stages
are matched on (configuration, instance, program, stage). Where a
classifier gives several entries for one stage (one per reading of P01c,
or one per attempt), the attempts before a final attempt are dropped and
the remaining entries are compared as a set, value by reading where readings are given (as an
object {reading: value}, or as one entry per reading). Simplification and the identical-to-posed flag
are compared only where either classifier gives a residual, and a stage
both classifiers mark not reached is compared on that alone. Prints, per axis, the
agreement, and every stage on which the classifiers differ, with both.
"""
import collections, json, sys

AXES = ["reached", "semantic", "representation", "simplification", "identical_to_posed", "execution_state"]

def norm(v):
    if isinstance(v, str) and "reading" in v:      # "complete (rational reading); unsound (finite reading)"
        return tuple(sorted(x.split("(")[0].strip().lower() for x in v.split(";")))
    if isinstance(v, list):
        return tuple(sorted(str(x).lower() for x in v))
    return None if v is None else str(v).lower()

def load(path):
    out = collections.defaultdict(list)
    for e in json.load(open(path))["outcomes"]:
        if e.get("final_attempt") is False:
            continue
        prog = e["program"]
        if prog.startswith(e["configuration"] + "/"):   # some give the program as <configuration>/<file>
            prog = prog[len(e["configuration"]) + 1:]
        out[(e["configuration"], e["instance"], prog, e["stage"])].append(e)
    return out

def per_reading(e, ax):
    """An axis's value(s), paired with the reading where a classifier gives
    readings: either as an object {reading: value} on one entry, or as one
    entry per reading with a `reading` field. Values without a reading are
    compared as they are."""
    v = e.get(ax)
    if isinstance(v, str) and "reading)" in v:  # "complete (rational reading); unsound (finite reading)"
        return {f"{x.split('(')[1].split()[0]}: {x.split('(')[0].strip().lower()}" for x in v.split(";")}
    if isinstance(v, dict):
        return {f"{k}: {norm(x)}" for k, x in v.items()}
    if isinstance(v, str) and ": " in v and ax in ("semantic", "simplification"):   # "open: complete; closed: unsound"
        return {x.strip().lower() for x in v.split(";")}
    if e.get("reading") and ax in ("semantic", "simplification"):
        return {f"{e['reading']}: {x}" for x in flat(norm(v))}
    return set(flat(norm(v)))


def flat(v):
    return v if isinstance(v, tuple) else (v,)

def compare(a, b):
    """The axes on which two classifiers' entries for one stage differ, as
    [(axis, A's values, B's values)]; [] if they agree."""
    out = []
    unreached = all(norm(e.get("reached")) == "false" for e in a + b)
    residual = any(norm(e.get("representation")) == "residual" for e in a + b)
    for ax in AXES:
        if ax in ("simplification", "identical_to_posed") and not residual:
            continue                                # applies to a residual only (SPECIFICATION, Outcomes 2)
        if ax != "reached" and unreached:
            continue                                # both: not reached (AMENDMENTS 3.2); nothing to class
        sa = sorted({x for e in a for x in per_reading(e, ax)}, key=str)
        sb = sorted({x for e in b for x in per_reading(e, ax)}, key=str)
        labelled = lambda s: s and all(isinstance(x, str) and ": " in x for x in s)
        if labelled(sa) != labelled(sb):        # one value given without readings: the same under every reading
            strip = lambda s: sorted({x.split(": ", 1)[1] if isinstance(x, str) and ": " in x else x for x in s}, key=str)
            sa, sb = strip(sa), strip(sb)
        if sa != sb:
            out.append((ax, sa, sb))
    return out


def main(a_path, b_path):
    A, B = load(a_path), load(b_path)
    keys = sorted(set(A) | set(B), key=str)
    agree = collections.Counter(); diffs = []
    for k in keys:
        a, b = A.get(k, []), B.get(k, [])
        if not a or not b:
            diffs.append((k, "missing in " + ("A" if not a else "B"), None, None)); continue
        d = compare(a, b)
        bad = {x[0] for x in d}
        for ax in AXES:
            if ax not in bad:
                agree[ax] += 1
        diffs += [(k,) + x for x in d]
    print(f"stages: {len(keys)} (A {len(A)}, B {len(B)})")
    for ax in AXES:
        print(f"  {ax}: {agree[ax]}/{len(keys)}")
    print("\ndifferences (stage, axis, A, B):")
    for d in diffs:
        print("  ", *d, sep=" | ")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
