# Build token spans from marker specs. A marker is "L@k" (k-th token of source line L, 0-based, negative from the end)
# or "L:text#n" (n-th token on line L whose text is `text`, n defaults to 1). Each span runs from its marker to the
# token before the next marker. Then METRICS.md rule 20 is applied mechanically: a separator (';' or ',') that ends a
# span is moved to the span that follows it, since it separates the construct that follows.
import csv, sys
ROOT = "/Users/christopherhay/cp-roles/classifier-A/results/algol-60/tokens/"
def load(text):
    rows = list(csv.DictReader(open(ROOT + text + ".tokens.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE))
    toks = [(int(r["index"]), int(r["line"]), r["token"]) for r in rows]
    assert [t[0] for t in toks] == list(range(len(toks)))
    byline = {}
    for i, l, t in toks:
        byline.setdefault(l, []).append((i, t))
    return toks, byline
def resolve(m, byline):
    if "@" in m:
        l, k = m.split("@"); l, k = int(l), int(k)
        return byline[l][k][0]
    l, rest = m.split(":", 1)
    l = int(l)
    if "#" in rest and rest.rsplit("#", 1)[1].isdigit():
        t, n = rest.rsplit("#", 1); n = int(n)
    else:
        t, n = rest, 1
    hits = [i for i, x in byline[l] if x == t]
    if len(hits) < n:
        raise KeyError(f"marker {m}: token {t!r} occurs {len(hits)} times on line {l}: {[x for _, x in byline[l]]}")
    return hits[n - 1]
def build(text, spec):
    toks, byline = load(text)
    pts = []
    for m, c, con, rule in spec:
        pts.append((resolve(m, byline), c, con, rule, m))
    pts.sort()
    idx = [p[0] for p in pts]
    if idx[0] != 0: raise ValueError(f"{text}: first marker is not token 0")
    if len(set(idx)) != len(idx):
        raise ValueError(f"{text}: duplicate marker positions {[p for p in pts if idx.count(p[0]) > 1]}")
    spans = []
    for j, (s, c, con, rule, m) in enumerate(pts):
        e = pts[j + 1][0] - 1 if j + 1 < len(pts) else len(toks) - 1
        spans.append({"from": s, "to": e, "class": c, "construct": con, "rule": rule})
    # rule 20
    for j in range(len(spans) - 1):
        a, b = spans[j], spans[j + 1]
        if toks[a["to"]][2] in (";", ",") and a["to"] > a["from"]:
            a["to"] -= 1; b["from"] -= 1
    # merge nothing; check cover
    cov = []
    for s in spans: cov.extend(range(s["from"], s["to"] + 1))
    assert cov == list(range(len(toks))), text
    return spans, toks
def show(text, spans, toks, file=sys.stdout):
    cls = {}
    for s in spans:
        for i in range(s["from"], s["to"] + 1): cls[i] = s["class"]
    lines = {}
    for i, l, t in toks:
        lines.setdefault(l, []).append(f"{t}/{cls[i]}")
    for l in sorted(lines):
        print(f"{l:4} " + " ".join(lines[l]), file=file)
