#!/usr/bin/env python3
"""Labelled measurement reruns: rerun the cost and storage runs whose
measurement the instrumentation could not make.

    tools/rerun-measurements.py SYSTEM LABEL PROBLEM...

A PROBLEM may name one instance (P05b): then only that instance's records
are rerun.

Runs inside the image of the fixed measurement build (for Absys,
cp-agent-systems:spec-1.0-m2, absys-measure 8a0eefd), from the repository
root. For every cost or storage record under
results/SYSTEM/<configuration>/<problem>/raw/ in which an attempt reached
the safety limit, it runs the same configuration, problem, instance, mode
and program again through harnesses/SYSTEM/run, with HARNESS_RUN_LABEL set
to LABEL, into results/SYSTEM/<configuration>/<problem>/raw-rerun-m2/. The
original record is not touched: it stays the record of that run, and the
rerun is reported beside it, labelled. One line per rerun goes to
results/SYSTEM/rerun-m2-log.tsv, naming the original record.
"""
import glob, json, os, subprocess, sys, time

system, label, problems = sys.argv[1], sys.argv[2], sys.argv[3:]
log = open(f"results/{system}/rerun-m2-log.tsv", "a")
done = set()
if os.path.exists(f"results/{system}/rerun-m2-log.tsv"):
    for l in open(f"results/{system}/rerun-m2-log.tsv"):
        f = l.rstrip("\n").split("\t")
        if len(f) > 2 and f[2] == "exit 0":
            done.add(f[1])
for arg in problems:
    prob, inst = arg[:3], (arg if len(arg) > 3 else None)
    for rec in sorted(glob.glob(f"results/{system}/*/{prob}/raw/*.json")):
        d = json.load(open(rec))
        run = d["run"]
        if run["mode"] not in ("cost", "storage") or rec in done or (inst and run["instance"] != inst):
            continue
        hit = any(a.get("safety_limit", {}).get("hit") for s in d["stages"] for a in s["attempts"])
        if not hit:
            continue
        out = f"results/{system}/{run['configuration']}/{prob}/raw-rerun-m2/"
        os.makedirs(out, exist_ok=True)
        t = time.time()
        r = subprocess.run([f"harnesses/{system}/run", run["configuration"], prob, run["instance"], run["mode"],
                            run["program"]["path"], out], capture_output=True, text=True,
                           env={**os.environ, "HARNESS_RUN_LABEL": f"{label}; original record {rec}"})
        line = f"{time.strftime('%FT%TZ', time.gmtime())}\t{rec}\texit {r.returncode}\t{time.time() - t:.1f}s"
        print(line, flush=True)
        log.write(line + "\n"); log.flush()
        if r.returncode != 0:
            log.write("\t" + (r.stderr or r.stdout).strip().replace("\n", "\n\t")[:2000] + "\n")
