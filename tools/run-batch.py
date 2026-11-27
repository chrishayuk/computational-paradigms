#!/usr/bin/env python3
"""Run every program of a batch through its system's harness.

Runs inside the system's pinned image, from the repository root:

    tools/run-batch.py SYSTEM PROBLEM...        e.g. tools/run-batch.py absys P01 P02 P03

For each configuration of SYSTEM that has a folder under programs/SYSTEM/,
each instance of each PROBLEM in harnesses/stages.json, and each mode the
configuration allows, it finds the program (programs/SYSTEM/CONFIG/<instance
id> or <sub-problem id>, with the system's extension), and calls

    harnesses/SYSTEM/run CONFIG PROBLEM INSTANCE MODE PROGRAM results/SYSTEM/CONFIG/PROBLEM/raw/

A file named <sub-problem id>-<name>.<ext> is a named variant and is run the
same way. The driver chooses nothing about the runs themselves: it only
enumerates them. One line per run goes to results/SYSTEM/batch-log.tsv.
"""
import json, os, subprocess, sys, time

EXT = {"absys": [".ab1", ".ab2", ".abs"], "swi-prolog": [".pl"], "python": [".py"],
       "algol-60": [".alg", ".a60"]}
MODES = {"x1sim": ["behaviour"]}          # PROTOCOL / systems file: x1sim is behaviour only

def main():
    system, problems = sys.argv[1], sys.argv[2:]
    stages = json.load(open("harnesses/stages.json"))["problems"]
    root = f"programs/{system}"
    configs = sorted(d for d in os.listdir(root) if os.path.isdir(f"{root}/{d}"))
    log = open(f"results/{system}/batch-log.tsv", "a") if os.path.isdir(f"results/{system}") else None
    if log is None:
        os.makedirs(f"results/{system}", exist_ok=True)
        log = open(f"results/{system}/batch-log.tsv", "a")
    for cfg in configs:
        files = os.listdir(f"{root}/{cfg}")
        for p in stages:
            if p["problem"] not in problems:
                continue
            for sp in p["subproblems"]:
                for inst in sp["instances"]:
                    progs = []
                    for stem in (inst["id"], sp["id"]):
                        hit = [f for f in files if os.path.splitext(f)[0] == stem and os.path.splitext(f)[1] in EXT[system]]
                        if hit:
                            progs.append(hit[0]); break
                    progs += sorted(f for f in files if os.path.splitext(f)[1] in EXT[system]
                                    and os.path.splitext(f)[0].startswith(sp["id"] + "-"))
                    if not progs:
                        print(f"NO PROGRAM\t{cfg}\t{inst['id']}", flush=True)
                        log.write(f"{time.strftime('%FT%TZ', time.gmtime())}\t{cfg}\t{inst['id']}\t-\t-\tno program\n")
                        continue
                    for prog in progs:
                        for mode in MODES.get(cfg, ["behaviour", "cost", "storage"]):
                            out = f"results/{system}/{cfg}/{p['problem']}/raw/"
                            os.makedirs(out, exist_ok=True)
                            t = time.time()
                            r = subprocess.run([f"harnesses/{system}/run", cfg, p["problem"], inst["id"], mode,
                                                f"{root}/{cfg}/{prog}", out], capture_output=True, text=True)
                            line = f"{time.strftime('%FT%TZ', time.gmtime())}\t{cfg}\t{inst['id']}\t{prog}\t{mode}\texit {r.returncode}\t{time.time()-t:.1f}s"
                            print(line, flush=True)
                            log.write(line + "\n"); log.flush()
                            if r.returncode != 0:
                                log.write("\t" + (r.stderr or r.stdout).strip().replace("\n", "\n\t")[:2000] + "\n")

if __name__ == "__main__":
    main()
