# Checks python.json: valid JSON, every token of every text covered exactly once; prints totals.
import json, csv, collections
REPO = "."
d = json.load(open("results/python/classes/A/python.json"))
texts = [r[0] for r in list(csv.reader(open(REPO + "/results/python/tokens/TEXTS.tsv"), delimiter="\t"))[1:]]
assert sorted(texts) == sorted(d["tokens"]), "texts differ"
grand = collections.Counter(); byconf = collections.defaultdict(collections.Counter)
for t in texts:
    n = sum(1 for _ in open(REPO + "/results/python/tokens/" + t + ".tokens.tsv", encoding="utf-8")) - 1
    cov = [0] * n
    for s in d["tokens"][t]:
        assert s["class"] in "PCRSH" and len(s["class"]) == 1
        for i in range(s["from"], s["to"] + 1): cov[i] += 1
        grand[s["class"]] += s["to"] - s["from"] + 1
        byconf[t.split("/")[0]][s["class"]] += s["to"] - s["from"] + 1
    assert all(c == 1 for c in cov), t
print("all", len(texts), "texts covered exactly once; tokens", sum(grand.values()), dict(grand))
for c, v in byconf.items(): print(c, sum(v.values()), dict(v))
oc = collections.Counter((e["semantic"], e["representation"], e.get("simplification")) for e in d["outcomes"])
for k, v in sorted(oc.items(), key=str): print(v, k)
print(collections.Counter(tuple(e["execution_state"]) for e in d["outcomes"]))
print(collections.Counter((e["configuration"], e["expressibility"]) for e in d["expressibility"]))
