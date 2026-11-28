import json, glob, os, csv
REPO = "/Users/christopherhay/cp-roles/classifier-1B-A2"
OUT = "/Users/christopherhay/cp-roles/classes-1B-A/swi-prolog-P04"
TOK = REPO + "/results/swi-prolog/tokens"
RS = REPO + "/results/swi-prolog"

def toks(path):
    rows = list(csv.reader(open(f"{TOK}/{path}.tokens.tsv"), delimiter="\t"))[1:]
    return [r[2] for r in rows]

R_HEAD = "harness README 12: heads of stage/3 (with :-) are H"
R_UNK = "harness README 12: the whole of each unknowns/2 fact is H"
R_QRY = "harness README 12: query/2 clause head is H; this clause is a bodiless fact"
R_END = "the clause terminator of the harness-contract stage/3 clause, taken with its H frame (head); cf. rule 20"
R_CONST = "rule 1 (stage information: the constant of the stage; removing it changes the solutions); CONSTANTS block entry, markers are comments (harness README 12)"
R_MEMB = "rule 1: reads the stage's constant into the query (removing it changes the solutions); memberchk/2 of library(lists) is outside plain's core, listed under external mechanisms (rule 12)"
R_DEF = "P: transcription of the problem's definition case, in presentation order (rules 1, 3); sequences as Prolog lists"
R_DISJ = "rule 6: a disjunction the problem states is P; alternatives in presentation order"
R_GOAL = "P: the query's goal (rule 1); separator by rule 20"
R_TAB = "METRICS class C: tabling declarations; rule 1 (changes termination only, not the least-relation solutions)"

def S(a,b,c,con,rule): return {"from":a,"to":b,"class":c,"construct":con,"rule":rule}

def loopdisj(off, loop_first):
    # off = index of the memberchk token
    o = off
    sp = [S(o, o+8, "P", "goal memberchk(alternative_value(K), Cs): the stage's constant k", R_MEMB),
          S(o+9, o+10, "P", "separator ',' and opening '(' of the disjunction", R_DISJ + "; rule 20 for the separator; rule 10")]
    if loop_first:
        sp += [S(o+11, o+14, "P", "disjunct loop(X)", R_DISJ),
               S(o+15, o+15, "P", "disjunction connective ;", R_DISJ),
               S(o+16, o+18, "P", "disjunct X = K (equality as unification)", R_DISJ)]
    else:
        sp += [S(o+11, o+13, "P", "disjunct X = K (equality as unification)", R_DISJ),
               S(o+14, o+14, "P", "disjunction connective ;", R_DISJ),
               S(o+15, o+18, "P", "disjunct loop(X)", R_DISJ)]
    sp += [S(o+19, o+19, "P", "closing ')' of the disjunction", R_DISJ)]
    return sp

spans = {}
for tab in (False, True):
    base = "tabling" if tab else "constraints"
    d = 6 if tab else 0
    for x, lf in (("a", True), ("b", False)):
        sp = [S(0,4,"P","CONSTANTS entry alternative_value(1).",R_CONST)]
        if tab: sp.append(S(5,10,"C",":- table loop/1.",R_TAB))
        sp += [S(5+d,14+d,"P","definition case loop(x) if loop(x): loop(X) :- loop(X).",R_DEF),
               S(15+d,23+d,"H","unknowns(main, ['X']).",R_UNK),
               S(24+d,34+d,"H","stage(1, [X], Cs) :- (head)",R_HEAD)]
        sp += loopdisj(35+d, lf)
        sp += [S(55+d,55+d,"H","'.' ending the stage/3 clause",R_END),
               S(56+d,62+d,"H","query(_, _).",R_QRY)]
        spans[f"{base}/P04{x}.pl"] = sp
    # P04c (left, ground), P04e (right, ground)
    for x in ("c","e"):
        sp = [S(0,8,"P","CONSTANTS entry alist_argument([a, a]).",R_CONST)]
        if tab: sp.append(S(9,14,"C",":- table alist/1.",R_TAB))
        if x == "c":
            sp += [S(9+d,26+d,"P","alist-left case 1: alist(S) :- alist(M), S = [a|M]. (conjuncts in the order written)",R_DEF),
                   S(27+d,32+d,"P","alist-left case 2: alist([]).",R_DEF)]
        else:
            sp += [S(9+d,14+d,"P","alist-right case 1: alist([]).",R_DEF),
                   S(15+d,28+d,"P","alist-right case 2: alist([a|M]) :- alist(M).",R_DEF + "; the head pattern [a|M] transcribes <a> ++ m")]
        o = 33+d if x=="c" else 29+d
        sp += [S(o,o+7,"H","unknowns(main, []).",R_UNK),
               S(o+8,o+17,"H","stage(1, [], Cs) :- (head)",R_HEAD),
               S(o+18,o+26,"P","goal memberchk(alist_argument(S), Cs): the stage's constant sequence",R_MEMB),
               S(o+27,o+31,"P","separator and goal alist(S): the query",R_GOAL),
               S(o+32,o+32,"H","'.' ending the stage/3 clause",R_END),
               S(o+33,o+39,"H","query(_, _).",R_QRY)]
        spans[f"{base}/P04{x}.pl"] = sp
    for x in ("d","f"):
        sp = []
        if tab: sp.append(S(0,5,"C",":- table alist/1.",R_TAB))
        if x == "d":
            sp += [S(0+d,17+d,"P","alist-left case 1: alist(S) :- alist(M), S = [a|M].",R_DEF),
                   S(18+d,23+d,"P","alist-left case 2: alist([]).",R_DEF)]
            o = 24+d
        else:
            sp += [S(0+d,5+d,"P","alist-right case 1: alist([]).",R_DEF),
                   S(6+d,19+d,"P","alist-right case 2: alist([a|M]) :- alist(M).",R_DEF)]
            o = 20+d
        sp += [S(o,o+8,"H","unknowns(main, ['S']).",R_UNK),
               S(o+9,o+19,"H","stage(1, [S], _) :- (head)",R_HEAD),
               S(o+20,o+23,"P","goal alist(S): the query",R_GOAL),
               S(o+24,o+24,"H","'.' ending the stage/3 clause",R_END),
               S(o+25,o+31,"H","query(_, _).",R_QRY)]
        spans[f"{base}/P04{x}.pl"] = sp

# check coverage, and dump span texts for inspection
for path, sp in spans.items():
    t = toks(path)
    cov = [0]*len(t)
    for s in sp:
        for i in range(s["from"], s["to"]+1): cov[i] += 1
    assert all(c == 1 for c in cov), (path, cov)
    with open(f"{OUT}/spans-check.txt", "a") as fh:
        fh.write(f"== {path} ({len(t)} tokens)\n")
        for s in sp:
            fh.write(f"  {s['from']:3}-{s['to']:3} {s['class']}  {' '.join(t[s['from']:s['to']+1])}\n")

json.dump(spans, open(f"{OUT}/spans.json","w"), indent=1)
tot = {}
for path, sp in spans.items():
    for s in sp: tot.setdefault(path,{}).setdefault(s["class"],0); tot[path][s["class"]] += s["to"]-s["from"]+1
print(json.dumps(tot))
