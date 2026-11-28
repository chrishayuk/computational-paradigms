"""Class the frozen tokens of the batch-1B P05-P08 SWI-Prolog texts by construct.
Read-only on the repository; writes tokens.json beside this script."""
import csv, json, os, re, sys
REPO = "/Users/christopherhay/cp-roles/classifier-1B-A"
TOK = REPO + "/results/swi-prolog/tokens"
PROG = REPO + "/programs/swi-prolog"
OUT = os.path.dirname(os.path.abspath(__file__))

def read_tokens(path):
    rows = list(csv.reader(open(path), delimiter="\t", quoting=csv.QUOTE_NONE))
    assert rows[0] == ["index", "line", "token"], rows[0]
    toks = [(int(r[0]), int(r[1]), r[2]) for r in rows[1:]]
    assert [t[0] for t in toks] == list(range(len(toks)))
    return toks

def const_lines(src):
    b = e = None
    for i, l in enumerate(open(src), 1):
        if "CONSTANTS BEGIN" in l and l.lstrip().startswith("%"): b = i
        if "CONSTANTS END" in l and l.lstrip().startswith("%"): e = i
    return (b, e)

OPEN, CLOSE = set("([{"), set(")]}")
def clauses(toks):
    out, cur, d = [], [], 0
    for t in toks:
        cur.append(t)
        if t[2] in OPEN: d += 1
        elif t[2] in CLOSE: d -= 1
        elif t[2] == "." and d == 0:
            out.append(cur); cur = []
    assert not cur, cur
    return out

def split_top(ts, seps):
    """split ts at depth-0 tokens in seps; returns list of (sep_token_or_None, part)"""
    parts, cur, d, sep = [], [], 0, None
    for t in ts:
        if t[2] in OPEN: d += 1
        elif t[2] in CLOSE: d -= 1
        if d == 0 and t[2] in seps:
            parts.append((sep, cur)); cur = []; sep = t; continue
        cur.append(t)
    parts.append((sep, cur))
    return parts

def span(ts, cls, construct, rule):
    return {"from": ts[0][0], "to": ts[-1][0], "class": cls, "construct": construct, "rule": rule}

def text(ts): return " ".join(t[2] for t in ts)

EVAL = {"sum", "diff", "product", "sum_known", "diff_known", "product_known"}

def wrapper_spans(sep, g, kind):
    """when(Cond, Goal) / freeze(V, Goal): wrapper C, inner goal P (rule 10)."""
    # g: [name, '(', ..., ',', ..., ')']
    assert g[1][2] == "(" and g[-1][2] == ")"
    inner = g[2:-1]
    parts = split_top(inner, {","})
    assert len(parts) == 2, text(g)
    (_, cond), (comma, goal) = parts
    pre = ([sep] if sep else []) + g[:2] + cond
    res = [span(pre, "C", "%s/2 wrapper and its %s (%s)" % (kind, "condition" if kind == "when" else "variable", text(cond)),
                "C: coroutine and freeze calls; rule 10 (the tokens that introduce a construct, and its condition, take its class)")]
    res.append(span([comma] + goal, "P", "the goal %s/2 holds: %s" % (kind, text(goal)), "rule 10 (inner construct classed on its own); rule 20 (separator); rule 1 / rule 19 (the relation itself)"))
    res.append(span([g[-1]], "C", "%s/2 wrapper, closing parenthesis" % kind, "rule 10"))
    return res

def goal_spans(sep, g, ctx):
    """class one body goal (with its preceding separator, rule 20)"""
    ts = ([sep] if sep else []) + g
    name = g[0][2]
    s = text(g)
    if name == "h_param":
        return [span(ts, "H", "harness call h_param/2 (the instance's presentation order)", "H: the harness's own calls (harnesses/swi-prolog/README.md 2.3)")]
    if name in ("when", "freeze"):
        return wrapper_spans(sep, g, name)
    if name == "!":
        return [span(ts, "C", "cut", "C: cuts; rule 2 (a cut that commits beyond the head test)")]
    if name in ("nonvar", "var"):
        return [span(ts, "R", "test of which places are known: %s" % s, "rule 19 (the tests of which places are known are R, the holding/dispatch, not the relation)")]
    if name == "memberchk":
        return [span(ts, "P", "reads the stage's constant from the harness-supplied list: %s" % s, "rule 1 (the stage's information, k); memberchk/2 of library(lists), external mechanism (rule 12)")]
    if name == "member" and "pick" in s:
        return [span(ts, "P", "pick(x) over the closed world of the stage's pick facts: %s" % s, "rule 6 (a set of facts the problem states, enumerated as stated); rule 9 (member/2 in place of the facts' lookup, equivalent in the direction used; listed)")]
    if name == "forall":
        return [span(ts, "P", "asserts the stage's closed-world facts: %s" % s, "rule 1 (the information of the stage); assertz/1 for posing definitions (systems file, core)")]
    if name == "assertz":
        return [span(ts, "P", "a definition case that arrives at this stage, added by assertz/1: %s" % s, "rule 1 (the information of the stage, a case of the problem's definition)")]
    if name == "dif":
        return [span(ts, "P", "x ≠ k as dif/2: %s" % s, "P: the connective (inequality); dif/2 states ≠ soundly on unknowns, so it is the relation, not a delay wrapper (rule 1)")]
    if name == "\\\\+" or name == "\\+":
        return [span(ts, "P", "negation: %s" % s, "P: the connective (negation) the problem states")]
    if name == "relations" or name == "relation":
        return [span(ts, "P", "the conjunction of the stage's relations in the instance's presentation order: %s" % s, "rule 1 (the problem's relations, in the order the problem poses them); see notes")]
    if ctx in EVAL or ctx == "factor":
        if name in ("factor",) or any(x[2] in ("is", "=:=") for x in g):
            return [span(ts, "P", "evaluator: computing one place from the others, or testing a known relation: %s" % s, "rule 19 (computing any one place, in every direction, and testing a fully known relation, is P); rule 8")]
    return [span(ts, "P", "goal: %s" % s, "P: the problem's relation, equality, arithmetic or comparison (rule 1)")]

def clause_spans(cl, in_const, stagek):
    s = text(cl)
    if cl[0][2] == ":-":
        d = cl[1][2]
        if d == "use_module":
            return [span(cl, "P", "loads %s, whose relations state the problem's arithmetic/comparison" % text(cl[1:-1]),
                         "rule 12 (a library outside the core is counted as its call tokens, and listed under external mechanisms); rule 1 (without it the stage's relations are undefined)")]
        if d == "dynamic":
            return [span(cl, "C", "dynamic declaration of the closed-world relations", "rule 11 (a declaration that changes how an undefined relation behaves is C, and is listed)")]
        if d == "table":
            return [span(cl, "C", "tabling declaration: %s" % text(cl[2:-1]), "C: tabling declarations")]
        if d == "set_prolog_flag":
            return [span(cl, "C", "unknown flag set to fail (the closed reading)", "rule 11 (the unknown flag is C, and is listed; it chooses a reading of P08)")]
        raise ValueError(s)
    if in_const:
        return [span(cl, "P", "constant of stage %s: %s" % (stagek, s), "P: the information of the stage (its constant), in the CONSTANTS block")]
    hb = split_top(cl[:-1], {":-"})
    head = hb[0][1]
    name = head[0][2]
    if name in ("unknowns", "query") and len(hb) == 1:
        return [span(cl, "H", "harness-contract declaration %s" % s, "H: fixed by the harness contract (harnesses/swi-prolog/README.md 2.1)")]
    if name == "stage":
        assert len(hb) == 2
        neck = hb[1][0]
        res = [span(head + [neck], "H", "stage/3 clause head (harness contract)", "H: the head of stage/3 is fixed by the harness contract (README 2.1: head H; body classed)")]
        for sep, g in split_top(hb[1][1], {","}):
            res += goal_spans(sep, g, "stage")
        res.append(span([cl[-1]], "H", "end of the stage/3 clause", "H with its clause head"))
        return res
    if name in ("mem", "setdiff", "nonmajor", "rev", "conc"):
        return [span(cl, "P", "definition case of %s as the problem gives it: %s" % (name, s), "P: transcription of the problem's definition case (rule 3); negation as \\+ is the connective")]
    if name in ("relation", "relations"):
        return [span(cl, "P", "presentation-order dispatch, %s: %s" % (name, s), "rule 1 (the stage's relations in the order the instance names them, the problem's presentation order); see notes for the alternative reading")]
    if name in EVAL or name == "factor":
        res = []
        if len(hb) == 1:
            return [span(cl, "P", "fact of evaluator %s" % s, "rule 19")]
        neck = hb[1][0]
        res.append(span(head + [neck], "P", "evaluator clause head %s (the primitive relation %s, written as a relation)" % (text(head), name),
                        "rule 19 (the evaluator: computing one place from the others is P in every direction); rule 8"))
        for sep, g in split_top(hb[1][1], {","}):
            res += goal_spans(sep, g, name)
        res.append(span([cl[-1]], "P", "end of evaluator clause", "with its clause head"))
        return res
    raise ValueError("unclassified clause: " + s)

def classify(relpath):
    toks = read_tokens(os.path.join(TOK, relpath + ".tokens.tsv"))
    b, e = const_lines(os.path.join(PROG, relpath))
    # stage tags inside constants block
    tags = {}
    if b:
        k = None
        for i, l in enumerate(open(os.path.join(PROG, relpath)), 1):
            if b < i < e:
                m = re.match(r"\s*%\s*stage\s+(\d+)", l)
                if m: k = int(m.group(1))
                tags[i] = k
    spans = []
    for cl in clauses(toks):
        ln = cl[0][1]
        in_const = bool(b) and b < ln < e
        spans += clause_spans(cl, in_const, tags.get(ln))
    # coverage check
    cov = [0] * len(toks)
    for sp in spans:
        for i in range(sp["from"], sp["to"] + 1): cov[i] += 1
    assert all(c == 1 for c in cov), (relpath, [i for i, c in enumerate(cov) if c != 1][:20])
    return spans, len(toks)

if __name__ == "__main__":
    rows = list(csv.reader(open(TOK + "/TEXTS-1B-P05-P08.tsv"), delimiter="\t"))
    assert rows[0] == ["text", "also the text of"]
    result, totals = {}, {}
    for r in rows[1:]:
        spans, n = classify(r[0])
        result[r[0]] = spans
        t = {}
        for sp in spans: t[sp["class"]] = t.get(sp["class"], 0) + sp["to"] - sp["from"] + 1
        totals[r[0]] = (n, t)
    json.dump(result, open(os.path.join(OUT, "tokens.json"), "w"), indent=1, ensure_ascii=False)
    for k, (n, t) in totals.items(): print(k, n, t)
    agg = {}
    for k, (n, t) in totals.items():
        for c, v in t.items(): agg[c] = agg.get(c, 0) + v
    print("ALL", sum(n for n, _ in totals.values()), agg, len(totals))
