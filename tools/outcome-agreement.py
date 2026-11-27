#!/usr/bin/env python3
"""Compare two classifiers' stage outcomes for one system.

    tools/outcome-agreement.py A.json B.json

Each file is a classifier's output (sandbox/briefs/classifier.md). Stages
are matched on (configuration, instance, program, stage). Where a
classifier gives several entries for one stage (one per reading of P01c,
or one per attempt), the attempts before a final attempt are dropped and
the remaining entries are compared as a set. Simplification and the identical-to-posed flag
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
        out[(e["configuration"], e["instance"], e["program"], e["stage"])].append(e)
    return out

def flat(v):
    return v if isinstance(v, tuple) else (v,)

A, B = load(sys.argv[1]), load(sys.argv[2])
keys = sorted(set(A) | set(B), key=str)
agree = collections.Counter(); diffs = []
for k in keys:
    a, b = A.get(k, []), B.get(k, [])
    if not a or not b:
        diffs.append((k, "missing in " + ("A" if not a else "B"), None, None)); continue
    unreached = all(norm(e.get("reached")) == "false" for e in a + b)
    residual = any(norm(e.get("representation")) == "residual" for e in a + b)
    for ax in AXES:
        if ax in ("simplification", "identical_to_posed") and not residual:
            agree[ax] += 1; continue                # applies to a residual only (SPECIFICATION, Outcomes 2)
        if ax != "reached" and unreached:
            agree[ax] += 1; continue                # both: not reached (AMENDMENTS 3.2); nothing to class
        sa = sorted({x for e in a for x in flat(norm(e.get(ax)))}, key=str)
        sb = sorted({x for e in b for x in flat(norm(e.get(ax)))}, key=str)
        if sa == sb: agree[ax] += 1
        else: diffs.append((k, ax, sa, sb))
print(f"stages: {len(keys)} (A {len(A)}, B {len(B)})")
for ax in AXES:
    print(f"  {ax}: {agree[ax]}/{len(keys)}")
print("\ndifferences (stage, axis, A, B):")
for d in diffs:
    print("  ", *d, sep=" | ")
