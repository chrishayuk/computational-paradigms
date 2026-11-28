# Show each line with the class of each token, from spans.json (read-only check).
import json, sys, csv
REPO = "."
text = sys.argv[1]
spans = json.load(open("spans.json"))[text]
cls = {}
for s in spans:
    for i in range(s["from"], s["to"] + 1): cls[i] = s["class"]
lines = {}
with open(f"{REPO}/results/python/tokens/{text}.tokens.tsv") as f:
    r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE); next(r)
    for row in r: lines.setdefault(int(row[1]), []).append((int(row[0]), row[2]))
for n in sorted(lines):
    segs = []; cur = None
    for i, t in lines[n]:
        t = {"<NEWLINE>": "⏎", "<INDENT>": "→", "<DEDENT>": "←"}.get(t, t)
        if cls[i] != cur:
            segs.append(f"[{cls[i]}]"); cur = cls[i]
        segs.append(t)
    print(f"L{n:<4d}", " ".join(segs))
