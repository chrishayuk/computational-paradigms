"""Classify every stage of every behaviour record of P05-P08 (SWI-Prolog), and the
cost/storage differences. Read-only on the repository; writes outcomes.json."""
import json, glob, os, re, sys
ROOT = "./results/swi-prolog"
OUT = os.path.dirname(os.path.abspath(__file__))

def load(path):
    r = json.load(open(path)); st = {}
    for s in r["stages"]:
        a = s["attempts"][-1]; c = a["computations"][0]; q = c["queries"][0]
        src = c["steps"].get("restart_cost_source") or ""
        nr = re.search(r"stopped by (budget|the end of the process) during stage (\d+), before stage (\d+) was posed", src)
        st[s["stage"]] = dict(
            attempts=len(s["attempts"]), posed=a["posed"]["how"], reason=a["posed"].get("reason"),
            answers=[x["verbatim"] for x in q["answers"]], ended_by=q["ended_by"], collected=q.get("collected_on"),
            states=c["execution_state"]["states"], err=c["execution_state"].get("error_verbatim"),
            observe=a["observe"]["raw"], susp=c["suspended"]["items"], notes=a.get("notes") or [],
            src=src, notreached=nr, safety=a["safety_limit"]["hit"], print=a.get("print") or "")
    return r, st

def ans(d):
    if d["answers"]: return " ; ".join(x.strip().rstrip(".").replace("\n", " ") for x in d["answers"])
    return "(no answer; print() gave '%s')" % d["print"].strip().replace("\n", " ")

def E(conf, inst, prog, rec, stage, **kw):
    e = dict(configuration=conf, instance=inst, program=prog, record=rec, stage=stage, reached=True,
             semantic=None, representation=None, simplification=None, identical_to_posed=None, residual_size=None,
             execution_state=None, residual_equivalence=None, observations=None, rule=None)
    e.update(kw); return e

def not_reached(conf, inst, prog, rec, stage, d, fault, extra=""):
    m = d["notreached"]
    why = ("the replay of stages 1..%d stopped in stage %s (%s), before stage %d was posed" % (stage - 1, m.group(2), "the posed conjunction failed there" if m and m.group(1) != "budget" else "the error raised there", stage)) if m else "the replay did not reach this stage (harness_faults)"
    if m and m.group(1) == "budget" and d["err"]:
        why += "; the record's restart_cost_source says 'stopped by budget', but the attempt's error is %s, not a budget" % d["err"].split("\n")[0]
    return E(conf, inst, prog, rec, stage, reached=False, semantic="not reached", representation=None,
             execution_state=["not reached"], observations="Not reached: " + why + ". The reposed run's own report was '%s' (%s), which is the earlier stage's outcome, not this stage's (AMENDMENTS.md 3.2). %s" % (ans(d), d["ended_by"], extra),
             rule="AMENDMENTS.md 3.2 (never reached is not reached, with what stopped the run)" + ("; brief: an INVALID record whose replay did not reach the stage" if fault else ""))

def sess_note(conf, d):
    if conf != "session": return ""
    n = "; ".join(d["notes"])
    return (" Session: answers collected on %s; posed %s. %s" % (d["collected"], d["posed"], ("Incremental computation: " + n + ".") if n else "")).rstrip()

UNK = {"P05": ["X"], "P06a": ["X"], "P06b": ["X"], "P06c": ["X"], "P06d": ["D"], "P06e1": [], "P06e2": [], "P06e3": ["P"],
       "P07a": ["X", "Y", "Z"], "P07b": ["X", "Y"], "P07c": ["X", "Y"], "P07d": ["W", "U", "V"], "P07e": ["W", "U", "V"], "P07f": ["X", "Y"], "P07g": ["X"],
       "P08a": ["A", "B", "C", "X", "Y", "Z"], "P08b": ["A", "B", "X", "Y", "Z"], "P08c": ["B"]}
def unknowns_repr(inst, d):
    names = UNK.get(inst[:3] if inst.startswith("P05") else inst.split(".")[0], [])
    txt = d["answers"][-1] if d["answers"] else d["observe"]
    txt = txt.strip().rstrip(".").strip()
    if not txt: return "none held (nothing is held after failure)" if not d["err"] else "none held"
    # split top-level ', ' / ',\n' separated items
    items, depth, cur = [], 0, ""
    for ch in txt:
        if ch in "([{": depth += 1
        if ch in ")]}": depth -= 1
        if ch == "," and depth == 0: items.append(cur.strip()); cur = ""
        else: cur += ch
    items.append(cur.strip())
    binds, goals = {}, []
    for it in items:
        m = re.match(r"^([A-Z]\w*) = (.*)$", it, re.S)
        if m and m.group(1) in names: binds[m.group(1)] = m.group(2).strip()
        elif it and it != "true": goals.append(it)
    def final(n, seen=()):
        v = binds.get(n)
        if v is None: return None
        if v in names and v not in seen: return final(v, seen + (n,)) or ("=" + v)
        return v
    out = []
    for n in names:
        v = final(n)
        g = [x for x in goals if re.search(r"\b%s\b" % n, x)]
        if v is None:
            if g: out.append("%s: attributed variable, residual %s" % (n, " , ".join(g)))
            elif any(re.search(r"\b%s\b" % n, x) for x in binds.values()): out.append("%s: free variable occurring in another unknown's term" % n)
            else: out.append("%s: free (unbound) variable" % n)
        elif v.startswith("="): out.append("%s: identified with %s (free)" % (n, v[1:]))
        else:
            fv = [x for x in names if re.search(r"\b%s\b" % x, v)]
            if fv: out.append("%s: bound to %s, a term containing unknowns" % (n, v))
    return "; ".join(out) or "none (all bound to values)"

def common(conf, d, alts, susp_txt, withdrawn="none", manual="none"):
    d = dict(d); d["_unk"] = unknowns_repr(CUR_INST[0], d)
    return ("Answers: %s (ended_by %s). Unknowns left unknown: %s. Alternatives: %s. Suspended work: %s. Withdrawn: %s. Manual actions: %s.%s"
            % (ans(d), d["ended_by"], d.get("_unk", "none"), alts, susp_txt, withdrawn, manual, sess_note(conf, d)))

def susp(d):
    s = d["susp"]
    if not s: return "nothing held (the query failed back past its start)"
    parts = ["%s attributed variable(s), %s residual goal(s)" % (s.get("attributed_variables"), s.get("residual_goals"))]
    if s.get("engine_waiting_for_next_stage"): parts.append("%d engine waiting in h_wait/0 (the pending application)" % s["engine_waiting_for_next_stage"])
    return "; ".join(parts)

def backtrack_alts(d, conf):
    if conf == "session" and d["collected"] == "separate-run":
        return "answers enumerated by backtracking on a separate run; the incremental engine holds the first answer with its open choicepoints (kept for backtracking, not live at once)"
    return "enumerated one at a time by backtracking; none held after the last answer; in a reposed configuration the computation ends with the process"

out, modes = [], []
CUR_INST = [None]
recs = sorted(glob.glob(os.path.join(ROOT, "*/P0[5-8]/raw/*.behaviour.*.json")))
for path in recs:
    rel = "results/swi-prolog/" + os.path.relpath(path, ROOT)
    r, S = load(path)
    conf = r["run"]["configuration"]; inst = r["run"]["instance"]; prog = r["run"]["program"]["path"].split("/")[-1]
    fault = path.endswith(".INVALID.json"); CUR_INST[0] = inst
    ents = []
    for k in sorted(S):
        d = S[k]
        if d["notreached"] or (fault and any("stage %d attempt" % k in f and "did not reach" in f for f in r["harness_faults"])):
            nr_e = not_reached(conf, inst, prog, rel, k, d, fault)
            if fault: nr_e["harness_fault"] = True
            ents.append(nr_e); continue
        st = d["states"]; A = d["answers"]; e = None
        err = d["err"].split("\n")[0] if d["err"] else None
        # ---------------- P05 ----------------
        if inst == "P05a":
            exp = {1: ["1", "2", "3"], 2: ["2", "3"], 3: ["3"]}[k]
            got = [re.sub(r"[^0-9]", "", a) for a in A]
            wd = {1: "none", 2: "X = 1 (reported at stage 1) is withdrawn: absent from stage 2's answers; %s" % ("the engine backtracked past it into stage 1's member/2" if conf == "session" else "shown only by recomputation, the stage being reposed"),
                  3: "X = 2 (reported at stages 1-2) is withdrawn: absent from stage 3's answers; %s" % ("dif/2 failed on it and the engine backtracked into stage 1" if conf == "session" else "shown only by recomputation (reposed)")}[k]
            assert got == exp, (path, k, A)
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                  residual_equivalence="explicit values x ∈ {%s}, equal to the valid outcomes" % ", ".join(exp),
                  observations=common(conf, d, backtrack_alts(d, conf) + "; problem-defined alternatives (values of x held): %d, not counted by the program (h_held/2 not called; unavailable)" % len(exp), susp(d), wd),
                  rule="SPECIFICATION Outcomes 1-3")
        elif inst == "P05b":
            if k == 1:
                if err:
                    e = E(conf, inst, prog, rel, k, semantic="none reported", representation=None, execution_state=st,
                          observations="x > 1 on an unknown is an error in plain Prolog: %s. observe() read 'true' (no binding held). %s" % (err, common(conf, d, "none", susp(d))),
                          rule="SPECIFICATION Outcomes 1 (none reported), 3 (error, verbatim)")
                elif "2..sup" in A[0]:
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=False,
                          residual_size="1 relation (X in 2..sup), 1 occurrence of x; input 1 relation (x > 1), 1 occurrence", execution_state=st,
                          residual_equivalence="X in 2..sup over the integers is {x ∈ ℤ : x ≥ 2} = {x ∈ ℤ : x > 1}; comparisons hold only of integers (SPECIFICATION, Arithmetic), so this is exactly the valid outcome; no domain was imposed",
                          observations="The comparison is held as a clpfd domain, transformed from x > 1 to the interval 2..sup (held, reported as a residual). " + common(conf, d, "none (deterministic)", susp(d)),
                          rule="SPECIFICATION Outcomes 1-2, simplification; AMENDMENTS 3.4 (no domain imposed)")
                else:
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
                          residual_size="1 relation (freeze(X, X>1)), 1 occurrence of x; input 1 relation, 1 occurrence", execution_state=st,
                          residual_equivalence="freeze(X, X>1) holds x > 1 until x is bound, and then tests it; it denotes {x : x > 1}, which (> holding only of integers) is the valid outcome. A non-integer binding would raise a type error rather than fail; no stage binds one",
                          observations="The comparison is held (delayed by freeze/2), unchanged. " + common(conf, d, "none", susp(d)),
                          rule="SPECIFICATION Outcomes 1-2")
            else:
                assert [re.sub(r"[^0-9]", "", a) for a in A] == ["2", "3"], (path, A)
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                      residual_equivalence="explicit x ∈ {2, 3}, the valid outcomes",
                      observations="The held comparison was resumed by pick's bindings (%s). " % ("clpfd domain check" if conf in ("constraints", "session") else "freeze/2 woken") + common(conf, d, backtrack_alts(d, conf) + "; problem-defined alternatives: 2, not counted by the program (unavailable)", susp(d)),
                      rule="SPECIFICATION Outcomes 1-3")
        elif inst == "P05c":
            if k == 1:
                assert len(A) == 3
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                      residual_equivalence="explicit x ∈ {1, 2, 3}",
                      observations=common(conf, d, backtrack_alts(d, conf) + "; problem-defined alternatives: 3, not counted (unavailable)", susp(d)), rule="SPECIFICATION Outcomes 1-3")
            elif k == 2:
                assert not A
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                      residual_equivalence="no solutions reported (false.), and the valid outcome is none: the empty set reported as empty (answer completeness: reported that there are none, yes)",
                      observations="The empty outcome is reported as failure ('false.'): x = 4 fails against every pick. " + common(conf, d, "none", susp(d), "X = 1, 2, 3 (stage 1) all withdrawn, shown as failure") + (" The engine's computation failed, so nothing is left to receive stage 3 (the harness starts a new engine)." if conf == "session" else ""),
                      rule="SPECIFICATION Outcomes 1 (complete; the empty set reported as empty)")
        # ---------------- P06 ----------------
        elif inst in ("P06a", "P06c"):
            if k == 1:
                if A and "dif" in A[0]:
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
                          residual_size="1 relation (dif(X, 1)), 1 occurrence of x; input 1 relation (not (x = 1)), 1 occurrence", execution_state=st,
                          residual_equivalence="dif(X, 1) denotes every value other than 1, over all values (not restricted to integers): the valid outcome",
                          observations="The negation is held as a condition (dif/2), not decided. " + common(conf, d, "none (deterministic)", susp(d)), rule="SPECIFICATION Outcomes 1-2; P06 observations")
                else:
                    assert not A
                    e = E(conf, inst, prog, rel, k, semantic="unsound", representation="explicit", execution_state=st,
                          residual_equivalence="reports no solution (false.) where every value other than 1 is valid",
                          observations="\\+ X = 1 is decided at once, at stage 1's first goal after reading the constant (X unifies with 1, so the negation fails): reports no solution. P06a/P06c: unsound by the problem file. " + common(conf, d, "none", susp(d)),
                          rule="P06 observations (a system that reports no solution for P06a is unsound)")
            else:
                if inst == "P06a":
                    assert A and "X = 2" in A[0]
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="X = 2",
                          observations="dif/2 resumed and discharged by x = 2. P06a and P06b give the same outcome. " + common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1-3")
                else:
                    assert not A
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                          residual_equivalence="none reported (false.), valid none: the inconsistency detected when x = 1 woke dif/2",
                          observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1")
        elif inst == "P06b":
            assert A and "X = 2" in A[0]
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="X = 2",
                  observations=("The negation is decided on a known value. " if k == 2 else "") + common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1-3")
        elif inst == "P06d":
            assert A and "[1, 3]" in A[0]
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="D = [1, 3]",
                  observations=common(conf, d, ("one answer, then the request for more failed" if d["answers"][0].endswith(" ") else "one answer without choicepoints (tabled)"), susp(d)), rule="SPECIFICATION Outcomes 1-3")
        elif inst == "P06e1":
            assert A and A[0].startswith("true")
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="true",
                  observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1")
        elif inst == "P06e2":
            assert not A
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="false (no answer), valid false",
                  observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1")
        elif inst == "P06e3":
            assert A and A[0].startswith("P = brown")
            e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st, residual_equivalence="P = brown, the only valid outcome",
                  observations="p and k are both bound (student(P), maths(K)) before \\+ takes(P, K) is decided. " + common(conf, d, "one answer" + (", then the request for more failed" if d["answers"][0].endswith(" ") else ", no choicepoint (tabled)"), susp(d)), rule="SPECIFICATION Outcomes 1")
        # ---------------- P07 ----------------
        elif inst.startswith("P07"):
            sub = inst[:4]
            if err:
                held = d["observe"].strip()
                extra = ""
                if held and held != "true":
                    extra = " observe() read the bindings held when the error reached the harness: '%s'. They are recorded as an observation, not as the report (see notes: an error is classed none reported%s)." % (held.replace("\n", " "), "; U = 0 is a binding made by factor/3's head pattern, not the problem's information" if "U = 0" in held else "")
                e = E(conf, inst, prog, rel, k, semantic="none reported", representation=None, execution_state=st,
                      observations="Error, verbatim: %s.%s Mechanism: the relations are evaluated one at a time in one direction (is/2), and the first one with two unknown places raises an instantiation error. %s" % (err, extra, common(conf, d, "none", susp(d))),
                      rule="SPECIFICATION Outcomes 1 (none reported), 3 (error)")
            elif sub == "P07a" or sub == "P07d":
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                      residual_equivalence=ans(d), observations="Solved by %s. " % ("clpfd propagation" if conf in ("constraints", "session") else "one relation at a time as its places become known (when/2 wakes the evaluator)") + common(conf, d, "none", susp(d)),
                      rule="SPECIFICATION Outcomes 1-3")
            elif sub == "P07e":
                assert not A
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="explicit", execution_state=st,
                      residual_equivalence="no solution (false.), valid none: the inconsistency is detected (15 is not a multiple of 2); no rational answer is given",
                      observations="Detected by %s. " % ("clpfd propagation on W*2 #= 15" if conf in ("constraints", "session") else "the woken evaluator: 15 mod 2 =\\= 0") + common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1; P07 observations")
            elif sub == "P07b":
                ident = "when(" in A[0]
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=ident,
                      residual_size="2 relations, 4 occurrences of unknowns; input 2 relations (x + y = 10, x − y = 4), 4 occurrences",
                      execution_state=st,
                      residual_equivalence=("4+Y#=X and X+Y#=10 over the integers: x = y + 4, so 2y + 4 = 10, y = 3, x = 7; exactly the valid outcome. The smaller x = 7, y = 3 exists and was not reached" if not ident else
                                            "the two held goals decide x + y = 10 (sum_known) and x − y = 4 (diff_known) once a place is known; together they denote {(7, 3)}, the valid outcome; x = 7, y = 3 is smaller and was not reached"),
                      observations=("clpfd holds the two linear relations without eliminating (x − y = 4 is rewritten 4+Y#=X). " if not ident else "Each relation is held by when/2 until one of its unknown places is known. ") + common(conf, d, "none", susp(d)),
                      rule="SPECIFICATION Outcomes, simplification (the P07b example); check_residuals.py")
            elif sub == "P07c":
                ident = True
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reduced", identical_to_posed=True,
                      residual_size="1 relation, 2 occurrences; input 1 relation, 2 occurrences", execution_state=st,
                      residual_equivalence="x + y = 10 held over the integers (no domain imposed): every integer pair with x + y = 10",
                      observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes, simplification (the P07c example)")
            elif sub == "P07f":
                e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="inconsistency undetected", identical_to_posed=True,
                      residual_size="2 relations, 4 occurrences; input 2 relations, 4 occurrences", execution_state=st,
                      residual_equivalence="x + y = 10 and x + y = 11 denote the empty set; held without being reported as none",
                      observations="Inconsistency not detected (%s). " % ("clpfd does not compare the two sums over unbounded domains" if conf in ("constraints", "session") else "each relation waits for a known place") + common(conf, d, "none", susp(d)),
                      rule="SPECIFICATION Outcomes, simplification (the P07f example); P07 observations")
            elif sub == "P07g":
                if not A:
                    e = E(conf, inst, prog, rel, k, semantic="unsound", representation="explicit", execution_state=st,
                          residual_equivalence="reports no solution (false.) where x = 3 and x = −3 are valid",
                          observations="product(X, X, 9) with X unknown reaches factor(9, X, X), whose first head binds X = 0 and commits (cut); 9 =:= 0 fails, so the call fails: no solution reported, neither root found. " + common(conf, d, "none", susp(d)),
                          rule="SPECIFICATION Outcomes 1 (reports none where valid outcomes exist)")
                elif "when(" in A[0]:
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=True,
                          residual_size="1 relation (x · x = 9), 2 occurrences of x; input 1 relation, 2 occurrences", execution_state=st,
                          residual_equivalence="the held product_known(X, X, 9) tests X*X =:= 9 once X is bound: it denotes {3, −3}, the valid outcomes; neither root is found; the explicit x = 3 ; x = −3 is smaller",
                          observations="Neither solution found; the relation is held. " + common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes, simplification; P07 observations")
                else:
                    e = E(conf, inst, prog, rel, k, semantic="complete", representation="residual", simplification="reducible", identical_to_posed=False,
                          residual_size="1 relation (X in -3\\/3), 1 occurrence; input 1 relation (x · x = 9), 2 occurrences", execution_state=st,
                          residual_equivalence="X in -3\\/3 is exactly {−3, 3}, the valid outcomes; both solutions are found, as a domain, not labelled; the explicit form (two answers, no relation left) is smaller (see notes)",
                          observations="Both solutions found, by clpfd propagation, as the domain -3\\/3 (no labeling). " + common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes, simplification; P07 observations")
        # ---------------- P08 ----------------
        elif inst.startswith("P08"):
            sub = inst
            failv = "unknown-fail" in prog
            def p08(closed, opn, **kw):
                return E(conf, inst, prog, rel, k, semantic="closed: %s; open: %s" % (closed, opn), semantic_closed=closed, semantic_open=opn, **kw)
            if k == 1:
                if sub in ("P08a", "P08b"):
                    assert A and "A = [X, Y, Z]" in A[0]
                    e = p08("complete", "complete", representation="solved form", execution_state=st, residual_equivalence="a = ⟨x, y, z⟩, x, y, z free",
                            observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1-2; P08 readings")
                else:
                    assert A and A[0].startswith("true")
                    e = p08("complete", "complete", representation="solved form", execution_state=st, residual_equivalence="true: conc defined, b free, nothing to decide",
                            observations=common(conf, d, "none", susp(d)), rule="SPECIFICATION Outcomes 1-2")
            elif err:
                e = p08("none reported", "none reported", representation=None, execution_state=st,
                        observations="State 3 of P08 (a reference to a definition that is unavailable, an error): %s. observe() read '%s' when the error reached the harness. Can be told apart from failure: yes (an error, not 'false.'). %s" % (err, d["observe"].strip().replace("\n", " "), common(conf, d, "none", susp(d))),
                        rule="SPECIFICATION Outcomes 1, 3 (error); P08 (state 3)")
            elif not A and not d["susp"].get("engine_waiting_for_next_stage") and "suspended" not in st:
                e = p08("complete", "unsound", representation="explicit", execution_state=st,
                        residual_equivalence="no solutions (false.): the closed reading's valid outcome (none); under the open reading valid outcomes exist, so reporting none is unsound",
                        observations="State 1 of P08 (an undefined relation is false): with unknown = fail the call of rev/2 fails. Cannot be told apart from failure. " + common(conf, d, "none", susp(d)) +
                        (" The engine's computation failed, so the next stage needs a new engine (a reposed run)." if conf == "session" else ""),
                        rule="P08 readings (a system that reports no solutions is unsound under open, complete under closed); rule 11 (the flag is C)")
            elif "suspended" in st and not A:
                obs = d["observe"].strip().replace("\n", ", ")
                if sub in ("P08a", "P08b"):
                    eqs = "a = ⟨x, y, z⟩" if k == 2 else "x = y, a = ⟨y, y, z⟩"
                    size = "the equations (%s, solved) and 1 pending application rev(a, b), held unchanged; input: the same equations and rev(a, b)" % eqs
                else:
                    size = "1 pending application rev(⟨1, 2⟩, b), held unchanged; b free; input: rev(⟨1, 2⟩, b)" + (" and rev case 1" if k == 3 else "")
                e = p08("unsound", "complete", representation="residual", simplification="reduced", identical_to_posed=True, residual_size=size, execution_state=st,
                        residual_equivalence="observe(): '%s', with the application held in the engine (waiting clause, h_wait/0). Under the open reading this is the valid outcome (the equations, b free, rev(a, b) pending); under the closed reading the valid outcome is none, and this report denotes solutions" % obs,
                        observations="State 4 of P08 (a computation awaiting its definition), by the session S mechanism: the call of the undefined rev/2 is given a waiting clause and the engine waits. Shown as an engine waiting in h_wait/0 with no answer; can be told apart from failure: yes. %s%s"
                                     % ("At stage 3 of P08c the waiting clause found no clause of rev/2 whose head unifies with rev([1, 2], B) (case 1 is rev([], [])), so the application stays held, not failed and not resumed with the partial definition. " if sub == "P08c" and k == 3 else "", common(conf, d, "none", susp(d))),
                        rule="P08 (open reading: held pending application is complete / residual; closed reading: valid none)")
            else:
                # answers after definition arrived
                a0 = A[0]
                if sub == "P08a":
                    rep = {4: "solved form", 5: "solved form", 6: "explicit"}[k]
                    exp = {4: "x = y, a = ⟨y, y, z⟩, b = ⟨z, y, y⟩", 5: "x = y = z, a = b = ⟨z, z, z⟩", 6: "x = y = z = 42, a = b = ⟨42, 42, 42⟩, c = ⟨42, 42⟩"}[k]
                else:
                    rep, exp = "explicit", "b = ⟨2, 1⟩"
                e = p08("complete", "complete", representation=rep, execution_state=st, residual_equivalence="%s; equal to the valid outcome under both readings (%s)" % (ans(d), exp),
                        observations=(("Stage 4 resumed the pending application in the same computation (no restart, no intervention): the waiting clause found rev/2's own clauses, removed itself and called rev. " if k == 4 else "") +
                                      ("Under the closed reading the earlier valid conclusion 'none' (stages 2-3) is withdrawn by the definition's arrival; this system never reported it (it held the application), so no reported conclusion is withdrawn. " if k == 4 and sub == "P08a" else "") +
                                      common(conf, d, "none", susp(d))),
                        rule="SPECIFICATION Outcomes 1-2; P08 readings")
        if e is None:
            raise SystemExit("unclassified %s stage %d %r" % (rel, k, d))
        if fault: e["harness_fault"] = True
        ents.append(e)
    out += ents

json.dump(out, open(os.path.join(OUT, "outcomes.json"), "w"), indent=1, ensure_ascii=False)
from collections import Counter
print(len(out), Counter(e["semantic"] for e in out))
