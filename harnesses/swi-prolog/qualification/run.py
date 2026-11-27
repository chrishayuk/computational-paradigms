#!/usr/bin/env python3
"""Qualification of the SWI-Prolog harness (harnesses/swi-prolog/README.md,
"Qualification"). Runs inside the pinned swipl:11.0.1 image, from the
repository root:

    python3 harnesses/swi-prolog/qualification/run.py

(rerun.sh starts it in the image from the host, and writes output.txt).
Only made-up programs are run (programs/), against the made-up stages file
stages-made-up.json; no problem P01-P16 and none of their constants are
used. Every record goes under records/ and is kept; every one is checked
with harnesses/validate.py. Exit status 0 if every check passed.
"""

import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RUN = os.path.join(REPO, "harnesses", "swi-prolog", "run")
CHECK = os.path.join(REPO, "harnesses", "swi-prolog", "check")
VALIDATE = os.path.join(REPO, "harnesses", "validate.py")
STAGES = os.path.relpath(os.path.join(HERE, "stages-made-up.json"), REPO)
PROGS = os.path.relpath(os.path.join(HERE, "programs"), REPO)
RECORDS = os.path.relpath(os.path.join(HERE, "records"), REPO)
EXPECTED = os.path.join(REPO, "systems", "swi-prolog", "probes", "expected-macos-arm64.txt")
TOPLEVEL_OPTS = "set_prolog_flag(answer_write_options,[quoted(true),portray(true),max_depth(0),spacing(next_argument)])"

ALL = ["behaviour", "cost", "storage"]
RESULTS = []          # (section, name, ok, detail)
NEW_RECORDS = []


def say(*a):
    print(*a, flush=True)


def result(section, name, ok, detail=""):
    RESULTS.append((section, name, ok, detail))
    say("  %s  %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail else ""))


def harness(config, problem, instance, mode, prog):
    out = os.path.join(RECORDS, config, problem, "raw")
    env = dict(os.environ, CP_SWI_STAGES=STAGES, CP_PURPOSE="qualification",
               CP_QUAL_LATE_REV="yzzyxetalqz",     # xlate.pl's word, reversed
               CP_QUAL_TRACE=os.path.join(HERE, "programs", "noexec-trace.txt"))
    before = set(glob.glob(os.path.join(REPO, out, "*.json")))
    p = subprocess.run([RUN, config, problem, instance, mode, os.path.join(PROGS, prog), out],
                       cwd=REPO, env=env, capture_output=True, text=True)
    after = set(glob.glob(os.path.join(REPO, out, "*.json")))
    new = sorted(after - before)
    rec = None
    for f in new:
        NEW_RECORDS.append(f)
        if not f.endswith(".INVALID.json"):
            with open(f, encoding="utf-8") as fh:
                rec = json.load(fh)
    return p.returncode, rec, (new[-1] if new else None), p.stdout + p.stderr


def direct(prog, k, cap):
    p = subprocess.run(["swipl", "-f", "none", "-q", "direct.pl", "--", os.path.join("programs", prog), str(k), str(cap)],
                       cwd=HERE, capture_output=True, text=True)
    q = subprocess.run(["swipl", "-f", "none", "-q", "direct.pl", "--", os.path.join("programs", prog), str(k), str(cap)],
                       cwd=HERE, capture_output=True, text=True, env=dict(os.environ, DIRECT_END_ONLY="1"))
    d = {}
    for line in p.stdout.splitlines() + q.stdout.splitlines():
        if "=" in line:
            key, v = line.split("=", 1)
            d[key] = v
    return d


def plist(v):
    """A Prolog list of integers, as direct.pl prints it."""
    v = v.strip()
    if not v.startswith("["):
        return v
    return [int(x) for x in v[1:-1].split(",") if x.strip()]


def stripped_copy(prog):
    """The program without its CONSTANTS block, as the harness loads it."""
    lines = open(os.path.join(REPO, PROGS, prog), encoding="utf-8").read().split("\n")
    b = [i for i, l in enumerate(lines) if "CONSTANTS BEGIN" in l]
    e = [i for i, l in enumerate(lines) if "CONSTANTS END" in l]
    if b and e:
        lines = ["" if b[0] <= i <= e[0] else l for i, l in enumerate(lines)]
    d = "/tmp/cp-qual-toplevel"
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, prog)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def toplevel(prog, k, names, n_requests, consts):
    """The system's own toplevel, run directly: the query of stages 1..k
    (each with its constants, as the harness passes them), and n_requests
    ';' (requests for another answer), then end of input."""
    vs = "[" + ",".join(names) + "]"
    q = ", ".join(["stage(%d,%s,%s)" % (j, vs, consts[j]) for j in range(1, k + 1)] + ["query(%d,%s)" % (k, vs)]) + ".\n"
    inp = q + ";\n" * n_requests
    p = subprocess.run(["swipl", "-f", "none", "-q", "-g", TOPLEVEL_OPTS, stripped_copy(prog)],
                       cwd=REPO, input=inp, capture_output=True, text=True)
    return p.stdout


def stage_answers(rec, k, comp="main"):
    st = rec["stages"][k - 1]["attempts"][-1]
    for c in st["computations"]:
        if c["id"] == comp:
            return c
    return None


def restated_at(rec, k):
    c = stage_answers(rec, k)
    s = c["steps"]
    base = s["restart_cost"] or 0
    return [a["steps_at"] + base for a in c["queries"][0]["answers"]], (s["to_end"] + base if s["to_end"] is not None else None)


# ------------------------------------------------------------------ runs ---

def run_matrix():
    say("== runs (made-up programs, made-up stages file %s)" % STAGES)
    m = {}

    def go(key, config, problem, inst, modes, prog):
        for mode in modes:
            t = time.time()
            rc, rec, path, out = harness(config, problem, inst, mode, prog)
            m[(key, config, inst, mode)] = rec
            say("  run %-6s %-11s %-12s %-9s %-16s exit %d  %.1fs  %s" %
                (key, config, inst, mode, prog, rc, time.time() - t, os.path.basename(path) if path else "(no record)"))
            if rc != 0:
                say("    " + out.strip().replace("\n", "\n    "))
    for c in ["plain", "tabling", "coroutines", "constraints", "session"]:
        go("x01", c, "X01", "X01a", ALL, "x01-flag.pl")
    for c in ["plain", "session"]:
        go("x02", c, "X02", "X02a", ALL, "x02-commit.pl")
        for i in ["X03a.UV", "X03a.VU"]:
            go("x03", c, "X03", i, ALL, "x03-spawn.pl")
        for i in ["X04a.n10", "X04a.n4997", "X04a.n4998"]:
            go("x04", c, "X04", i, ["behaviour", "cost"], "x04-budget.pl")
        go("x05", c, "X05", "X05a", ["behaviour"], "x05-timeout.pl")
        go("x06", c, "X06", "X06a", ALL, "x06-error.pl")
        for i in ["X09a.n5.up", "X09a.n5.down"]:
            go("x09", c, "X09", i, ALL, "x09-count.pl")
            go("x09n", c, "X09", i, ALL, "x09-nocount.pl")
        for i in ["X10a.all", "X10a.any"]:
            go("x10", c, "X10", i, ALL, "x10-modes.pl")
        go("x11", c, "X11", "X11a", ALL, "x11-replace.pl")
        go("x12", c, "X12", "X12a", ALL, "x12-fallback.pl")
    go("x07", "plain", "X07", "X07a", ["behaviour"], "x07-fixed.pl")
    for c in ["coroutines", "session"]:
        go("x08f", c, "X08", "X08a", ALL, "x08-freeze.pl")
    for c in ["constraints", "session"]:
        go("x08c", c, "X08", "X08a", ALL, "x08-clpfd.pl")
        go("x08w", c, "X08", "X08a", ALL, "x08-wait.pl")
        go("x08u", c, "X08", "X08a", ["behaviour"], "x08-undef.pl")
    go("x10t", "tabling", "X10", "X10a.all", ALL, "x10-table.pl")
    go("xerr", "plain", "X01", "X01a", ["behaviour"], "xerr-syntax.pl")
    for c in ["plain", "session"]:
        go("xlate", c, "X01", "X01a", ["behaviour"], "xlate.pl")
    go("xthr", "session", "X06", "X06a", ["behaviour"], "xerr-throw.pl")
    go("pgen", "plain", "X10", "X10a.all", ALL, "probe-gen.pl")
    go("pwork", "plain", "X10", "X10a.all", ALL, "probe-work.pl")
    go("pw2", "plain", "X10", "X10a.all", ALL, "probe-w2.pl")
    go("pfrz", "coroutines", "X10", "X10a.all", ALL, "probe-freeze.pl")
    go("pclp", "constraints", "X10", "X10a.all", ALL, "probe-clpfd.pl")
    go("ptab", "tabling", "X10", "X10a.all", ALL, "probe-table.pl")
    return m


# ---------------------------------------------------------------- checks ---

DIRECT = [  # (key, config, instance, program, stages)
    ("x01", "plain", "X01a", "x01-flag.pl", 3),
    ("x08f", "coroutines", "X08a", "x08-freeze.pl", 3),
    ("x08c", "constraints", "X08a", "x08-clpfd.pl", 3),
    ("x10", "plain", "X10a.all", "x10-modes.pl", 1),
    ("x10t", "tabling", "X10a.all", "x10-table.pl", 1),
    ("x11", "plain", "X11a", "x11-replace.pl", 3),
    ("x12", "plain", "X12a", "x12-fallback.pl", 2),
    ("pgen", "plain", "X10a.all", "probe-gen.pl", 1),
    ("pwork", "plain", "X10a.all", "probe-work.pl", 1),
    ("pw2", "plain", "X10a.all", "probe-w2.pl", 1),
    ("pfrz", "coroutines", "X10a.all", "probe-freeze.pl", 1),
    ("pclp", "constraints", "X10a.all", "probe-clpfd.pl", 1),
    ("ptab", "tabling", "X10a.all", "probe-table.pl", 1),
]


def check_direct(m):
    say("== (a) the system run directly against the answers, steps and store the harness collects")
    for key, config, inst, prog, K in DIRECT:
        beh = m.get((key, config, inst, "behaviour"))
        cost = m.get((key, config, inst, "cost"))
        sto = m.get((key, config, inst, "storage"))
        if not (beh and cost and sto):
            result("a", "%s %s: records" % (key, config), False, "a record is missing")
            continue
        for k in range(1, K + 1):
            d = direct(prog, k, 20)
            c = stage_answers(beh, k)
            q = c["queries"][0]
            names = [n.strip("' ") for n in d["names"].strip("[]").split(",") if n.strip()]
            # answers, against the toplevel's own output
            n_req = len(q["answers"]) if q["ended_by"] == "exhausted" and q["answers"] and not q["answers"][-1]["verbatim"].endswith(".\n\n") else max(len(q["answers"]) - 1, 0)
            if q["ended_by"] == "exhausted" and not q["answers"]:
                n_req = 0
            consts = {j: d["consts%d" % j] for j in range(1, k + 1)}
            tl = toplevel(prog, k, names, n_req, consts)
            mine = "".join(a["verbatim"] for a in q["answers"])
            ok = tl.startswith(mine) and (q["ended_by"] != "exhausted" or q["answers"] and q["answers"][-1]["verbatim"].endswith(".\n\n") or tl[len(mine):].startswith("false."))
            result("a", "%s %s stage %d: %d answer(s) verbatim as the toplevel prints them" % (key, config, k, len(q["answers"])), ok,
                   "" if ok else "toplevel %r, harness %r" % (tl[:300], mine[:300]))
            # steps (cost mode), against statistics/2 and call_with_inference_limit/3
            at, end = restated_at(cost, k)
            dat = plist(d.get("at", "[]"))
            dfirst = int(d["first"]) if d.get("first", "none") != "none" else None
            ok1 = (not at and dfirst is None) or (at and at[0] == dfirst)
            result("a", "%s %s stage %d: steps to the first answer %s = statistics/2 difference - 1 (%s)" %
                   (key, config, k, at[0] if at else None, dfirst), ok1)
            say("  info  %s %s stage %d: call_with_inference_limit/3 smallest limit %s, statistics/2 difference - 1 %s%s" %
                (key, config, k, d.get("minlimit"), dfirst,
                 "" if (at and int(d["minlimit"]) == dfirst + 1) else "  (they differ: QUESTIONS.md S16)"))
            ok2 = at == dat[:len(at)] and len(at) == min(len(dat), 20)
            result("a", "%s %s stage %d: steps at every answer %s = call_with_inference_limit/3 per answer %s" % (key, config, k, at, dat), ok2)
            if q["ended_by"] == "exhausted" and not (q["answers"] and q["answers"][-1]["verbatim"].endswith(".\n\n")):
                result("a", "%s %s stage %d: steps to the end %s = statistics/2 around (goal, fail ; true), first in a fresh process, %s" % (key, config, k, end, d.get("end_cold")),
                       str(end) == d.get("end_cold"))
            # choicepoints at answers (storage)
            cs = stage_answers(sto, k)
            cps = [a["alternatives_at"] for a in cs["queries"][0]["answers"]]
            dcps = plist(d.get("cps", "[]"))
            result("a", "%s %s stage %d: retained choicepoints at each answer %s = the probe's cp_since/2 %s" % (key, config, k, cps, dcps[:len(cps)]),
                   cps == dcps[:len(cps)])
            # attributed variables and residual goals at the first answer
            if config in ("coroutines", "constraints") and len(q["answers"]) == 1 and d.get("attvars") not in (None, "none"):
                sb = c["suspended"]["items"] or {}
                ok = sb.get("attributed_variables") == int(d["attvars"]) and sb.get("residual_goals") == int(d["residual_goals"])
                result("a", "%s %s stage %d: attributed variables %s, residual goals %s = term_attvars/2, copy_term/3 directly (%s, %s)" %
                       (key, config, k, sb.get("attributed_variables"), sb.get("residual_goals"), d["attvars"], d["residual_goals"]), ok)
            # tables
            if config == "tabling" and d.get("tables"):
                qs = sto["stages"][k - 1]["attempts"][-1]["store"]["quantities"]
                ok = qs["tables"]["boundary"] == int(d["tables"]) and qs["table_answers"]["boundary"] == int(d["table_answers"])
                result("a", "%s %s stage %d: tables %s, table answers %s = current_table/2, trie_property/2 directly (%s, %s); table_space_used %s, directly %s" %
                       (key, config, k, qs["tables"]["boundary"], qs["table_answers"]["boundary"], d["tables"], d["table_answers"],
                        qs["table_space_used_bytes"]["boundary"], d.get("table_space_used_bytes")), ok)
            # every mode: the same answers and steps
            same = True
            for other in (cost, sto):
                co = stage_answers(other, k)
                if [a["verbatim"] for a in co["queries"][0]["answers"]] != [a["verbatim"] for a in q["answers"]]:
                    same = False
                if co["steps"]["restated"] != c["steps"]["restated"] or \
                        [a["steps_at"] for a in co["queries"][0]["answers"]] != [a["steps_at"] for a in q["answers"]]:
                    same = False
            result("a", "%s %s stage %d: behaviour, cost and storage runs give the same answers and the same steps" % (key, config, k), same)


def check_probes(m):
    say("== (a) the systems file's probes, run through the harness, against probes/expected-macos-arm64.txt")
    exp = {}
    with open(EXPECTED) as f:
        for line in f:
            parts = line.rstrip("\n").split("|", 2)
            if len(parts) == 3 and "=" in parts[2]:
                k, v = parts[2].split("=", 1)
                exp[(parts[1], k)] = v
    w = m.get(("pwork", "plain", "X10a.all", "cost"))
    if w:
        s = stage_answers(w, 1)["steps"]
        result("a", "probe work/0: steps of stage(1) and query(1) %s = the probe's delta(work) %s (call/1 + work's body + statistics/2, i.e. the same count)" %
               (s["to_end"], exp[("inferences[plain]", "work_warm_1")]), str(s["to_end"]) == exp[("inferences[plain]", "work_warm_1")])
        result("a", "probe work/0: the budget-relevant count %s - 1 = the probe's minlimit_work %s" % (s["to_end"], exp[("inferences[plain]", "minlimit_work")]),
               str(s["to_end"] - 1) == exp[("inferences[plain]", "minlimit_work")])
    w = m.get(("pw2", "plain", "X10a.all", "cost"))
    if w:
        s = stage_answers(w, 1)["steps"]
        result("a", "probe w2/0: steps %s = the probe's delta(w2) %s" % (s["to_end"], exp[("inferences[plain]", "w2_warm")]),
               str(s["to_end"]) == exp[("inferences[plain]", "w2_warm")])
    g = m.get(("pgen", "plain", "X10a.all", "storage"))
    if g:
        c = stage_answers(g, 1)
        cps = [a["alternatives_at"] for a in c["queries"][0]["answers"]]
        # the probe counts inside findall/3, which adds 2 (measurement.md, section 1)
        p = subprocess.run(["swipl", "-f", "none", "-q", "-g",
                            "use_module('../../../systems/swi-prolog/probes/cpcount'),consult('programs/probe-gen.pl'),cp_mark(M),findall(N,(gen(4,_),cp_since(M,N)),Ns),msort(Ns,S),clumped(S,H),writeq(Ns-H),nl",
                            "-t", "halt"], cwd=HERE, capture_output=True, text=True)
        txt = p.stdout.strip()
        ns = [int(x) for x in txt.split("]-")[0].strip("[").split(",")]
        hist = txt.split("]-", 1)[1]
        result("a", "probe gen(4,_): the probe's histogram %s = expected %s" % (hist, exp[("choicepoints[main]", "gen4_histogram_cp_count")]),
               hist == exp[("choicepoints[main]", "gen4_histogram_cp_count")])
        result("a", "probe gen(4,_): retained choicepoints at the harness's 20 answers %s = the probe's first 20, less findall/3's 2 (%s)" %
               (cps, [n - 2 for n in ns[:20]]), cps == [n - 2 for n in ns[:20]])
    f = m.get(("pfrz", "coroutines", "X10a.all", "behaviour"))
    if f:
        it = stage_answers(f, 1)["suspended"]["items"]
        result("a", "probe freeze: attributed variables %s, residual goals %s = expected %s, %s" %
               (it["attributed_variables"], it["residual_goals"], exp[("attvars[counts]", "freeze_attvars")], exp[("attvars[counts]", "freeze_residual_goals")]),
               str(it["attributed_variables"]) == exp[("attvars[counts]", "freeze_attvars")] and str(it["residual_goals"]) == exp[("attvars[counts]", "freeze_residual_goals")])
    f = m.get(("pclp", "constraints", "X10a.all", "behaviour"))
    if f:
        it = stage_answers(f, 1)["suspended"]["items"]
        result("a", "probe clpfd: attributed variables %s, residual goals %s = expected %s, %s" %
               (it["attributed_variables"], it["residual_goals"], exp[("attvars[counts]", "clpfd_attvars")], exp[("attvars[counts]", "clpfd_residual_goals")]),
               str(it["attributed_variables"]) == exp[("attvars[counts]", "clpfd_attvars")] and str(it["residual_goals"]) == exp[("attvars[counts]", "clpfd_residual_goals")])
    t = m.get(("ptab", "tabling", "X10a.all", "storage"))
    if t:
        qs = t["stages"][0]["attempts"][-1]["store"]["quantities"]
        ok = (str(qs["tables"]["boundary"]) == exp[("tables[usage]", "after_path1_tables")] and
              str(qs["table_answers"]["boundary"]) == exp[("tables[usage]", "after_path1_answers")] and
              str(qs["table_space_used_bytes"]["boundary"]) == exp[("tables[usage]", "after_path1_table_space_used")])
        result("a", "probe path(1,_): tables %s, answers %s, table_space_used %s = expected %s, %s, %s" %
               (qs["tables"]["boundary"], qs["table_answers"]["boundary"], qs["table_space_used_bytes"]["boundary"],
                exp[("tables[usage]", "after_path1_tables")], exp[("tables[usage]", "after_path1_answers")],
                exp[("tables[usage]", "after_path1_table_space_used")]), ok)


def check_incremental(m):
    say("== (b) incremental (session) and reposed posing give the same answers")
    pairs = [("x01", "plain", "X01a"), ("x08f", "coroutines", "X08a"), ("x08c", "constraints", "X08a"),
             ("x10", "plain", "X10a.all"), ("x10", "plain", "X10a.any"), ("x11", "plain", "X11a"),
             ("x12", "plain", "X12a"), ("x09", "plain", "X09a.n5.up"), ("x09", "plain", "X09a.n5.down"),
             ("x03", "plain", "X03a.UV"), ("x03", "plain", "X03a.VU"), ("x04", "plain", "X04a.n10")]
    for key, rc, inst in pairs:
        for mode in ("behaviour", "cost"):
            a = m.get((key, rc, inst, mode))
            b = m.get((key, "session", inst, mode))
            if not (a and b):
                continue
            ok, why = True, []
            for st_a, st_b in zip(a["stages"], b["stages"]):
                ca = st_a["attempts"][-1]["computations"]
                cb = st_b["attempts"][-1]["computations"]
                for x, y in zip(ca, cb):
                    va = [z["verbatim"] for z in x["queries"][0]["answers"]]
                    vb = [z["verbatim"] for z in y["queries"][0]["answers"]]
                    if va != vb or x["queries"][0]["ended_by"] != y["queries"][0]["ended_by"]:
                        ok = False
                        why.append("stage %d: %s vs %s" % (st_a["stage"], va, vb))
                    if mode == "cost":
                        # the separate run's restated steps (session) and the reposed run's
                        ra = x["steps"]["restated"]
                        sr = st_b["attempts"][-1].get("separate_run")
                        rb = sr["steps_restated"] if sr else y["steps"]["restated"]
                        if ra != rb:
                            ok = False
                            why.append("stage %d: restated steps %s vs %s" % (st_a["stage"], ra, rb))
            result("b", "%s %s vs session, %s, %s: answers%s per stage" % (key, rc, inst, mode, " and restated steps" if mode == "cost" else ""),
                   ok, "; ".join(why))
    say("  (x02 is not compared: a reposed run replays the commit as x = v, while the session computation keeps its own alternatives, so their answers after the commit may differ by design; P11)")


def states(rec, k, att=-1):
    a = rec["stages"][k - 1]["attempts"][att]
    return [c["execution_state"]["states"] for c in a["computations"]], a


def check_limits(m):
    say("== (c) budget, safety limit and error paths")
    for c in ["plain", "session"]:
        r = m.get(("x04", c, "X04a.n4997", "behaviour"))
        s, a = states(r, 1)
        st = a["computations"][0]["steps"]
        result("c", "%s budget 5000: a stage of exactly 5000 steps finishes (%s, steps %s)" % (c, s, st["to_end"]),
               s == [["finished"]] and st["to_end"] == 5000)
        r = m.get(("x04", c, "X04a.n4998", "behaviour"))
        s, a = states(r, 1)
        st = a["computations"][0]["steps"]
        if c == "plain":
            result("c", "%s budget 5000: a stage of 5001 steps is budget, stopped at 5001 (%s, %s), observe() read at the stop: %r" %
                   (c, s, st["restated"], a["observe"]["raw"]), s == [["budget"]] and st["restated"] == 5001 and a["observe"]["raw"])
            s2, a2 = states(r, 2)
            result("c", "%s after budget: stage 2 reposed (%s, %s), restart cost %s measured in-run" %
                   (c, a2["posed"]["how"], a2["posed"]["reason"], a2["computations"][0]["steps"]["restart_cost"]),
                   a2["posed"]["how"] == "reposed" and a2["posed"]["reason"] == "after-budget" and
                   a2["computations"][0]["steps"]["restart_cost"] is not None)
        else:
            # in session stage 1's own computation has no query(1): 5000 steps, within budget; its
            # answers, taken on a separate run with query(1), take 5001 and run out
            result("c", "%s budget 5000: the incremental stage 1 (no query, %s steps) goes on; its separate run (stage + query, 5001) is budget (%s)" %
                   (c, st["restated"], s), s == [["budget"]] and st["restated"] == 5000)
            s2, a2 = states(r, 2)
            result("c", "%s: stage 2 is posed into the same computation (%s, %s)" % (c, a2["posed"]["how"], a2["posed"]["reason"]),
                   a2["posed"]["how"] == "incremental")
        r = m.get(("x04", c, "X04a.n10", "behaviour"))
        s, a = states(r, 3)
        st = a["computations"][0]["steps"]
        result("c", "%s budget in program code without harness entries: stopped within slack (stage steps %s <= 5000 + 8 + 1)" % (c, st["to_end"]),
               s == [["budget"]] and 5000 < st["to_end"] <= 5009)
        r = m.get(("x05", c, "X05a", "behaviour"))
        a = r["stages"][1]["attempts"]
        result("c", "%s safety limit: stage 2 stopped at 1 s (%s), rerun at 3 s (%s, %s), both timeout" %
               (c, a[0]["safety_limit"]["action"], a[1]["posed"]["reason"], a[1]["safety_limit"]["action"]),
               len(a) == 2 and a[0]["safety_limit"]["action"] == "rerun" and a[1]["safety_limit"]["action"] == "final-timeout" and
               a[1]["posed"]["reason"] == "safety-rerun")
        a3 = r["stages"][2]["attempts"][0]
        result("c", "%s after a final timeout: stage 3 reposed (%s), its replay stopped by the limit; restart cost %s read when it stopped" %
               (c, a3["posed"]["reason"], a3["computations"][0]["steps"]["restart_cost"]),
               a3["posed"]["reason"] == "after-timeout" and a3["computations"][0]["steps"]["restart_cost"] is not None)
        r = m.get(("x06", c, "X06a", "behaviour"))
        s, a = states(r, 2)
        if c == "plain":
            result("c", "%s error: stage 2 error, verbatim %r" % (c, a["computations"][0]["execution_state"]["error_verbatim"][:80]), s == [["error"]])
            s, a = states(r, 3)
            result("c", "%s after error: stage 3 reposed (%s)" % (c, a["posed"]["reason"]), a["posed"]["reason"] == "after-error")
        else:
            result("c", "%s: the undefined procedure of stage 2 waits (session's S code) instead of an error (%s)" % (c, s), s == [["suspended"]])
    r = m.get(("x07", "plain", "X07a", "behaviour"))
    a = r["stages"][0]["attempts"]
    result("c", "fixed safety limit: one attempt, %s" % a[0]["safety_limit"]["action"],
           len(a) == 1 and a[0]["safety_limit"]["action"] == "fixed-limit-timeout")
    r = m.get(("xerr", "plain", "X01a", "behaviour"))
    s, a = states(r, 1)
    result("c", "a syntax error: the system's message on stderr %r, and the stage is error" % a["stderr"][:90], s == [["error"]] and "Syntax error" in a["stderr"])
    r = m.get(("xthr", "session", "X06a", "behaviour"))
    s, a = states(r, 2)
    s3, a3 = states(r, 3)
    result("c", "session error (stage 2 throws): %s, verbatim %r; stage 3 %s %s" %
           (s, (a["computations"][0]["execution_state"]["error_verbatim"] or "")[:60], a3["posed"]["how"], a3["posed"]["reason"]),
           s == [["error"]] and a3["posed"]["how"] == "reposed" and a3["posed"]["reason"] == "after-error")
    r = m.get(("x08w", "constraints", "X08a", "behaviour"))
    s, a = states(r, 1)
    result("c", "h_wait/0 outside session: error", s == [["error"]])
    r = m.get(("x08w", "session", "X08a", "behaviour"))
    s, a = states(r, 1)
    s2, a2 = states(r, 2)
    result("c", "session: stage 1 waits (%s), stage 2 posted into the waiting computation answers %s" %
           (s, [x["verbatim"] for x in a2["computations"][0]["queries"][0]["answers"]]),
           s == [["suspended"]] and a2["computations"][0]["queries"][0]["answers"])
    r = m.get(("x08u", "session", "X08a", "behaviour"))
    s, a = states(r, 1)
    s2, a2 = states(r, 2)
    result("c", "session S code: a call of an undefined procedure waits (%s); the stage that defines it gives %s" %
           (s, [x["verbatim"] for x in a2["computations"][0]["queries"][0]["answers"]]),
           s == [["suspended"]] and [x["verbatim"] for x in a2["computations"][0]["queries"][0]["answers"]] == ["M = 5.\n\n"])
    r = m.get(("x08u", "constraints", "X08a", "behaviour"))
    s, a = states(r, 1)
    result("c", "the same program in constraints: existence error (%s)" % s, s == [["error"]])


def check_anticipation(m):
    say("== no anticipation: a later stage's constant is not in the process before its stage")
    for c in ["plain", "session"]:
        r = m.get(("xlate", c, "X01a", "behaviour"))
        outs = [st["attempts"][-1]["stdout"] for st in r["stages"]]
        seps = [(st["attempts"][-1].get("separate_run") or {}).get("stdout") or "" for st in r["stages"]]
        ok = all("LATE-PRESENT" not in o for o in outs[:2] + seps[:2]) and "stage 3: LATE-PRESENT" in outs[2]
        result("n", "%s: stages 1 and 2 (and their separate runs) see no trace of stage 3's constant among the process's atoms and strings; stage 3 does: %r" %
               (c, [o.strip().split("\n")[-1] for o in outs]), ok)


def check_hcalls(m):
    say("== H calls cost the program nothing: x09-count.pl (h_count/1, h_candidate/0, h_held/2) and x09-nocount.pl")
    for c in ["plain", "session"]:
        for inst in ["X09a.n5.up", "X09a.n5.down"]:
            for mode in ALL:
                a, b = m.get(("x09", c, inst, mode)), m.get(("x09n", c, inst, mode))
                if not (a and b):
                    continue
                sa = [st["attempts"][-1]["computations"][0]["steps"]["restated"] for st in a["stages"]]
                sb = [st["attempts"][-1]["computations"][0]["steps"]["restated"] for st in b["stages"]]
                ops = a["stages"][0]["attempts"][-1]["computations"][0]["problem_operations"]
                result("h", "%s %s %s: steps with counters %s = without %s; problem operations %s" % (c, inst, mode, sa, sb, ops), sa == sb)


def check_effects(m):
    say("== effects log (made-up X02)")
    for c in ["plain", "session"]:
        r = m.get(("x02", c, "X02a", "behaviour"))
        e = r["effects"]
        mine = [x for st in r["stages"] for a in st["attempts"] for x in a["effects"] if x["log"] == "classification"]
        result("e", "%s: %d classification entries appended after %d earlier ones; replayed commitments %s" %
               (c, len(mine), e["entries_before_run"], [a["posed"]["replayed_commitments"] for st in r["stages"] for a in st["attempts"] if a["posed"]["replayed_commitments"]][:1]),
               len(e["log_after_run"]) == e["entries_before_run"] + len(mine))
        r = m.get(("x02", c, "X02a", "cost"))
        obs = [x for st in r["stages"] for a in st["attempts"] for x in a["effects"]]
        result("e", "%s cost run: its %d entries go to the observation log only" % (c, len(obs)), all(x["log"] == "observation" for x in obs))


def check_validate():
    say("== (d) every record of this run passes validate.py")
    recs = [f for f in NEW_RECORDS]
    bad = [f for f in recs if f.endswith(".INVALID.json")]
    p = subprocess.run([sys.executable, VALIDATE, "--stages", STAGES] + [f for f in recs if not f.endswith(".INVALID.json")],
                       cwd=REPO, capture_output=True, text=True)
    invalid = [l for l in p.stdout.splitlines() if "INVALID" in l]
    result("d", "%d records written, %d kept as INVALID by the harness, validate.py: %d invalid" % (len(recs), len(bad), len(invalid)),
           not bad and not invalid and p.returncode == 0, "\n".join(invalid[:10]))


def check_check():
    say("== check executes nothing")
    trace = os.path.join(HERE, "programs", "noexec-trace.txt")
    if os.path.exists(trace):
        os.remove(trace)
    for c in ["plain", "session"]:
        p = subprocess.run([CHECK, c, os.path.join(PROGS, "noexec.pl")], cwd=REPO, capture_output=True, text=True,
                           env=dict(os.environ, CP_QUAL_TRACE=trace))
        out = p.stdout + p.stderr
        traced = os.path.exists(trace)
        result("g", "check %s noexec.pl: exit %d, no marker printed, no file written" % (c, p.returncode),
               "EXECUTED-" not in out and not traced, out if ("EXECUTED-" in out or traced) else "")
    say("  -- the same program run by the harness does leave its trace (so the marker works):")
    rc, rec, path, out = harness("plain", "X10", "X10a.all", "behaviour", "noexec.pl")
    a = rec["stages"][0]["attempts"][0]
    result("g", "harness run of noexec.pl prints the marker (stdout %r) and writes the file" % a["stdout"][:80],
           "EXECUTED-" in a["stdout"] and os.path.exists(trace))
    if os.path.exists(trace):
        os.remove(trace)
    say("  -- check on every qualification program:")
    for prog in sorted(os.listdir(os.path.join(REPO, PROGS))):
        if not prog.endswith(".pl"):
            continue
        cfg = ("session" if "wait" in prog else "tabling" if "table" in prog else
               "constraints" if "clpfd" in prog else "coroutines" if "freeze" in prog else "plain")
        p = subprocess.run([CHECK, cfg, os.path.join(PROGS, prog)], cwd=REPO, capture_output=True, text=True)
        expect = 1 if prog in ("xerr-syntax.pl",) else 0
        result("g", "check %s %s: exit %d" % (cfg, prog, p.returncode), p.returncode == expect,
               (p.stdout + p.stderr) if p.returncode != expect else "")
    if os.path.exists(trace):
        os.remove(trace)


def check_usage():
    say("== usage errors write no record and exit 2")
    env = dict(os.environ, CP_SWI_STAGES=STAGES, CP_PURPOSE="qualification")
    out = os.path.join(RECORDS, "usage")
    for args in (["nosuch", "X01", "X01a", "behaviour"], ["plain", "X01", "nosuch", "behaviour"],
                 ["plain", "X01", "X01a", "nosuch"], ["plain", "X02", "X01a", "behaviour"]):
        p = subprocess.run([RUN] + args + [os.path.join(PROGS, "x01-flag.pl"), out], cwd=REPO, env=env, capture_output=True, text=True)
        none = not glob.glob(os.path.join(REPO, out, "*.json"))
        result("u", "run %s: exit %d, no record" % (" ".join(args), p.returncode), p.returncode == 2 and none)


def main():
    t0 = time.time()
    say("SWI-Prolog harness qualification, %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    say(subprocess.run(["swipl", "--version"], capture_output=True, text=True).stdout.strip())
    m = run_matrix()
    check_direct(m)
    check_probes(m)
    check_incremental(m)
    check_limits(m)
    check_anticipation(m)
    check_hcalls(m)
    check_effects(m)
    check_validate()
    check_check()
    check_usage()
    n_ok = sum(1 for r in RESULTS if r[2])
    say("== %d checks, %d passed, %d failed (%.0f s)" % (len(RESULTS), n_ok, len(RESULTS) - n_ok, time.time() - t0))
    for r in RESULTS:
        if not r[2]:
            say("  FAILED [%s] %s %s" % (r[0], r[1], r[3]))
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
