"""Compare two classifiers' classes for the calibration programs.

    python3 agreement.py A.json B.json TOKENS_DIR

Each classifier's file maps a program path to a list of spans
{"from": i, "to": j, "class": "P|C|R|S|H", "construct": ..., "rule": ...},
inclusive token indices, covering every token of the program's
.tokens.tsv. Prints, per program and per system: tokens, each
classifier's totals by class, agreement, and the disagreeing tokens with
their constructs.
"""
import collections
import json
import os
import sys

CLASSES = "PCRSH"


def expand(spans, n, who, prog):
    cls = [None] * n
    for s in spans:
        for i in range(s["from"], s["to"] + 1):
            if 0 <= i < n:
                cls[i] = (s["class"], s.get("construct", ""), s.get("rule", ""))
    missing = [i for i, c in enumerate(cls) if c is None]
    if missing:
        print(f"  ! {who} left {len(missing)} tokens of {prog} unclassed: {missing[:10]}")
    return cls


def main(a_path, b_path, tok_dir):
    A, B = json.load(open(a_path)), json.load(open(b_path))
    per_system = collections.defaultdict(lambda: [0, 0])
    by_class = collections.Counter()
    for prog in sorted(set(A) | set(B)):
        tsv = os.path.join(tok_dir, prog + ".tokens.tsv")
        toks = [l.rstrip("\n").split("\t") for l in open(tsv, encoding="utf-8")][1:]
        n = len(toks)
        a = expand(A.get(prog, []), n, "A", prog)
        b = expand(B.get(prog, []), n, "B", prog)
        agree = sum(1 for x, y in zip(a, b) if x and y and x[0] == y[0])
        tot = lambda c: collections.Counter(x[0] for x in c if x)
        ta, tb = tot(a), tot(b)
        print(f"\n## {prog}: {n} tokens, agreement {agree}/{n} ({100*agree/max(n,1):.1f}%)")
        print("  class  A      B")
        for c in CLASSES:
            print(f"  {c}      {ta[c]:<6} {tb[c]}")
        system = prog.split("/")[0]
        per_system[system][0] += agree
        per_system[system][1] += n
        runs = []
        for i, (x, y) in enumerate(zip(a, b)):
            if x and y and x[0] != y[0]:
                by_class[(x[0], y[0])] += 1
                if runs and runs[-1][1] == i - 1 and runs[-1][2] == (x[0], y[0]):
                    runs[-1][1] = i
                else:
                    runs.append([i, i, (x[0], y[0]), x[1], y[1]])
        for r in runs:
            text = " ".join(toks[k][2] for k in range(r[0], r[1] + 1))
            print(f"  tokens {r[0]}-{r[1]} A={r[2][0]} B={r[2][1]}: {text[:80]}")
            print(f"      A: {r[3][:70]} | B: {r[4][:70]}")
    print("\n## per system")
    for s, (g, n) in sorted(per_system.items()):
        print(f"  {s}: {g}/{n} ({100*g/max(n,1):.1f}%)")
    print("\n## disagreements by (A, B) class")
    for k, v in by_class.most_common():
        print(f"  {k[0]}→{k[1]}: {v}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
