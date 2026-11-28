# Assemble swi-prolog.json from tokens.json, outcomes.json and the hand-written
# lists below; check token coverage again.
import json, glob, os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
RES = REPO + "/results/swi-prolog"

tokens = json.load(open(HERE + "/tokens.json"))
outcomes = json.load(open(HERE + "/outcomes.json"))

def rec(config, instance, mode):
    ps = sorted(glob.glob(f"{RES}/{config}/{instance[:3]}/raw/{instance}.{mode}.*.json"))
    assert len(ps) == 1
    return os.path.relpath(ps[0], REPO)

MD = []
FAULT = "storage record with a harness_faults entry ('unreadable harness event': the at_exception event was interleaved with another write and could not be parsed), so the harness wrote 'HARNESS FAULT: no end event for the computation' as the computation's error. A fault of the measurement, not of the program; the behaviour run's class stands (PROTOCOL, Modes: a disagreement is a fault of the instrumentation)"
for c in ("plain", "coroutines", "constraints", "session"):
    MD.append({"configuration": c, "instance": "P09a.BA", "program": "P09a.pl", "mode": "storage",
               "record": rec(c, "P09a.BA", "storage"), "stage": 1, "computation": "A",
               "behaviour": {"semantic": "none reported", "execution_state": ["budget"], "record": rec(c, "P09a.BA", "behaviour")},
               "this_mode": {"semantic": "none reported", "execution_state": ["error"], "steps": None},
               "harness_fault": True,
               "note": FAULT + ". Steps unavailable (null), not 0 (AMENDMENTS 3.1). B, which ran first, is the same as in the behaviour run."})
MD.append({"configuration": "session", "instance": "P09a.AB", "program": "P09a.pl", "mode": "storage",
           "record": rec("session", "P09a.AB", "storage"), "stage": 1, "computation": "A",
           "behaviour": {"semantic": "none reported", "execution_state": ["budget"], "record": rec("session", "P09a.AB", "behaviour")},
           "this_mode": {"semantic": "none reported", "execution_state": ["error"], "steps": None},
           "harness_fault": True, "note": FAULT + "."})
MD.append({"configuration": "session", "instance": "P09a.AB", "program": "P09a.pl", "mode": "storage",
           "record": rec("session", "P09a.AB", "storage"), "stage": 1, "computation": "B",
           "behaviour": {"semantic": "complete", "representation": "explicit", "execution_state": ["finished"], "answers": ["B = [3, 2, 1].\n\n"]},
           "this_mode": {"semantic": "none reported", "representation": None, "execution_state": ["error"], "answers": []},
           "harness_fault": True,
           "note": "In the order A then B, the fault in A's computation left B with no answer and the same 'no end event' error: the harness lost B's result after A's budget. A measurement fault (the semantic results of the two modes disagree, which PROTOCOL reports as a fault of the instrumentation); B is complete in the behaviour and cost runs."})
for rd in ("P09d1", "P09d2"):
    MD.append({"configuration": "plain", "instance": "P09d", "program": "P09d.pl", "mode": "storage",
               "record": rec("plain", "P09d", "storage"), "stage": 1, "computation": "main", "reading": rd,
               "behaviour": {"semantic": "none reported", "execution_state": ["budget"]},
               "this_mode": {"semantic": "none reported", "execution_state": ["error"], "steps": None},
               "harness_fault": True,
               "note": FAULT + "; here the unparsed text is SWI-Prolog's 'Unknown message: inference_limit_exceeded'. The observation of s's prefix is also missing (observe raw empty)."})

EXPR = []
def ex(c, sp, e, reason, direction=None):
    EXPR.append({"configuration": c, "subproblem": sp, "direction": direction, "expressibility": e, "reason": reason})
ALL = ["plain", "tabling", "coroutines", "constraints", "session"]
for c in ALL:
    ex(c, "P09a", "expressible", "loop, conc and rev are transcribed clause by clause, the two computations as spawned/4 clauses; no R token" + ("; the table directive is C" if c == "tabling" else "") + ". The configuration runs the two computations one after the other, not side by side (a property of the configuration recorded under coordination, not of expressibility)")
    ex(c, "P09b", "expressible", "both computations are transcribed (equality as unification); no R token")
    ex(c, "P09c", "expressible", "gen and sum3 are transcribed by their cases, arithmetic by is/2 in the direction the query uses (rule 8)" if c in ("plain", "tabling") else
       "gen and sum3 are transcribed; freeze/2 (C) makes the producer demand-driven; arithmetic " + ("by is/2 in the direction used" if c == "coroutines" else "as clpfd constraints") + "; no R token")
    ex(c, "P09d", "expressible", "genu and sum3 transcribed; no R token. Expressibility does not depend on the reading; the outcome does (plain and tabling never reach the consumer)" if c in ("plain", "tabling") else
       "genu and sum3 transcribed, producer delayed by freeze/2 (C); no R token")
for c in ("plain", "tabling"):
    ex(c, "P09e", "not expressible", "the core has arithmetic only by evaluation (is/2), which needs all but one place known. The program writes each primitive relation as one clause per direction (R: heads, nonvar tests), which keeps the relation's meaning only where two places are known; on the problem's own input neither x nor y is known, and it raises an instantiation error. No reformulation in plain can hold x = y + 1 with both unknown without supporting code (a store of held relations, rule 19), so the primary program runs as a reformulation that changes the meaning on this input")
ex("coroutines", "P09e", "expressible with reformulation", "the primitive relations a + b = c and a - b = c are written as mode-dispatching definitions the problem does not give (R tokens: 124 in sum/3, diff/3, sum_known/3, diff_known/3 heads, nonvar tests and the dispatch calls), held by when/2 (C) until two places are known. The meaning is kept on every input the problem uses (integers; any two places known decides the third)")
for c in ("constraints", "session"):
    ex(c, "P09e", "expressible", "each relation is one clpfd constraint, #=/2, over the unbounded integers; no domain imposed, no R token")
for c in ALL:
    ex(c, "P10a", "expressible", "the named quantity b as one database fact, replaced natively by retractall/1 and assertz/1 (systems file core: 'for replacing state between stages'); no R token")
for c in ("plain", "tabling"):
    ex(c, "P10b", "not expressible", "stage 1 needs d = 2 * b held while b has no value; in plain the standing relation can only be an evaluation (is/2), which raises an instantiation error with b unknown, so the relation cannot be held without supporting code. Stages 2-4 are served by the same rule (d recomputed from b). R tokens: the if-then-else for a quantity with no value (5 tokens)")
ex("coroutines", "P10b", "expressible with reformulation", "the standing relation is a rule over the stored fact, delayed by freeze/2 (C) until b is known; the query needs a case the problem does not give, b with no value, written as an if-then-else (R, 5 tokens). The meaning is kept on every stage's input (d from b; d is never given)")
for c in ("constraints", "session"):
    ex(c, "P10b", "expressible with reformulation", "the standing relation is a clpfd constraint in an asserted rule, held by the solver while b is unknown; the query's case for b with no value is an if-then-else (R, 5 tokens)")
for c in ALL:
    ex(c, "P10c", "expressible with reformulation", "replacement as in P10a; the query's case for d with no value yet (stage 1) is an if-then-else the problem does not give (R, 6 tokens with its separator)")
    ex(c, "P10d", "expressible with reformulation", "a relation posed as a goal cannot be withdrawn, so stage 2's x > k is held as data, held(y, relation), applied by an interpreter of the held relations in the query (forall/2 over held/2 with call/1); R tokens: 25 (the held/2 wrappers, 5 tokens in each of stages 2 and 3, and the 15-token forall with its separator). The withdrawal itself is native (retract/1). Meaning kept on every input the stages use")
    ex(c, "P11a", "expressible", "the conjunction is transcribed in the order written; pick by member/2 over its facts; emit is the harness stub; no R token" + ("; x >= k delayed by freeze/2 (C)" if c == "coroutines" else ""))
    ex(c, "P11b", "expressible", "as P11a, emit before the test, in the order written; no R token")
    ex(c, "P11c", "expressible", "stages transcribed; the commit stage reads back the harness's verbatim answer as x = v on replay (P, commit being a problem token); no R token")
    ex(c, "P11d", "expressible", "as P11c" + ("; in session the commitment is not held by the incremental computation (the selection is made on a separate run), which makes stage 3 unsound: a behaviour of the configuration and harness, not of expressibility" if c == "session" else ""))

SM = []
for p in ["P09a.pl", "P09b.pl", "P09c.pl", "P09d.pl", "P09e.pl", "P10a.pl", "P10b.pl", "P10c.pl", "P10d.pl", "P11a.pl", "P11b.pl", "P11c.pl", "P11d.pl"]:
    SM.append({"configuration": "session", "program": p, "mechanism": "wait for an undefined procedure (harnesses/swi-prolog/S/session-wait.pl)",
               "listed_at_phase_4": True, "tokens": 0,
               "note": "Loaded by the harness before every session program (S-mechanisms.md: 19 lines, 158 tokens by the harness author's tokeniser; counted once per configuration, not per program). No token of this program is S, and the program never calls a procedure without a definition in the engine (every relation read before it has clauses is declared dynamic/1), so the mechanism is present but not exercised. The program supplies no S of its own."})

# token check against the tsv files
texts = [l.split("\t")[0] for l in open(RES + "/tokens/TEXTS-1C-P09-P11.tsv").read().splitlines()[1:]]
assert sorted(texts) == sorted(tokens)
for t, spans in tokens.items():
    n = sum(1 for _ in open(f"{RES}/tokens/{t}.tokens.tsv")) - 1
    cov = [0] * n
    for s in spans:
        assert s["class"] in "PCRSH"
        for i in range(s["from"], s["to"] + 1):
            cov[i] += 1
    assert all(x == 1 for x in cov), t

out = {"tokens": tokens, "outcomes": outcomes, "mode_differences": MD, "expressibility": EXPR,
       "late_definition": [], "s_mechanisms": SM}
json.dump(out, open(HERE + "/swi-prolog.json", "w"), indent=1, ensure_ascii=False)
json.load(open(HERE + "/swi-prolog.json"))

tot = {}
per = {}
for t, spans in tokens.items():
    for s in spans:
        n = s["to"] - s["from"] + 1
        tot[s["class"]] = tot.get(s["class"], 0) + n
        per.setdefault(t, {}).setdefault(s["class"], 0)
        per[t][s["class"]] += n
print("totals", tot, sum(tot.values()))
for t in texts:
    print(t, per[t])
from collections import Counter
print(Counter((e["semantic"]) for e in outcomes))
print(Counter((e["representation"]) for e in outcomes))
print(Counter(tuple(e["execution_state"]) for e in outcomes))
print(Counter(e["effects"]["class"] for e in outcomes if "effects" in e))
