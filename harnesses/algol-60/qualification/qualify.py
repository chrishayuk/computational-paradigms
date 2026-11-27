#!/usr/bin/env python3
"""Qualification of the ALGOL 60 harness (harnesses/algol-60/README.md, 'Qualification').

Run inside the pinned image, from the repository root:

    python3 harnesses/algol-60/qualification/qualify.py

Every program it runs is a made-up program (qualification/programs/), on the
made-up problems X01-X09 of qualification/stages-made-up.json. No problem
P01-P16 and none of their constants is used. Records go to
qualification/records/<UTC timestamp>/, which is new for every run; the
report is printed (qualification/output.txt is a copy of one run's).

Sections:
  A  the system run directly and the harness agree: output, answers, steps
     (against --max-steps itself), the systems file's step probes, store
  B  incremental and reposed posing give the same answers; modes agree
  C  budget, safety limit (rerun and fixed), error and usage paths
  D  every record passes harnesses/validate.py
  E  check executes nothing
  F  no anticipation: each stage's constants reach the program only with its
     pose or replay message (from a trace of every write to the system's
     input); a stage re-created for its budget is marked as such
"""

import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
Q = "harnesses/algol-60/qualification"
P = Q + "/programs"
STAGES = Q + "/stages-made-up.json"
RUN = "harnesses/algol-60/run"
CHECK = "harnesses/algol-60/check"
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
OUT = "%s/records/%s" % (Q, STAMP)
ENV = dict(os.environ, HARNESS_PURPOSE="qualification", HARNESS_STAGES=STAGES)

results = []


def check(name, ok, detail=""):
    results.append((name, ok))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("\n        " + detail) if detail and not ok else ""))
    sys.stdout.flush()


def sh(cmd, inp=None, cwd=ROOT, env=None):
    return subprocess.run(cmd, input=inp, capture_output=True, cwd=cwd, env=env or ENV)


def harness(config, problem, inst, mode, prog, sub):
    outdir = "%s/%s" % (OUT, sub)
    r = sh([RUN, config, problem, inst, mode, prog, outdir])
    recs = sorted(glob.glob(os.path.join(ROOT, outdir, "%s.%s.*.json" % (inst, mode))))
    rec = json.load(open(recs[-1])) if recs and r.returncode == 0 else None
    if r.returncode != 0:
        print("        run exit %d: %s" % (r.returncode, r.stderr.decode()[-2000:]))
    return r.returncode, rec


def params_line(rec):
    return rec["stages"][0]["attempts"][0]["posed"]["instance_parameters_passed"]["line"]


def stage_consts(prog):
    """Stage k's constants lines, 'k:' removed (README 2.1), parsed here independently of run."""
    c = os.path.join(ROOT, os.path.splitext(prog)[0] + ".constants")
    out = {}
    if os.path.isfile(c):
        for line in open(c, encoding="utf-8"):
            if line.strip():
                k, v = line.split(":", 1)
                out.setdefault(int(k), []).append(v.strip() + "\n")
    return out


def msg(prog, code, k):
    return ("%d %d\n" % (code, k)).encode() + "".join(stage_consts(prog).get(k, [])).encode()


def direct(config, prog, inp, limit=None, measure=False):
    """The system itself, on the input the harness would give, its input
    closed at the end (no harness code involved)."""
    if config == "x1sim":
        d = "/tmp/qual-x1sim"
        os.makedirs(d, exist_ok=True)
        subprocess.run(["cp", os.path.join(ROOT, prog), d + "/prog.a60"])
        return subprocess.run(["x1sim", "prog.a60"], input=inp, capture_output=True, cwd=d)
    cmd = ["algol60-measure" if measure else "algol60"] + (["--x1"] if config == "x1" else [])
    if limit is not None:
        cmd += ["--max-steps", str(limit)]
    if measure:
        cmd += ["--measure"]
    return subprocess.run(cmd + [prog], input=inp, capture_output=True, cwd=ROOT)


def answers_of(text):
    return re.findall(r"\[answer\](.*?)\[/answer\]", text, re.S)


def segments(text):
    out, start = [], 0
    for m in re.finditer(re.escape("[end]"), text):
        out.append(text[start:m.end()])
        start = m.end()
    out.append(text[start:])
    return out


def comp(rec, k, cid="main", attempt=-1):
    a = rec["stages"][k - 1]["attempts"][attempt]
    return [c for c in a["computations"] if c["id"] == cid][0], a


def stage_answers(rec):
    return [[x["verbatim"] for c in s["attempts"][-1]["computations"] for q in c["queries"] for x in q["answers"]]
            for s in rec["stages"]]


def incremental_input(rec, K):
    p = rec["run"]["program"]["path"]
    return params_line(rec).encode() + b"".join(msg(p, 1, k) for k in range(1, K + 1))


def prefix_input(rec, k):
    return incremental_input(rec, k)


def stopped(res):
    return re.search(rb"stopped after \d+ steps\s*$", res.stderr.strip()) is not None


def section_a():
    print("\n== A. The system run directly and the harness agree")
    for config, prog in (("report", P + "/x01-incremental.alg"), ("x1", P + "/x01-incremental.alg"),
                         ("x1", P + "/x01-x1.a60"), ("x1sim", P + "/x01-x1.a60"),
                         ("report", P + "/x02-incremental.alg")):
        prob = "X02" if "x02" in prog else "X01"
        inst = prob + "a"
        code, rec = harness(config, prob, inst, "behaviour", prog, "A-%s-%s" % (config, os.path.basename(prog)))
        if rec is None:
            check("A1 %s %s: harness ran" % (config, prog), False)
            continue
        K = len(rec["stages"])
        d = direct(config, prog, incremental_input(rec, K))
        dsegs = segments(d.stdout.decode())
        hsegs = [s["attempts"][-1]["print"] for s in rec["stages"]]
        check("A1 %s %s: each stage's output as the harness recorded it equals the system's own output, "
              "run directly on the same input" % (config, os.path.basename(prog)),
              dsegs[:K] == hsegs, "direct %r\n        harness %r" % (dsegs[:K], hsegs))
        check("A2 %s %s: the answers the harness collected equal the [answer] texts of the direct output"
              % (config, os.path.basename(prog)),
              [answers_of(s) for s in dsegs[:K]] == stage_answers(rec))

    print("\n-- steps: the harness's counts against --max-steps itself")
    for config in ("report", "x1"):
        for prog, prob in ((P + "/x01-incremental.alg", "X01"), (P + "/x01-reposed.alg", "X01")):
            code, rec = harness(config, prob, "X01a", "cost", prog, "A-steps-%s-%s" % (config, os.path.basename(prog)))
            if rec is None:
                check("A3 %s %s cost run" % (config, prog), False)
                continue
            for k in range(1, len(rec["stages"]) + 1):
                c, a = comp(rec, k)
                R = c["steps"]["restated"]
                if rec["run"]["posing"] == "incremental":
                    inp = prefix_input(rec, k)
                else:
                    inp = params_line(rec).encode() + \
                        b"".join(msg(prog, 2, j) for j in range(1, k)) + msg(prog, 1, k)
                ok_at = not stopped(direct(config, prog, inp, limit=R))
                stops_below = stopped(direct(config, prog, inp, limit=R - 1))
                check("A3 %s %s stage %d: restated steps %d: the interpreter run directly with --max-steps %d "
                      "does not stop, with %d it stops" % (config, os.path.basename(prog), k, R, R, R - 1),
                      ok_at and stops_below)
                if c["steps"]["restart_cost"] is not None:
                    rc = c["steps"]["restart_cost"]
                    inp2 = params_line(rec).encode() + b"".join(msg(prog, 2, j) for j in range(1, k))
                    check("A4 %s %s stage %d: restart cost %d agrees with --max-steps on stages 1..%d alone"
                          % (config, os.path.basename(prog), k, rc, k - 1),
                          not stopped(direct(config, prog, inp2, limit=rc)) and stopped(direct(config, prog, inp2, limit=rc - 1)))
                if c["steps"]["stage"] is not None and k > 1:
                    prev = comp(rec, k - 1)[0]["steps"]["restated"]
                    check("A5 %s %s stage %d: incremental steps = restated(k) - restated(k-1)"
                          % (config, os.path.basename(prog), k), c["steps"]["stage"] == R - prev)

    print("\n-- the systems file's step probes (systems/algol-60/README.md, Units)")
    base = None
    expect = {"block": 3, "proc": 3, "forstep": 5, "forlist": 1}
    for name in ("base", "block", "proc", "forstep", "forlist"):
        code, rec = harness("report", "X08", "X08a", "cost", P + "/x08-%s.alg" % name, "A-probe-%s" % name)
        s = comp(rec, 1)[0]["steps"]["stage"] if rec else None
        if name == "base":
            base = s
            check("A6 probe base: stage steps measured (%r)" % s, s is not None)
        else:
            check("A6 probe %s: stage steps %r - base %r = %d, as the systems file says"
                  % (name, s, base, expect[name]), s is not None and base is not None and s - base == expect[name])

    print("\n-- store: the harness's storage record against --measure run directly")
    for config in ("report", "x1"):
        code, rec = harness(config, "X01", "X01a", "storage", P + "/x01-incremental.alg", "A-store-%s" % config)
        if rec is None:
            check("A7 storage run", False)
            continue
        for k in range(1, len(rec["stages"]) + 1):
            d = direct(config, P + "/x01-incremental.alg", prefix_input(rec, k), measure=True)
            table = {}
            for l in d.stderr.decode().splitlines():
                m = re.match(r"^(\w+)\t(-?\d+)\t(-?\d+)$", l)
                if m:
                    table[m.group(1)] = (int(m.group(2)), int(m.group(3)))
            q = rec["stages"][k - 1]["attempts"][-1]["store"]["quantities"]
            ok = True
            for name, v in q.items():
                if v["peak"] is not None and v["peak"]["value"] != table[name][1]:
                    ok = False
                if v["boundary"] is not None and v["boundary"] != table[name][0]:
                    ok = False
            check("A7 %s stage %d: every store figure the harness recorded equals algol60-measure --measure "
                  "on stages 1..%d run directly" % (config, k, k), ok and bool(q))
            c = comp(rec, k)[0]
            rw = c["steps"]["repeated_work"]
            check("A8 %s stage %d: repeated work recorded from name_repeat_evaluations (%r)" % (config, k, rw),
                  rw is not None and "name_repeat_evaluations" in rw)


def section_b():
    print("\n== B. Incremental and reposed posing give the same answers; modes agree")
    pairs = [("report", "X01", P + "/x01-incremental.alg", P + "/x01-reposed.alg"),
             ("x1", "X01", P + "/x01-incremental.alg", P + "/x01-reposed.alg"),
             ("x1sim", "X01", P + "/x01-x1.a60", P + "/x01-x1-reposed.a60"),
             ("report", "X02", P + "/x02-incremental.alg", P + "/x02-reposed.alg")]
    for config, prob, inc, rep in pairs:
        _, ri = harness(config, prob, prob + "a", "behaviour", inc, "B-%s-%s-inc" % (config, prob))
        _, rr = harness(config, prob, prob + "a", "behaviour", rep, "B-%s-%s-rep" % (config, prob))
        if not ri or not rr:
            check("B1 %s %s runs" % (config, prob), False)
            continue
        hows = [s["attempts"][-1]["posed"]["how"] for s in rr["stages"]]
        hows_i = [s["attempts"][-1]["posed"]["how"] for s in ri["stages"]]
        check("B1 %s %s: incremental (%s) and reposed (%s) runs give the same answers at every stage"
              % (config, prob, ",".join(hows_i), ",".join(hows)), stage_answers(ri) == stage_answers(rr),
              "%r\n        %r" % (stage_answers(ri), stage_answers(rr)))
        if prob == "X02":
            rc = rr["stages"][2]["attempts"][0]["posed"]["replayed_commitments"]
            v = stage_answers(rr)[1][0]
            check("B2 X02 reposed: stage 3 replays the commit of stage 2 as v = %r, verbatim as first selected" % v,
                  rc == [{"stage": 2, "value_verbatim": v, "selected_in_run": rr["run"]["run_id"]}])
            log = rr["effects"]["log_after_run"]
            check("B3 X02 reposed: entries emitted while replaying stage 1 are marked during_replay_of 1",
                  [e["during_replay_of"] for e in log] == [None, 1, None, 1])
            logi = ri["effects"]["log_after_run"]
            check("B4 X02 incremental: one entry per emit of the computation (the re-created stages' emits are "
                  "not appended again)", [(e["entry"], e["stage"]) for e in logi] == [("chose 1 ", 1), ("commit 1 ", 2)])
    for config in ("report", "x1"):
        got = {}
        for mode in ("behaviour", "cost", "storage"):
            _, r = harness(config, "X01", "X01a", mode, P + "/x01-incremental.alg", "B-modes-%s" % config)
            got[mode] = stage_answers(r) if r else None
        check("B5 %s: behaviour, cost and storage runs give the same answers" % config,
              got["behaviour"] is not None and got["behaviour"] == got["cost"] == got["storage"])
    for order in ("UV", "VU"):
        for config, prog in (("report", P + "/x03-spawn.alg"), ("x1sim", P + "/x03-x1.a60")):
            _, r = harness(config, "X03", "X03a." + order, "behaviour", prog, "B-spawn-%s" % config)
            if not r:
                check("B6 spawn %s %s" % (config, order), False)
                continue
            cs = r["stages"][0]["attempts"][0]["computations"]
            check("B6 %s X03a.%s: spawned in the instance's order, each with its own query and budget, side by side false"
                  % (config, order), [c["id"] for c in cs] == list(order) and all(c["spawned"] and c["side_by_side"] is False for c in cs)
                  and sorted(x["verbatim"].replace(" ", "") for c in cs for q in c["queries"] for x in q["answers"]) == ["u=55", "v=100"])


def section_c():
    print("\n== C. Budget, safety limit, error and usage paths")
    _, r = harness("report", "X04", "X04a", "behaviour", P + "/x04-budget.alg", "C-budget")
    if r:
        s2, _ = comp(r, 2)
        s3, a3 = comp(r, 3)
        check("C1 report X04 stage 2: state budget, budget_exhausted, answers printed before the budget kept (%r)"
              % [x["verbatim"] for x in s2["queries"][0]["answers"]],
              s2["execution_state"]["states"] == ["budget"] and s2["steps"]["budget_exhausted"]
              and s2["queries"][0]["ended_by"] == "budget" and s2["steps"]["stage"] == 1000000)
        check("C2 report X04 stage 3: reposed after-budget (the interpreter cannot continue past --max-steps)",
              a3["posed"]["how"] == "reposed" and a3["posed"]["reason"] == "after-budget")
    _, r = harness("report", "X05", "X05a", "behaviour", P + "/x05-error.alg", "C-error")
    if r:
        s2, _ = comp(r, 2)
        _, a3 = comp(r, 3)
        check("C3 report X05 stage 2: state error with the interpreter's message verbatim (%r)"
              % s2["execution_state"]["error_verbatim"],
              s2["execution_state"]["states"] == ["error"] and "outside the bounds" in (s2["execution_state"]["error_verbatim"] or ""))
        check("C4 report X05 stage 3: reposed after-error", a3["posed"]["reason"] == "after-error")
    for config, prog in (("x1sim", P + "/x05-x1.a60"),):
        _, r = harness(config, "X05", "X05a", "behaviour", prog, "C-error-x1sim")
        if r:
            s2, _ = comp(r, 2)
            check("C5 x1sim X05 stage 2: state error, x1sim's message verbatim (%r)" % s2["execution_state"]["error_verbatim"],
                  s2["execution_state"]["states"] == ["error"] and "Error" in (s2["execution_state"]["error_verbatim"] or ""))
    for config, prog in (("report", P + "/x06-timeout.alg"), ("x1sim", P + "/x06-x1.a60")):
        _, r = harness(config, "X06", "X06a", "behaviour", prog, "C-timeout-" + config)
        if r:
            atts = r["stages"][1]["attempts"]
            check("C6 %s X06 stage 2: the safety limit stops attempt 1 (action rerun), attempt 2 is reposed at the "
                  "raised limit and stops too (final-timeout); answers before the stop kept (%r)"
                  % (config, [x["verbatim"] for x in atts[0]["computations"][0]["queries"][0]["answers"]]),
                  len(atts) == 2 and atts[0]["safety_limit"]["action"] == "rerun"
                  and atts[1]["safety_limit"]["action"] == "final-timeout" and atts[1]["posed"]["how"] == "reposed"
                  and atts[1]["limit_s"] == 8 and atts[0]["computations"][0]["execution_state"]["states"] == ["timeout"])
            a3 = r["stages"][2]["attempts"][0]
            check("C7 %s X06 stage 3: reposed after-timeout" % config, a3["posed"]["reason"] == "after-timeout")
    _, r = harness("report", "X07", "X07a.n5", "behaviour", P + "/x07-fixed.alg", "C-fixed")
    if r:
        atts = r["stages"][0]["attempts"]
        check("C8 report X07: under a fixed limit the first stop is final (fixed-limit-timeout, no rerun)",
              len(atts) == 1 and atts[0]["safety_limit"]["action"] == "fixed-limit-timeout")
    for args, what in ((["cost", "x1sim"], "cost mode for x1sim"), (["behaviour", "nosuch"], "an unknown configuration")):
        mode, config = args
        r = sh([RUN, config, "X01", "X01a", mode, P + "/x01-x1.a60", OUT + "/C-usage"])
        made = glob.glob(os.path.join(ROOT, OUT, "C-usage", "*.json"))
        check("C9 %s: usage error, exit 2, no record" % what, r.returncode == 2 and not made)
    r = sh([RUN, "report", "X01", "X99a", "behaviour", P + "/x01-x1.a60", OUT + "/C-usage"])
    check("C9 an unknown instance: usage error, exit 2", r.returncode == 2)


def section_d():
    print("\n== D. Every record passes validate.py")
    files = sorted(f for f in glob.glob(os.path.join(ROOT, OUT, "**", "*.json"), recursive=True))
    r = sh([sys.executable, "harnesses/validate.py", "--stages", STAGES] + files)
    out = r.stdout.decode()
    n_valid = out.count(": valid")
    print("        %d record files" % len(files))
    check("D1 all %d records valid (validate.py exit %d, %d 'valid')" % (len(files), r.returncode, n_valid),
          r.returncode == 0 and n_valid == len(files) and files, out[-3000:])
    inval = glob.glob(os.path.join(ROOT, OUT, "**", "*.INVALID.json"), recursive=True)
    check("D2 no INVALID record was written", not inval)
    faults = []
    for f in files:
        faults += json.load(open(f))["harness_faults"]
    check("D3 no record has a harness fault", not faults, repr(faults[:5]))


def section_e():
    print("\n== E. check executes nothing")
    marker = b"MARKER-IF-EXECUTED-7f3a"
    for config, prog in (("report", P + "/x09-marker.alg"), ("x1", P + "/x09-marker.alg"), ("x1sim", P + "/x09-marker.a60")):
        before = set(os.listdir(os.path.join(ROOT, P)))
        r = sh([CHECK, config, prog])
        after = set(os.listdir(os.path.join(ROOT, P)))
        d = direct(config, prog, b"")
        check("E1 %s: the marker program run directly prints its marker (%r)" % (config, d.stdout[:40]), marker in d.stdout)
        check("E2 %s: check exits %d, its output has no marker, and no file appears beside the program"
              % (config, r.returncode), r.returncode == 0 and marker not in r.stdout + r.stderr and before == after,
              (r.stdout + r.stderr).decode()[-800:])
    r = sh([CHECK, "report", P + "/x01-x1.a60"])
    check("E3 report: check reports a program in the X1 form verbatim as an error (exit 1)",
          r.returncode == 1 and b"not declared" in r.stdout)
    for config, prog in (("report", P + "/x01-incremental.alg"), ("x1", P + "/x01-x1.a60"), ("x1sim", P + "/x01-x1.a60")):
        r = sh([CHECK, config, prog])
        check("E4 %s: check accepts %s" % (config, os.path.basename(prog)), r.returncode == 0)


def section_f():
    print("\n== F. No anticipation: a stage's constants reach the program only when the stage is posed")
    cases = (("report", P + "/x01-incremental.alg", "behaviour"), ("report", P + "/x01-reposed.alg", "behaviour"),
             ("x1", P + "/x01-incremental.alg", "cost"), ("x1sim", P + "/x01-x1.a60", "behaviour"),
             ("x1sim", P + "/x01-x1-reposed.a60", "behaviour"), ("report", P + "/x06-timeout.alg", "behaviour"))
    for config, prog, mode in cases:
        trace = os.path.join(ROOT, OUT, "F-trace-%s-%s-%s.jsonl" % (config, os.path.basename(prog), mode))
        os.makedirs(os.path.dirname(trace), exist_ok=True)
        prob = "X06" if "x06" in prog else "X01"
        env = dict(ENV, HARNESS_INPUT_TRACE=trace)
        outdir = "%s/F-%s-%s-%s" % (OUT, config, os.path.basename(prog), mode)
        r = sh([RUN, config, prob, prob + "a", mode, prog, outdir], env=env)
        streams = {}
        for l in open(trace, encoding="utf-8"):
            e = json.loads(l)
            streams.setdefault(e["pid"], []).append(e["data"])
        sc = stage_consts(prog)
        values = {v: k for k, vs in sc.items() for v in vs}
        bad = []
        for pid, writes in streams.items():
            if writes[0].count("\n") != 1 or any(writes[0] == v for v in values):
                bad.append("process %s: its first write is not the instance line alone: %r" % (pid, writes[0]))
            for w in writes[1:]:
                lines = w.splitlines(keepends=True)
                head = lines[0].split()
                k = int(head[1]) if len(head) >= 2 else None
                rest = lines[1:]
                if head and head[0] == "3":
                    rest = rest[1:]           # the replayed value v
                if rest != sc.get(k, []):
                    bad.append("process %s: message %r carries %r, stage %s's constants are %r"
                               % (pid, lines[0], rest, k, sc.get(k, [])))
        check("F1 %s %s %s: in all %d processes the harness started (attempts and probes), the input before a "
              "stage's message holds no constants, and each pose or replay message of stage k carries exactly "
              "stage k's lines" % (config, os.path.basename(prog), mode, len(streams)),
              r.returncode == 0 and streams and not bad, "; ".join(bad[:3]))
    print("\n-- the stage re-created for its budget is marked as such")
    _, rec = harness("report", "X01", "X01a", "cost", P + "/x01-incremental.alg", "F-recreated")
    _, rec2 = harness("report", "X02", "X02a", "behaviour", P + "/x02-incremental.alg", "F-recreated-commit")
    for r_, name in ((rec, "X01 cost"), (rec2, "X02 behaviour")):
        for k in range(1, len(r_["stages"]) + 1):
            c, a = comp(r_, k)
            marks = [n for n in a.get("notes", []) if n.startswith("recreated_for_budget: true")]
            if k == 1:
                check("F2 %s stage 1: fresh, not marked re-created" % name, not marks)
                continue
            m = re.search(r"prefix_steps: (\d+)", marks[0]) if marks else None
            prev = comp(r_, k - 1)[0]["steps"]["restated"]
            ok = bool(m) and a["posed"]["how"] == "incremental"
            if prev is not None and m:
                ok = ok and int(m.group(1)) == prev
                if c["steps"]["stage"] is not None:
                    ok = ok and c["steps"]["stage"] == c["steps"]["restated"] - int(m.group(1))
            check("F2 %s stage %d: marked recreated_for_budget, prefix_steps %s = restated steps of stage %d, "
                  "not charged to the stage" % (name, k, m and m.group(1), k - 1), ok)
    c3 = [n for n in rec2["stages"][2]["attempts"][0].get("notes", []) if n.startswith("recreated_for_budget")]
    check("F3 X02 stage 3: the note lists commit stage 2 as carried out again in the re-created prefix",
          bool(c3) and "prefix_commit_stages_carried_out_again: [2]" in c3[0])


def main():
    os.chdir(ROOT)
    print("ALGOL 60 harness qualification, %s, records in %s" % (STAMP, OUT))
    print("harness commit %s" % subprocess.run(["git", "-c", "safe.directory=*", "rev-parse", "HEAD"],
                                               capture_output=True, text=True).stdout.strip())
    section_a()
    section_b()
    section_c()
    section_e()
    section_f()
    section_d()
    n_fail = sum(1 for _, ok in results if not ok)
    print("\n%d checks, %d passed, %d failed" % (len(results), len(results) - n_fail, n_fail))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
