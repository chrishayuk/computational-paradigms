import json, sys, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from summarize import summ, ROOT
mode = sys.argv[1]; pats = sys.argv[2:]
for pat in pats:
  for p in sorted(glob.glob(os.path.join(ROOT, pat))):
    s = summ(p)
    if s["mode"] != mode: continue
    print("###", s["path"], s["program"], "complete=%s" % s["complete"], "faults=%s" % s["harness_faults"], "manual=%s" % s["manual_actions"])
    if s["incomplete_reason"]: print("   incomplete:", s["incomplete_reason"])
    for d in s["stages"]:
        print("  st%d a%d %s ans=%s end=%s states=%s obs=%r susp=%s pd=%s%s%s%s" % (d["stage"], d["attempt"], d["posed"], [a.replace("\n","\\n") for a in d.get("answers",[])], d.get("ended_by"), d.get("states"), d["observe"], d.get("susp"), d.get("alt",{}).get("problem_defined"),
              (" ERR=" + d["err"].replace("\n"," | ")) if d.get("err") else "", (" SEP=" + d["separate_run"]) if d.get("separate_run") else "", (" STDERR="+d["stderr"].replace("\n"," | ")) if d.get("stderr") else ""))
