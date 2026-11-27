"""Qualification of the Python harness: reruns every check and prints what it
found. Run it inside the pinned image, from the repository root:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \\
        cp-agent-python:spec-1.0 python3 -B -s harnesses/python/qualification/qualify.py

Records go to harnesses/python/qualification/records/<UTC stamp>/; the
printed report is what harnesses/python/qualification/output.txt holds.
Only made-up problems (qualification/stages-qual.json, X01-X10) are run.
"""
import datetime
import glob
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
Q = "harnesses/python/qualification"
PROG = Q + "/programs"
STAGES = Q + "/stages-qual.json"
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = "%s/records/%s" % (Q, STAMP)
PY = "/usr/local/bin/python3"
ENV = dict(os.environ, CP_STAGES=STAGES, CP_PURPOSE="qualification")

results = []


def say(*a):
    print(*a, flush=True)


def check(name, ok, detail=""):
    results.append((name, ok))
    say("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  [" + detail + "]") if detail else ""))


def run(config, problem, inst, mode, prog, expect_rc=0, env=None):
    outdir = "%s/%s/%s/raw" % (OUT, config, problem)
    os.makedirs(os.path.join(REPO, outdir), exist_ok=True)
    before = set(glob.glob(os.path.join(REPO, outdir, "*.json")))
    p = subprocess.run(["harnesses/python/run", config, problem, inst, mode, PROG + "/" + prog, outdir],
                       cwd=REPO, env=env or ENV, capture_output=True, text=True)
    after = set(glob.glob(os.path.join(REPO, outdir, "*.json"))) - before
    if p.returncode != expect_rc:
        say("   run exit status %d (expected %d): %s %s" % (p.returncode, expect_rc, p.stdout, p.stderr))
    rec = None
    new = [a for a in after if not a.endswith(".INVALID.json")]
    if new:
        rec = json.load(open(sorted(new)[-1]))
    return p, rec


def direct(prog, K, n=None, spawns=None):
    args = [PY, "-B", "-s", "-P", Q + "/direct.py", PROG + "/" + prog, str(K)]
    if n is not None or spawns:
        args.append(str(n or 0))
    if spawns:
        args.append(",".join(spawns))
    p = subprocess.run(args, cwd=REPO, capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED="0"))
    line = [l for l in p.stderr.splitlines() if l.startswith("DIRECT ")]
    return json.loads(line[0][7:]), p.stdout


def final(rec, k):
    return rec["stages"][k - 1]["attempts"][-1]


def comp(att, name="main"):
    return [c for c in att["computations"] if c["id"] == name][0]


def answers(att, name="main"):
    c = comp(att, name)
    return [a["verbatim"] for q in c["queries"] for a in q["answers"]]


def states(att, name="main"):
    return comp(att, name)["execution_state"]["states"]


def program_pid():
    """The pid of the program's interpreter process (runtime.py) now running."""
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                cmd = open("/proc/%s/cmdline" % d, "rb").read()
            except OSError:
                continue
            if b"harnesses/python/runtime.py" in cmd:
                return int(d)
    return None


def scan_memory(pid, needles):
    """Count each needle's UTF-8 bytes in every readable mapping of the
    process, read from outside through /proc/<pid>/mem."""
    counts = {n: 0 for n in needles}
    with open("/proc/%d/maps" % pid) as f:
        maps = f.read().splitlines()
    with open("/proc/%d/mem" % pid, "rb") as mem:
        for line in maps:
            addr, perms = line.split()[:2]
            if "r" not in perms:
                continue
            a, b = (int(x, 16) for x in addr.split("-"))
            try:
                mem.seek(a)
                data = mem.read(b - a)
            except (OSError, ValueError, OverflowError):
                continue
            for n in needles:
                counts[n] += data.count(n.encode())
    return counts


def main():
    say("Qualification of harnesses/python, %s" % STAMP)
    say(subprocess.run([PY, "-VV"], capture_output=True, text=True).stdout.strip())
    say("records: %s" % OUT)
    say("")

    say("== (a) the system run directly, and through the harness")
    # the README's example
    d, dout = direct("x01_total.py", 3)
    for mode in ("behaviour", "cost"):
        _, r = run("core", "X01", "X01a", mode, "x01_total.py")
        ok = all(answers(final(r, k)) == d[k - 1]["answers"] for k in (1, 2, 3))
        check("X01 example, %s: answers per stage equal the direct run's printed lines" % mode, ok,
              "harness %s, direct %s" % ([answers(final(r, k)) for k in (1, 2, 3)], [x["answers"] for x in d]))
        ok = "".join(final(r, k)["stdout"] for k in (1, 2, 3)) == dout
        check("X01 example, %s: the program's stdout through the harness is byte-identical to the direct run's" % mode, ok)
        if mode == "cost":
            hs = [comp(final(r, k))["steps"]["to_end"] for k in (1, 2, 3)]
            ds = [x["steps"] for x in d]
            check("X01 example, cost: instructions per stage equal the direct count (probes/meter.py's method)", hs == ds, "harness %s, direct %s" % (hs, ds))
            ho = [comp(final(r, k))["problem_operations"] for k in (1, 2, 3)]
            do = [x["ops"] for x in d]
            check("X01 example, cost: relation calls per stage equal the direct PY_START count", ho == do, "harness %s, direct %s" % (ho, do))
    # counts and store
    d, _ = direct("x06_counts.py", 3, 12)
    _, r = run("core", "X06", "X06a.n12", "cost", "x06_counts.py")
    hs = [comp(final(r, k))["steps"]["to_end"] for k in (1, 2, 3)]
    check("X06 cost: instructions per stage equal the direct count", hs == [x["steps"] for x in d], "harness %s, direct %s" % (hs, [x["steps"] for x in d]))
    ops = comp(final(r, 1))["problem_operations"]
    check("X06 cost: calls of f(12) = 2 f(12) - 1 = 465 (closed form), and equal to the direct count",
          ops == {"f": 465} and d[0]["ops"] == {"f": 465}, "harness %s, direct %s" % (ops, d[0]["ops"]))
    _, r = run("core", "X06", "X06a.n12", "storage", "x06_counts.py")
    bt = comp(final(r, 2))["alternatives"]["by_type"]
    check("X06 storage: 17 suspended generator frames for generators nested 16 deep (probe p4: 17)",
          bt.get("suspended generator frames (gc, process-wide)") == 17, str(bt))
    check("X06 storage: the registered pending generator counts 1 and makes the state 'alternatives pending'",
          bt.get("suspended generators") == 1 and states(final(r, 2)) == ["alternatives pending"], str(states(final(r, 2))))
    same = all(answers(final(r, k)) == d[k - 1]["answers"] for k in (1, 2, 3))
    check("X06 storage: answers equal the direct run's", same)
    # the systems file's probe workloads
    probe = subprocess.run([PY, "-B", "-s", "-c",
        "import sys; sys.path[:0]=['systems/python/probes']\n"
        "import meter, p6_budget, tracemalloc\n"
        "a=meter.count_mon(p6_budget.finite,100)[1]; b=meter.count_mon(p6_budget.finite,1000)[1]\n"
        "import p3_memory\n"
        "tracemalloc.start(1); r,cur,peak=p3_memory.traced(p3_memory.build_and_drop,10**6)\n"
        "print(a,b,peak)"], cwd=REPO, capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED="0"))
    a, b, peak = (int(x) for x in probe.stdout.split())
    say("   probes run now in this image: count_mon(finite, 100) = %d, count_mon(finite, 1000) = %d; traced peak growth of build_and_drop(10**6) = %d" % (a, b, peak))
    check("probe p6 figures reproduced in this image (systems/python/probes/out/3.13.7.txt: 609, 6009)", (a, b) == (609, 6009))
    _, r = run("core", "X09", "X09a", "cost", "x09_probes.py")
    s0, s1, s2 = (comp(final(r, k))["steps"]["to_end"] for k in (2, 3, 4))
    say("   X09 stages 2, 3, 4 (finite(100), finite(100), finite(1000)): %d, %d, %d instructions. The first pass through the loop's tail (stage 2) is one instruction fewer than later passes, in the direct run as well: the interpreter's, not the harness's." % (s0, s1, s2))
    check("X09 cost: stage 4 minus stage 3 (finite(1000) against finite(100), same warm code path) = 6009 - 609 (probe p6)", s2 - s1 == b - a, "harness %d - %d = %d" % (s2, s1, s2 - s1))
    check("X09 cost: one call of each registered relation per stage", [comp(final(r, k))["problem_operations"] for k in (1, 2, 3, 4, 5)] == [{}, {"finite": 1}, {"finite": 1}, {"finite": 1}, {"build_and_drop": 1}])
    d, _ = direct("x09_probes.py", 5)
    check("X09 cost: instructions per stage equal the direct count", [comp(final(r, k))["steps"]["to_end"] for k in (1, 2, 3, 4, 5)] == [x["steps"] for x in d],
          "harness %s, direct %s" % ([comp(final(r, k))["steps"]["to_end"] for k in (1, 2, 3, 4, 5)], [x["steps"] for x in d]))
    _, r = run("core", "X09", "X09a", "storage", "x09_probes.py")
    q = final(r, 5)["store"]["quantities"]
    growth = q["traced_bytes"]["peak"]["value"] - q["traced_bytes_at_window_start"]["boundary"]
    check("X09 storage: traced peak growth of stage 5 (build and drop 10^6 ints) agrees with probe p3 (40,000,208) to within 4 KiB of harness traffic",
          abs(growth - peak) < 4096, "harness %d, probe now %d, difference %d" % (growth, peak, growth - peak))
    check("X09 storage: answers equal those of the cost run", [answers(final(r, k)) for k in (1, 2, 3, 4, 5)] == [x["answers"] for x in d])
    _, rb = run("core", "X09", "X09a", "behaviour", "x09_probes.py")
    check("X09: behaviour, cost and storage runs give the same answers",
          [answers(final(rb, k)) for k in (1, 2, 3, 4, 5)] == [answers(final(r, k)) for k in (1, 2, 3, 4, 5)])
    # spawned computations
    for config, inst, order in (("core", "X03a.UV", ["U", "V"]), ("core", "X03a.VU", ["V", "U"]), ("stdlib-concurrency", "X03a.UV", ["U", "V"])):
        d, _ = direct("x03_two.py", 1, 0, order)
        _, r = run(config, "X03", inst, "behaviour", "x03_two.py")
        att = final(r, 1)
        ok = all(answers(att, nm) == d[0]["spawned"][nm]["answers"] for nm in order)
        idx = [c["id"] for c in sorted((c for c in att["computations"] if c["spawned"]), key=lambda c: c["spawn_index"])]
        check("X03 %s %s: each spawned computation's answers equal the direct run's; spawn order %s; side_by_side %s" %
              (config, inst, idx, comp(att, order[0])["side_by_side"]), ok and idx == order)
    _, r = run("core", "X03", "X03a.UV", "cost", "x03_two.py")
    d, _ = direct("x03_two.py", 1, 0, ["U", "V"])
    check("X03 core cost: each spawned computation's instructions equal the direct count",
          all(comp(final(r, 1), nm)["steps"]["to_end"] == d[0]["spawned"][nm]["steps"] for nm in ("U", "V")),
          str([(nm, comp(final(r, 1), nm)["steps"]["to_end"], d[0]["spawned"][nm]["steps"]) for nm in ("U", "V")]))
    say("")

    say("== (b) incremental and reposed posing")
    _, ri = run("core", "X01", "X01a", "behaviour", "x01_total.py")
    _, rr = run("core", "X01", "X01a", "behaviour", "x01_total_reposed.py")
    check("X01: the same answers at every stage, incremental and reposed",
          [answers(final(ri, k)) for k in (1, 2, 3)] == [answers(final(rr, k)) for k in (1, 2, 3)])
    check("X01: the same observe() at every stage, incremental and reposed",
          [final(ri, k)["observe"]["raw"] for k in (1, 2, 3)] == [final(rr, k)["observe"]["raw"] for k in (1, 2, 3)])
    rc = [comp(final(rr, k))["steps"]["restart_cost"] for k in (2, 3)]
    check("X01 reposed: every later stage has a measured in-run restart cost, and budget = restart cost + 10^6",
          all(x is not None for x in rc) and all(comp(final(rr, k))["steps"]["budget"] == 10**6 + comp(final(rr, k))["steps"]["restart_cost"] for k in (2, 3)), str(rc))
    _, ri = run("core", "X02", "X02a", "behaviour", "x02_pick.py")
    _, rr = run("core", "X02", "X02a", "behaviour", "x02_pick_reposed.py")
    check("X02 (effects, commit): the same answers at every stage, incremental and reposed",
          [answers(final(ri, k)) for k in (1, 2, 3)] == [answers(final(rr, k)) for k in (1, 2, 3)],
          str([answers(final(rr, k)) for k in (1, 2, 3)]))
    rcm = final(rr, 3)["posed"]["replayed_commitments"]
    check("X02 reposed: stage 3 replays commit stage 2 as the verbatim answer it gave", rcm == [{"stage": 2, "value_verbatim": answers(final(rr, 2))[0], "selected_in_run": rr["run"]["run_id"]}], str(rcm))
    eff = [(e["stage"], e["during_replay_of"]) for st in rr["stages"] for a in st["attempts"] for e in a["effects"]]
    check("X02 reposed: the effect is logged once per run of stage 1, marked during_replay_of 1 when replayed", eff == [(1, None), (2, 1), (3, 1)], str(eff))
    e2 = rr["effects"]
    check("X02: the classification log is never reset (the second run starts after the first run's entries)",
          e2["entries_before_run"] == len(ri["effects"]["log_after_run"]) and len(e2["log_after_run"]) == e2["entries_before_run"] + 3,
          "entries_before_run %d" % e2["entries_before_run"])
    _, rc_ = run("core", "X02", "X02a", "cost", "x02_pick.py")
    check("X02 cost: entries go only to the observation log", all(e["log"] == "observation" for st in rc_["stages"] for a in st["attempts"] for e in a["effects"])
          and rc_["effects"]["log_after_run"] == rr["effects"]["log_after_run"])
    say("")

    say("== (c) budget, safety limit and error paths")
    d, _ = direct("x04a_budget.py", 2)
    _, r = run("core", "X04", "X04a", "cost", "x04a_budget.py")
    s1 = comp(final(r, 1))["steps"]
    s2 = comp(final(r, 2))["steps"]
    check("X04a: stage 1 ends in budget after exactly 10^6 instructions", states(final(r, 1)) == ["budget"] and s1["to_end"] == 10**6, str(s1["to_end"]))
    check("X04a: stage 2 continues the same computation (continued_after_budget) and the total equals the uninterrupted direct count",
          final(r, 2)["posed"]["continued_after_budget"] and s1["to_end"] + s2["to_end"] == d[0]["steps"] + d[1]["steps"],
          "harness %d + %d, direct %d + %d" % (s1["to_end"], s2["to_end"], d[0]["steps"], d[1]["steps"]))
    check("X04a: the answers are those of the direct run, in total", answers(final(r, 1)) + answers(final(r, 2)) == d[0]["answers"] + d[1]["answers"])
    _, r = run("core", "X04", "X04e", "behaviour", "x04e_endless.py")
    check("X04e: an endless loop is budget at stage 1, continued and budget again at stage 2, each at exactly 10^6",
          states(final(r, 1)) == ["budget"] and states(final(r, 2)) == ["budget"] and comp(final(r, 2))["steps"]["to_end"] == 10**6
          and comp(final(r, 1))["alternatives"]["at_budget"] == comp(final(r, 1))["alternatives"]["at_boundary"] > 0,
          "frontier entries at budget: %s" % comp(final(r, 1))["alternatives"]["at_budget"])
    _, r = run("core", "X04", "X04b", "behaviour", "x04b_error.py")
    err = comp(final(r, 2))["execution_state"]["error_verbatim"] or ""
    check("X04b: a RecursionError is error, with its traceback verbatim, and stage 3 is reposed after-error",
          states(final(r, 2)) == ["error"] and err.startswith("Traceback (most recent call last):") and "RecursionError" in err
          and final(r, 3)["posed"]["how"] == "reposed" and final(r, 3)["posed"]["reason"] == "after-error" and answers(final(r, 3)) == ["r = 2, t = 9"])
    for prog in ("x11_error_at_1.py", "x11_error_at_1_reposed.py", "x11_error_at_start.py", "x11_error_at_start_reposed.py"):
        p, r = run("core", "X01", "X01a", "behaviour", prog)
        ok = p.returncode == 0 and r is not None and len(r["stages"]) == 3
        if ok:
            ok = all(states(final(r, k)) == ["error"] for k in (1, 2, 3)) and all(
                final(r, k)["posed"]["how"] == "reposed" and final(r, k)["posed"]["reason"] == "after-error"
                and comp(final(r, k))["steps"]["restart_cost"] is not None
                and comp(final(r, k))["steps"]["budget"] == 10**6 + comp(final(r, k))["steps"]["restart_cost"] for k in (2, 3))
        check("X01 over three stages, a program that raises %s (%s): run exits 0, every stage is error, stages 2 and 3 are reposed after-error with the stopped run's whole count as restart cost, and the record is valid" %
              ("at stage 1" if "at_1" in prog else "in its set-up, before its first cp.stage()", "reposed" if "reposed" in prog else "incremental"),
              ok, "exit %d; restart costs %s" % (p.returncode, [comp(final(r, k))["steps"]["restart_cost"] for k in (2, 3)] if r else None))
    _, r = run("core", "X04", "X04b", "behaviour", "x04b_die.py")
    check("X04b, os.abort(): the process ends by SIGABRT; the stage is error and stage 3 reposed",
          states(final(r, 2)) == ["error"] and final(r, 2)["exit"]["signal"] == "SIGABRT" and final(r, 3)["posed"]["reason"] == "after-error",
          str(final(r, 2)["exit"]))
    _, r = run("core", "X04", "X04c", "behaviour", "x04c_cloop.py")
    a1, a2 = r["stages"][1]["attempts"]
    check("X04c: a loop inside one C call is stopped by the safety limit (4 s), rerun reposed (8 s), final timeout; stage 3 reposed after-timeout",
          a1["safety_limit"]["action"] == "rerun" and a2["safety_limit"]["action"] == "final-timeout" and a2["posed"]["reason"] == "safety-rerun"
          and a2["posed"]["how"] == "reposed" and final(r, 3)["posed"]["reason"] == "after-timeout" and answers(final(r, 3)) == ["r = 1, t = 2"])
    _, r = run("core", "X05", "X05a", "behaviour", "x05_cloop.py")
    check("X05: under a fixed limit the first stop is final (fixed-limit-timeout), no second attempt",
          len(r["stages"][0]["attempts"]) == 1 and r["stages"][0]["attempts"][0]["safety_limit"]["action"] == "fixed-limit-timeout")
    _, r = run("core", "X04", "X04d", "behaviour", "x04d_many.py")
    q1 = comp(final(r, 1))["queries"][0]
    check("X04d: 25 answers printed, the first 20 collected, ended_by cap; the rest stay in stdout",
          len(q1["answers"]) == 20 and q1["ended_by"] == "cap" and final(r, 1)["stdout"].count("\n") == 25)
    check("X04d: a registered stack with entries left is 'alternatives pending'", states(final(r, 2)) == ["alternatives pending"]
          and comp(final(r, 2))["alternatives"]["at_boundary"] == 24)
    _, r = run("stdlib-concurrency", "X07", "X07a.AB", "behaviour", "x07_wait.py")
    check("X07 stdlib-concurrency: a computation blocked in a wait is reported suspended (undetermined, by quiescence); the other finishes",
          states(final(r, 1), "A") == ["suspended"] and not comp(final(r, 1), "A")["execution_state"]["determined"] and states(final(r, 1), "B") == ["finished"])
    _, r = run("core", "X03", "X03a.UV", "behaviour", "x03_missing_v.py")
    check("X03 with V not registered: V is recorded spawned, state undetermined, and the record is valid",
          comp(final(r, 1), "V")["execution_state"]["determined"] is False and answers(final(r, 1), "U") == ["u = 10", "u = 20", "u = 30"])
    _, r = run("core", "X08", "X08a.n1000", "behaviour", "x08_growth.py")
    a = final(r, 1)
    check("X08: CPU time and maximum resident set size are recorded where the problem asks (P13; X08 by its made-up flag)",
          a["cpu_time_s"] is not None and a["max_rss_kb"] and a["max_rss_kb"] > 1000, "cpu %s s, rss %s KiB" % (a["cpu_time_s"], a["max_rss_kb"]))
    # usage errors: exit 2, no record
    for args, why in ((["nonsense", "X01", "X01a", "behaviour"], "unknown configuration"),
                      (["core", "X01", "X01z", "behaviour"], "unknown instance"),
                      (["core", "X01", "X01a", "fast"], "unknown mode"),
                      (["core", "X02", "X01a", "behaviour"], "instance of another problem")):
        outdir = "%s/usage" % OUT
        p = subprocess.run(["harnesses/python/run"] + args + [PROG + "/x01_total.py", outdir], cwd=REPO, env=ENV, capture_output=True, text=True)
        check("usage error (%s): exit status 2 and no record" % why, p.returncode == 2 and not glob.glob(os.path.join(REPO, outdir, "*.json")), p.stderr.strip())
    p = subprocess.run(["harnesses/python/run", "core", "X01", "X01a", "behaviour", PROG + "/check_static.py", OUT + "/usage"], cwd=REPO, env=ENV, capture_output=True, text=True)
    check("a program without a valid CP-POSING line: exit status 2 and no record", p.returncode == 2, p.stderr.strip())
    say("")

    say("== (f) no anticipation: a stage's constants reach the program's process only when that stage is posed")
    early, later = "QZ-EARLY-STAGE-CONSTANT-1180", "QZ-LATER-STAGE-CONSTANT-5521"
    on_disk = open(os.path.join(REPO, PROG, "x10_nolookahead.py")).read()
    check("X10: the program's file on disk holds both stages' constants", early in on_disk and later in on_disk)
    for k in (1, 2):
        for f in ("/tmp/cpq-ready-%d" % k, "/tmp/cpq-go-%d" % k):
            if os.path.exists(f):
                os.unlink(f)
    outdir = "%s/core/X10/raw" % OUT
    os.makedirs(os.path.join(REPO, outdir), exist_ok=True)
    proc = subprocess.Popen(["harnesses/python/run", "core", "X10", "X10a", "behaviour", PROG + "/x10_nolookahead.py", outdir],
                            cwd=REPO, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    found = {}
    for k in (1, 2):
        t0 = time.time()
        while not os.path.exists("/tmp/cpq-ready-%d" % k) and time.time() - t0 < 50:
            time.sleep(0.05)
        pid = program_pid()
        found[k] = scan_memory(pid, [early, later]) if pid else None
        say("   stage %d: the program's process (pid %s) holds %r" % (k, pid, found[k]))
        open("/tmp/cpq-go-%d" % k, "w").close()
    proc.communicate()
    check("X10 stage 1: the whole memory of the program's process holds stage 1's constant and not stage 2's",
          found[1] is not None and found[1][early] > 0 and found[1][later] == 0, str(found[1]))
    check("X10 stage 2: once stage 2 is posed, its constant is there", found[2] is not None and found[2][later] > 0, str(found[2]))
    recs = glob.glob(os.path.join(REPO, outdir, "*.json"))
    r = json.load(open(recs[0])) if recs else None
    check("X10: the program received each stage's constants as s.constants (answers list what it held)",
          r is not None and answers(final(r, 1)) == ["EARLY"] and answers(final(r, 2)) == ["EARLY, LATER"])
    for k in (1, 2):
        for f in ("/tmp/cpq-ready-%d" % k, "/tmp/cpq-go-%d" % k):
            if os.path.exists(f):
                os.unlink(f)
    say("")

    say("== (c2) extended admits the S mechanisms (S-mechanisms.md), and only extended")
    d, _ = direct("x01_total.py", 3)
    pe = subprocess.run(["harnesses/python/check", "extended", PROG + "/x01_extended.py"], cwd=REPO, capture_output=True, text=True)
    pc = subprocess.run(["harnesses/python/check", "core", PROG + "/x01_extended.py"], cwd=REPO, capture_output=True, text=True)
    _, re_ = run("extended", "X01", "X01a", "behaviour", "x01_extended.py")
    got = [answers(final(re_, k)) for k in (1, 2, 3)] if re_ else None
    check("S import: check passes it in extended and refuses it in core; run in extended gives the answers of the direct run of x01_total.py",
          pe.returncode == 0 and "an S mechanism of extended" in pe.stdout and pc.returncode == 1 and "only the extended configuration adds" in pc.stdout
          and got == [x["answers"] for x in d],
          "extended answers %s, direct %s" % (got, [x["answers"] for x in d]))
    say("   " + pe.stdout.strip().replace("\n", "\n   "))
    say("   " + pc.stdout.strip().replace("\n", "\n   "))
    say("")

    say("== (d) every record validates")
    recs = sorted(glob.glob(os.path.join(REPO, OUT, "**", "*.json"), recursive=True))
    recs = [x for x in recs if not x.endswith(".effects.jsonl")]
    p = subprocess.run([PY, "-B", "-s", "harnesses/validate.py", "--stages", STAGES] + recs, cwd=REPO, capture_output=True, text=True)
    bad = [l for l in p.stdout.splitlines() if "INVALID" in l or l.startswith("  error")]
    invalid = glob.glob(os.path.join(REPO, OUT, "**", "*.INVALID.json"), recursive=True)
    check("validate.py on all %d records: all valid, none kept as INVALID" % len(recs), p.returncode == 0 and not bad and not invalid, "; ".join(bad[:5]))
    say("")

    say("== (e) check executes nothing")
    marker = "/tmp/cp-check-marker-file"
    if os.path.exists(marker):
        os.unlink(marker)
    p = subprocess.run(["harnesses/python/check", "core", PROG + "/check_marker.py"], cwd=REPO, capture_output=True, text=True)
    check("check on a program whose only effects are writing a file and printing a marker: no file, no marker, exit 0",
          not os.path.exists(marker) and "CP-CHECK-MARKER-PRINTED" not in p.stdout + p.stderr and p.returncode == 0)
    say("   " + p.stdout.strip().replace("\n", "\n   "))
    p2 = subprocess.run([PY, "-B", "-s", PROG + "/check_marker.py"], cwd=REPO, capture_output=True, text=True)
    check("control: running that program directly does write the file and print the marker",
          os.path.exists(marker) and "CP-CHECK-MARKER-PRINTED" in p2.stdout)
    if os.path.exists(marker):
        os.unlink(marker)
    p = subprocess.run(["harnesses/python/check", "core", PROG + "/check_syntax_error.py"], cwd=REPO, capture_output=True, text=True)
    direct_err = subprocess.run([PY, "-B", "-s", PROG + "/check_syntax_error.py"], cwd=REPO, capture_output=True, text=True).stderr
    last = [l for l in direct_err.splitlines() if l.strip()]
    check("check reports a syntax error verbatim, as the interpreter does, exit 1",
          p.returncode == 1 and all(l in p.stdout for l in last[-3:]), "interpreter: %r" % last[-1])
    say("   " + p.stdout.strip().replace("\n", "\n   "))
    p = subprocess.run(["harnesses/python/check", "core", PROG + "/check_static.py"], cwd=REPO, capture_output=True, text=True)
    check("check reports static errors: bad CP-POSING, a non-literal constant, threading in core, a block constant used as a name, an unknown cp call, no cp.stage()",
          p.returncode == 1 and p.stdout.count("error:") == 6)
    say("   " + p.stdout.strip().replace("\n", "\n   "))
    p = subprocess.run(["harnesses/python/check", "core", PROG + "/check_untagged.py"], cwd=REPO, capture_output=True, text=True)
    p2 = subprocess.run(["harnesses/python/run", "core", "X01", "X01a", "behaviour", PROG + "/check_untagged.py", OUT + "/usage"], cwd=REPO, env=ENV, capture_output=True, text=True)
    check("a constant not tagged with a stage: check reports it, and run refuses the program (exit 2, no record)",
          p.returncode == 1 and "before any '# stage k' line" in p.stdout and p2.returncode == 2, p2.stderr.strip())
    say("   " + p.stdout.strip().replace("\n", "\n   "))
    for prog, config in (("x01_total.py", "core"), ("x06_counts.py", "core"), ("x07_wait.py", "stdlib-concurrency"), ("x09_probes.py", "core"), ("x10_nolookahead.py", "core")):
        p = subprocess.run(["harnesses/python/check", config, PROG + "/" + prog], cwd=REPO, capture_output=True, text=True)
        check("check %s %s: no errors" % (config, prog), p.returncode == 0, p.stdout.strip().splitlines()[0])
    say("")
    n_ok = sum(1 for _, ok in results if ok)
    say("%d of %d checks passed" % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
