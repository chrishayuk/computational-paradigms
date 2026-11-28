# Verify python.json: valid JSON; every token of every text of TEXTS-1C-P09-P10.tsv covered exactly once.
import json, csv
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
d = json.load(open("python.json"))
texts = [r[0] for r in csv.reader(open(f"{REPO}/results/python/tokens/TEXTS-1C-P09-P10.tsv"), delimiter="\t")][1:]
assert sorted(texts) == sorted(d["tokens"]), set(texts) ^ set(d["tokens"])
tot = {}
for t in texts:
    n = sum(1 for _ in open(f"{REPO}/results/python/tokens/{t}.tokens.tsv")) - 1
    cover = [0] * n
    for s in d["tokens"][t]:
        assert s["class"] in "PCRSH" and s["from"] <= s["to"]
        for i in range(s["from"], s["to"] + 1): cover[i] += 1
    assert all(c == 1 for c in cover), t
    for s in d["tokens"][t]:
        tot[s["class"]] = tot.get(s["class"], 0) + s["to"] - s["from"] + 1
print("ok", len(texts), "texts", sum(tot.values()), "tokens", tot)
