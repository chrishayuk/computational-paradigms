"""Build token spans from tokens_spec.SPECS; check coverage; print per-line view.

Usage: python3 build_tokens.py REPO_ROOT [--show TEXT]
Writes tokens.json beside this script.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens_spec import SPECS  # noqa: E402

root = sys.argv[1]
show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None
LAYOUT = ("<INDENT>", "<DEDENT>")


def load_tokens(text):
    path = os.path.join(root, "results/python/tokens", text + ".tokens.tsv")
    rows = [l.rstrip("\n").split("\t") for l in open(path)][1:]
    return [(int(i), int(ln), t) for i, ln, t in rows]


def resolve(text, toks, marker):
    anchor, occ, col, cls, construct, rule = marker
    src = open(os.path.join(root, "programs/python", text)).read().split("\n")
    lines = [n + 1 for n, l in enumerate(src) if l.strip().startswith(anchor)]
    if not lines:
        raise SystemExit(f"{text}: anchor not found: {anchor!r}")
    ln = lines[occ]
    on_line = [t for t in toks if t[1] == ln]
    if not on_line:
        raise SystemExit(f"{text}: no tokens on line {ln} ({anchor!r})")
    if col is None:
        k = next(n for n, t in enumerate(on_line) if t[2] not in LAYOUT)
    elif isinstance(col, int):
        k = col if col >= 0 else len(on_line) + col
    elif col.startswith("tok:") or col.startswith("after:"):
        kind, rest = col.split(":", 1)
        parts = rest.rsplit(":", 1) if rest.count(":") and rest.rsplit(":", 1)[1].isdigit() else [rest]
        x, nth = parts[0], int(parts[1]) if len(parts) > 1 else 0
        hits = [n for n, t in enumerate(on_line) if t[2] == x]
        k = hits[nth] + (1 if kind == "after" else 0)
    else:
        raise SystemExit("bad col " + col)
    return on_line[k][0], (cls, construct, rule)


out = {}
for text, markers in SPECS.items():
    toks = load_tokens(text)
    starts = {}
    for m in markers:
        i, val = resolve(text, toks, m)
        if i in starts and starts[i] != val:
            raise SystemExit(f"{text}: two markers at {i}: {starts[i]} / {val}")
        starts[i] = val
    if 0 not in starts:
        raise SystemExit(f"{text}: no marker at 0")
    cur, stack, assigned = None, [], []
    for i, ln, t in toks:
        if i in starts:
            cur = starts[i]
        if t == "<INDENT>":
            stack.append(cur)
            assigned.append(cur)
        elif t == "<DEDENT>":
            assigned.append(stack.pop())
        else:
            assigned.append(cur)
    spans = []
    for (i, ln, t), val in zip(toks, assigned):
        if spans and spans[-1]["_v"] == val and spans[-1]["to"] == i - 1:
            spans[-1]["to"] = i
        else:
            spans.append({"from": i, "to": i, "class": val[0], "construct": val[1], "rule": val[2], "_v": val})
    for s in spans:
        del s["_v"]
    # coverage check
    covered = [0] * len(toks)
    for s in spans:
        for i in range(s["from"], s["to"] + 1):
            covered[i] += 1
    assert all(c == 1 for c in covered), text
    assert [t[0] for t in toks] == list(range(len(toks))), text
    out[text] = spans
    if show == text:
        by_line = {}
        for (i, ln, t), val in zip(toks, assigned):
            by_line.setdefault(ln, []).append(f"{t}/{val[0]}")
        for ln in sorted(by_line):
            print(f"{ln:>4} {' '.join(by_line[ln])}")

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokens.json"), "w"), indent=1, ensure_ascii=False)
for text, spans in out.items():
    tot = {}
    for s in spans:
        tot[s["class"]] = tot.get(s["class"], 0) + s["to"] - s["from"] + 1
    print(text, sum(tot.values()), dict(sorted(tot.items())))
