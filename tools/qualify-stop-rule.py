#!/usr/bin/env python3
"""Qualify run-batch.py's P13 rule (larger n not run after a run stopped by a limit).

    tools/qualify-stop-rule.py RESULTS_ROOT_CHECKOUT

For every P13 (configuration, sub-problem, instance, program, mode) with records
under CHECKOUT/results, the driver's smaller_n_stopped() is evaluated three ways:
primaries before named variants, named variants before primaries (each with a fresh
module, so a fresh cache), and by an oracle written here that reads every record
afresh, without the driver's helpers. All three must agree. Then two fixed cases:
a record named *.INVALID.json that was stopped must not trigger the rule, and a
stopped record of another program must not either. Prints the disagreements and a
count; exits 1 if there is any.
"""
import copy, glob, gzip, importlib.util, json, os, shutil, sys, tempfile

co = sys.argv[1]
drv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run-batch.py")

def fresh():
    spec = importlib.util.spec_from_file_location("rb", drv)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def load(p):
    return json.load(gzip.open(p) if p.endswith(".gz") else open(p))

def oracle_stopped(r):
    for st in r["stages"]:
        for a in st["attempts"]:
            if a["safety_limit"]["hit"]:
                return True
            for c in a["computations"]:
                if c["steps"]["budget_exhausted"] or {"budget", "timeout"} & set(c["execution_state"]["states"]):
                    return True
                if any(q["ended_by"] in ("budget", "timeout") for q in c["queries"]):
                    return True
    return False

def oracle(out, sp, inst, prog, mode):
    n = inst["parameters"]["n"]
    for other in sp["instances"]:
        if other["parameters"]["n"] >= n:
            continue
        for f in sorted(os.listdir(out)):
            if f.startswith(other["id"] + "." + mode + ".") and ".INVALID." not in f and f.endswith((".json", ".json.gz")):
                r = load(os.path.join(out, f))
                if r["run"]["program"]["path"] == prog and oracle_stopped(r):
                    return other["id"]
    return None

os.chdir(co)
p13 = [p for p in json.load(open("harnesses/stages.json"))["problems"] if p["problem"] == "P13"][0]
cases = set()
for f in glob.glob("results/*/*/P13/raw/*.json") + glob.glob("results/*/*/P13/raw/*.json.gz"):
    if ".INVALID." in f:
        continue
    r = load(f)["run"]
    cases.add((os.path.dirname(f) + "/", r["subproblem"], r["program"]["path"], r["mode"]))
sps = {sp["id"]: sp for sp in p13["subproblems"]}
rows = sorted((out, sp, inst["id"], prog, mode) for out, sp, prog, mode in cases for inst in sps[sp]["instances"])
primary_first = sorted(rows, key=lambda x: ("/variants/" in x[3], x))
variant_first = sorted(rows, key=lambda x: ("/variants/" not in x[3], x))
res = {}
for name, order in (("primary-first", primary_first), ("variant-first", variant_first)):
    m = fresh()
    for out, sp, iid, prog, mode in order:
        inst = [i for i in sps[sp]["instances"] if i["id"] == iid][0]
        res.setdefault((out, sp, iid, prog, mode), {})[name] = m.smaller_n_stopped(out, sps[sp], inst, prog, mode)
bad = 0
for (out, sp, iid, prog, mode), v in sorted(res.items()):
    inst = [i for i in sps[sp]["instances"] if i["id"] == iid][0]
    v["oracle"] = oracle(out, sps[sp], inst, prog, mode)
    if len(set(v.values())) != 1:
        bad += 1; print("DISAGREE", out, iid, prog, mode, v)
print(f"{len(res)} cases (instance, program, mode), {sum(1 for v in res.values() if v['oracle'])} stopped by a smaller n; disagreements: {bad}")

# fixed cases, in a scratch copy
tmp = tempfile.mkdtemp()
src = next((f for f in glob.glob("results/*/*/P13/raw/*.json") if ".INVALID." not in f and oracle_stopped(load(f))), None)
if src:
    r = load(src); run = r["run"]; sp = sps[run["subproblem"]]
    small, big = sp["instances"][0], sp["instances"][-1]
    rr = copy.deepcopy(r); rr["run"]["instance"] = small["id"]
    name = f"{small['id']}.{run['mode']}.20990101T000000Z"
    json.dump(rr, open(f"{tmp}/{name}.INVALID.json", "w"))
    got = fresh().smaller_n_stopped(tmp + "/", sp, big, run["program"]["path"], run["mode"])
    print("an INVALID record that was stopped triggers the rule:", got is not None); bad += got is not None
    os.remove(f"{tmp}/{name}.INVALID.json")
    json.dump(rr, open(f"{tmp}/{name}.json", "w"))
    got = fresh().smaller_n_stopped(tmp + "/", sp, big, run["program"]["path"] + ".other", run["mode"])
    print("a stopped record of another program triggers the rule:", got is not None); bad += got is not None
    got = fresh().smaller_n_stopped(tmp + "/", sp, big, run["program"]["path"], run["mode"])
    print("a stopped record of the same program triggers the rule:", got is not None); bad += got is None
shutil.rmtree(tmp)
sys.exit(1 if bad else 0)
