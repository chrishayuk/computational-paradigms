# Build the token spans from spec.py and check that every token of every
# text is covered exactly once. Reads only the token files of the batch.
import csv, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec import SPEC

REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
TOK = REPO + "/results/swi-prolog/tokens"

def load(path):
    rows = []
    with open(f"{TOK}/{path}.tokens.tsv") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            rows.append((int(row[0]), int(row[1]), row[2]))
    return rows

def resolve(rows, marker):
    m = re.match(r"^(\d+)(?::(.+?))?(?::(\d+))?([+-]\d+)?$", marker)
    # handle text that may itself contain ':' (like ':-'); parse manually
    off = 0
    mo = re.search(r"([+-]\d+)$", marker)
    body = marker
    if mo and not re.fullmatch(r"\d+", marker):
        off = int(mo.group(1)); body = marker[:mo.start()]
    parts = body.split(":", 1)
    line = int(parts[0])
    text, n = None, 1
    if len(parts) == 2:
        rest = parts[1]
        mm = re.match(r"^(.*):(\d+)$", rest)
        if mm and mm.group(1) != "":
            text, n = mm.group(1), int(mm.group(2))
        else:
            text = rest
    cands = [i for (i, l, t) in rows if l == line and (text is None or t == text)]
    if len(cands) < n:
        raise ValueError(f"marker {marker}: not found")
    return cands[n - 1] + off

def build(path):
    rows = load(path)
    segs = []
    for (mk, cls, cons, rule) in SPEC[path]:
        segs.append((resolve(rows, mk), cls, cons, rule, mk))
    starts = [s[0] for s in segs]
    if starts != sorted(starts) or len(set(starts)) != len(starts):
        raise ValueError(f"{path}: markers out of order: {[(s[4], s[0]) for s in segs]}")
    if starts[0] != 0:
        raise ValueError(f"{path}: first segment starts at {starts[0]}")
    out = []
    for k, (st, cls, cons, rule, mk) in enumerate(segs):
        to = segs[k + 1][0] - 1 if k + 1 < len(segs) else len(rows) - 1
        out.append({"from": st, "to": to, "class": cls, "construct": cons, "rule": rule})
    cov = [0] * len(rows)
    for s in out:
        for i in range(s["from"], s["to"] + 1):
            cov[i] += 1
    assert all(c == 1 for c in cov), path
    return rows, out

if __name__ == "__main__":
    texts = [l.split("\t")[0] for l in open(TOK + "/TEXTS-1C-P09-P11.tsv").read().splitlines()[1:]]
    missing = [t for t in texts if t not in SPEC]
    assert not missing, missing
    result = {}
    tot = {}
    verbose = "-v" in sys.argv
    for t in texts:
        rows, spans = build(t)
        result[t] = spans
        for s in spans:
            tot[s["class"]] = tot.get(s["class"], 0) + s["to"] - s["from"] + 1
        if verbose:
            print("=====", t)
            for s in spans:
                print(f'  {s["from"]:>3}-{s["to"]:<3} {s["class"]}  {" ".join(r[2] for r in rows[s["from"]:s["to"]+1])}')
    json.dump(result, open(os.path.dirname(os.path.abspath(__file__)) + "/tokens.json", "w"), indent=1)
    print("totals", tot, sum(tot.values()))
