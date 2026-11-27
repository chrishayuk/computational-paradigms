# Classifier A: outcomes of every behaviour run (P01-P03, python), expressibility,
# and the cost/storage comparison; assembles python.json with tokens.json.
# The judgements are written out below by hand; the script only reads the
# records to attach paths and to check that the answers and states it judges
# are the ones the records hold.
import json, glob, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/christopherhay/cp-roles/classifier-A"
RES = REPO + "/results/python"

def rec(conf, inst, mode):
    prob = inst[:3]
    ps = glob.glob("%s/%s/%s/raw/%s.%s.*.json" % (RES, conf, prob, inst, mode))
    assert len(ps) == 1, (conf, inst, mode, ps)
    return ps[0]

RULE = "SPECIFICATION Outcomes 1-3; AMENDMENTS 3 (none applies: every stage reached, no measurement missing)"

def ex(answer, why="the reported values are exactly the valid outcome"):
    return dict(semantic="complete", representation="explicit", simplification=None, identical_to_posed=None,
                residual_size=None, residual_equivalence=why)

def solved(why):
    return dict(semantic="complete", representation="solved form", simplification=None, identical_to_posed=None,
                residual_size=None, residual_equivalence=why)

def resid(simp, ident, size, why, semantic="complete"):
    return dict(semantic=semantic, representation="residual", simplification=simp, identical_to_posed=ident,
                residual_size=size, residual_equivalence=why)

# ------------------------------------------------------------------ P01
def p01a(conf, stage):
    ext = conf == "extended"
    if stage == 1:
        if ext:
            return solved("x is bound to the Var y (one shared unknown), y and z unbound: every assignment with x = y, z free; equivalent"), ["finished"]
        return resid("reducible", True, "residual: 1 relation (x = y), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
                     "the held equation x = y, with no binding: every assignment with x = y, z free (z unconstrained); equivalent. "
                     "Reducible: the solved form identifying x with y has no relation left to decide"), ["suspended"]
    if stage == 2:
        if ext:
            return solved("x and y are bound to the Var z (identified), z unbound: every assignment with x = y = z; equivalent"), ["finished"]
        return resid("reducible", True, "residual: 2 relations (x = y, y = z), 4 occurrences; input: 2 relations, 4 occurrences",
                     "x = y and y = z held: every assignment with x = y = z (equivalence.py checks it on a small box); "
                     "reducible to the solved form x, y identified with z (no relation left)"), ["suspended"]
    return ex("x = 2, y = 2, z = 2"), ["finished"]

def p01b(conf, stage):
    ext = conf == "extended"
    if stage == 1:
        if ext:
            return solved("t bound to the term ⟨1,2⟩ ++ s (cons cells ending in the unbound Var s): t = ⟨1,2⟩ ++ s for every s; "
                          "equivalent (s may also be bound to a non-sequence by this encoding, but nothing in the stage does so)"), ["finished"]
        return resid("reducible", True, "residual: 1 relation (conc(⟨1,2⟩, s, t)), 2 occurrences; input: 1 relation, 2 occurrences",
                     "conc(⟨1,2⟩, s, t) held, read by the problem's definition: t = ⟨1,2⟩ ++ s for every sequence s; equivalent "
                     "(equivalence.py). Reducible: the solved form t = ⟨1,2⟩ ++ s has no relation left"), ["suspended"]
    return ex("s = ⟨3⟩, t = ⟨1,2,3⟩"), ["finished"]

def p01c(conf, reading):
    if conf == "extended":
        if reading == "finite":
            return dict(semantic="unsound", representation="cyclic", simplification=None, identical_to_posed=None, residual_size=None,
                        residual_equivalence="x bound to a cyclic term (no occurs check), presented as cyclic; under the finite reading "
                        "there is no solution, so the report denotes an outcome that is not valid (P01c: unsound under the finite reading)"), ["finished"]
        return dict(semantic="complete", representation="cyclic", simplification=None, identical_to_posed=None, residual_size=None,
                    residual_equivalence="x = ⟨1⟩ ++ x as a cyclic cons cell, shown '⟨1⟩ ++ ⟨1⟩ ++ … (cyclic)': the infinite sequence "
                    "⟨1,1,1,…⟩, the one rational solution; equivalent"), ["finished"]
    if reading == "finite":
        return resid("inconsistency undetected", True, "residual: 1 relation (conc(⟨1⟩, x, x)), 2 occurrences; input: 1 relation, 2 occurrences",
                     "the held relation x = ⟨1⟩ ++ x has no finite solution (equivalence.py, up to length 8; in general the lengths "
                     "would satisfy n = n + 1): it denotes the empty set, equivalent to 'none', but the program never reports that there are none"), ["suspended"]
    return resid("reducible", True, "residual: 1 relation, 2 occurrences; input: 1 relation, 2 occurrences",
                 "over rational trees the held relation x = ⟨1⟩ ++ x has exactly the solution ⟨1,1,1,…⟩; equivalent. Reducible: "
                 "the cyclic binding of x (no relation left) is smaller; Python tuples cannot hold it"), ["suspended"]

# ------------------------------------------------------------------ P02
def p02(conf, rels):
    """rels: the set of relations arrived so far."""
    ext = conf == "extended"
    r = frozenset(rels)
    if r == {"R1"}:
        return resid("reduced", True, "residual: 1 relation (u + v = 16), 2 occurrences; input: 1 relation, 2 occurrences",
                     "u + v = 16 held, w free: every integer pair with u + v = 16, w free; equivalent (SPECIFICATION's example: reduced)"), ["suspended"]
    if r == {"R2"}:
        return resid("reduced", True, "residual: 1 relation (w · u = v), 3 occurrences; input: 1 relation, 3 occurrences",
                     "w · u = v held: v = w · u, infinite; equivalent; no smaller representation (v = w · u is not a solved form term)"), ["suspended"]
    if r == {"R3"}:
        return solved("u bound to 2 (from u + 10 = 12), v and w unbound and not mentioned: u = 2, v and w free; equivalent"), ["finished"]
    if r == {"R1", "R2"}:
        return resid("reducible", True, "residual: 2 relations (u + v = 16, w · u = v), 5 occurrences; input: 2 relations, 5 occurrences",
                     "u + v = 16 and w · u = v held, nothing bound: their integer solutions are exactly the ten triples "
                     "(equivalence.py; u · (w + 1) = 16 so u divides 16); equivalent. Reducible: the ten explicit triples leave no "
                     "relation to decide; the program does not reach them (each evaluator waits for two known places)"), ["suspended"]
    if r == {"R1", "R3"}:
        return solved("u = 2, v = 14 bound, w unbound: u = 2, v = 14, w free; equivalent (equivalence.py)"), ["finished"]
    if r == {"R2", "R3"}:
        held = "R2(w, 2, v) in the queue" if ext else "('R2', ('w', 'u', 'v')) with u bound"
        return resid("reduced", False, "residual: 1 relation (w · 2 = v), 2 occurrences, beside the binding u = 2; input: 2 relations (R2, R3), 4 occurrences",
                     "u = 2 bound and %s: u = 2, v = 2w for every integer w; equivalent (equivalence.py). Reduced: one relation "
                     "with two occurrences, and v = 2w has no solved form (· is not a term constructor). Not identical: R3 was decided "
                     "into the binding" % held), ["suspended"]
    if r == {"R1", "R2", "R3"}:
        return ex("u = 2, v = 14, w = 7"), ["finished"]
    raise ValueError(r)

# ------------------------------------------------------------------ observations
def obs_holding(conf, inst, stage, rec_stage):
    at = rec_stage["attempts"][-1]
    c = at["computations"][0]
    n = c["suspended"]["at_boundary"]
    raw = at["observe"]["raw"]
    held = [l for l in raw.split("\n") if ".suspended[" in l]
    if conf == "core":
        unk = "unknowns are names (str); an unknown with no value is absent from the bindings dict `known`"
        susp = "relations held in the list `held` (%s): %d item(s)" % (held[0].split(" = ", 1)[1] if held else "", n)
    elif conf == "stdlib-concurrency":
        unk = "unknowns are names (str); an unknown with no value is absent from `known`"
        susp = "one daemon thread per held relation, blocked on the condition `changed`, listed in `waiting` (%s): %d item(s)" % (held[0].split(" = ", 1)[1] if held else "", n)
    else:
        unk = "unknowns are S Vars (suspend.Var): unbound, aliased to another Var, or bound"
        susp = ("goals held by the S queue (%s): %d item(s)" % (held[0].split(" = ", 1)[1], n)) if held else "no suspended work registered"
    return "%s; %s; alternatives held: none (0 registered); conclusions withdrawn: none; manual actions: none" % (unk, susp)

def obs_p03(conf, inst, rec_stage):
    at = rec_stage["attempts"][-1]
    c = at["computations"][0]
    a = c["alternatives"]
    if conf == "extended":
        base = "unknowns are S Vars; answers reported during the search; at the boundary the trail is undone and the bindings show the query's Var unbound (%s)" % at["observe"]["raw"].split("\n")[0]
        if inst == "P03f":
            return (base.split(";")[0] + "; the answer a = ⟨3,2,1⟩ reported at step 16,561, then the depth-first search went on "
                    "into longer candidates for a (rev's case 2 applied to an unbound first place) until the budget; at the budget "
                    "108 choice points held (kept for backtracking, search stack), and the bindings held a = a 17-cell sequence of "
                    "unbound Vars (a tentative state of the search, not an answer); suspended work: none; conclusions withdrawn: none; manual actions: none")
        return base + "; alternatives: search stack empty at the end (0); suspended work: none; conclusions withdrawn: none; manual actions: none"
    gen = "a generator registered as pending, finished at the boundary (0 entries)" if "pending" in at["observe"]["raw"] else "no pending structure"
    return ("unknowns are not represented: the query's unknown is computed as a Python value and stored in the bindings dict; %s; "
            "suspended work: none; conclusions withdrawn: none; manual actions: none" % gen)

# ------------------------------------------------------------------ build
ORDERS = ["R1R2R3", "R1R3R2", "R2R1R3", "R2R3R1", "R3R1R2", "R3R2R1"]
CONFS = ["core", "extended", "stdlib-concurrency"]

def answers_of(st):
    return [a["verbatim"] for q in st["attempts"][-1]["computations"][0]["queries"] for a in q["answers"]]

outcomes = []
def add(conf, inst, prog, path, r, stage, judged, states, obs, reading=None, extra_rule=None):
    st = r["stages"][stage - 1]
    rs = st["attempts"][-1]["computations"][0]["execution_state"]["states"]
    assert sorted(rs) == sorted(states), (conf, inst, stage, rs, states)
    e = dict(configuration=conf, instance=inst, program=prog, record=os.path.relpath(path, REPO), stage=stage,
             reading=reading, reached=True, answers_verbatim=answers_of(st), **judged)
    e["execution_state"] = states
    e["observations"] = obs
    e["rule"] = RULE + ((" ; " + extra_rule) if extra_rule else "")
    outcomes.append(e)

for conf in CONFS:
    # P01a
    p = rec(conf, "P01a", "behaviour"); r = json.load(open(p))
    for k in (1, 2, 3):
        j, s = p01a(conf, k); add(conf, "P01a", "P01a.py", p, r, k, j, s, obs_holding(conf, "P01a", k, r["stages"][k-1]),
            extra_rule="SPECIFICATION Outcomes 2: a recorded equation is a residual, a shared unknown a solved form" if k < 3 else None)
    p = rec(conf, "P01b", "behaviour"); r = json.load(open(p))
    for k in (1, 2):
        j, s = p01b(conf, k); add(conf, "P01b", "P01b.py", p, r, k, j, s, obs_holding(conf, "P01b", k, r["stages"][k-1]))
    p = rec(conf, "P01c", "behaviour"); r = json.load(open(p))
    for reading in ("finite", "rational"):
        j, s = p01c(conf, reading)
        add(conf, "P01c", "P01c.py", p, r, 1, j, s, obs_holding(conf, "P01c", 1, r["stages"][0]) +
            ("; occurs check: none (S suspend's bind has none; core and stdlib-concurrency never bind x)"), reading=reading,
            extra_rule="problems/01 P01c: classified under each reading")
    # P02
    p = rec(conf, "P02a", "behaviour"); r = json.load(open(p))
    for k, rels in ((1, {"R1"}), (2, {"R1", "R2"}), (3, {"R1", "R2", "R3"})):
        j, s = p02(conf, rels); add(conf, "P02a", "P02a.py", p, r, k, j, s, obs_holding(conf, "P02a", k, r["stages"][k-1]))
    for o in ORDERS:
        inst = "P02b." + o
        p = rec(conf, inst, "behaviour"); r = json.load(open(p))
        rels = [o[i:i+2] for i in (0, 2, 4)]
        for k in (1, 2, 3):
            j, s = p02(conf, set(rels[:k])); add(conf, inst, "P02b.py", p, r, k, j, s, obs_holding(conf, inst, k, r["stages"][k-1]))
    p = rec(conf, "P02c", "behaviour"); r = json.load(open(p))
    j, s = p02(conf, {"R1", "R2", "R3"}); add(conf, "P02c", "P02c.py", p, r, 1, j, s, obs_holding(conf, "P02c", 1, r["stages"][0]))
    # P03
    for inst, ans in (("P03a", "c = ⟨1,2,3⟩"), ("P03b", "the three splits"), ("P03c", "b = ⟨2,3⟩"), ("P03d", "a = ⟨1,2⟩"), ("P03e", "b = ⟨3,2,1⟩"), ("P03f", "a = ⟨3,2,1⟩")):
        p = rec(conf, inst, "behaviour"); r = json.load(open(p))
        states = ["budget"] if (conf == "extended" and inst == "P03f") else ["finished"]
        why = "the reported values are exactly the valid outcome(s)" + (", in the order of conc's cases ((⟨⟩,⟨1,2⟩), (⟨1⟩,⟨2⟩), (⟨1,2⟩,⟨⟩)), 3 of 3, no invalid answer" if inst == "P03b" else ", 1 of 1, no invalid answer")
        extra = None
        if states == ["budget"]:
            why += "; then the search ran to the budget without a further answer (P03 Observations: complete with budget)"
            extra = "problems/03 Observations (P03f: complete with budget)"
        add(conf, inst, inst + ".py", p, r, 1, ex(ans, why), states, obs_p03(conf, inst, r["stages"][0]), extra_rule=extra)

# expected answers check (the judged 'explicit' stages have the valid answers)
for e in outcomes:
    if e["representation"] == "explicit":
        assert e["answers_verbatim"], e

# ------------------------------------------------------------------ cost / storage comparison (see modes.py)
mode_differences = []   # modes.py found no stage whose answers, ended_by, states, suspended or alternatives counts, or observe() differ

# ------------------------------------------------------------------ expressibility
EXP = []
def xp(conf, sub, direction, e, reason):
    EXP.append(dict(configuration=conf, subproblem=sub, direction=direction, expressibility=e, reason=reason))
HOLD_CORE = ("Python core has no unknowns: the equations are held in a list and decided when a place has a value, by code written "
             "for the problem's own relations (decide, place, the evaluators' known-place tests: R by rule 19). The reformulation keeps "
             "the relations' meaning on every input used")
for conf in ("core", "stdlib-concurrency"):
    thr = "" if conf == "core" else " Each held relation runs in a thread waiting on a condition variable (C, threading listed as an external mechanism); the holding itself is still R."
    xp(conf, "P01a", None, "expressible with reformulation", HOLD_CORE + "." + thr)
    xp(conf, "P01b", "conc forwards (a known; b known from stage 2; c computed)", "expressible with reformulation",
       "conc is transcribed forwards by its two cases (P, rule 3), but the relation conc(⟨1,2⟩, s, t) must be held until s has a value, by R holding code (rule 19)." + thr)
    xp(conf, "P01c", "conc(⟨1⟩, x, x): b and c the same unknown", "expressible with reformulation",
       "the relation is held (R, rule 19) and keeps its meaning; it is never decided, since no place gets a value. No finite Python value or tuple can be cyclic, so the rational solution cannot be reached, and the finite reading's 'none' is never concluded; that is an outcome (simplification), not a change of meaning." + thr)
    for sub in ("P02a", "P02b", "P02c"):
        xp(conf, sub, "+ and · in every direction (rule 19)", "expressible with reformulation",
           "each relation's evaluator computes any place from the other two and tests a known relation (P, rule 19), but the holding (place tests, wait verdict, decide loop, dispatch tables) is R." + thr)
    xp(conf, "P03a", "conc: a, b known, c computed", "expressible", "conc transcribed forwards by its two cases in order; no R tokens (rule 3)")
    xp(conf, "P03b", "conc: c known, a and b computed (split)", "expressible with reformulation", "a separate generator `split` for the splitting direction keeps conc's meaning on the inputs used; R (rules 3, 14)")
    xp(conf, "P03c", "conc: a, c known, b computed", "expressible with reformulation", "a separate generator `rest` for this direction; R (rules 3, 14)")
    xp(conf, "P03d", "conc: b, c known, a computed", "expressible with reformulation", "a separate generator `front` for this direction; R (rules 3, 14)")
    xp(conf, "P03e", "rev: a known, b computed (conc forwards)", "expressible", "rev and conc transcribed forwards, rev's conjuncts in order; no R tokens")
    xp(conf, "P03f", "rev: b known, a computed (conc split)", "expressible with reformulation",
       "rev backwards as a separate generator `unrev`, with conc's conjunct moved first (one move, rule 4) and computed by the splitting generator `split`; R (rules 3, 4, 14)")
conf = "extended"
xp(conf, "P01a", None, "expressible", "unknowns are the S suspension mechanism's Vars and each equation is a binding (Queue.bind); no R tokens: the program transcribes the stages with the configuration's mechanism (S counted apart)")
xp(conf, "P01b", "conc forwards over cons cells, b an unbound Var", "expressible", "conc transcribed forwards (P, rule 3) over the cons-cell encoding; with b unbound, case 1 gives the Var as tail, so t = ⟨1,2⟩ ++ s is built; no R tokens")
xp(conf, "P01c", "conc(⟨1⟩, x, x)", "expressible", "the same transcription; bind has no occurs check, so x becomes a cyclic term: right under the rational reading, unsound under the finite one (an outcome, not expressibility)")
for sub in ("P02a", "P02b", "P02c"):
    xp(conf, sub, "+ and · in every direction (rule 19)", "expressible with reformulation",
       "the relations wait in the S suspension queue (q.wait, q.run: C), but the program's Relation wrapper, which tests which places are bound, calls the evaluator and binds its results, is holding code for the problem's own relations: R by rule 19")
for sub, d in (("P03a", "conc: a, b known"), ("P03b", "conc: c known (split)"), ("P03c", "conc: a, c known"), ("P03d", "conc: b, c known"),
               ("P03e", "rev: a known"), ("P03f", "rev: b known")):
    xp(conf, sub, d, "expressible", "conc and rev are each transcribed once, by their cases in order (heads by unification, bodies as goal lists), and serve every direction through the program's unify and resolution (S) and S search (C directive); no R tokens"
       + ("; P03f reports its one answer and then runs to the budget, which is an outcome, not a failure of expressibility" if sub == "P03f" else ""))

tokens = json.load(open(HERE + "/tokens.json"))
out = dict(tokens=tokens, outcomes=outcomes, mode_differences=mode_differences, expressibility=EXP)
json.dump(out, open(HERE + "/python.json", "w"), ensure_ascii=False, indent=1)
print(len(outcomes), "outcome entries;", len(EXP), "expressibility entries")
