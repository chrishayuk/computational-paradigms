#!/usr/bin/env python3
"""Run every program of a batch through its system's harness.

Runs inside the system's pinned image, from the repository root:

    tools/run-batch.py SYSTEM PROBLEM...        e.g. tools/run-batch.py absys P01 P02 P03

For each configuration of SYSTEM that has a folder under programs/SYSTEM/,
each instance of each PROBLEM in harnesses/stages.json, and each mode the
configuration allows, it finds the program (programs/SYSTEM/CONFIG/<instance
id>, or a dot-prefix of it such as P12a.n8 for P12a.n8.all, or <sub-problem
id>, with the system's extension), and calls

    harnesses/SYSTEM/run CONFIG PROBLEM INSTANCE MODE PROGRAM results/SYSTEM/CONFIG/PROBLEM/raw/

A file named <sub-problem id>-<name>.<ext> is a named variant and is run the
same way, as is any file in the configuration's variants/ folder whose name
begins with the sub-problem id (<id>.<name>.<ext> or <id>-<name>.<ext>). The driver chooses nothing about the runs themselves: it only
enumerates them. One line per run goes to results/SYSTEM/batch-log.tsv.

    --configs A,B     run only these configurations
    --skip-logged     skip every run batch-log.tsv records as exit 0 (a validated record);
                      a run that ended with any other exit is run again
                      (so an interrupted batch resumes without repeating a run)
    --log PATH        write the log lines to PATH instead of results/SYSTEM/batch-log.tsv
                      (one log per job when jobs run in parallel; from batch 1C);
                      --skip-logged then reads PATH
"""
import gzip, json, os, subprocess, sys, time

EXT = {"absys": [".ab1", ".ab2", ".abs"], "swi-prolog": [".pl"], "python": [".py"],
       "algol-60": [".alg", ".a60"]}
MODES = {"x1sim": ["behaviour"]}          # PROTOCOL / systems file: x1sim is behaviour only

def stopped_by_limit(path):
    """A record stopped by either limit (P13, Budget): the safety limit hit, or a
    query ended by the step budget or the time limit, at any stage."""
    try:
        r = json.load(gzip.open(path) if path.endswith(".gz") else open(path))
    except Exception:
        return False
    for st in r.get("stages", []):
        for a in st.get("attempts", []):
            if (a.get("safety_limit") or {}).get("hit"):
                return True
            for c in a.get("computations") or []:
                for q in c.get("queries") or []:
                    if q.get("ended_by") in ("budget", "timeout"):
                        return True
    return False

_limit_cache = {}
def smaller_n_stopped(out, sp, inst, prog_path, mode):
    """P13's rule (QUESTIONS.md Q10): the larger values of n are not run after a run
    stopped by a limit, per configuration, task (sub-problem and program) and mode.
    Returns the smaller instance whose record was stopped, or None."""
    n = (inst.get("parameters") or {}).get("n")
    for other in sp["instances"]:
        m = (other.get("parameters") or {}).get("n")
        if other is inst or m is None or n is None or m >= n:
            continue
        for f in sorted(os.listdir(out)) if os.path.isdir(out) else []:
            if not (f.startswith(other["id"] + "." + mode + ".") and (f.endswith(".json") or f.endswith(".json.gz"))):
                continue
            path = os.path.join(out, f)
            if path not in _limit_cache:
                try:
                    r = json.load(gzip.open(path) if path.endswith(".gz") else open(path))
                    same = r["run"]["program"]["path"] == prog_path
                except Exception:
                    same = False
                _limit_cache[path] = same and stopped_by_limit(path)
            if _limit_cache[path]:
                return other["id"]
    return None

def main():
    args = sys.argv[1:]
    only = skip = None
    logpath = None
    if "--log" in args:                        # one log per job (batch 1C)
        i = args.index("--log"); logpath = args[i + 1]; del args[i:i + 2]
    if "--configs" in args:                    # run only these configurations (comma-separated)
        i = args.index("--configs"); only = set(args[i + 1].split(",")); del args[i:i + 2]
    if "--skip-logged" in args:                # skip runs batch-log.tsv already records as finished
        args.remove("--skip-logged"); skip = set()
        lp = logpath or f"results/{args[0]}/batch-log.tsv"
        if os.path.exists(lp):
            for l in open(lp):
                f = l.rstrip("\n").split("\t")
                if len(f) >= 6 and f[5] == "exit 0":       # exit 0: the harness wrote a record that validated
                    skip.add((f[1], f[2], f[3], f[4]))
    system, problems = args[0], args[1:]
    stages = json.load(open("harnesses/stages.json"))["problems"]
    root = f"programs/{system}"
    configs = sorted(d for d in os.listdir(root) if os.path.isdir(f"{root}/{d}"))
    os.makedirs(f"results/{system}", exist_ok=True)
    if logpath:
        os.makedirs(os.path.dirname(logpath) or ".", exist_ok=True)
    log = open(logpath or f"results/{system}/batch-log.tsv", "a")
    for cfg in configs:
        if only is not None and cfg not in only:
            continue
        files = os.listdir(f"{root}/{cfg}")
        for p in stages:
            if p["problem"] not in problems:
                continue
            for sp in p["subproblems"]:
                for inst in sp["instances"]:
                    progs = []
                    # the instance id, then each shorter dot-prefix of it (P12a.n8 for
                    # P12a.n8.all: one file serving both answer modes; batch 1C),
                    # then the sub-problem id
                    parts = inst["id"].split(".")
                    stems = [".".join(parts[:k]) for k in range(len(parts), 0, -1)] + [sp["id"]]
                    for stem in dict.fromkeys(stems):
                        hit = [f for f in files if os.path.splitext(f)[0] == stem and os.path.splitext(f)[1] in EXT[system]]
                        if hit:
                            progs.append(hit[0]); break
                    progs += sorted(f for f in files if os.path.splitext(f)[1] in EXT[system]
                                    and os.path.splitext(f)[0].startswith(sp["id"] + "-"))
                    vdir = f"{root}/{cfg}/variants"            # named variants kept in a folder of their own (batch 1B)
                    if os.path.isdir(vdir):
                        progs += sorted("variants/" + f for f in os.listdir(vdir) if os.path.splitext(f)[1] in EXT[system]
                                        and (f.startswith(sp["id"] + ".") or f.startswith(sp["id"] + "-")))
                    if not progs:
                        print(f"NO PROGRAM\t{cfg}\t{inst['id']}", flush=True)
                        log.write(f"{time.strftime('%FT%TZ', time.gmtime())}\t{cfg}\t{inst['id']}\t-\t-\tno program\n")
                        continue
                    for prog in progs:
                        for mode in MODES.get(cfg, ["behaviour", "cost", "storage"]):
                            if skip is not None and (cfg, inst["id"], prog, mode) in skip:
                                continue
                            out = f"results/{system}/{cfg}/{p['problem']}/raw/"
                            os.makedirs(out, exist_ok=True)
                            if (p.get("limits") or {}).get("stop_larger_n_after_limit"):
                                prev = smaller_n_stopped(out, sp, inst, f"{root}/{cfg}/{prog}", mode)
                                if prev:
                                    line = f"{time.strftime('%FT%TZ', time.gmtime())}\t{cfg}\t{inst['id']}\t{prog}\t{mode}\tnot run: {prev} was stopped by a limit (P13, Budget)"
                                    print(line, flush=True); log.write(line + "\n"); log.flush()
                                    continue
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
