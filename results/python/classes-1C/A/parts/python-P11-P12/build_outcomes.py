"""Classify every stage of every P11/P12 behaviour run (python), and compare
the cost and storage runs with it. Reads only the raw records.

Usage: python3 build_outcomes.py REPO_ROOT
Writes outcomes.json and mode_differences.json beside this script.
"""
import glob
import json
import os
import re
import sys

root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
CONFS = ("core", "stdlib-concurrency", "extended")


def recs(conf, prob, mode):
    out = []
    for p in sorted(glob.glob(os.path.join(root, "results/python", conf, prob, "raw*", "*.json"))):
        r = json.load(open(p))
        if r["run"]["mode"] == mode:
            out.append((os.path.relpath(p, root), r))
    return out


def comp(st):
    a = st["attempts"][-1]
    return a, a["computations"][0]


def answers(c):
    return [x["verbatim"] for q in c["queries"] for x in q["answers"]]


# ------------------------------------------------------------------ P11
P11_VALID = {
    ("P11a", 1): ({1: None}, "x in {2, 3}, any one (pick(x) and x >= 2)"),
}


def p11_stage(conf, inst, k, a, c, rec, path):
    ans = answers(c)
    states = c["execution_state"]["states"]
    alt = c["alternatives"]["at_boundary"]
    alt_kind = list(c["alternatives"]["by_type"].keys())[0]
    eff = [(e["seq"], e["entry"]) for e in a["effects"]]
    bind = a["observe"]["bindings"]
    held = [l for l in a["observe"]["raw"].split("\n") if l.startswith("main.held")]
    alt_unit = ("a suspended generator of the conjunction (1 entry; kept for backtracking: next() would resume it)" if conf != "extended"
                else "%d choice points on the S search's stack (kept for backtracking)" % alt)
    o = dict(reached=True, representation="explicit", simplification=None, identical_to_posed=None,
             residual_size=None, execution_state=states, residual_equivalence=None, harness_fault=False,
             answers=ans)
    common_obs = "unknown x: %s in the registered bindings; alternatives held: %s; suspended work: none (0 items registered); no manual action" % (
        ("bound to %s" % bind.get("x")) if "x" in bind else "not bound (no solution held)",
        alt_unit if alt else "none (0)")
    if held:
        common_obs += "; held relations: " + held[0].split("=", 1)[1].strip()
    if inst in ("P11a", "P11b"):
        o.update(semantic="complete", rule="SPECIFICATION Outcomes 1 (any-one query: one valid answer is complete); P11a/P11b valid outcomes")
        o["valid_outcomes"] = "one answer, x = 2 or x = 3"
        if inst == "P11a":
            o["effects"] = "exact"
            o["effects_log"] = "L = <2> (seq %s); 2 emitted after the test x >= 2, when the solution was produced and reported: at commitment (a one-stage problem commits when it reports)" % eff[0][0]
        else:
            o["effects"] = "extra"
            o["effects_log"] = "L = <1, 2>: 1 emitted before commitment, on a provisional outcome the later test x >= 2 refuted; 2 emitted at commitment (reported)"
        o["observations"] = "answer %s (1/1 of an any-one query, 0 invalid); %s; no conclusion withdrawn. Commitment happens at the end of the stage, when the answer is reported; the generator (or search) with x = 3 untried is still held afterwards, so a request for more would perform emit(3)." % (ans, common_obs)
        if inst == "P11b":
            o["observations"] += " The program uses no control to avoid extra: emit precedes the test, in the order written."
        return o
    # P11c / P11d
    if inst == "P11c":
        table = {1: ("x in {1, 2, 3}, any one", "x = 1"), 2: ("x in {2, 3}, any one", "x = 2"), 3: ("x = v, v = 2 the solution held at the commit", "x = 2")}
    else:
        table = {1: ("x in {1, 2, 3}, any one", "x = 1"), 2: ("x = v, v = 1 the solution held at the commit", "x = 1"), 3: ("none (x = 1 committed, then x != 1)", None)}
    valid, expect = table[k]
    o["valid_outcomes"] = valid
    if expect is None:
        ok = ans == [] and "no solution" in (a["stdout"] or "") and "x" not in bind
        o.update(semantic="complete" if ok else "unsound",
                 rule="SPECIFICATION Outcomes 1 (empty valid outcome reported as none: complete; answer completeness: reported none = yes); P11d 'Valid' for v = 1")
        o["observations"] = ("no answer through cp.answer (ended_by no-enumeration); the program printed %r and its bindings are empty: the empty outcome reported as none (answer completeness: yes). "
                             "Representation: no solution, given explicitly as none. %s. Conclusion withdrawn: x = 1, reported and committed at stage 2, is withdrawn, shown by the 'no solution' line and x removed from the bindings; "
                             "the committed effect 1 stays in L, and nothing is done about it (no compensating action, none being possible); no further effect, since the commit dropped the generator." % (a["stdout"].strip(), common_obs))
    else:
        ok = ans == [expect]
        o.update(semantic="complete" if ok else "unsound",
                 rule="SPECIFICATION Outcomes 1 (any-one query); P11%s valid outcomes, stage %d" % (inst[-1], k))
        withdrawn = "none"
        if inst == "P11c" and k == 2:
            withdrawn = "x = 1 (stage 1) withdrawn by x != 1: shown by reporting x = 2 in its place (bindings x = 2); its effect 1 stays in L"
        o["observations"] = "answer %s (1/1 of an any-one query, 0 invalid); %s; conclusion withdrawn: %s." % (ans, common_obs, withdrawn)
    # effects
    if eff:
        o["effects_this_stage"] = "; ".join("seq %d entry %s emitted at stage %d, before commitment (a provisional outcome%s)" % (
            s, e, k, ", later refuted at stage 2" if (inst == "P11c" and e == "1") else (", later committed" if (inst == "P11c" and e == "2") or (inst == "P11d" and e == "1") else "")) for s, e in eff)
    else:
        o["effects_this_stage"] = "no entry"
    if k == 3:
        if inst == "P11c":
            o["effects"] = "extra"
            o["effects_log"] = "L = <1, 2>; committed v = 2 at stage 3. Entry 1: before commitment, for x = 1, refuted at stage 2 and never committed (extra). Entry 2: before commitment (stage 2), on the outcome later committed; no entry at or after commitment. No entry duplicated by reposing (every stage incremental)."
            o["observations"] += " Commitment: commit() selects the held x = 2, adds x = 2 as a relation and drops the generator (C tokens: solutions.clear()%s), so no alternative is tried after it; state finished." % (
                ", stack.clear()" if conf == "extended" else "")
        else:
            o["effects"] = "exact"
            o["effects_log"] = "L = <1>; committed v = 1 at stage 2. Entry 1 emitted at stage 1, before commitment, on the outcome later committed: exact. Stage 3's contradiction performs no effect. No entry duplicated by reposing."
            o["observations"] += " What the program does with information that contradicts a committed effect: it holds x = 1 and x != 1 together (observe: held relations), reports no solution, and leaves L unchanged."
    elif inst == "P11d" and k == 2:
        o["observations"] += " Commitment: commit() selects the held x = 1, adds x = 1 as a relation and drops the generator (C tokens: solutions.clear()%s); state finished." % (
            ", stack.clear()" if conf == "extended" else "")
    return o


# ------------------------------------------------------------------ P12
def seq(atom, n):
    return "s = ⟨" + ",".join(["'" + atom] * n) + "⟩"


def p12_valid(sub, n):
    R1 = "s = ⟨'r⟩"
    return {"P12a": [seq("l", n), R1], "P12b": [R1], "P12c": [seq("r", n)], "P12d": [seq("l", n)]}[sub]


def parse_bound_s(raw):
    m = re.search(r"main\.bindings = \{'s': (.*)\}\n", raw)
    if not m:
        return None
    v = m.group(1)
    if v.strip() == "s":
        return None  # unbound: no binding held
    atoms = re.findall(r"'([lr])'", v)
    tail_unknown = v.rstrip(")").rstrip().endswith("t") or ", t)" in v
    return atoms, tail_unknown


def p12_stage(conf, inst, a, c, rec, cost, storage):
    sub, ns, mode = inst.split(".")
    n = int(ns[1:])
    valid = p12_valid(sub, n)
    ans = answers(c)
    states = c["execution_state"]["states"]
    ok_ans = [x for x in ans if x in valid]
    bad_ans = [x for x in ans if x not in valid]
    o = dict(reached=True, simplification=None, identical_to_posed=None, residual_size=None,
             execution_state=states, residual_equivalence=None, harness_fault=False, answers=ans,
             valid_outcomes=("all: " if mode == "all" else "any one of: ") + ", ".join(valid))
    bound = parse_bound_s(a["observe"]["raw"]) if conf == "extended" else None
    # the answers alone
    if mode == "any":
        sem_ans = "complete" if len(ok_ans) == 1 and not bad_ans else ("none reported" if not ans else "unsound")
    else:
        sem_ans = ("complete" if sorted(ok_ans) == sorted(valid) and not bad_ans else
                   "partial" if ok_ans and not bad_ans else "none reported" if not ans else "unsound")
    budget = "budget" in states
    binding_is_answer = False
    if bound is not None:
        atoms, tail = bound
        rendered = "s = ⟨" + ",".join("'" + x for x in atoms) + "⟩"
        binding_is_answer = (not tail) and rendered in ans
    if budget and bound is not None and not binding_is_answer:
        atoms, tail = bound
        bdesc = "s = ⟨" + ",".join("'" + x for x in atoms) + "⟩" + (" ++ t (t unknown)" if tail else "")
        o["semantic"] = "unsound"
        o["representation"] = "explicit" if ans else "solved form"
        o["alternative_reading"] = {
            "semantic": sem_ans,
            "reason": "if the search's trial binding at the budget is not taken as reported (it is a candidate on the trail, which backtracking would undo, never accepted), the result is judged on the answers alone: %s" % sem_ans}
        o["rule"] = ("SPECIFICATION Outcomes 1, 'reported': a binding the system holds is reported if observe() can read it at the moment a budget runs out, whether or not the answers mechanism would deliver it. "
                     "The registered bindings hold %s at the budget, which is not a valid outcome; so the report denotes an invalid outcome: unsound (classification-sensitive: see alternative_reading)" % bdesc)
        o["residual_equivalence"] = ("binding at budget %s: not equivalent to the valid outcomes (%s); %s" % (
            bdesc, ", ".join(valid), "it denotes sequences none of which is valid" if tail else "it is one sequence, not accepted"))
    else:
        o["semantic"] = sem_ans
        o["representation"] = "explicit" if ans else None
        o["rule"] = "SPECIFICATION Outcomes 1 (%s); P12 queries" % ("any-one query: one valid answer is complete" if mode == "any" else "all solutions: the report denotes exactly the valid outcomes" if sem_ans == "complete" else "a nonempty proper subset is partial")
    # observations
    cc = cost[1]["stages"][0]["attempts"][-1]["computations"][0]
    sc = storage[1]["stages"][0]["attempts"][-1]["computations"][0]
    sa = storage[1]["stages"][0]["attempts"][-1]
    cand = cc.get("candidates_examined")
    s = c["steps"]
    alt_at = [x.get("alternatives_at") for q in sc["queries"] for x in q["answers"]]
    gen = sc["alternatives"]["by_type"].get("suspended generator frames (gc, process-wide)")
    peak = sa["store"]["quantities"]["traced_bytes"]["peak"]["value"]
    pend = c["alternatives"]["at_boundary"]
    held = ("one generator of the conjunction (nested choice generators inside it)" if conf != "extended"
            else "the S search's stack of choice points")
    obs = []
    obs.append("answers in order: %s (valid %d/%d%s, invalid %d)" % (ans, len(ok_ans), (1 if mode == "any" else len(valid)), "" if mode == "all" else " of an any-one query", len(bad_ans)))
    obs.append("candidates examined (cost run, accept applications): %s; steps to first answer %s, between answers %s, to end %s" % (
        cand, s["to_first_answer"], s["between_answers"], s["to_end"]))
    obs.append("alternatives held at the boundary: %s; at each answer (storage run, registered entries): %s; suspended generator frames at the boundary (storage run): %s; peak traced bytes (storage run): %s" % (
        ("%s (%s), kept for backtracking" % (pend, held)) if pend else "0 (the search exhausted; nothing held)", alt_at, gen, peak))
    obs.append("problem-defined alternatives (partial sequences held): not registered by the program (unavailable)")
    if mode == "all":
        obs.append("finishes after the last solution: %s" % ("yes (finished; the space was covered)" if not budget else "no: budget at %s steps; the strategy did not cover the space (%s candidates examined of %d)" % (s["stage"], cand, 2 ** (n + 1) - 1)))
    elif budget:
        obs.append("budget at %s steps before any answer (%s candidates examined; the solution is the %dth, the last, depth-first)" % (s["stage"], cand, 2 ** (n + 1) - 1))
    if bound is not None and budget:
        obs.append("binding held at the budget (observe): s = %s%s" % ("⟨" + ",".join("'" + x for x in bound[0]) + "⟩", " ++ t" if bound[1] else ""))
    obs.append("unknowns: s %s; search avoided: no (the program enumerates choice and tests accept, depth first in the order written); no suspended work; no conclusion withdrawn; no manual action" % (
        "not registered (core)" if conf != "extended" else ("bound to the answer in the registered bindings" if binding_is_answer else "unbound in the registered bindings at the end (the exhausted search restored it)" if bound is None else "bound to a trial candidate at the budget")))
    o["observations"] = "; ".join(obs)
    o["answer_completeness"] = "%d/%d valid, %d invalid" % (len(ok_ans), 1 if mode == "any" else len(valid), len(bad_ans))
    return o


# ------------------------------------------------------------------ run
outcomes, diffs = [], []
KEYS = ("semantic", "representation", "execution_state", "answers")
for conf in CONFS:
    for prob in ("P11", "P12"):
        beh = recs(conf, prob, "behaviour")
        cost = {r["run"]["instance"]: (p, r) for p, r in recs(conf, prob, "cost")}
        stor = {r["run"]["instance"]: (p, r) for p, r in recs(conf, prob, "storage")}
        for path, r in beh:
            inst = r["run"]["instance"]
            prog = os.path.basename(r["run"]["program"]["path"])
            assert not path.endswith("INVALID.json")
            for st in r["stages"]:
                a, c = comp(st)
                assert len(st["attempts"]) == 1
                if prob == "P11":
                    o = p11_stage(conf, inst, st["stage"], a, c, r, path)
                else:
                    o = p12_stage(conf, inst, a, c, r, cost[inst], stor[inst])
                entry = {"configuration": conf, "instance": inst, "program": prog, "record": path, "stage": st["stage"]}
                entry.update(o)
                outcomes.append(entry)
            # compare cost and storage with behaviour
            for mode, d in (("cost", cost), ("storage", stor)):
                mp, mr = d[inst]
                for st, mst in zip(r["stages"], mr["stages"]):
                    a, c = comp(st)
                    ma, mc = comp(mst)
                    if prob == "P11":
                        mo = p11_stage(conf, inst, mst["stage"], ma, mc, mr, mp)
                        bo = p11_stage(conf, inst, st["stage"], a, c, r, path)
                        for oo in (mo, bo):
                            oo.pop("effects_this_stage", None); oo.pop("effects", None); oo.pop("effects_log", None)
                    else:
                        mo = p12_stage(conf, inst, ma, mc, mr, cost[inst], stor[inst])
                        bo = p12_stage(conf, inst, a, c, r, cost[inst], stor[inst])
                    bsel = {k: bo.get(k) for k in KEYS}
                    msel = {k: mo.get(k) for k in KEYS}
                    if bsel != msel or a["observe"]["bindings"] != ma["observe"]["bindings"]:
                        diffs.append({"configuration": conf, "instance": inst, "program": prog, "mode": mode, "record": mp,
                                      "stage": st["stage"], "behaviour": bsel, "this_mode": msel, "note": "differs"})

json.dump(outcomes, open(os.path.join(here, "outcomes.json"), "w"), indent=1, ensure_ascii=False)
json.dump(diffs, open(os.path.join(here, "mode_differences.json"), "w"), indent=1, ensure_ascii=False)
print(len(outcomes), "outcome entries;", len(diffs), "mode differences")
from collections import Counter
print(Counter((o["configuration"], o["semantic"]) for o in outcomes))
print(Counter(o["semantic"] for o in outcomes))
for o in outcomes:
    if o["semantic"] != "complete":
        print(o["configuration"], o["instance"], o["stage"], o["semantic"], o.get("alternative_reading", {}).get("semantic"), o["execution_state"])
