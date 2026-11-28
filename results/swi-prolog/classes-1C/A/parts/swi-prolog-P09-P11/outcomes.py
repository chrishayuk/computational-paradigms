# Outcome classes of the behaviour runs of P09-P11, by hand, written as data.
# Reads the records only to take their paths and to check the facts each
# class relies on (answers, states), so that a class cannot silently disagree
# with its record.
import json, glob, os

REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
RES = REPO + "/results/swi-prolog"
CONFIGS = ["plain", "tabling", "coroutines", "constraints", "session"]

def rec(config, instance, mode="behaviour"):
    prob = instance[:3]
    ps = sorted(glob.glob(f"{RES}/{config}/{prob}/raw/{instance}.{mode}.*.json"))
    assert len(ps) == 1, (config, instance, mode, ps)
    return ps[0]

def facts(path):
    d = json.load(open(path))
    out = {}
    for st in d["stages"]:
        a = st["attempts"][-1]
        for c in a["computations"]:
            out[(st["stage"], c["id"])] = {
                "answers": [x["verbatim"] for q in c["queries"] for x in q["answers"]],
                "states": c["execution_state"]["states"],
                "ended_by": [q["ended_by"] for q in c["queries"]],
                "collected_on": [q["collected_on"] for q in c["queries"]],
                "posed": a["posed"]["how"], "reason": a["posed"]["reason"],
                "observe": a["observe"]["raw"],
                "susp": c["suspended"].get("at_boundary"),
            }
    return d, out

OUT = []

def add(config, instance, stage, sem, rep, simp, ident, size, state, equiv, obs, rule,
        computation="main", reading=None, check=None, effects=None, prog=None):
    path = rec(config, instance)
    d, f = facts(path)
    fx = f[(stage, computation)]
    if check is not None:
        assert check(fx), (config, instance, stage, computation, fx)
    assert sorted(fx["states"]) == sorted(state), (config, instance, stage, fx["states"], state)
    e = {
        "configuration": config, "instance": instance,
        "program": prog or (instance.split(".")[0] + ".pl"),
        "record": os.path.relpath(path, REPO),
        "stage": stage, "computation": computation, "reading": reading,
        "reached": True, "semantic": sem, "representation": rep,
        "simplification": simp, "identical_to_posed": ident, "residual_size": size,
        "execution_state": state, "residual_equivalence": equiv,
        "observations": obs, "rule": rule, "harness_fault": False,
        "answers_verbatim": fx["answers"], "posed": f'{fx["posed"]}/{fx["reason"]}',
    }
    if effects is not None:
        e["effects"] = effects
    OUT.append(e)

ans = lambda *xs: (lambda fx: fx["answers"] == list(xs))
noans = lambda fx: fx["answers"] == []

SEQ = "sequential, not side by side (side_by_side false; harness README 2.2, QUESTIONS S5)"

# ===================================================================== P09a
for c in CONFIGS:
    for inst in ("P09a.AB", "P09a.BA"):
        order = "A then B" if inst.endswith("AB") else "B then A"
        if c == "tabling":
            add(c, inst, 1, "complete", "explicit", None, None, None, ["finished"],
                "valid outcome for A is none; the tabled loop/1 completed its table with no answer and the query failed ('false.'), which reports that there are none",
                f"A: loop(x) tabled; SLG completes the table of loop(_) with no answer and fails. Computations ran {SEQ}, {order}; B was reported whether A ran first or second, since A ends. No unknown left: x has no binding. No alternatives (0 choicepoints, storage), no suspended work.",
                "SPECIFICATION Outcomes 1 (complete; empty set reported as empty); P09a valid outcomes: none for A",
                computation="A", check=noans)
        else:
            add(c, inst, 1, "none reported", None, None, None, None, ["budget"],
                "valid outcome for A is none; nothing was reported before the budget ran out",
                f"A: loop(x) recurses to the budget (10^6 inferences, restated 1000009); x stays a free variable (observe: 'true'). Computations ran {SEQ}, {order}: in {'A then B, B ran only after A had exhausted its own budget' if order == 'A then B' else 'B then A, B was reported before A started'}. No alternatives or suspended work recorded at the budget.",
                "SPECIFICATION Outcomes 1 (none reported) and 3 (budget); P09a valid outcomes: none for A. Budget, not nontermination proved",
                computation="A", check=noans)
        add(c, inst, 1, "complete", "explicit", None, None, None, ["finished"],
            "b = <3, 2, 1> is the one valid outcome",
            f"B: rev(<1,2,3>, b) answered 'B = [3, 2, 1].' and exited without choicepoints. Its outcome does not depend on the order ({order}); it was not reported while A ran, since the computations ran {SEQ}. A's budget did not affect B (each has its own budget).",
            "SPECIFICATION Outcomes 1-3; P09a valid outcome for B",
            computation="B", check=ans("B = [3, 2, 1].\n\n"))

# ===================================================================== P09b
for c in CONFIGS:
    add(c, "P09b", 1, "complete", "explicit", None, None, None, ["finished"],
        "valid outcome for A is none; x = 1 and x = 2 failed and the query reported none ('false.')",
        f"A failed at once (7 inferences); its failure did not affect B. Ran {SEQ}.",
        "SPECIFICATION Outcomes 1 (complete, empty set reported as empty); P09b",
        computation="A", check=noans)
    add(c, "P09b", 1, "complete", "explicit", None, None, None, ["finished"],
        "y = 3 is the one valid outcome",
        "B answered 'Y = 3.' after A had failed: A's failure did not affect B.",
        "SPECIFICATION Outcomes 1-3; P09b", computation="B", check=ans("Y = 3.\n\n"))

# ===================================================================== P09c
for c in ("plain", "tabling"):
    a = "S = [1, 2, 3, 4, 5],\nTotal = 6 " if c == "plain" else "S = [1, 2, 3, 4, 5],\nTotal = 6.\n\n"
    add(c, "P09c", 1, "complete", "explicit", None, None, None, ["finished"],
        "total = 6, s = <1,2,3,4,5>: the one valid outcome",
        ("The producer gen ran to its end before the consumer sum3 was called (textual order, no coroutining): the consumer did not act on s before the producer finished. "
         + ("A retry was offered and failed ('false.'): 1 choicepoint at the answer (storage)." if c == "plain" else "Tabled: answer from the completed table, no choicepoint.")),
        "SPECIFICATION Outcomes 1-3", check=ans(a))
for c in ("coroutines", "constraints", "session"):
    add(c, "P09c", 1, "complete", "residual", "reducible", False,
        "1 relation held, gen(4, a), beside s = <1,2,3> ++ a and total = 6; input: 2 relations (gen(1, s), sum3(s, total))", ["suspended"],
        "Equivalent: gen(4, a) holds of exactly a = <4, 5> (case 2 twice, then case 1 at 6 > 5), so the residual denotes exactly s = <1,2,3,4,5>, total = 6. Reducible: the explicit s = <1,2,3,4,5> has no relation left",
        "The consumer acted on s before the producer finished: sum3's head bound s to <p,q,r> ++ m, which woke gen three times; the rest of the producer, gen(4, _A), is held as one frozen goal (1 attributed variable, 1 residual goal). The unknown tail of s is a free variable with a freeze attribute. No choicepoints. "
        + ("Session: answers collected in the engine (the instance's last stage)." if c == "session" else ""),
        "SPECIFICATION Outcomes 1-2 (residual, reducible: a smaller equivalent representation exists)",
        check=ans("S = [1, 2, 3|_A],\nTotal = 6,\nfreeze(_A, gen(4, _A)).\n\n"))

# ===================================================================== P09d
for c in ("plain", "tabling"):
    n = "1,000,004" if c == "plain" else "83,333"
    for rd in ("P09d1", "P09d2"):
        add(c, "P09d", 1, "none reported", None, None, None, None, ["budget"],
            ("finite reading: valid outcome none; nothing finished was reported, and total was never bound" if rd == "P09d1"
             else "stream reading: valid outcome total = 6; total was never computed, since sum3 was never called"),
            f"The producer genu ran first and never ended; at the budget s was bound to a prefix <1, ..., {n}> with a free tail (observe, read in the exception hook), and total was unbound: the consumer never acted on s. "
            + ("Tabling: each genu call is a new tabled variant; the budget stopped it with 1 open choicepoint (storage)." if c == "tabling" else "No choicepoints or suspended work.")
            + (" Producer state (P09d2): budget." if rd == "P09d2" else ""),
            "P09d1/P09d2 readings (problems/09); SPECIFICATION Outcomes 1, 3 (budget)", reading=rd, check=noans)
for c in ("coroutines", "constraints", "session"):
    add(c, "P09d", 1, "complete", "residual", "inconsistency undetected", False,
        "1 relation held, genu(4, a), beside s = <1,2,3> ++ a and total = 6; input: 2 relations", ["suspended"],
        "Finite reading: genu has no finite instance, so genu(4, a) denotes the empty set and the whole answer denotes no solution, equivalent to the valid outcome none; the system has not reported that there are none",
        "Answer 'S = [1, 2, 3|_A], Total = 6, freeze(_A, genu(4, _A))': total = 6 is bound, but conditional on a held producer goal that has no finite solution. The answer is not a finished outcome (state suspended). Read as total = 6 alone it would be unsound; read with its residual, as SPECIFICATION Outcomes 2 asks, it denotes the empty set. The consumer acted on s before the producer finished (sum3's head woke genu three times).",
        "P09d1 (problems/09); SPECIFICATION Outcomes 1 (complete, emptiness recorded by simplification) and 2",
        reading="P09d1", check=ans("S = [1, 2, 3|_A],\nTotal = 6,\nfreeze(_A, genu(4, _A)).\n\n"))
    add(c, "P09d", 1, "complete", "residual", "reduced", False,
        "1 relation held, genu(4, a), beside s = <1,2,3> ++ a and total = 6; input: 2 relations", ["suspended"],
        "Stream reading: genu read as the greatest relation; genu(4, a) holds of a = <4,5,6,...>, so the answer denotes total = 6 and s = <1,2,3,...>, the valid outcome. No smaller finite representation of the infinite s exists",
        "total = 6 computed while the producer is held, demand-driven and idle: producer state suspended (one frozen genu(4, _A), 1 attributed variable). The consumer acted on s before the producer finished.",
        "P09d2 (problems/09): complete for total whether or not the producer ever stops; producer state recorded separately",
        reading="P09d2", check=ans("S = [1, 2, 3|_A],\nTotal = 6,\nfreeze(_A, genu(4, _A)).\n\n"))

# ===================================================================== P09e
for c in ("plain", "tabling"):
    add(c, "P09e", 1, "none reported", None, None, None, None, ["error"],
        "valid outcomes: every integer pair with x = y + 1; nothing was reported",
        "is/2 raised an instantiation error at once (6 inferences): sum(y, 1, x) had neither y nor x known, so its last clause evaluated x - 1 with x unbound. The system neither held, enumerated nor reported a deadlock; the error is distinguishable from completion.",
        "SPECIFICATION Outcomes 1 (none reported), 3 (error, recorded verbatim in the record)", check=noans)
add("coroutines", "P09e", 1, "complete", "residual", "reducible", True,
    "2 relations held (sum_known(y, 1, x) and diff_known(x, 1, y), each under when/2); input: 2 relations, x = y + 1 and y = x - 1", ["suspended"],
    "Equivalent: each held goal, once woken, decides its relation over the integers (it computes the third place by is/2 or tests it), so the conjunction denotes {(x, y) : x = y + 1, y = x - 1} = {(x, y) : x = y + 1}, the valid outcomes. Reducible: x = y + 1 alone is equivalent, with one relation fewer",
    "The system suspended: two when/2 goals, one per relation (2 attributed variables, 2 residual goals), with conditions simplified to 'either place known'. Unknowns x and y are free variables with when attributes. State suspended, distinguishable from completion. It did not enumerate or report a deadlock.",
    "SPECIFICATION Outcomes 1-2; identical to the posed information: the two relations are held as posed, untransformed",
    check=lambda fx: fx["answers"][0].startswith("when(("))
for c in ("constraints", "session"):
    add(c, "P09e", 1, "complete", "residual", "reducible", False,
        "2 relations held, both Y+1 #= X; input: 2 relations", ["suspended"],
        "Equivalent: clpfd rewrote y = x - 1 as y + 1 = x, the same relation as x = y + 1 over the integers, so the residual denotes exactly the valid outcomes. Reducible: the two goals are the same constraint, and one alone is equivalent",
        "The solver held both constraints (2 attributed variables, 2 residual goals), without domains; nothing enumerated. State suspended, distinguishable from completion. Unknowns are clpfd variables with no domain bound."
        + (" Session: answers collected in the engine." if c == "session" else ""),
        "SPECIFICATION Outcomes 1-2 (reducible; not identical to the posed information, since the second relation was transformed)",
        check=ans("Y+1#=X,\nY+1#=X.\n\n"))

# ===================================================================== P10a
for c in CONFIGS:
    vals = {1: "B = 10.\n\n", 2: "B = 15.\n\n", 3: "B = 7.\n\n"}
    for k in (1, 2, 3):
        sep = (c == "session" and k < 3)
        add(c, "P10a", k, "complete", "explicit", None, None, None, ["finished"],
            f"b = {vals[k].split('=')[1].strip(' .\n')}, the valid outcome",
            ("b is held as one fact b(V), replaced natively by retractall/1 and assertz/1; the earlier value is not retrievable after it is replaced. "
             + ("Session: the stage was received into the engine; its answer was collected on a separate run of stages 1..k, the engine holding only the database fact (observe 'true')." if sep
                else ("Reposed: stages 1..k replayed in a fresh process, every replacement carried out." if (c != "session" and k > 1) else ""))),
            "SPECIFICATION Outcomes 1-3; P10a", check=ans(vals[k]))

# ===================================================================== P10b
for c in CONFIGS:
    if c in ("plain", "tabling"):
        add(c, "P10b", 1, "none reported", None, None, None, None, ["error"],
            "valid outcome d = 2 * b with neither valued; nothing was reported",
            "The query applied the standing relation d is 2 * b with b unknown: instantiation error. plain cannot hold the relation. Stage 2 was reposed after the error.",
            "SPECIFICATION Outcomes 1, 3 (error)", check=noans)
    elif c == "coroutines":
        add(c, "P10b", 1, "complete", "residual", "reduced", True,
            "1 relation held, d = 2 * b (as freeze(B, D is 2*B)); input: 1 relation", ["suspended"],
            "Equivalent: the held goal computes d = 2 * b as soon as b is known, and holds nothing else, so it denotes d = 2 * b over the integers with neither valued. Reduced: one relation, each unknown once",
            "b has no value (no fact b/1; the query left B unknown); the relation is held as one frozen goal on B (1 attributed variable). D is not propagated to B if D were given first (is/2 one way), which the stages never do.",
            "SPECIFICATION Outcomes 1-2", check=ans("freeze(B, D is 2*B).\n\n"))
    else:
        add(c, "P10b", 1, "complete", "residual", "reduced", True,
            "1 relation held, 2*B #= D; input: 1 relation", ["suspended"],
            "Equivalent: the clpfd constraint 2*B #= D is the relation d = 2 * b over the integers, with no domain imposed",
            "b has no value; the relation is held by the solver (2 attributed variables, 1 residual goal)."
            + (" Session: the answer was collected on a separate run of stage 1; the engine itself holds the asserted rule (the query, which applies it, runs only where answers are collected: QUESTIONS S4), observe 'true'." if c == "session" else ""),
            "SPECIFICATION Outcomes 1-2", check=ans("2*B#=D.\n\n"))
    for k, a in ((2, "B = 10,\nD = 20.\n\n"), (3, "B = 15,\nD = 30.\n\n"), (4, "B = 7,\nD = 14.\n\n")):
        obs = "d recomputed from b's current value by the standing rule each time the query applies it: 1 dependent value recomputed per replacement (P10b observation). "
        if c == "session" and k < 4:
            obs += "Session: answers on a separate run; the engine holds the database state only."
        elif c != "session":
            obs += "Reposed: every stage replayed" + (" (after the stage-1 error)" if (k == 2 and c in ("plain", "tabling")) else "") + "."
        add(c, "P10b", k, "complete", "explicit", None, None, None, ["finished"],
            "valid: " + a.replace("\n", " ").replace(".", "").strip(), obs,
            "SPECIFICATION Outcomes 1-3; P10b", check=ans(a))

# ===================================================================== P10c
for c in CONFIGS:
    for k, a in ((1, "B = 10.\n\n"), (2, "B = 10,\nD = 20.\n\n"), (3, "B = 15,\nD = 20.\n\n"), (4, "B = 7,\nD = 20.\n\n")):
        obs = ("d has no value yet: D left unbound (not shown), as the valid outcome says. " if k == 1 else "")
        obs += ("d computed once at stage 2 from b then, and not recomputed when b is replaced (snapshot). " if k >= 3 else "")
        if c == "session" and k < 4:
            obs += "Session: answers on a separate run."
        add(c, "P10c", k, "complete", "explicit", None, None, None, ["finished"],
            "valid: " + a.replace("\n", " ").replace(".", "").strip() + (" (d without a value)" if k == 1 else ""), obs.strip(),
            "SPECIFICATION Outcomes 1-3; P10c", check=ans(a))

# ===================================================================== P10d
for c in CONFIGS:
    for k, a in ((1, ("X = 1 ", "X = 2 ", "X = 3.\n\n")), (2, ("X = 2 ", "X = 3.\n\n")), (3, ("X = 1 ", "X = 2 ", "X = 3.\n\n"))):
        if k == 1:
            obs = "Three answers by backtracking; alternatives kept for backtracking (1 choicepoint at each of the first two answers, storage). "
        elif k == 2:
            obs = "x = 1, reported at stage 1, is withdrawn: shown only by its absence from the answers. "
        else:
            obs = "The withdrawal of x > 1 brought the alternative x = 1 back, without restating pick: the held relation was removed by retract/1 and pick re-solved over what is held. "
        if c == "session":
            obs += ("Session: answers on a separate run; the engine holds the database state." if k < 3 else "Session: stage 3 received into the engine; answers collected in it.")
        else:
            obs += ("Reposed: every stage replayed, the withdrawal included." if k > 1 else "")
        add(c, "P10d", k, "complete", "explicit", None, None, None, ["finished"],
            "valid: x in {" + ", ".join(x.split("=")[1].strip(" .\n") for x in a) + "}", obs.strip(),
            "SPECIFICATION Outcomes 1-3; P10d", check=ans(*a))

# ===================================================================== P11a, P11b
for c in CONFIGS:
    add(c, "P11a", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
        "an any-one query; x = 2 is one of the valid outcomes {2, 3}",
        "answers(1) stopped at the cap with 1 choicepoint left (pick's remaining clause). Commitment is the end of the query (committed when reported). L = <2>: emitted after the test, on the outcome then reported.",
        "SPECIFICATION Outcomes 1 (any-one query); problems/11 Commitment",
        check=ans("X = 2 "),
        effects={"class": "exact", "log": ["2"], "when": ["2: in the derivation of the reported answer, after the test: at commitment"], "reposing_duplicates": 0})
    add(c, "P11b", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
        "an any-one query; x = 2 is one of the valid outcomes {2, 3}",
        "answers(1) stopped at the cap, 1 choicepoint left. emit ran before the test, so x = 1 was emitted, then refuted by x >= 2, then x = 2 emitted and reported. No deferral of the effect.",
        "SPECIFICATION Outcomes 1; problems/11 P11b ('a log of <1, 2> is extra')",
        check=ans("X = 2 "),
        effects={"class": "extra", "log": ["1", "2"], "when": ["1: before commitment, on a provisional outcome later refuted", "2: at commitment (the reported answer)"], "reposing_duplicates": 0})

# ===================================================================== P11c
for c in ("plain", "tabling", "coroutines", "constraints"):
    add(c, "P11c", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
        "any-one; x = 1 is one of {1, 2, 3}",
        "Provisional outcome x = 1, emitted at once (seq 1). 1 choicepoint left.",
        "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 1 "))
    add(c, "P11c", 2, "complete", "explicit", None, None, None, ["alternatives pending"],
        "any-one; x = 2 is one of {2, 3}",
        "Reposed: stage 1 replayed, x = 1 emitted again (seq 2, a reposing duplicate), refuted by x /= 1, then x = 2 emitted (seq 3) and reported. The answer x = 1 of stage 1 is withdrawn, shown only by the new answer.",
        "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 2 "))
    add(c, "P11c", 3, "complete", "explicit", None, None, None, ["alternatives pending"],
        "commit: one answer, x = 2, valid ({2, 3})",
        "Commit stage first posed: it adds nothing; the system selects v = 2 by its answer (commitment = the reported answer at stage 3). Reposed: stage 1 replayed again, emitting 1 and 2 (seq 4, 5, both reposing duplicates).",
        "problems/11 Commitment and P11c", check=ans("X = 2 "),
        effects={"class": "extra", "log": ["1", "1", "2", "1", "2"],
                 "when": ["seq 1 '1': stage 1, before commitment, provisional, later refuted",
                          "seq 2 '1': stage-2 run, replay of stage 1, before commitment, duplicate of seq 1 by reposing",
                          "seq 3 '2': stage-2 run, replay of stage 1, before commitment, on the outcome later committed",
                          "seq 4 '1': stage-3 run, replay of stage 1, before commitment, duplicate by reposing",
                          "seq 5 '2': stage-3 run, replay of stage 1, in the run that commits, duplicate of seq 3 by reposing"],
                 "reposing_duplicates": 3,
                 "note": "Without the reposing duplicates L would be <1, 2>, still extra: 1 was emitted for x = 1, refuted at stage 2"})
add("session", "P11c", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
    "any-one; x = 1 is one of {1, 2, 3}",
    "Incremental engine at x = 1, emitted (classification log seq 1); the answer was collected on a separate run, whose emit went to the observation log (not judged). Open choicepoints in the engine.",
    "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 1 "))
add("session", "P11c", 2, "complete", "explicit", None, None, None, ["alternatives pending"],
    "any-one; x = 2 is one of {2, 3}",
    "Stage 2 received into the engine: dif(x, 1) failed, the engine backtracked into pick, emitted 2 (seq 2) and holds x = 2. Answer from a separate run (observation log entries, not judged). x = 1 withdrawn, shown by the new answer.",
    "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 2 "))
add("session", "P11c", 3, "complete", "explicit", None, None, None, ["alternatives pending"],
    "commit: x = 2, valid",
    "Commit stage received into the engine, adding nothing; the engine's answer x = 2 is the committed outcome (collected in the engine, the last stage). No reposing, so no duplicates.",
    "problems/11", check=ans("X = 2 "),
    effects={"class": "extra", "log": ["1", "2"],
             "when": ["seq 1 '1': stage 1, before commitment, provisional, later refuted", "seq 2 '2': stage 2, before commitment, on the outcome later committed"],
             "reposing_duplicates": 0})

# ===================================================================== P11d
for c in ("plain", "tabling", "coroutines", "constraints"):
    add(c, "P11d", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
        "any-one; x = 1 is one of {1, 2, 3}", "x = 1 emitted (seq 1), 1 choicepoint left.",
        "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 1 "))
    add(c, "P11d", 2, "complete", "explicit", None, None, None, ["alternatives pending"],
        "commit: x = 1 selected, valid; the valid outcome is now x = 1",
        "Reposed: stage 1 replayed (seq 2, '1', a reposing duplicate); the commit stage, first posed, adds nothing, and the reported answer x = 1 is the commitment v = 1.",
        "problems/11 Commitment", check=ans("X = 1 "))
    add(c, "P11d", 3, "complete", "explicit", None, None, None, ["finished"],
        "v = 1, so x /= 1 contradicts it: the valid outcome is none, and the query failed ('false.'), reporting none",
        "Reposed with the commitment replayed as x = 1 (replayed_commitments 'X = 1 '). In the replay, stage 1 emitted 1 (seq 3, duplicate), the replayed commit x = 1 and then x /= 1 failed, and backtracking into pick emitted 2 and 3 (seq 4, 5), each failing the replayed commit. Effects after commitment, for outcomes never committed. The system showed the contradiction as failure; it did not withdraw the earlier conclusion x = 1 in any other way.",
        "problems/11 P11d (v = 1: valid outcome none)", check=noans,
        effects={"class": "extra", "log": ["1", "1", "1", "2", "3"],
                 "when": ["seq 1 '1': stage 1, before commitment, on the outcome later committed",
                          "seq 2 '1': stage-2 run (the commit run), replay of stage 1, duplicate by reposing",
                          "seq 3 '1': stage-3 run, replay of stage 1, after commitment, duplicate by reposing",
                          "seq 4 '2': stage-3 run, replay of stage 1, after commitment, for an outcome never committed",
                          "seq 5 '3': stage-3 run, replay of stage 1, after commitment, for an outcome never committed"],
                 "reposing_duplicates": 2,
                 "note": "problems/11 says L = <1> would be exact. Without the 2 duplicates L is <1, 2, 3>: the entries 2 and 3 come from re-exploring pick's alternatives in the replay, before the replayed commitment is reached, so extra"})
add("session", "P11d", 1, "complete", "explicit", None, None, None, ["alternatives pending"],
    "any-one; x = 1 is one of {1, 2, 3}", "Engine at x = 1, emitted (seq 1); answer on a separate run (observation log).",
    "SPECIFICATION Outcomes 1; problems/11", check=ans("X = 1 "))
add("session", "P11d", 2, "complete", "explicit", None, None, None, ["alternatives pending"],
    "commit: x = 1 selected (the separate run's answer), valid",
    "The commit's answer was collected on a separate run of stages 1-2 (QUESTIONS S4), so the selection v = 1 was made there; in the engine the commit stage, first posed, added nothing (h_commitment/1 fails when not replaying), and the engine still holds pick's alternatives.",
    "problems/11 Commitment", check=ans("X = 1 "))
add("session", "P11d", 3, "unsound", "explicit", None, None, None, ["alternatives pending"],
    "v = 1 was committed at stage 2, so x /= 1 makes the valid outcome none; the system reported x = 2, which is not valid",
    "Stage 3 received into the engine: dif(x, 1) failed, the engine backtracked past the commit stage into pick, emitted 2 (seq 2) and re-ran the commit stage (still adding nothing), and answered x = 2. The commitment was not held by the incremental computation: what the system did with information contradicting a committed effect was to undo the commitment by backtracking. The earlier conclusion x = 1 was withdrawn silently.",
    "problems/11 P11d; SPECIFICATION Outcomes 1 (unsound: an outcome that is not valid)", check=ans("X = 2 "),
    effects={"class": "extra", "log": ["1", "2"],
             "when": ["seq 1 '1': stage 1, before commitment, on the outcome later committed", "seq 2 '2': stage 3, after commitment, for an outcome never committed"],
             "reposing_duplicates": 0})

if __name__ == "__main__":
    # every behaviour record of P09-P11 has entries for all its stages
    seen = {(e["configuration"], e["instance"], e["stage"], e["computation"]) for e in OUT}
    for c in CONFIGS:
        for p in ("P09", "P10", "P11"):
            for path in glob.glob(f"{RES}/{c}/{p}/raw/*.behaviour.*.json"):
                d, f = facts(path)
                for (st, comp) in f:
                    assert (c, d["run"]["instance"], st, comp) in seen, (c, path, st, comp)
    json.dump(OUT, open(os.path.dirname(os.path.abspath(__file__)) + "/outcomes.json", "w"), indent=1)
    print(len(OUT), "entries")
