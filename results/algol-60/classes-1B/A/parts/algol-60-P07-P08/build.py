"""Assemble algol-60.json (classifier A, batch 1B, P07-P08)."""
import json, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = "./"
tokens = json.load(open(os.path.join(HERE, "tokens.json")))

UNK_P07 = ("each unknown is a Boolean 'known' flag and an integer value; an unknown without a value is "
           "reported 'held' (it is in a held relation) or 'free'")
UNK_P08 = ("sequences a, b, c: a Boolean flag and a cell index into hd/tl; elements x, y, z: indices 1-3 into "
           "ek/ev (flag and value); an element without a value is printed by its name; x = y is held as a "
           "relation, never as an identification of the two unknowns")

# per (instance, stage): classification common to the three configurations
C = {}


def o(inst, stage, **k):
    C[(inst, stage)] = k


for inst in ["P07a", "P07a.132", "P07a.213", "P07a.231", "P07a.312", "P07a.321"]:
    o(inst, 1, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None,
      residual_size=None, residual_equivalence="explicit x = 5, y = 4, z = 3 is the valid outcome (equiv.py: the only solution)",
      obs="solved one relation at a time as its places became known (local propagation, in the posed order); "
          "no alternatives; no suspended work; the examination counts differ by order (R1/R2/R3-examined); "
          "posed fresh (reposed program, one stage); no withdrawal; no manual action")
o("P07b", 1, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=True,
  residual_size="2 relations, 4 occurrences of unknowns (x + y = 10, x - y = 4); input the same: 2 relations, 4 occurrences; reduced form x = 7, y = 3 has 0 relations",
  residual_equivalence="the held pair x + y = 10, x - y = 4 has exactly the solution x = 7, y = 3 (by hand: add the two; equiv.py window check)",
  obs="not solved: no relation acts while both its unknowns are unknown, and there is no elimination; "
      "x, y reported 'held'; suspended: held-relations 2; no alternatives; no withdrawal; no manual action")
o("P07c", 1, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
  residual_size="1 relation, 2 occurrences (x + y = 10); input 1 relation, 2 occurrences",
  residual_equivalence="the residual is the posed relation itself, which is the valid outcome",
  obs="held unresolved; x, y 'held'; suspended: held-relations 1; no alternatives; no withdrawal; no manual action")
o("P07d", 1, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="w = 7, u = 2, v = 14: w = 7 is the valid outcome; u and v are the posed values",
  obs="solved one relation at a time: R2 and R3 gave u and v, then R1 gave w by exact division (v ÷ u with a divisibility test); "
      "no alternatives; no suspended work; no withdrawal; no manual action")
o("P07e", 1, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="no answer printed and the observe block says 'no solution': the valid outcome is none; inconsistency detected (15 is not a multiple of 2; no 15/2 reported)",
  obs="inconsistency detected by the divisibility test in R1's evaluator; reported none (answer completeness: yes); "
      "u = 2, v = 15 bound; no held relations; no alternatives; no withdrawal; no manual action")
o("P07f", 1, semantic="complete", representation="residual", simplification="inconsistency undetected", identical_to_posed=True,
  residual_size="2 relations, 4 occurrences (x + y = 10, x + y = 11); input the same",
  residual_equivalence="the held pair has no solution, as the valid outcome (none); not reported as none",
  obs="inconsistency not detected: both relations held as posed; x, y 'held'; suspended: held-relations 2; "
      "answer completeness (empty): reported none: no; no withdrawal; no manual action")
o("P07g", 1, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="answers x = 3 and x = -3: both valid solutions, nothing else (2 of 2, 0 invalid)",
  obs="both solutions found, by computing the integer root (entier(sqrt(c) + 0.5), checked by squaring) and its negation; "
      "the two values of x are held all at once in the array xs (not reported as alternatives: no [alternatives] tag, held_as none); "
      "no suspended work; no withdrawal; no manual action")

# P08a/P08b stages 1-3 (shared), P08a 4-6
S1 = dict(semantic="complete", representation="solved form", simplification=None, identical_to_posed=None, residual_size=None,
          residual_equivalence="a = (x, y, z) with b, c, x, y, z free: the valid outcome under both readings",
          by_reading={"open": "complete", "closed": "complete"})
S2 = dict(semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
          residual_size="1 relation to decide (rev((x, y, z), b), pending), 4 occurrences; input 2 relations (a = (x, y, z), rev(a, b)), the first held as the binding of a",
          residual_equivalence="open reading: a = (x, y, z), b free, rev(a, b) pending, which is what is held (a's value put in its place). Closed reading: the valid outcome is none, and the report denotes solutions: unsound",
          by_reading={"open": "complete", "closed": "unsound"})
S3 = dict(semantic="complete", representation="residual", simplification="reducible", identical_to_posed=True,
          residual_size="2 relations to decide (rev((x, y, z), b) pending; x = y), 6 occurrences; input 3 relations; the solved form identifies x with y and leaves only rev pending",
          residual_equivalence="open: a = (x, y, z) with x = y held equals a = (y, y, z), x = y (equiv.py, union-find); b free; rev pending. Closed: valid none; report denotes solutions: unsound",
          by_reading={"open": "complete", "closed": "unsound"})
for inst in ("P08a", "P08b"):
    o(inst, 1, obs="a bound to the term (x, y, z); x, y, z free; nothing held; rev and conc 'not yet defined'; no alternatives; no withdrawal; no manual action", **S1)
    o(inst, 2, obs="state 4 of P08 (an application awaiting its definition), shown as 'rev(a, b): held as posed, awaiting the definition of rev, neither true nor false'; "
                   "suspended: pending-applications 1; b 'held'; told apart from failure (no 'no solution', the application is listed as awaiting); no alternatives; no withdrawal; no manual action", **S2)
    o(inst, 3, obs="x = y held as a relation (not identified: neither has a value); rev(a, b) still awaiting its definition; "
                   "suspended: pending-applications 1, held-relations 1; " + ("P08b ends here: the definition never arrives, and the report stays distinguishable from failure (the application is held, 'neither true nor false'); " if inst == "P08b" else "") +
                   "no alternatives; no withdrawal; no manual action", **S3)
o("P08a", 4, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=False,
  residual_size="1 relation to decide (x = y), 2 occurrences, with a = (x, y, z), b = (z, y, x) bound; input 3 relations and the definitions; the solved form x = y, a = (y, y, z), b = (z, y, y) has none",
  residual_equivalence="a = (x, y, z), b = (z, y, x) under x = y equals x = y, a = (y, y, z), b = (z, y, y) (equiv.py, union-find); same under both readings",
  by_reading={"open": "complete", "closed": "complete"},
  obs="stage 4 resumed the held application in the same computation (examine2 ran when defined became true; rev/1 1, rev/2 3, conc/1 3, conc/2 3 = 6 conc applications, n(n+1)/2 for n = 3); "
      "not posed again, no intervention; suspended: held-relations 1 (x = y); under the closed reading the program never reported 'none', so no conclusion is withdrawn; no alternatives; no manual action")
o("P08a", 5, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=False,
  residual_size="2 relations to decide (x = y, y = z), 4 occurrences, with a, b bound to terms of x, y, z; input 4 relations and the definitions; the solved form x = y = z, a = b = (z, z, z) has none",
  residual_equivalence="a = (x, y, z), b = (z, y, x) under x = y, y = z equals a = b = (z, z, z), x = y = z (equiv.py)",
  by_reading={"open": "complete", "closed": "complete"},
  obs="y = z held as a relation beside x = y; suspended: held-relations 2; no new rev or conc work; no alternatives; no withdrawal; no manual action")
o("P08a", 6, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="a = b = (42, 42, 42), c = (42, 42), x = y = z = 42: the valid outcome under both readings",
  by_reading={"open": "complete", "closed": "complete"},
  obs="b = s ++ c decomposed with b known: 42 given to z by the element equation, then to y and x through the held x = y, y = z (propagation); "
      "c = the rest of b; nothing held; no alternatives; no withdrawal; no manual action")
# P08c
o("P08c", 1, semantic="complete", representation="solved form", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="'b free': the stage has no unknowns (b is not yet posed), so the report denotes no constraint, as the valid outcome",
  by_reading={"open": "complete", "closed": "complete"},
  obs="only conc's flag set; nothing held; no alternatives; no withdrawal; no manual action")
o("P08c", 2, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
  residual_size="1 relation to decide (rev((1, 2), b), pending), 1 occurrence; input 1 application (and conc's definition)",
  residual_equivalence="open: b free, rev((1, 2), b) pending, which is what is held. Closed: valid none; report denotes solutions: unsound",
  by_reading={"open": "complete", "closed": "unsound"},
  obs="state 4 (awaiting its definition): 'rev(s, b): held as posed, neither true nor false, examined again at each stage'; suspended: pending-applications 1; no alternatives; no withdrawal; no manual action")
o("P08c", 3, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
  residual_size="1 relation to decide (rev((1, 2), b), pending), 1 occurrence; input 1 application, conc's definition and rev case 1",
  residual_equivalence="open: b free, pending, since case 2 may yet arrive: what is held. Closed: valid none (case 1 does not cover a sequence of two); report denotes solutions: unsound",
  by_reading={"open": "complete", "closed": "unsound"},
  obs="the application was examined again with the partial definition (case 1's head test failed, case 2 absent: status 'cannot tell'), and held, not failed; "
      "shown as 'awaiting the rest of the definition of rev'; rev/1 count 0 (it counts only a case that applies); suspended: pending-applications 1; stage 4 can still reach it; no alternatives; no withdrawal; no manual action")
o("P08c", 4, semantic="complete", representation="explicit", simplification=None, identical_to_posed=None, residual_size=None,
  residual_equivalence="b = (2, 1): the valid outcome",
  by_reading={"open": "complete", "closed": "complete"},
  obs="stage 4 resumed the held application in the same computation (rev/1 1, rev/2 2, conc/1 2, conc/2 1: 3 conc applications, n(n+1)/2 for n = 2); not posed again, no intervention; "
      "under the closed reading the program never reported 'none' at stages 2-3, so nothing is withdrawn; nothing held; no alternatives; no manual action")

outcomes = []
behaviour = {}
for conf in ("report", "x1", "x1sim"):
    for p in sorted(glob.glob(R + f"results/algol-60/{conf}/P0[78]/raw/*.behaviour.*.json")):
        d = json.load(open(p))
        inst = d["run"]["instance"]
        prog = os.path.basename(d["run"]["program"]["path"])
        rel = p.replace(R, "")
        behaviour[(conf, inst)] = rel
        fault = p.endswith(".INVALID.json")
        for s in d["stages"]:
            a = s["attempts"][-1]
            c = a["computations"][0]
            k = C[(inst, s["stage"])]
            states = c["execution_state"]["states"]
            susp = c["suspended"]["items"]
            note = ""
            if conf == "x1sim" and d["run"]["posing"] == "incremental":
                posing = "received into x1sim's one live process (the same computation)"
            elif d["run"]["posing"] == "incremental":
                posing = "incremental; report/x1 re-created the earlier stages in a fresh process for the budget (recreated_for_budget, prefix steps not charged); not a replay"
            else:
                posing = "reposed program, one stage, posed fresh"
            entry = {
                "configuration": conf, "instance": inst, "program": prog, "record": rel,
                "stage": s["stage"], "reached": True,
                "semantic": k["semantic"],
                "semantic_by_reading": k.get("by_reading"),
                "representation": k["representation"],
                "simplification": k["simplification"],
                "identical_to_posed": k["identical_to_posed"],
                "residual_size": k["residual_size"],
                "execution_state": states,
                "residual_equivalence": k["residual_equivalence"],
                "observations": (UNK_P07 if inst.startswith("P07") else UNK_P08) + ". " + k["obs"] +
                                f". Suspended items in the record: {json.dumps(susp)}. Posing: {posing}. Answers verbatim: {json.dumps([x['verbatim'] for q in c['queries'] for x in q['answers']])}",
                "rule": "SPECIFICATION.md Outcomes 1-3; P08: classified under both readings (problems/08), semantic = open reading" if inst.startswith("P08") else "SPECIFICATION.md Outcomes 1-3; problems/07 Observations",
            }
            if fault:
                entry["harness_fault"] = True
            outcomes.append(entry)

# mode comparisons: computed by modes.py: no stage differs
mode_differences = []

expr = []
for conf in ("report", "x1", "x1sim"):
    for sp in ["P07a", "P07b", "P07c", "P07d", "P07e", "P07f", "P07g"]:
        reason = ("ALGOL 60 has no unknowns or relations: each relation is written as an evaluator that computes any place from the "
                  "others or tests it (P, rule 19), inside code written for this problem that holds it until enough places are known "
                  "and re-examines the held relations to a fixpoint (R, rule 19). The reformulation keeps the relations' meaning on every input: "
                  "what it cannot solve it holds unchanged")
        extra = {"P07a": "; every order of the relations posed by the instance line is served (the posed order drives the examination order)",
                 "P07b": "; it does not solve the pair (no elimination), but holds it, which is equivalent",
                 "P07c": "", "P07d": "; w · u = v is decided by exact integer division with a divisibility test, u = 0 handled",
                 "P07e": "; the divisibility test detects the inconsistency over the integers",
                 "P07f": "; the two relations are held, the contradiction undetected, which is still equivalent",
                 "P07g": "; x · x = c is solved for x by the integer square root (entier(sqrt(c) + 0.5), checked by squaring) and its negation, a computation of the place x from c (rule 19)"}[sp]
        expr.append({"configuration": conf, "subproblem": sp, "direction": None, "expressibility": "expressible with reformulation", "reason": reason + extra})
    for sp, dirs in [("P08a", [("rev(a, b), a known, b computed", "rev is a mode-faithful transcription by its two cases, in order (P, rule 3); its application is held by problem-specific code (examine2, R, rule 19) until the Boolean defined (stage 4) and a are known"),
                               ("conc(q, <h>, r), q and h known, r computed", "transcribed by its two cases, in order, in the one direction rev uses (P, rule 3)"),
                               ("b = s ++ c, b and s known (c computed), or s and c known (b computed)", "the ++ encoding's decomposition and construction (P, rules 15, 19), held by examine6 (R) until b or c is known"),
                               ("the late arrival of the definition", "ALGOL 60 has no definitions that arrive while a program runs: the text of rev and conc is in the program from the start, and stage 4's information is reduced to a flag (R, rule 19; a reading of P08 that rule 11 would make C if it were a declaration). The reformulation gives the open reading's valid outcomes at every stage")]),
                     ("P08b", [("rev(a, b), a known, b computed", "as P08a; the definition never arrives, so rev is never applied; the application is held by examine2 (R)"),
                               ("the late arrival of the definition", "as P08a: the absence of the definition is a flag that stays false")]),
                     ("P08c", [("rev(s, b), s known, b computed, by the cases that have arrived", "rev and conc transcribed by their cases (P), with an extra status result (found / none / cannot tell) and per-case arrival flags (R, rule 19); case 1's two sequences arrive as stage-3 constants"),
                               ("conc(q, <h>, r), q and h known, r computed", "transcribed by its two cases, in the direction rev uses (P), with the status result and conc's arrival flag (R)"),
                               ("the arrival of a definition in parts", "as P08a: the cases' code is in the program, their arrival flags (and case 1's arguments) arrive; the open reading's outcomes at every stage")])]:
        for dname, rsn in dirs:
            expr.append({"configuration": conf, "subproblem": sp, "direction": dname, "expressibility": "expressible with reformulation" if ("late" in dname or "parts" in dname or dname.startswith("rev") or dname.startswith("b =") or sp == "P08c") else "expressible", "reason": rsn})

late = []
ev = {
    ("report", "P08a.alg"): "The procedures conc (tokens 247-318) and rev (319-387), transcribed by their cases (P), are in the text from the start; the Boolean defined (decl 56-57, R) is set by stage 4's message (defined := true, 1913-1915, R); the application's evaluator examine2 (564-620) waits on 'if defined ∧ ak then' (568-572, R). Records: stages 2-3 show 'rev(a, b): held as posed, awaiting the definition of rev, neither true nor false' with pending-applications 1 and rev/conc operation counts 0; at stage 4 the same computation decides it (b = (z, y, x), rev/2 3, conc/2 3) without reposing.",
    ("x1", "P08a.a60"): "As report: decl of defined 56-57 (R), defined := true 1805-1807 (R), examine2's guard 'if defined ∧ ak then' 568-572 (R); conc 247-318 and rev 319-387 in the text (P); examine2 564-620. x1 and x1sim records show the same stages: held at 2-3, decided at 4.",
    ("report", "P08c.alg"): "conc (256-356) and rev (357-503), by their cases (P, with status results R), are in the text from the start; examine2 is 504-582; flags concdef, rev1def, rev2def (decls 42-47, R) are set by stages 1, 3, 4 (1055-1057, 1122-1125, 1133-1135, R); conc waits on 'if ¬ concdef then conc := 2' (280-283), rev on 'if rev1def then' (386-389) and 'if st ≠ 1 ∧ rev2def then' (415-422), and gives 'cannot tell' until both cases have arrived ('st := if rev1def ∧ rev2def then 0 else 2', 488-497); examine2 releases the application only when 'concdef ∧ rev1def ∧ rev2def' (570-577). Stage 3 also delivers case 1's two sequences as constants (readseq, 109-192, P), so part of case 1 is data that arrives, but the code that uses it is already in the program. Records: stages 2-3 held ('awaiting the definition of rev', then 'awaiting the rest'), stage 4 decided b = (2, 1) in the same computation.",
    ("x1", "P08c.a60"): "As report (conc 253-353, rev 354-500, examine2 501-579, readseq 109-189): decls 42-47, conc's 'if ¬ concdef then' 277-280, rev's 'if rev1def then' 383-386 and 'if st ≠ 1 ∧ rev2def then' 412-419, 'st := if rev1def ∧ rev2def then 0 else 2' 485-494, examine2's 'if concdef ∧ rev1def ∧ rev2def then' 567-574, flags set at 992-994, 1050-1053, 1061-1063 (all R). x1 and x1sim records: held at 2-3, decided at 4.",
}
for conf in ("report", "x1", "x1sim"):
    ext = "alg" if conf == "report" else "a60"
    tconf = "report" if conf == "report" else "x1"
    for prog in ("P08a", "P08b", "P08c"):
        base = "P08a" if prog in ("P08a", "P08b") else "P08c"
        e = ev[(tconf, f"{base}.{ext}")]
        if prog == "P08b":
            e = "P08b is the same text as P08a (stages 1-3 only). " + e.split(" Records:")[0] + " Records: stages 2-3 hold the application as awaiting its definition; the flag never becomes true and the run ends with it held."
        if conf == "x1sim":
            e = "Same text as x1 (tokens classed under x1). " + e
        late.append({"configuration": conf, "program": f"{prog}.{ext}", "kind": "permission awaited", "evidence": e})

sm = []
for conf in ("report", "x1", "x1sim"):
    ext = "alg" if conf == "report" else "a60"
    for prog in ["P07a", "P07b", "P07c", "P07d", "P07e", "P07f", "P07g", "P08a", "P08b", "P08c"]:
        sm.append({"configuration": conf, "program": f"{prog}.{ext}", "mechanism": "none",
                   "listed_at_phase_4": True, "tokens": 0,
                   "note": "S-mechanisms.md lists none for this configuration. The program's holding code (evaluators, propagate, the definition flags) is written for this problem's own relations: R by rule 19, not S. The list-cell encoding (cons, same, hd/tl) is the systems file's sequence encoding, P (rule 15)."})

out = {"tokens": tokens, "outcomes": outcomes, "mode_differences": mode_differences,
       "expressibility": expr, "late_definition": late, "s_mechanisms": sm}
json.dump(out, open(os.path.join(HERE, "algol-60.json"), "w"), ensure_ascii=False, indent=1)
print(len(outcomes), "outcome entries;", len(expr), "expressibility;", len(late), "late;", len(sm), "s")
