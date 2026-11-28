# Writes algol-60.json: the token spans (from build.py's tokens.json), the outcome of every stage of every behaviour
# record, the mode differences (cost and storage against behaviour), and expressibility.
import json, re, csv
D = "results/algol-60/classes/A/"
tokens = json.load(open(D + "tokens.json"))
recs = [json.loads(l) for l in open(D + "summary.jsonl")]
cost = {(r["configuration"], r["instance"]): r for r in recs if r["mode"] == "cost"}

def steps_note(conf, inst, st):
    r = cost.get((conf, inst))
    if not r:
        return "steps: unavailable (x1sim is behaviour only; systems file)"
    c = r["stages"][st - 1]["attempts"][-1]["comps"][0]["steps"]
    rw = (c.get("repeated_work") or {}).get("name_repeat_evaluations")
    return f"steps (cost run): incremental {c['stage']}, restated {c['restated']}, name_repeat_evaluations {rw}; the steps include the program's printing"

NONE_ALT = "alternatives: none held (no [alternatives] reported)"
NO_WD = "conclusions withdrawn: none"
NO_MAN = "manual actions: none"
HELDREP = "unknowns: each unknown is an integer (or a sequence cell index) with a Boolean known flag; an unknown without a value is printed as 'held' (it occurs in a held relation) or 'free'"

def o(sem, rep, simp, ident, size, state, eq, obs, rule):
    return dict(semantic=sem, representation=rep, simplification=simp, identical_to_posed=ident, residual_size=size,
                execution_state=state, residual_equivalence=eq, observations=obs, rule=rule)

R1 = "u + v = 16"; R2 = "w . u = v"; R3 = "u + 10 = 12"
def p02(rels, inst_note=""):
    """classification of a P02 stage by the set of relations that have arrived"""
    s = frozenset(rels)
    if s == {"R1"}:
        return o("complete", "residual", "reduced", True, "1 relation (u + v = 16), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
                 ["suspended"], "equivalent: the held relation is R1 itself, w reported free; denotes every integer pair with u + v = 16, w free (by hand; check_residuals.py on a box)",
                 f"{HELDREP}. R1 held, waiting for u or v (suspended held-relations 1). {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 1-2 (the P02 stage 1 example: complete / residual / reduced)")
    if s == {"R2"}:
        return o("complete", "residual", "reduced", True, "1 relation (w . u = v), 3 occurrences of unknowns; input: 1 relation, 3 occurrences",
                 ["suspended"], "equivalent: the held relation is R2 itself; denotes every integer triple with v = w . u (by hand; check_residuals.py on a box)",
                 f"{HELDREP}. R2 held, waiting for two of u, v, w (suspended held-relations 1). {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 1-2")
    if s == {"R3"}:
        return o("complete", "solved form", None, False, None, ["finished"],
                 "equivalent: u = 2 with v and w free is exactly the valid outcome (u = 2; v, w free)",
                 f"{HELDREP}; here u bound to 2, v and w free. Nothing held (R3 decided at once). {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 2 (solved form: each unknown bound or free, no relation left)")
    if s == {"R1", "R2"}:
        return o("complete", "residual", "reducible", True,
                 "2 relations (u + v = 16, w . u = v), 5 occurrences of unknowns; input: 2 relations, 5 occurrences. The smaller equivalent is the ten explicit triples (no relation left)",
                 ["suspended"], "equivalent: the conjunction R1, R2 is held unchanged; over the integers it has exactly the ten triples of the problem file (u divides 16), checked by check_residuals.py on [-60, 60]^3, which contains all ten",
                 f"{HELDREP}. R1 and R2 both held, neither has enough known places (suspended held-relations 2); the ten solutions are not derived. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 1 (correctness and simplification kept apart; like P07b, reducible)")
    if s == {"R1", "R3"}:
        return o("complete", "solved form", None, False, None, ["finished"],
                 "equivalent: u = 2, v = 14, w free is exactly the valid outcome",
                 f"{HELDREP}; u = 2 and v = 14 bound, w free. Nothing held: R3 gave u, and R1 then gave v. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 2 (solved form)")
    if s == {"R2", "R3"}:
        return o("complete", "residual", "reduced", False,
                 "1 relation (w . 2 = v, the held R2 printed with u's value), 2 occurrences of unknowns, and the binding u = 2; input: 2 relations (w . u = v, u + 10 = 12), 4 occurrences",
                 ["suspended"], "equivalent: u = 2 and w . 2 = v is the valid outcome u = 2, v = 2w (substituting the determined u preserves the set); check_residuals.py on a box",
                 f"{HELDREP}; u = 2 bound, v and w held. R2 held, waiting for v or w (suspended held-relations 1); R3 decided and released. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 1-2 (reduced: v = 2w has the same size)")
    if s == {"R1", "R2", "R3"}:
        return o("complete", "explicit", None, False, None, ["finished"],
                 "explicit: u = 2, v = 14, w = 7, the one valid outcome",
                 f"Every unknown has its value; nothing held. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                 "SPECIFICATION Outcomes 1-2")
    raise ValueError(rels)

ORDERS = {"P02a": ["R1", "R2", "R3"], "P02b.R1R2R3": ["R1", "R2", "R3"], "P02b.R1R3R2": ["R1", "R3", "R2"],
          "P02b.R2R1R3": ["R2", "R1", "R3"], "P02b.R2R3R1": ["R2", "R3", "R1"], "P02b.R3R1R2": ["R3", "R1", "R2"],
          "P02b.R3R2R1": ["R3", "R2", "R1"]}
LAST_ORDER_NOTE = {  # how the held relations were taken up when the last relation arrived, from the examination counters
}

def classify(inst, st):
    if inst == "P01a":
        if st == 1:
            return [o("complete", "residual", "reduced", True, "1 relation (x = y), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
                      ["suspended"], "equivalent: x = y held with z free denotes every assignment with x = y, z free (by hand)",
                      f"{HELDREP}. The relation between x and y is held as a recorded equation (r1), not as one shared unknown; z free. Suspended: 1 held equation, waiting for x or y. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                      "SPECIFICATION Outcomes 1-2; the held equation is a relation still to decide, so residual, not solved form (see notes)")]
        if st == 2:
            return [o("complete", "residual", "reduced", True, "2 relations (x = y, y = z), 4 occurrences of unknowns; input: 2 relations, 4 occurrences",
                      ["suspended"], "equivalent: x = y and y = z held denote every assignment with x = y = z (by hand)",
                      f"{HELDREP}. Two recorded equations held (suspended held-relations 2), each waiting for one of its places; x, y, z not merged. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                      "SPECIFICATION Outcomes 1-2")]
        if st == 3:
            return [o("complete", "explicit", None, False, None, ["finished"], "explicit: x = y = z = 2, the one valid outcome",
                      f"The value reached every unknown in the one propagate call of the stage: z from z = 2, then y from y = z, then x from x = y on successive passes (the program examines the held equations in posed order until a pass changes nothing). Nothing held. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                      "SPECIFICATION Outcomes 1-2")]
    if inst == "P01b":
        if st == 1:
            return [o("complete", "residual", "reducible", True,
                      "1 relation (conc(<1,2>, s, t)), 2 occurrences of unknowns; input: 1 relation, 2 occurrences. The smaller equivalent is the solved form t = <1,2> ++ s (no relation left)",
                      ["suspended"], "equivalent: conc(<1,2>, s, t) over sequences holds exactly when t = <1,2> ++ s (by the two cases of conc; check_residuals.py by enumeration of short sequences)",
                      f"{HELDREP}. The relation is held as posed (r1), waiting for s; t is not built as <1,2> followed by an unknown tail, since the encoding has no unknown inside a structure. Suspended: 1 held relation. conc applied 0 times. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                      "SPECIFICATION Outcomes 1-2 (reducible: a solved form exists that the program did not reach)")]
        if st == 2:
            return [o("complete", "explicit", None, False, None, ["finished"], "explicit: s = <3>, t = <1,2,3>, the one valid outcome",
                      f"The value of s reached t in one propagate call: s = b2 gave s, then conc(a1, s, t) computed t (conc/1 once, conc/2 twice). Nothing held. {NONE_ALT}. {NO_WD}. {NO_MAN}.",
                      "SPECIFICATION Outcomes 1-2")]
    if inst == "P01c":
        base = f"{HELDREP}. x = <1> ++ x is held as posed (r1), waiting for x to be known, which no stage gives; suspended: 1 held relation; conc applied 0 times. Occurs check: not applicable, the program has no unification and makes no cyclic value. {NONE_ALT}. {NO_WD}. {NO_MAN}."
        return [dict(reading="finite", **o("complete", "residual", "inconsistency undetected", True,
                      "1 relation (x = <1> ++ x), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
                      ["suspended"], "equivalent: the held equation has no finite solution (a solution of length n would have length n + 1), so it denotes the empty set, the valid outcome; the program did not report that there are none",
                      base, "SPECIFICATION Outcomes 1 (empty set as residual: inconsistency undetected, like P07f); P01c's finite reading")),
                dict(reading="rational", **o("complete", "residual", "reduced", True,
                      "1 relation (x = <1> ++ x), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
                      ["suspended"], "equivalent: over rational trees the held equation has exactly the one solution <1, 1, 1, ...>; it is held as an equation, not presented as a cyclic value",
                      base, "SPECIFICATION Outcomes 1-2; P01c's rational reading (not 'cyclic': no cyclic term is presented)"))]
    if inst in ORDERS:
        return [p02(ORDERS[inst][:st])]
    if inst == "P02c":
        return [p02(["R1", "R2", "R3"])]
    P03 = {"P03a": "c = <1,2,3>", "P03b": "the three pairs (<>, <1,2>), (<1>, <2>), (<1,2>, <>), in that order", "P03c": "b = <2,3>",
           "P03d": "a = <1,2>", "P03e": "b = <3,2,1>", "P03f": "a = <3,2,1>, exactly one"}
    if inst in P03:
        how = {"P03a": "conc computed forward", "P03b": "split, a separately written direction (R), enumerating by recursion and printing each answer as found",
               "P03c": "strip, a separately written direction (R)", "P03d": "prefix, a separately written direction (R), trying every suffix of c",
               "P03e": "rev and conc computed forward", "P03f": "unrev and lastsplit, separately written directions (R), with the conjuncts of rev's case 2 taken in the other order"}[inst]
        return [o("complete", "explicit", None, False, None, ["finished"], f"explicit: {P03[inst]}; every valid outcome, no invalid one",
                  f"Computed by {how}. After the last answer the program finished (it knows it has found every answer: the recursion is exhausted); nothing held. {NONE_ALT} at the end; during the search the recursion stack holds the partial answer in path (depth-first). {NO_WD}. {NO_MAN}.",
                  "SPECIFICATION Outcomes 1-3")]
    raise ValueError(inst)

outcomes = []
for r in recs:
    if r["mode"] != "behaviour": continue
    for s in r["stages"]:
        a = s["attempts"][-1]; c = a["comps"][0]
        for cl in classify(r["instance"], s["stage"]):
            # the record's own state must agree with the classification's execution state
            assert c["states"] == cl["execution_state"], (r["record"], s["stage"], c["states"], cl["execution_state"])
            ent = {"configuration": r["configuration"], "instance": r["instance"], "program": r["program"], "record": r["record"],
                   "stage": s["stage"], "reached": True}
            if "reading" in cl: ent["reading"] = cl.pop("reading")
            ent.update(cl)
            ent["answers_verbatim"] = c["answers"][0][2]
            ent["observations"] = ent["observations"] + " " + steps_note(r["configuration"], r["instance"], s["stage"]) + "."
            ent["posed"] = a["posed"][0]
            outcomes.append(ent)

mode_differences = []  # modes.py found no stage whose answers, state, held work, operations or observe differ

EXP = []
REASON_HOLD = "ALGOL 60 has no unknowns or relations: the program holds each relation until its places are known with code written for this problem's own relations (known flags, held flags, propagate: R by METRICS rule 19). The evaluators' computations are P; the reformulation keeps each relation's meaning over the problem's integer (or integer-coded) values on every input the stages use. No S mechanism is used (S-mechanisms.md: none)."
for conf in ("report", "x1", "x1sim"):
    for sp, e, d, why in [
        ("P01a", "expressible with reformulation", None, REASON_HOLD + " Each unknown holds an integer, and P01a's only value is an integer."),
        ("P01b", "expressible with reformulation", "conc(+, +, -)", REASON_HOLD + " conc itself is a mode-faithful transcription in the direction used (a, s known; t computed), P by rule 3."),
        ("P01c", "expressible with reformulation", "conc(+, +, -), inside the test of x = a ++ x", REASON_HOLD + " Under the finite reading the held equation is a faithful (if undetected) statement of the empty set; under the rational reading the program cannot hold a cyclic value, but the held equation keeps the relation's meaning."),
        ("P02a", "expressible with reformulation", None, REASON_HOLD),
        ("P02b", "expressible with reformulation", None, REASON_HOLD + " One program text serves all six orders, reading the order from the instance line."),
        ("P02c", "expressible with reformulation", None, REASON_HOLD + " With all three relations in one stage, R1 and R2 still cannot be computed in the order written, so the same holding is used."),
        ("P03a", "expressible", "conc(+, +, -)", "conc is transcribed as a function computing c from a and b by its two cases, the direction the query uses (METRICS rule 3)."),
        ("P03b", "expressible with reformulation", "conc(-, -, +)", "A function cannot run backwards; split is a separately written direction (R, rule 14) with an extra argument path/d (R, rules 3 and 5). It keeps conc's meaning on every sequence c."),
        ("P03c", "expressible with reformulation", "conc(+, -, +)", "strip is a separately written direction (R, rule 14), keeping conc's meaning on every a and c."),
        ("P03d", "expressible with reformulation", "conc(-, +, +)", "prefix is a separately written direction (R, rule 14), with the extra argument path/d and sequence equality used only there (R, rule 15). It keeps conc's meaning on every b and c."),
        ("P03e", "expressible", "rev(+, -), conc(+, +, -)", "rev and conc are transcribed as functions computing their last place by their cases in order, conjuncts of rev's case 2 in order (METRICS rule 3)."),
        ("P03f", "expressible with reformulation", "rev(-, +), conc(-, +, +) with the second place a singleton", "unrev and lastsplit are separately written directions (R, rule 14), with an extra argument (path/d) and the two conjuncts of rev's case 2 taken in the other order (one move, rule 4). They keep rev's meaning on every b."),
    ]:
        EXP.append({"configuration": conf, "subproblem": sp, "direction": d, "expressibility": e, "reason": why})

json.dump({"tokens": tokens, "outcomes": outcomes, "mode_differences": mode_differences, "expressibility": EXP},
          open(D + "algol-60.json", "w"), indent=1, ensure_ascii=False)
print(len(outcomes), "outcome entries;", len(tokens), "texts")
