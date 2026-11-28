import json, sys, glob, os, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from summarize import summ, ROOT
mode = sys.argv[1]
groups = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(ROOT, "*/P0[5-8]/raw/*.json"))):
    s = summ(p)
    if s["mode"] != mode: continue
    conf = s["path"].split("/")[0]
    sig = []
    for d in s["stages"]:
        sig.append((d["stage"], d["attempt"], d["posed"], tuple(d.get("answers", [])), d.get("ended_by"), tuple(d.get("states") or []),
                    d["observe"], re.sub(r"_[0-9]+", "_N", d.get("err") or ""), json.dumps(d.get("susp"), sort_keys=True)))
    groups[(s["instance"], s["program"])].append((conf, tuple(sig), s["path"]))
for k, v in sorted(groups.items()):
    by = collections.defaultdict(list)
    for conf, sig, path in v: by[sig].append(conf)
    print(k, " | ".join(",".join(c) for c in by.values()))
