"""Assemble python.json from tokens.json, outcomes.json, mode_differences.json."""
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
tokens = json.load(open(os.path.join(here, "tokens.json")))
outcomes = json.load(open(os.path.join(here, "outcomes.json")))
diffs = json.load(open(os.path.join(here, "mode_differences.json")))

R_P11CD = ("expressible with reformulation: pick, x != k, x = v (the commitment) and emit are transcribed (P), but a relation that arrives after "
           "stage 1's solution was taken cannot be added to a Python generator's computation; the program holds the solution taken and the "
           "relations added, and retries the generator when one is refuted (known, solutions, added, holds' dispatch, satisfies, advance, add: "
           "R by METRICS rule 19, %s R tokens). The reformulation keeps the meaning on every input (any constants of the same shapes).")
R_P11AB = ("expressible: the conjunction is transcribed in the order written as %s; pick by its facts, the comparison, emit; "
           "no R tokens.")
R_P12 = ("expressible: choice(n, s) is transcribed by its two cases in order, in the one direction the query uses (s unknown, n given), %s; "
         "accept by its facts%s; the query in the order written; no R tokens. The constants block holds accept's facts for each n posed "
         "(8, 12, 16), which is the stage's information, not a reformulation.")


def count(text, cls):
    return sum(s["to"] - s["from"] + 1 for s in tokens[text] if s["class"] == cls)


expr = []
for conf in ("core", "stdlib-concurrency", "extended"):
    base = "core" if conf != "extended" else "extended"
    for sub in ("P11a", "P11b", "P11c", "P11d", "P12a", "P12b", "P12c", "P12d"):
        text = "%s/%s.py" % (base, sub)
        if sub in ("P11a", "P11b"):
            e, r = "expressible", R_P11AB % ("a generator of its solutions" if base == "core" else "goals solved by the S search over the program's resolution and unifier (S, as the extended configuration provides)")
        elif sub in ("P11c", "P11d"):
            e, r = "expressible with reformulation", R_P11CD % count(text, "R")
        else:
            e, r = "expressible", R_P12 % (
                ("as a generator (rule 3, mode-faithful)", " with `in` (rule 9, listed)") if base == "core" else
                ("as a relation of cases with head unification, solved by the S search", " as cases unified with s"))
        if conf == "stdlib-concurrency":
            r += " The text is the core text; no module of stdlib-concurrency is used."
        expr.append({"configuration": conf, "subproblem": sub, "direction": None, "expressibility": e, "reason": r})


def tok_of(text, pred):
    return sum(s["to"] - s["from"] + 1 for s in tokens[text] if s["class"] == "S" and pred(s["construct"]))


smech = []
for conf in ("core", "stdlib-concurrency", "extended"):
    for sub in ("P11a", "P11b", "P11c", "P11d", "P12a", "P12b", "P12c", "P12d"):
        prog = sub + ".py"
        if conf != "extended":
            smech.append({"configuration": conf, "program": prog, "mechanism": "none", "listed_at_phase_4": None, "tokens": 0,
                          "note": "no S, and no import at all (no external mechanism)"})
            continue
        text = "extended/" + prog
        smech += [
            {"configuration": conf, "program": prog, "mechanism": "backtracking search (S/search.py: search, undo, the trail convention)", "listed_at_phase_4": True,
             "tokens": tok_of(text, lambda c: "backtracking search" in c),
             "note": "tokens: the program's import of it (S); the mechanism itself is 176 tokens (S-mechanisms.md), counted once for the configuration. Its call search(...) is classed C (directive)."},
            {"configuration": conf, "program": prog, "mechanism": "suspension queue (S/suspend.py: Var, deref, Queue.bind with a trail)", "listed_at_phase_4": True,
             "tokens": tok_of(text, lambda c: "suspension queue" in c),
             "note": "tokens: the program's import of it (S); the mechanism itself is 537 tokens, counted once for the configuration. Used only for Var, deref and Queue.bind (no goal ever waits)."},
            {"configuration": conf, "program": prog, "mechanism": "unify (the program's own unifier, with its binder Queue and the shared trail%s)" % (", and NIL, unused here" if sub.startswith("P11") else ""), "listed_at_phase_4": False,
             "tokens": tok_of(text, lambda c: c.startswith("unify(") or c.startswith("binder") or c.startswith("trail") or c.startswith("NIL")),
             "note": "not listed in S-mechanisms.md; the same text as in this configuration's P03 and P04 programs (provenance comment); counted once for the configuration"},
            {"configuration": conf, "program": prog, "mechanism": "resolution (the program's own children and done: a goal list reduced by the cases of its first goal's relation)", "listed_at_phase_4": False,
             "tokens": tok_of(text, lambda c: c.startswith("children(") or c.startswith("done(")),
             "note": "not listed in S-mechanisms.md; general over relations (rule 19); counted once for the configuration"},
        ]
        tot = sum(s["to"] - s["from"] + 1 for s in tokens[text] if s["class"] == "S")
        assert tot == sum(m["tokens"] for m in smech[-4:]), (text, tot)

out = {
    "tokens": tokens,
    "outcomes": outcomes,
    "mode_differences": diffs,
    "expressibility": expr,
    "late_definition": [],
    "s_mechanisms": smech,
}
json.dump(out, open(os.path.join(here, "python.json"), "w"), indent=1, ensure_ascii=False)

# checks and totals
for text, spans in tokens.items():
    idx = sorted((s["from"], s["to"]) for s in spans)
    assert idx[0][0] == 0
    for (a, b), (c, d) in zip(idx, idx[1:]):
        assert c == b + 1, (text, b, c)
tot = {}
for text, spans in tokens.items():
    for s in spans:
        tot[s["class"]] = tot.get(s["class"], 0) + s["to"] - s["from"] + 1
print("all texts", sum(tot.values()), dict(sorted(tot.items())))
for base in ("core", "extended"):
    t = {}
    for text, spans in tokens.items():
        if text.startswith(base + "/"):
            for s in spans:
                t[s["class"]] = t.get(s["class"], 0) + s["to"] - s["from"] + 1
    print(base, sum(t.values()), dict(sorted(t.items())))
json.load(open(os.path.join(here, "python.json")))
print("valid JSON;", len(outcomes), "outcomes;", len(expr), "expressibility;", len(smech), "s_mechanism rows")
for m in smech:
    if m["configuration"] == "extended":
        print(m["program"], m["mechanism"][:30], m["tokens"])
