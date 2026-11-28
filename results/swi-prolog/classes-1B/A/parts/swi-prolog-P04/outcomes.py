import json, glob, os
REPO = "/Users/christopherhay/cp-roles/classifier-1B-A2"
OUT = "/Users/christopherhay/cp-roles/classes-1B-A/swi-prolog-P04"
RS = REPO + "/results/swi-prolog"
CONFIGS = ["plain", "tabling", "coroutines", "constraints", "session"]
spans = json.load(open(f"{OUT}/spans.json"))
tokens = {}
for path, sp in spans.items():
    tokens[path] = sp

def rec(c, inst, mode):
    fs = sorted(glob.glob(f"{RS}/{c}/P04/raw/{inst}.{mode}.*.json"))
    assert len(fs) == 1, (c, inst, mode, fs)
    return os.path.relpath(fs[0], REPO), json.load(open(fs[0]))

def facts(r):
    a = r["stages"][0]["attempts"]
    last = a[-1]; comp = last["computations"][0]; q = comp["queries"][0]
    return dict(attempts=len(a), states=comp["execution_state"]["states"], n=len(q["answers"]),
                answers=[x["verbatim"] for x in q["answers"]], ended_by=q["ended_by"],
                steps=comp["steps"]["restated"], first=comp["steps"]["to_first_answer"],
                steps_by_attempt=[x["computations"][0]["steps"]["restated"] for x in a],
                susp=comp["suspended"]["at_boundary"], obs=last["observe"]["raw"],
                faults=r["harness_faults"], limits=[x["limit_s"] for x in a])

COMMON_OBS = "one stage, so no conclusion withdrawn; no manual actions (record manual_actions empty); "

def judge(c, inst, f):
    tab = c == "tabling"
    o = dict(reached=True, semantic=None, representation=None, simplification=None,
             identical_to_posed=None, residual_size=None, execution_state=list(f["states"]),
             residual_equivalence=None, observations=None, rule=None, answer_completeness=None)
    obs_alt = "alternatives (retained choicepoints) are not measured in behaviour mode (null = unavailable, AMENDMENTS 3.1)"
    if inst == "P04a":
        if not tab:
            o.update(semantic="none reported",
                residual_equivalence="nothing reported, so no residual or solved form to compare. The valid outcome x = 1 is never reached: loop(X), the first disjunct in presentation order, recurses without end (SLD, depth-first, textual order) and the second disjunct X = K is never tried",
                observations=COMMON_OBS + f"X stays unbound (observe at the budget exception: {f['obs']!r}); {obs_alt}; the untried disjunct X = K is held for backtracking only; suspended work {f['susp']}; steps {f['steps']} (9 past the 10^6 budget, the overrun the harness records); answer completeness 0/1, 0 invalid",
                rule="SPECIFICATION Outcomes 1 (none reported), 3 (budget)", answer_completeness="0/1 valid, 0 invalid")
        else:
            o.update(semantic="complete", representation="explicit",
                residual_equivalence="explicit answer 'X = 1.' (no choicepoint) is exactly the valid outcome {x = 1}; checked by check_answers.py",
                observations=COMMON_OBS + f"tabled loop/1 completes with no answers (storage: 1 table, 0 table answers at the boundary), so the disjunction falls through to X = 1; the answer has no choicepoint, so the harness asked for no more; steps {f['steps']}; suspended {f['susp']}; no unknown left unknown; answer completeness 1/1, 0 invalid",
                rule="SPECIFICATION Outcomes 1 (complete), 2 (explicit), 3 (finished)", answer_completeness="1/1 valid, 0 invalid")
    elif inst == "P04b":
        if not tab:
            o.update(semantic="complete", representation="explicit",
                residual_equivalence="explicit answer 'X = 1' is exactly the valid outcome {x = 1}; no invalid answer (check_answers.py)",
                observations=COMMON_OBS + f"X = 1 reported at {f['first']} steps; the answer left a choicepoint (the second disjunct loop(X)), the harness asked for another, and loop(X) ran to the budget (steps {f['steps']}, 9 past budget); at the budget X is unbound again (observe {f['obs']!r}); {obs_alt}; suspended {f['susp']}; answer completeness 1/1, 0 invalid",
                rule="SPECIFICATION Outcomes 1 (complete: answers reported before the budget are classified), 2 (explicit), 3 (budget)", answer_completeness="1/1 valid, 0 invalid")
        else:
            o.update(semantic="complete", representation="explicit",
                residual_equivalence="explicit answer 'X = 1' then 'false.': exactly {x = 1}",
                observations=COMMON_OBS + f"X = 1 at {f['first']} steps with a choicepoint; the request for more ran the tabled loop(X), which completed with no answers, and the query failed ('false.'), steps {f['steps']}; nothing held at the boundary (observe empty; storage: 0 choicepoints, 1 table, 0 answers); suspended {f['susp']}; answer completeness 1/1, 0 invalid",
                rule="SPECIFICATION Outcomes 1, 2, 3 (finished: the last request failed)", answer_completeness="1/1 valid, 0 invalid")
    elif inst in ("P04c", "P04d"):
        what = "alist([a, a])" if inst == "P04c" else "alist(S)"
        if not tab:
            o.update(semantic="none reported",
                residual_equivalence=f"nothing reported. alist-left's first case calls alist(M) with M fresh before the conjunct S = [a|M]; {what} therefore recurses on a fresh unknown without end and never reaches case 2 (left recursion under SLD in textual order)",
                observations=COMMON_OBS + f"no binding at the budget (observe {f['obs']!r}); {obs_alt}; suspended {f['susp']}; steps {f['steps']}; " +
                    ("answer completeness 0/1" if inst == "P04c" else "infinite valid outcomes: no finite representation given; answers obtained: none; whether every solution would be reached given enough steps: no, none is ever reached (the recursion never tries case 2)"),
                rule="SPECIFICATION Outcomes 1 (none reported), 3 (budget)", answer_completeness=("0/1 valid, 0 invalid" if inst == "P04c" else "finite representation: no; answers obtained: none"))
        else:
            o.update(semantic="none reported", execution_state=["timeout"],
                residual_equivalence=f"nothing reported. Under tabling the inner call alist(M), M fresh, is a tabled call whose table has infinitely many answers; SLG evaluation keeps adding answers to it and never completes it, so {what} returns nothing",
                observations=COMMON_OBS + f"safety limit hit at 60 s (steps {f['steps_by_attempt'][0]}), rerun once at 600 s, final timeout (steps {f['steps_by_attempt'][-1]}, under the 10^6 budget: SLG table work is largely not counted as inferences); nothing could be read at the kill (observe {f['obs']!r}); the table grew without end (storage run: table answers at attempt 1 / attempt 2 in the notes); suspended {f['susp']}; " +
                    ("answer completeness 0/1" if inst == "P04c" else "infinite valid outcomes: no finite representation; answers obtained: none; every solution reached given enough steps: no (no answer is returned to the query before the table completes, which it never does)"),
                rule="SPECIFICATION Outcomes 1 (none reported), 3 (timeout, final after the one rerun; PROTOCOL Running, safety limit)", answer_completeness=("0/1 valid, 0 invalid" if inst == "P04c" else "finite representation: no; answers obtained: none"))
    elif inst == "P04e":
        o.update(semantic="complete", representation="explicit",
            residual_equivalence="'true.' with no unknowns: exactly the valid outcome (true, one solution); no choicepoint left",
            observations=COMMON_OBS + f"one answer 'true.' at {f['first']} steps, no choicepoint (the clause heads [] and [a|M] are told apart by first-argument indexing), so finished; " + ("tabled: 3 tables, 3 answers at the boundary (storage); " if tab else "") + f"suspended {f['susp']}; answer completeness 1/1, 0 invalid",
            rule="SPECIFICATION Outcomes 1, 2, 3 (finished)", answer_completeness="1/1 valid, 0 invalid")
    elif inst == "P04f":
        if not tab:
            o.update(semantic="partial", representation="explicit",
                residual_equivalence="20 explicit answers S = [], [a], ..., [a x 19], each valid, all distinct, 0 invalid (check_answers.py): a nonempty proper subset of the infinite valid outcomes; not a finite representation of them",
                observations=COMMON_OBS + f"answers in increasing length 0..19, 2 steps apart (first at {f['first']}, last at {f['steps']}); collection stopped at the cap with a choicepoint held (storage: 1 retained choicepoint of type clause at every answer and at the boundary; behaviour: not measured); every solution would be reached given enough steps (the sequence of length n is answer n+1); S bound to the 19-element list at the boundary; suspended {f['susp']}",
                rule="SPECIFICATION Outcomes 1 (partial: nonempty proper subset), 2 (explicit), 3 (alternatives pending); METRICS answer completeness (infinite)", answer_completeness="finite representation: no; answers obtained: the 20 listed, lengths 0-19 in order")
        else:
            o.update(semantic="none reported", execution_state=["timeout"],
                residual_equivalence="nothing reported. The tabled call alist(S), S fresh, has infinitely many answers; SWI-Prolog's tabling returns a completed table's answers to the query, and this table never completes, so no answer reaches the harness",
                observations=COMMON_OBS + f"safety limit at 60 s (steps {f['steps_by_attempt'][0]}), rerun at 600 s, final timeout (steps {f['steps_by_attempt'][-1]}); nothing read at the kill (observe {f['obs']!r}); table grew without end (storage); suspended {f['susp']}; every solution reached given enough steps: no answer is delivered at all; contrast the untabled text, which enumerates fairly",
                rule="SPECIFICATION Outcomes 1 (none reported), 3 (timeout, final)", answer_completeness="finite representation: no; answers obtained: none")
    return o

outcomes = []; diffs = []
for c in CONFIGS:
    for x in "abcdef":
        inst = f"P04{x}"
        path, r = rec(c, inst, "behaviour")
        f = facts(r)
        o = judge(c, inst, f)
        if c == "tabling" and inst in ("P04c","P04d","P04f"):
            sp, sr = rec(c, inst, "storage")
            ta = [a["store"]["quantities"].get("table_answers",{}).get("boundary") for a in sr["stages"][0]["attempts"]]
            o["observations"] += f"; storage run table_answers at the kill: {ta[0]} (60 s) and {ta[-1]} (600 s)"
        if c == "session":
            o["observations"] += "; session: one engine, the single stage posted fresh; S/session-wait.pl loaded but never fired (every procedure called is defined), no h_wait"
        entry = dict(configuration=c, instance=inst, program=f"{inst}.pl", record=path, stage=1, harness_fault=False)
        entry.update(o)
        outcomes.append(entry)
        bclass = {k: o[k] for k in ("semantic","representation","execution_state")}
        for mode in ("cost", "storage"):
            mp, mr = rec(c, inst, mode)
            mf = facts(mr)
            same_state = mf["states"] == f["states"]
            same_ans = mf["answers"] == f["answers"]
            if same_state and same_ans:
                continue
            fault = bool(mf["faults"])
            frag = mf["faults"][0][:160] if fault else ""
            this = dict(semantic=o["semantic"], representation=o["representation"],
                        execution_state_recorded=mf["states"],
                        execution_state_as_classed=f["states"] if fault else mf["states"],
                        answers=mf["answers"], steps_at_first_answer=mf["first"], suspended=mf["susp"])
            note = ("Harness fault, not the system's: the record's state 'error' (determined false) is the harness's failure to read its own event stream (harness_faults: an unreadable, interleaved event). "
                    f"The fragment that survives shows the budget exception ({frag!r}), so I class the stage budget, as in behaviour; semantic result unchanged ("
                    + ("the same answer X = 1" if mf["answers"] else "none reported") + "). Observations that depend on the end event (suspended, steps, store) are unavailable, not 0 (AMENDMENTS 3.1).")
            if inst == "P04b" and mf["first"] != f["first"]:
                note += f" Also: the answer's steps_at is {mf['first']} here against {f['first']} in behaviour, which the harness says should be equal across modes (harness README 6): an instrumentation discrepancy."
            diffs.append(dict(configuration=c, instance=inst, program=f"{inst}.pl", mode=mode, record=mp, stage=1, harness_fault=fault,
                              behaviour=bclass, this_mode=this, note=note))

expr = []
for c in CONFIGS:
    for x in "abcdef":
        inst = f"P04{x}"
        d = {"a": None, "b": None, "c": "alist-left, ground argument (test)", "d": "alist-left, open argument (generate)",
             "e": "alist-right, ground argument (test)", "f": "alist-right, open argument (generate)"}[x]
        reason = ("the definitions and the query are transcribed as written, in presentation order (cases and conjuncts in the problem's order, the disjunction's alternatives in its order); no R tokens"
                  + ("; the only addition is the table/1 directive, class C" if c == "tabling" else "")
                  + ". Expressibility is independent of whether the run terminates: the transcription's nontermination is the behaviour P04 probes, recorded on the outcome axes")
        expr.append(dict(configuration=c, subproblem=inst, direction=d, expressibility="expressible", reason=reason))

smech = []
for c in CONFIGS:
    for x in "abcdef":
        if c == "session":
            smech.append(dict(configuration=c, program=f"P04{x}.pl", mechanism="wait for an undefined procedure (harnesses/swi-prolog/S/session-wait.pl, a user:exception/3 hook)",
                              listed_at_phase_4=True, tokens=0,
                              note="loaded by the harness before every session program, so part of the configuration; it is not in the program text (0 S tokens in the program; S-mechanisms.md gives the file as 158 tokens by its own count, not classed here). In P04 it never fires: loop/1, alist/1 and memberchk/2 are all defined. The program supplies no S of its own."))
        else:
            smech.append(dict(configuration=c, program=f"P04{x}.pl", mechanism=None, listed_at_phase_4=None, tokens=0,
                              note="none: the configuration lists no S mechanism (S-mechanisms.md) and the program supplies none (0 S tokens). External mechanism, not S: memberchk/2 of library(lists)" + (" in this program" if x in "abce" else " (not used by this program)") + ("; tabling's table/1 directive" if c == "tabling" else "")))

result = dict(tokens=tokens, outcomes=outcomes, mode_differences=diffs, expressibility=expr, late_definition=[], s_mechanisms=smech)
json.dump(result, open(f"{OUT}/swi-prolog.json", "w"), indent=1, ensure_ascii=False)
print(len(outcomes), "outcomes", len(diffs), "diffs")
for d in diffs: print(d["configuration"], d["instance"], d["mode"], d["this_mode"]["execution_state_recorded"], d["this_mode"]["steps_at_first_answer"])
