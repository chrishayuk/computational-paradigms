# Assemble python.json: tokens (from spans.json, built by build.py from specs.py),
# outcomes, mode differences, expressibility, late definition and S mechanisms.
import json, glob, os
REPO = "."
spans = json.load(open("spans.json"))

def rec(cfg, prob, inst, mode="behaviour"):
    g = glob.glob(f"{REPO}/results/python/{cfg}/{prob}/raw/{inst}.{mode}.*.json")
    assert len(g) == 1, (cfg, inst, mode, g)
    return os.path.relpath(g[0], REPO)

CFGS = ["core", "extended", "stdlib-concurrency"]
out = []
def E(cfg, inst, program, record, stage, computation=None, reading=None, **kw):
    e = {"configuration": cfg, "instance": inst, "program": program, "record": record, "stage": stage}
    if computation: e["computation"] = computation
    if reading: e["reading"] = reading
    base = {"reached": True, "semantic": None, "representation": None, "simplification": None,
            "identical_to_posed": None, "residual_size": None, "execution_state": None,
            "residual_equivalence": None, "observations": None, "rule": None, "harness_fault": False}
    base.update(kw); e.update(base); out.append(e)

EXPL = dict(representation="explicit")
# ---------------------------------------------------------------- P09a
for cfg in CFGS:
    for order in ("AB", "BA"):
        r = rec(cfg, "P09", f"P09a.{order}")
        if cfg == "extended":
            E(cfg, f"P09a.{order}", "P09a.py", r, 1, "A", semantic="none reported", execution_state=["budget"],
              observations=("A: loop(x) solved by the S search with resolution: each choice point reduces loop(x) to loop(x); budget of 10^6 instructions "
                            "exhausted with 12,821 choice points on A's registered search stack (alternatives held for backtracking, not live); x an unbound Var throughout; "
                            "nothing suspended; no answer. The valid outcome is none, and the computation did not report that there are none (presumed nontermination). "
                            "Order: spawned %s; one after the other (side_by_side false). No conclusion withdrawn; no manual action." % ("first" if order == "AB" else "second")),
              rule="SPECIFICATION Outcomes 1 (none reported), 3 (budget)")
        else:
            E(cfg, f"P09a.{order}", "P09a.py", r, 1, "A", semantic="none reported", execution_state=["error"],
              observations=("A: loop(x) as a generator (yield from loop(x)); RecursionError: maximum recursion depth exceeded after 7,972 instructions "
                            "(994 applications of loop in cost mode). x given as None (unknown); its registered generator counts 0 (finished by the error). "
                            "Nothing suspended. The valid outcome is none; the error is not a report that there are none. "
                            + ("Run side by side with B (side_by_side true). " if cfg == "stdlib-concurrency" else "Run one after the other with B. ")
                            + "No conclusion withdrawn; no manual action."),
              rule="SPECIFICATION Outcomes 1 (none reported), 3 (error, recorded verbatim in the record)")
        obsB = ("B: b = <3,2,1> reported (cp.answer 'b = ⟨3,2,1⟩'), rev 4 and conc 6 applications (cost mode). ")
        if cfg == "extended":
            obsB += ("Reported during the S search; at the end of the stage B.bindings shows b unbound, since the exhausted search undoes its trail "
                     "(S/search.py) - the answer stands as reported. B's stack empty: finished. ")
        if cfg == "stdlib-concurrency":
            obsB += ("Side by side with A: B's outcome was reported while A ran (A then B) and is unaffected by A's error. "
                     + ("B's steps are recorded as 0 (to first answer 0) in this behaviour run and in the cost run, but 219 in the storage run and in order B,A: "
                        "a measurement artefact (B ran while A's traceback was formatted, when instruction events are off: harness README, confound 5); "
                        "read as unavailable (AMENDMENTS 3.1). " if order == "AB" else ""))
        else:
            obsB += ("A and B run one after the other; B's outcome is the same whether it runs before or after A, and A's %s does not affect it. " % ("budget" if cfg == "extended" else "error"))
        obsB += "No conclusion withdrawn; no manual action."
        E(cfg, f"P09a.{order}", "P09a.py", r, 1, "B", semantic="complete", representation="explicit",
          execution_state=["finished"], residual_equivalence="b = <3,2,1> is the valid outcome", observations=obsB,
          rule="SPECIFICATION Outcomes 1-3")
# ---------------------------------------------------------------- P09b
for cfg in CFGS:
    r = rec(cfg, "P09", "P09b")
    E(cfg, "P09b", "P09b.py", r, 1, "A", semantic="complete", representation="explicit", execution_state=["finished"],
      residual_equivalence="the valid outcome is empty; A reports no answer and prints 'no solution: x = 1 and x = 2'",
      observations=("A: the first equation binds x, the second tests it and fails; no answer; it printed that there is no solution (answer completeness: reported none, yes). "
                    + ("A.bindings = {} (a binding is registered only for a solution). " if cfg != "extended" else
                       "A.bindings shows x unbound: the failed conjunction's binding was undone through the trail. ")
                    + "No alternatives, nothing suspended. No conclusion withdrawn; no manual action."),
      rule="SPECIFICATION Outcomes 1 (complete: the report denotes exactly the empty set; printing is not an answer, but the empty set is denoted by no answer and the printed statement)")
    E(cfg, "P09b", "P09b.py", r, 1, "B", semantic="complete", representation="explicit", execution_state=["finished"],
      residual_equivalence="y = 3 is the valid outcome",
      observations=("B: y = 3. A's failure does not affect B (%s). No conclusion withdrawn; no manual action." %
                    ("run side by side" if cfg == "stdlib-concurrency" else "run after A, one after the other")),
      rule="SPECIFICATION Outcomes 1-3")
# ---------------------------------------------------------------- P09c
P09c_obs = {
 "core": "gen runs to its end (6 applications), then sum3 (1): the consumer does not act on s before the producer has finished; one sequential computation. Bindings s = (1,2,3,4,5), total = 6.",
 "extended": "Goals of the S suspension queue, first in first out: gen binds s cell by cell, sum3 waits on each unbound tail and resumes (gen 6, sum3 3 applications in cost mode), binding total once three elements are known: the consumer acts on s before the producer has finished, interleaved. Queue empty at the end.",
 "stdlib-concurrency": "One thread per relation application (gen 6, equal 7, sum3 2 in cost mode): sum3's thread waited once on the condition and was woken by a binding, so the consumer may act before the producer finishes, as the threads are scheduled (the order is not traced). Bindings held as cells: s = <1> ++ rest1, ..., rest5 = <>.",
}
for cfg in CFGS:
    E(cfg, "P09c", "P09c.py", rec(cfg, "P09", "P09c"), 1, semantic="complete", representation="explicit", execution_state=["finished"],
      residual_equivalence="s = <1,2,3,4,5>, total = 6, as valid",
      observations="Answer 's = ⟨1,2,3,4,5⟩, total = 6'. " + P09c_obs[cfg] + " Nothing left suspended. No conclusion withdrawn; no manual action.",
      rule="SPECIFICATION Outcomes 1-3")
# ---------------------------------------------------------------- P09d
for cfg in CFGS:
    r = rec(cfg, "P09", "P09d")
    if cfg == "core":
        common = ("genu calls itself before returning (tuples are finite): RecursionError after 7,013 instructions (996 applications of genu, cost mode); "
                  "sum3 is never reached, no binding is held (main.bindings = {}). ")
        E(cfg, "P09d", "P09d.py", r, 1, reading="P09d1", semantic="none reported", execution_state=["error"],
          observations=common + "Finite reading: valid outcome none; the error is not a report that there are none. No manual action.",
          rule="SPECIFICATION Outcomes 1 (none reported), 3 (error); problem P09d1")
        E(cfg, "P09d", "P09d.py", r, 1, reading="P09d2", semantic="none reported", execution_state=["error"],
          observations=common + "Stream reading: total = 6 is never computed. Producer state: error. The consumer never acts on s. No manual action.",
          rule="SPECIFICATION Outcomes 1, 3; problem P09d2")
    else:
        n = "5,008 cells (genu 5,008 applications, sum3 3, cost mode)" if cfg == "extended" else "1,129 cells (genu 1,129, equal 1,130, sum3 2, cost mode)"
        common = (("The producer runs until the budget: s is bound to a prefix of %s ending in an unbound tail, and total = 6 is bound by sum3 while the producer goes on. "
                   "No answer was reported (report() requires s known to its end). Registered waiting structure empty at the budget; " % n)
                  + ("the producer's next goal is in the queue's ready list, not registered. " if cfg == "extended" else
                     "the producer's threads keep running (the process was killed by the harness 5 s after the run ended). ")
                  + "The consumer acted on s before the producer finished. ")
        E(cfg, "P09d", "P09d.py", r, 1, reading="P09d1", semantic="none reported", execution_state=["budget"],
          observations=common + "Finite reading: total = 6 held while the producer still runs is an observation only (problem P09d1; SPECIFICATION, the exception for P09d1). No manual action.",
          rule="problem P09d1: 'none reported with budget, and the binding is recorded as an observation'")
        E(cfg, "P09d", "P09d.py", r, 1, reading="P09d2", semantic="complete", representation="solved form", execution_state=["budget"],
          residual_equivalence="total = 6 equals the valid outcome; s is bound to <1, 2, ..., k> ++ rest with rest unbound, a finite prefix of the stream <1, 2, 3, ...>, consistent with it",
          observations=common + "Stream reading: total = 6 is a binding observe() reads at the budget, so it is reported (SPECIFICATION, 'reported'); complete for total. Producer state: budget (still producing). No manual action.",
          rule="problem P09d2: 'a system that computes total = 6 is complete for total, whether or not the producer ever stops'; SPECIFICATION Outcomes 2 (solved form)")
# ---------------------------------------------------------------- P09e
P09e_held = {
 "core": "main.suspended[relations waiting for values] = [('+', ('y', 1, 'x')), ('-', ('x', 1, 'y'))]",
 "extended": "main.suspended[goals waiting for a binding] = {1: +(y, 1, x), 2: -(x, 1, y)}",
 "stdlib-concurrency": "main.suspended[relations waiting in their threads] = [('+', ('y', 1, 'x')), ('-', ('x', 1, 'y'))], each relation's thread blocked on the condition",
}
for cfg in CFGS:
    E(cfg, "P09e", "P09e.py", rec(cfg, "P09", "P09e"), 1, semantic="complete", representation="residual",
      simplification="reducible", identical_to_posed=True,
      residual_size="2 relations (y + 1 = x, x - 1 = y), 4 occurrences of unknowns; input: the same 2 relations, 4 occurrences; a smaller equivalent is the single relation x = y + 1 (1 relation, 2 occurrences)",
      execution_state=["suspended"],
      residual_equivalence="y + 1 = x and x - 1 = y are each equivalent to x = y + 1 over the integers, so their conjunction denotes exactly the valid pairs (checked by hand; check_residuals.py checks it on a grid of integers)",
      observations=(P09e_held[cfg] + "; bindings empty: x and y remain unknown (%s). Each relation was evaluated once (plus 1, minus 1, cost mode), found to need two known places, and held: neither part can proceed, which the program reports as suspended work with 2 items, not as a deadlock; it is told apart from completion by the registered waiting relations (determined). No answer. No conclusion withdrawn; no manual action." %
                    {"core": "absent from the bindings dict", "extended": "unbound Vars", "stdlib-concurrency": "absent from the bindings dict"}[cfg]),
      rule="SPECIFICATION Outcomes 1-3 ('reported' residual: held, acted on at a later stage, read by observe())")
# ---------------------------------------------------------------- P10a
vals = {1: "b = 10", 2: "b = 15", 3: "b = 7"}
for cfg in CFGS:
    r = rec(cfg, "P10", "P10a")
    for k in (1, 2, 3):
        E(cfg, "P10a", "P10a.py", r, k, semantic="complete", representation="explicit", execution_state=["finished"],
          residual_equivalence=vals[k] + ", as valid",
          observations=("Replacement native: an entry of a dict, replaced by assignment; the earlier value is not kept and cannot be retrieved. "
                        + ("b + 5 taken at b's value before the stage. The stage withdrew b = 10 (a replacement, not shown as a withdrawal). " if k == 2 else "")
                        + ("The stage withdrew b = 15 (replacement). " if k == 3 else "")
                        + "Nothing held. Same text in all three configurations. No manual action."),
          rule="SPECIFICATION Outcomes 1-3; P10 vocabulary (replacing stage)")
# ---------------------------------------------------------------- P10b
bvals = {2: "b = 10, d = 20", 3: "b = 15, d = 30", 4: "b = 7, d = 14"}
for cfg in CFGS:
    r = rec(cfg, "P10", "P10b")
    how = ("the relation held in a list and taken up again by maintain() after every stage" if cfg != "stdlib-concurrency"
           else "the relation given a thread of its own that waits on a condition and is woken by every replacement")
    E(cfg, "P10b", "P10b.py", r, 1, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
      residual_size="1 relation (d = 2 * b), 2 occurrences of unknowns; input: the same",
      execution_state=["suspended"],
      residual_equivalence="the held (2, 'b', 'd') is d = 2 * b, the valid outcome; neither has a value",
      observations="Standing relation held as (factor, source, target) = (2, 'b', 'd'), %s; no bindings; no answer. 1 suspended item. No manual action." % how,
      rule="SPECIFICATION Outcomes 2 (residual held and acted on at a later stage)")
    for k in (2, 3, 4):
        E(cfg, "P10b", "P10b.py", r, k, semantic="complete", representation="explicit", execution_state=["suspended"],
          residual_equivalence=bvals[k] + ", as valid",
          observations=("Answer '%s'. The standing relation is still held (1 suspended item), so the residual d = 2 * b is also held; classified on the explicit form, the residual recorded here (SPECIFICATION Outcomes 2, two forms). "
                        "One dependent value recomputed per replacement (times: 1 application, cost mode), in %s instructions. "
                        "Replacement native by assignment; earlier values not retrievable. %sNo manual action." %
                        (bvals[k], {"core": "113/122/122", "extended": "113/122/122", "stdlib-concurrency": "485/494/494"}[cfg].split("/")[k-2],
                         "The stage withdrew the earlier b and d (replacement). " if k > 2 else "")),
          rule="SPECIFICATION Outcomes 1-3")
# ---------------------------------------------------------------- P10c
cvals = {1: "b = 10", 2: "b = 10, d = 20", 3: "b = 15, d = 20", 4: "b = 7, d = 20"}
for cfg in CFGS:
    r = rec(cfg, "P10", "P10c")
    for k in (1, 2, 3, 4):
        E(cfg, "P10c", "P10c.py", r, k, semantic="complete", representation="explicit", execution_state=["finished"],
          residual_equivalence=cvals[k] + ", as valid",
          observations=("d computed once, at stage 2, from b's value then (a snapshot); it keeps 20 when b is replaced. " if k >= 2 else "")
                       + "Replacement native by assignment; earlier values not retrievable. Same text in all three configurations. No manual action.",
          rule="SPECIFICATION Outcomes 1-3")
# ---------------------------------------------------------------- P10d
dvals = {1: "x ∈ {1, 2, 3}", 2: "x ∈ {2, 3}", 3: "x ∈ {1, 2, 3}"}
for cfg in CFGS:
    r = rec(cfg, "P10", "P10d")
    for k in (1, 2, 3):
        if cfg == "extended":
            hold = "x's domain in the S propagator's store (%s), all values live at once" % {1: "{1, 2, 3}", 2: "{2, 3}", 3: "{1, 2, 3}"}[k]
            w = ("The withdrawal undid the store through its trail back to the mark of stage 2: the domain {1, 2, 3} restored and the constraint x > 1 removed, with no relation evaluated again (problem operations 0, 302 instructions); restated: no. " if k == 3 else "")
        else:
            hold = "a list of the values of x still held (%s), all live at once" % {1: "[1, 2, 3]", 2: "[2, 3]", 3: "[1, 2, 3]"}[k]
            w = ("The withdrawal restated: the values cleared and the information not withdrawn ((1, 'pick', None)) taken up again (pick 3 applications, cost mode)%s. " %
                 (", each relation in a new thread" if cfg == "stdlib-concurrency" else "") if k == 3 else "")
        E(cfg, "P10d", "P10d.py", r, k, semantic="complete", representation="explicit", execution_state=["finished"],
          residual_equivalence=dvals[k] + ", as valid (answers %s)" % {1: "x = 1, x = 2, x = 3", 2: "x = 2, x = 3", 3: "x = 1, x = 2, x = 3"}[k],
          observations=(hold + "; problem-defined alternatives %d. " % {1: 3, 2: 2, 3: 3}[k]
                        + ("Stage 2's narrowing lost the value 1 from the held values. " if k == 2 else "")
                        + w
                        + ("The alternative x = 1 that x > 1 removed comes back; the stage withdraws stage 2's conclusion x ∈ {2, 3}, shown only by answering x = 1 again (no explicit withdrawal). " if k == 3 else "")
                        + "The information given and not withdrawn is kept by stage (indexing written for the purpose: R). Nothing suspended. No manual action."),
          rule="SPECIFICATION Outcomes 1-3; P10 (retracting stage)")

# ---------------------------------------------------------------- expressibility
X = []
def XP(cfg, sub, direction, ex, reason): X.append({"configuration": cfg, "subproblem": sub, "direction": direction, "expressibility": ex, "reason": reason})
for cfg in CFGS:
    if cfg == "extended":
        XP(cfg, "P09a", "A: loop(x)", "expressible", "loop's one case transcribed as a relation of goals solved by the search (P tokens); unify and resolution are S")
        XP(cfg, "P09a", "B: rev forwards (conc forwards inside it)", "expressible", "rev and conc transcribed once each by their cases, heads by unification (P); no R tokens")
        XP(cfg, "P09b", None, "expressible", "the equations as bindings of Vars, the conjunction as 'and'; no R tokens")
    else:
        XP(cfg, "P09a", "A: loop(x)", "expressible", "loop as a generator of its own case (yield from loop(x)): a transcription; no R tokens")
        XP(cfg, "P09a", "B: rev forwards (conc forwards inside it)", "expressible", "rev and conc forwards, one branch per case (rule 3, METRICS' own example); no R tokens")
        XP(cfg, "P09b", None, "expressible", "the first equation an assignment, the second a comparison, in the direction reached (rule 8); no R tokens")
XP("core", "P09c", None, "expressible", "gen and sum3 forwards, one branch per case with the cases' guards (rules 2, 3); evaluated in the conjunction's order; no R tokens")
XP("extended", "P09c", None, "expressible with reformulation", "gen and sum3 transcribed as goals of the S queue, but sum3's verdict that it must wait on an unbound tail is R (rule 19), 7 R tokens, and report()'s test that s is known to its end is R; meaning kept")
XP("stdlib-concurrency", "P09c", None, "expressible with reformulation", "gen, sum3 and = transcribed, each with known-place tests and wait verdicts that are R (rule 19); RELATION table R; meaning kept on every input")
XP("core", "P09d", "P09d1 (finite)", "expressible", "genu forwards by its one case, the finite (least-relation) reading's transcription; no R tokens (it errs: the outcome, not the expressibility)")
XP("core", "P09d", "P09d2 (stream)", "expressible with reformulation", "my judgement: a tuple is finite, so the transcription cannot hold the stream s = <1, 2, 3, ...>; a lazy encoding (a generator or cells with an unknown tail and a suspended producer) would be a changed algorithm, R, keeping the meaning. No such program exists in core; the primary program's result stands for the transcription")
for cfg in ("extended", "stdlib-concurrency"):
    XP(cfg, "P09d", "P09d1 (finite)", "expressible with reformulation", "genu and sum3 transcribed, with sum3's wait verdict R (rule 19) and the known-to-its-end test R; a cell with an unbound tail represents a sequence still being produced")
    XP(cfg, "P09d", "P09d2 (stream)", "expressible with reformulation", "the same program: cells with an unbound tail and a producer goal that goes on give the stream reading's s incrementally; the wait verdicts are R")
for cfg in CFGS:
    XP(cfg, "P09e", None, "expressible with reformulation", "x = y + k and y = x - k held until two places are known: the evaluators' computing and testing are P, their known-place tests and wait verdicts R (rule 19, %s)" %
       {"core": "decide()/place() being S in my classes (general over relations: see notes; a problem-specific holding loop, R, would serve)", "extended": "around the S queue, Relation S", "stdlib-concurrency": "inside the program's relation threads, S"}[cfg])
    XP(cfg, "P10a", None, "expressible", "replacement is Python's own assignment; no R tokens")
    XP(cfg, "P10c", None, "expressible", "a snapshot is an assignment evaluated once; no R tokens")
    XP(cfg, "P10d", None, "expressible with reformulation", "pick, > and the filtering are P; withdrawal needs the information kept indexed by stage and %s, which is R (P10 Observations: indexing written for the purpose)" %
       {"core": "restated", "extended": "the store's trail marks per stage", "stdlib-concurrency": "restated in new threads"}[cfg])
XP("core", "P10b", None, "expressible with reformulation", "a relation that holds at all times is not native: it is held in a list and re-evaluated after every stage by maintain(), R (rule 19); times itself is P")
XP("extended", "P10b", None, "expressible with reformulation", "the same text as core")
XP("stdlib-concurrency", "P10b", None, "expressible with reformulation", "the relation's thread re-evaluates it on every change: the holding (source known, at all times) is R; the thread protocol is S")

# ---------------------------------------------------------------- S mechanisms (tokens from my classes)
def s_tokens(text, pred):
    return sum(s["to"] - s["from"] + 1 for s in spans[text] if s["class"] == "S" and pred(s))
SM = []
def SMe(cfg, prog, mech, listed, text, pred):
    SM.append({"configuration": cfg, "program": prog, "mechanism": mech, "listed_at_phase_4": listed, "tokens": s_tokens(text, pred)})
imp_search = lambda s: "S.search" in s["construct"] and "S.suspend" not in s["construct"] and "S.propagate" not in s["construct"]
# extended P09a: split the two import lines by hand (L38 search: tokens 0-8, L39 suspend: 9-19)
SM.append({"configuration": "extended", "program": "P09a.py", "mechanism": "backtracking search (S/search.py: search, undo, the trail convention): in the program, its import", "listed_at_phase_4": True, "tokens": 9})
SM.append({"configuration": "extended", "program": "P09a.py", "mechanism": "suspension queue (S/suspend.py: Var, deref, Queue.bind): in the program, its import", "listed_at_phase_4": True, "tokens": 11})
SMe("extended", "P09a.py", "unify (program-supplied: unification of terms with the trail, and its binder Queue)", False, "extended/P09a.py", lambda s: "unify" in s["construct"] or "binder" in s["construct"])
SMe("extended", "P09a.py", "resolution (program-supplied: children, done)", False, "extended/P09a.py", lambda s: "children" in s["construct"])
SM.append({"configuration": "extended", "program": "P09b.py", "mechanism": "backtracking search (S/search.py: undo and the trail convention only): its import", "listed_at_phase_4": True, "tokens": 7})
SM.append({"configuration": "extended", "program": "P09b.py", "mechanism": "suspension queue (S/suspend.py: Var, deref, Queue.bind): its import", "listed_at_phase_4": True, "tokens": 11})
for t in ("P09c", "P09d"):
    SM.append({"configuration": "extended", "program": t + ".py", "mechanism": "suspension queue (S/suspend.py: Var, deref, Queue.wait, bind, run, held): its import", "listed_at_phase_4": True, "tokens": 11})
    SMe("extended", t + ".py", "Goal (program-supplied: a relation application as a goal of the queue; its __repr__ is H)", False, f"extended/{t}.py", lambda s: "Goal" in s["construct"])
SM.append({"configuration": "extended", "program": "P09e.py", "mechanism": "suspension queue (S/suspend.py: Var, deref, Queue.wait, bind, run, held): its import", "listed_at_phase_4": True, "tokens": 11})
SMe("extended", "P09e.py", "Relation (program-supplied: a relation as a goal of the queue, by its evaluator; its __repr__ is H)", False, "extended/P09e.py", lambda s: "Relation" in s["construct"])
SM.append({"configuration": "extended", "program": "P10d.py", "mechanism": "constraint propagator (S/propagate.py: Store with a trail, var, relation, dom, cons): its import", "listed_at_phase_4": True, "tokens": 7})
SM.append({"configuration": "extended", "program": "P10d.py", "mechanism": "backtracking search (S/search.py: undo and the trail convention only): its import", "listed_at_phase_4": True, "tokens": 7})
SMe("core", "P09e.py", "relation-holding loop (program-supplied: decide, place, the held list), general over relations through EVALUATOR", False, "core/P09e.py", lambda s: True)
for t in ("P09c", "P09d", "P09e", "P10b", "P10d"):
    SMe("stdlib-concurrency", t + ".py", "relation threads (program-supplied: told, hold, pose, settle%s, the condition, waiting list and busy count; threading is an external mechanism)" % (", place" if t in ("P09c", "P09d", "P09e") else ""), False, f"stdlib-concurrency/{t}.py", lambda s: True)
# check that every S token is accounted for
acc = {}
for m in SM:
    key = m["configuration"] + "/" + m["program"]
    acc[key] = acc.get(key, 0) + m["tokens"]
for text, sp in spans.items():
    n = sum(s["to"] - s["from"] + 1 for s in sp if s["class"] == "S")
    if n != acc.get(text, 0):
        print("S tokens mismatch", text, n, acc.get(text, 0))

doc = {"tokens": spans, "outcomes": out, "mode_differences": [], "expressibility": X, "late_definition": [], "s_mechanisms": SM}
json.dump(doc, open("python.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "outcome entries;", len(X), "expressibility;", len(SM), "s mechanisms")
