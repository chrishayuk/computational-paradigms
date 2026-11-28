# Build the token spans of python.json from specs.py, and check coverage.
import csv, json, sys, importlib
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
LAYOUT = {"<NEWLINE>", "<INDENT>", "<DEDENT>"}
def tokens(text):
    out = []
    with open(f"{REPO}/results/python/tokens/{text}.tokens.tsv") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            out.append((int(row[0]), int(row[1]), row[2]))
    return out
def build(text, spec):
    toks = tokens(text)
    n = len(toks)
    assert [t[0] for t in toks] == list(range(n)), text
    byline = {}
    for i, ln, s in toks:
        byline.setdefault(ln, []).append(i)
    cls = [None] * n
    for sel, c, construct, rule in spec:
        if isinstance(sel, str):
            a, _, b = sel[1:].partition("-")
            a = int(a); b = int(b) if b else a
            idx = [i for ln in range(a, b + 1) for i in byline.get(ln, [])]
            if not idx: raise SystemExit(f"{text}: no tokens on {sel}")
        elif isinstance(sel, tuple):
            idx = list(range(sel[0], sel[1] + 1))
        else:
            idx = [sel]
        for i in idx:
            cls[i] = (c, construct, rule)
    # every read of s.constants (and its subscript) is H (harness README 7.3)
    for i in range(n - 2):
        if toks[i][2] == "s" and toks[i+1][2] == "." and toks[i+2][2] == "constants":
            j = i + 2
            if j + 3 < n and toks[j+1][2] == "[" and toks[j+3][2] == "]":
                j += 3
            for k in range(i, j + 1):
                cls[k] = ("H", "s.constants", "reading s.constants (harness README 7.3)")
    # layout-only lines unassigned: take the class of the next assigned token (rule 20), else previous
    for i in range(n):
        if cls[i] is None:
            ln = toks[i][1]
            if all(toks[j][2] in LAYOUT for j in byline[ln]):
                j = i + 1
                while j < n and (cls[j] is None and all(toks[k][2] in LAYOUT for k in byline[toks[j][1]])):
                    j += 1
                if j < n and cls[j] is not None:
                    cls[i] = cls[j]
                else:
                    k = i - 1
                    while k >= 0 and cls[k] is None: k -= 1
                    cls[i] = cls[k]
    missing = [toks[i] for i in range(n) if cls[i] is None]
    if missing: raise SystemExit(f"{text}: unclassed tokens {missing[:20]}")
    spans = []
    for i in range(n):
        if spans and spans[-1]["_k"] == cls[i]:
            spans[-1]["to"] = i
        else:
            spans.append({"from": i, "to": i, "class": cls[i][0], "construct": cls[i][1], "rule": cls[i][2], "_k": cls[i]})
    for s in spans: del s["_k"]
    return spans, n
if __name__ == "__main__":
    import specs
    importlib.reload(specs)
    allspans = {}
    totals = {}
    for text, spec in specs.SPEC.items():
        spans, n = build(text, spec)
        allspans[text] = spans
        t = {}
        for s in spans:
            t[s["class"]] = t.get(s["class"], 0) + s["to"] - s["from"] + 1
        assert sum(t.values()) == n
        totals[text] = (n, t)
        print(f"{text:32s} {n:5d} " + " ".join(f"{k}={t.get(k,0)}" for k in "PCRSH"))
    json.dump(allspans, open("spans.json", "w"), ensure_ascii=False, indent=0)
    if len(sys.argv) > 1:
        for s in allspans[sys.argv[1]]:
            print(s)
