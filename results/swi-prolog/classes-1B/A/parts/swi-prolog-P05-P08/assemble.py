"""Assemble swi-prolog.json from tokens.json, outcomes.json and the judgements below."""
import json, os, glob, re, csv
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "."
tokens = json.load(open(os.path.join(HERE, "tokens.json")))
outcomes = json.load(open(os.path.join(HERE, "outcomes.json")))
CONFS = ["plain", "tabling", "coroutines", "constraints", "session"]
rows = list(csv.reader(open(REPO + "/results/swi-prolog/tokens/TEXTS-1B-P05-P08.tsv"), delimiter="\t"))[1:]
textof = {}
for r in rows:
    textof[r[0]] = r[0]
    for o in r[1].split(): textof[o] = r[0]

def spans_of(conf, prog):
    return tokens[textof["%s/%s" % (conf, prog)]], textof["%s/%s" % (conf, prog)]

# ---------------- mode differences ----------------
beh = [e for e in outcomes if e["configuration"] == "session" and e["instance"] == "P05a" and e["stage"] == 3][0]
mode_differences = [{
    "configuration": "session", "instance": "P05a", "program": "P05a.pl", "mode": "storage",
    "record": "results/swi-prolog/session/P05/raw/P05a.storage.20261127T225651Z.json", "stage": 3,
    "behaviour": {k: beh[k] for k in ("semantic", "representation", "execution_state", "residual_equivalence")},
    "this_mode": {"semantic": "unsound", "representation": "explicit", "execution_state": ["finished"],
                  "residual_equivalence": "no answer (print 'false.'), where x = 3 is valid"},
    "note": "The storage run's stage 3 reports no solution (126 inferences restated, 94 in the stage, against 17 in behaviour and cost), after the engine had been held with 1 retained choicepoint at the end of stage 2 (the storage instrumentation's own count). The cost run agrees with behaviour. PROTOCOL.md (modes): two modes' semantic results must agree, and this disagreement is reported as a fault of the instrumentation (storage sampler / choicepoint walk in the session engine), not of the model."
}]

# ---------------- expressibility ----------------
SUBS = ["P05a", "P05b", "P05c", "P06a", "P06b", "P06c", "P06d", "P06e1", "P06e2", "P06e3",
        "P07a", "P07b", "P07c", "P07d", "P07e", "P07f", "P07g", "P08a", "P08b", "P08c"]
def rcount(conf, prog):
    sp, _ = spans_of(conf, prog)
    return sum(s["to"] - s["from"] + 1 for s in sp if s["class"] == "R")
expr = []
for conf in CONFS:
    for sub in SUBS:
        prog = sub + ".pl"; R = rcount(conf, prog); direction = None
        if sub.startswith("P05"):
            how = {"plain": "x > k as >/2 and x \u2260 k as \\=/2", "tabling": "the plain text", "coroutines": "x > k as freeze(X, X > K) (the freeze is C) and x \u2260 k as dif/2",
                   "constraints": "x > k as #>/2 and x \u2260 k as dif/2", "session": "the constraints text"}[conf]
            reason = "pick's closed world is the stage's facts, enumerated by member/2 (rule 6, rule 9); %s. No R tokens. %s" % (how,
                     "That >/2 errs on an unknown (P05b stage 1) is an outcome, not a want of expressibility." if conf in ("plain", "tabling") and sub == "P05b" else "")
            ex = "expressible"
        elif sub in ("P06a", "P06b", "P06c"):
            ex = "expressible"
            reason = ("not (x = 1) as \\+ X = K, the language's negation, a transcription (P); it is unsound when x is unknown (P06a, P06c), which is an outcome" if conf in ("plain", "tabling")
                      else "not (x = 1) as dif(X, K), sound on unknowns; a transcription (P)")
        elif sub == "P06d":
            ex = "expressible"; reason = "mem and setdiff transcribed case by case, negation as \\+ on a ground call" + ("; tabled (C)" if conf == "tabling" else "")
        elif sub.startswith("P06e"):
            ex = "expressible"; reason = "the closed world asserted from the stage's facts, nonmajor transcribed with its conjuncts in order; the :- dynamic declaration is C (rule 11)" + ("; :- table nonmajor/1 is C" if conf == "tabling" else "")
        elif sub.startswith("P07"):
            if conf in ("constraints", "session"):
                ex = "expressible"; reason = "each relation transcribed as a clpfd constraint over the unbounded integers (#=), no domain imposed, no labeling; P07a's presentation order honoured from h_param(order). No R tokens."
            elif conf == "coroutines":
                ex = "expressible with reformulation"
                reason = "+ and \u00b7 are held as when/2 goals over an evaluator (%d R tokens: the nonvar tests of which places are known, rule 19). The reformulation keeps each relation's meaning on every input used (it computes or tests in every direction once enough places are known, over the integers, with an integrality test for the product); the outcomes it gives are complete" % R
            else:
                ex = "expressible with reformulation"
                reason = ("is/2 evaluates in one direction only, so the relation is written as a mode dispatch (%d R tokens, rule 19). That reformulation does not hold a relation with two unknown places: it raises an instantiation error (P07a-f) or, in P07g, binds X = 0 through factor/3's head and fails (unsound). A reformulation that keeps the meaning on these inputs can be written in the core (reordering or eliminating by hand, R, rule 19's code written for the problem's own relations), so the sub-problem is judged expressible with reformulation; the program of record's reformulation does not achieve it" % R)
        else:
            ex = "expressible"
            reason = ("rev and conc transcribed as P03's cases (naive reverse by conc), each definition posed at its stage by assertz/1; the application before the definition is a call of an undefined procedure, whose behaviour the unknown flag (error in the primary; fail in the named variant, a C directive, rule 11) or, in session, the configuration's S mechanism decides" + ("; P08c's case 1 arrives as a stage constant and is asserted" if sub == "P08c" else ""))
            direction = "rev(a, b) with a partly known, b unknown" if sub != "P08c" else "rev(<1,2>, b)"
        expr.append({"configuration": conf, "subproblem": sub, "direction": direction, "expressibility": ex, "reason": reason})
# P07a orders: same program
# ---------------- late definition ----------------
def find(conf, prog, pat):
    sp, t = spans_of(conf, prog)
    return ["%d-%d (%s)" % (s["from"], s["to"], s["construct"].split(": ", 1)[-1]) for s in sp if re.search(pat, s["construct"])]
late = []
for conf in CONFS:
    for sub in ("P08a", "P08b", "P08c"):
        for prog in (sub + ".pl", sub + "-unknown-fail.pl"):
            app = find(conf, prog, r"rev \( (A|P) , B \)")
            dfn = find(conf, prog, r"assertz \( (\( )?rev")
            flag = find(conf, prog, r"unknown flag")
            _, t = spans_of(conf, prog)
            O = [e for e in outcomes if e["configuration"] == conf and e["instance"] == sub and e["program"] == prog]
            st = {e["stage"]: e for e in O}
            if conf == "session" and "unknown-fail" not in prog:
                kind = "code awaited"
                ev = ("The application %s (text %s) calls rev/2 before any clause of it exists; the session S mechanism (harnesses/swi-prolog/S/session-wait.pl, user:exception/3 hook) gives it a waiting clause, and the engine waits in h_wait/0 until a stage asserts rev/2's own clauses. The definition is information that arrives at its stage: %s. Records: stage 2%s ended suspended with the engine waiting (engine_waiting_for_next_stage = 1) and the bindings held; %s. Nothing in the program tests a flag: what is awaited is the clauses themselves."
                      % (", ".join(app), t, "; ".join(dfn) if dfn else "rev/2 is never defined (P08b)", "-3" if sub != "P08c" else "-3 (stage 3's case 1 did not unify with the call, so it stayed held)",
                         "P08b never defines rev, so the application stays held, suspended, to the last stage, distinguishable from failure" if sub == "P08b" else "at stage 4, the stage that brought the definition, the same computation resumed (%s)" % st[4]["residual_equivalence"].split(";")[0]))
            elif "unknown-fail" in prog:
                kind = "neither"
                ev = ("The directive %s sets the unknown flag to fail (C, rule 11), so the application %s fails at once (state 1, the closed reading). Records: stage 2 reports no answer ('false.'), execution finished%s; later stages are not reached, because every reposed replay fails at stage 2. The definitions (%s) never meet a held application."
                      % (", ".join(flag), ", ".join(app), " (in session the engine's computation failed: the record shows that the S hook did not make it wait: with unknown = fail no existence error arises for the hook to handle, and the record is INVALID, a harness fault)" if conf == "session" else "", "; ".join(dfn) if dfn else "none: P08b"))
            else:
                kind = "neither"
                ev = ("The application %s is a call of an undefined procedure with unknown = error (ISO default): it raises existence_error(procedure, rev/2) (state 3). Records: stage 2 ends in error; every later stage is posed by reposing after the error and its replay errs again at stage 2, so stages 3+ are not reached and the definitions (%s) are never applied to it. No declaration, flag test or waiting is in the program."
                      % (", ".join(app), "; ".join(dfn) if dfn else "none: P08b"))
            late.append({"configuration": conf, "program": prog, "kind": kind, "evidence": ev})
# ---------------- S mechanisms ----------------
smech = []
for conf in CONFS:
    for f in sorted(os.listdir(REPO + "/programs/swi-prolog/" + conf)):
        if not re.match(r"P0[5-8]", f): continue
        sp, t = spans_of(conf, f)
        own = sum(s["to"] - s["from"] + 1 for s in sp if s["class"] == "S")
        if conf == "session":
            used = f.startswith("P08") and "unknown-fail" not in f
            smech.append({"configuration": conf, "program": f, "mechanism": "wait for an undefined procedure (S/session-wait.pl, loaded by the harness in every session run)",
                          "listed_at_phase_4": True, "tokens": 158,
                          "used": used,
                          "note": ("exercised: stage 2's call of the undefined rev/2 waits until rev's clauses arrive. " if used else
                                   ("loaded but not exercised: with unknown = fail the call of rev/2 fails before any existence error, so the hook never fires. " if f.startswith("P08") else "loaded but not exercised: the program calls no undefined procedure. ")) +
                                  "Its tokens are the phase-4 listing's count (S-mechanisms.md: 158); no token file of it was given to classify, so they are not classed here and are not in this program's tokens. The program itself supplies no S code (0 S tokens by my classes)."})
        else:
            smech.append({"configuration": conf, "program": f, "mechanism": "none", "listed_at_phase_4": None, "tokens": own,
                          "used": False, "note": "No S mechanism: the configuration lists none (S-mechanisms.md) and the program supplies none (0 S tokens by my classes)."})
doc = {"tokens": tokens, "outcomes": outcomes, "mode_differences": mode_differences, "expressibility": expr, "late_definition": late, "s_mechanisms": smech}
json.dump(doc, open(os.path.join(HERE, "swi-prolog.json"), "w"), indent=1, ensure_ascii=False)
# checks
d = json.load(open(os.path.join(HERE, "swi-prolog.json")))
for k, sp in d["tokens"].items():
    n = sum(1 for _ in open(REPO + "/results/swi-prolog/tokens/%s.tokens.tsv" % k)) - 1
    cov = sorted(i for s in sp for i in range(s["from"], s["to"] + 1))
    assert cov == list(range(n)), k
print("ok", len(d["tokens"]), len(d["outcomes"]), len(d["mode_differences"]), len(d["expressibility"]), len(d["late_definition"]), len(d["s_mechanisms"]))
