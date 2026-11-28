"""Classifier A's token classes for algol-60 P07-P08 (batch 1B).

Classes each text's atoms (atoms.py) by the rules of METRICS.md, as
applied below, with per-family settings and overrides, and writes spans.
Run: python3 -I classify.py [--show TEXT]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from atoms import load, atoms  # noqa: E402

REPO = "."
TOK = REPO + "/results/algol-60/tokens/"

OUTPUT = {"outstring", "outinteger", "PRINTTEXT", "print", "NLCR", "SPACE"}
ADAPTERS = {"uname", "place", "state", "relations", "digits", "printint",
            "printel", "printseq", "seqplace", "seqstate", "elstate"}
HOLDING = {"examine1", "examine2", "examine3", "examine5", "examine6",
           "equal", "propagate"}
COUNTERS = {"x1", "x2", "x3", "rev1", "rev2", "conc1", "conc2"}
HARNESSVARS = {"n", "cap", "m", "i", "code", "k", "held"} | COUNTERS
OPS = {"∧", "∨", "¬", "(", ")", "[", "]", "true", "false"}

# declared names: class
DECL_COMMON = {
    "n": "H", "cap": "H", "m": "H", "i": "H", "code": "H", "k": "H",
    "held": "H", "x1": "H", "x2": "H", "x3": "H",
    "rev1": "H", "rev2": "H", "conc1": "H", "conc2": "H",
    "pass": "R", "changed": "R", "inconsistent": "P",
    "c1": "P", "c2": "P", "c3": "P",
    "xv": "P", "yv": "P", "zv": "P", "wv": "P", "uv": "P", "vv": "P",
    "xk": "R", "yk": "R", "zk": "R", "wk": "R", "uk": "R", "vk": "R",
    "r1": "R", "r2": "R", "r3": "R",
    "ord": "R",
    "r": "P", "nx": "P", "xs": "P",
    "j": "P", "top": "P", "nel": "P",
    "av": "P", "bv": "P", "cv": "P", "sv": "P", "pv": "P", "rv": "P",
    "ak": "R", "bk": "R", "ck": "R",
    "q1": "R", "q2": "R", "q3": "R", "q5": "R", "q6": "R",
    "defined": "R", "concdef": "R", "rev1def": "R", "rev2def": "R",
    "hd": "P", "ev": "P", "ek": "R",
}

FLAGS = {"xk", "yk", "zk", "wk", "uk", "vk", "ak", "bk", "ck", "ek",
         "r1", "r2", "r3", "q1", "q2", "q3", "q5", "q6", "defined",
         "concdef", "rev1def", "rev2def", "changed", "nx"}


def norm(toks, a, b):
    s = [t[2] for t in toks[a:b + 1]]
    if s and s[0] == ";":
        s = s[1:]
    return " ".join(s)


# Overrides: family -> {(procedure or 'main', atom text): (class, construct, rule)}
OV = {}

OV["P07g"] = {
    ("examine1", "if nx > 0 then"): ("R", "test of whether x is known (has values)", "19"),
    ("examine1", "integer j"): ("P", "local of the test of x's values", "19"),
    ("examine1", ", kept"): ("P", "local of the test of x's values", "19"),
    ("examine1", "else if c1 < 0 then"): ("P", "x times x = c with c negative: no integer square", "19"),
    ("main", "nx := 0"): ("R", "x has no value yet (holding state)", "19"),
    ("main", "if r1 then"): ("R", "the relation is examined while held", "19"),
    ("main", "examine1"): ("R", "call of the evaluator", "19"),
    ("main", "inconsistent := false"): ("P", "initially no contradiction", "1"),
}

OV["P08a"] = {
    ("main", "nel := 3"): ("P", "elements 1..3 are x, y, z (encoding)", "15"),
    ("main", "sv := 0"): ("P", "s empty until stage 6 (encoding)", "15"),
    ("main", "top := rev1 := rev2 := conc1 := conc2 := 0"): ("P", "cell allocator and counters initialised (one statement; top is the encoding's)", "15/13"),
    ("main", "ek [ nel ] := true"): ("R", "element of s marked known (unknowns' representation)", "19"),
    ("examine2", "integer r"): ("P", "rev's result", "19"),
    ("examine6", "integer p , e , w"): ("P", "locals of the decomposition b = s ++ c", "15"),
    ("examine6", "integer w , e , first , last , c"): ("P", "locals of the construction b = s ++ c", "15"),
    ("examine6", "if ¬ inconsistent then"): ("P", "c given or tested only if the elements agreed", "19"),
    ("examine6", "if p = 0 then"): ("P", "b shorter than s: no solution (decomposition)", "15"),
    ("examine6", "if last = 0 then"): ("P", "construction of s ++ c", "15"),
}

OV["P08c"] = {
    ("main", "sv := pv := rv := 0"): ("P", "sequences empty until read (encoding)", "15"),
    ("main", "top := rev1 := rev2 := conc1 := conc2 := 0"): ("P", "cell allocator and counters initialised (one statement; top is the encoding's)", "15/13"),
    ("main", "integer l1 , l2"): ("P", "lengths of the stage-3 constants", "P: stage information"),
    ("conc", "if ¬ concdef then"): ("R", "verdict to wait: conc's definition not arrived", "19"),
    ("conc", "conc := 2"): ("R", "status 'cannot tell'", "19"),
    ("conc", "conc := 1"): ("R", "status 'found'", "19"),
    ("conc", "conc := t"): ("R", "status passed up", "19"),
    ("conc", "integer t"): ("R", "status local", "19"),
    ("conc", ", d"): ("P", "conc's recursive result", "3"),
    ("conc", "if t = 1 then"): ("R", "status test", "19"),
    ("rev", "integer st"): ("R", "status local", "19"),
    ("rev", ", t"): ("R", "status local", "19"),
    ("rev", ", q"): ("P", "rev's conjunct variable q", "3"),
    ("rev", "st := 3"): ("R", "status 'no case yet'", "19"),
    ("rev", "if rev1def then"): ("R", "case 1 arrived? (verdict to wait)", "19"),
    ("rev", "if same ( a , pv ) then"): ("P", "head test of case 1, rev(p, r0)", "2"),
    ("rev", "st := 1"): ("R", "status 'found'", "19"),
    ("rev", "if st ≠ 1 ∧ rev2def then"): ("R", "case 2 arrived, and case 1 did not give r", "19"),
    ("rev", "if a ≠ 0 then"): ("P", "head test of case 2, h followed by l", "2"),
    ("rev", "t := rev ( tl [ a ] , q )"): ("P", "conjunct rev(l, q)", "3"),
    ("rev", "if t = 1 then"): ("R", "status test", "19"),
    ("rev", "t := conc ( q , cons ( hd [ a ] , 0 ) , r )"): ("P", "conjunct conc(q, <h>, r)", "3"),
    ("rev", "if t ≠ 0 then"): ("R", "status test", "19"),
    ("rev", "st := t"): ("R", "status", "19"),
    ("rev", "if st = 3 then"): ("R", "no case gave r: none if all cases arrived, else cannot tell", "19"),
    ("rev", "st := if rev1def ∧ rev2def then 0 else 2"): ("R", "closed verdict once every case has arrived, else wait", "19"),
    ("rev", "rev := st"): ("R", "status returned", "19"),
    ("examine2", "integer t"): ("R", "status local", "19"),
    ("examine2", ", r"): ("P", "rev's result", "19"),
    ("examine2", "t := rev ( sv , r )"): ("P", "the application rev(s, b)", "19"),
    ("examine2", "if t = 1 then"): ("R", "status test", "19"),
    ("examine2", "else if t = 0 then"): ("R", "status test", "19"),
    ("examine2", "if concdef ∧ rev1def ∧ rev2def then"): ("R", "held until every part of the definition has arrived", "19"),
}

FAMILY = {
    "P07a": "P07a", "P07b": "P07b", "P07c": "P07c", "P07d": "P07d",
    "P07f": "P07b", "P07g": "P07g", "P08a": "P08a", "P08c": "P08c",
}
PPROCS = {"cons", "same", "sameel", "conc", "rev", "readseq"}


def split_decls(toks, ats):
    out = []
    for a, b in ats:
        s = a + 1 if toks[a][2] == ";" else a
        if toks[s][2] in ("integer", "Boolean", "boolean") and toks[s + 1][2] not in ("array", "procedure"):
            cur = a
            for k in range(s, b + 1):
                if toks[k][2] == "," and k > cur:
                    out.append((cur, k - 1)); cur = k
            out.append((cur, b))
        else:
            out.append((a, b))
    return out


def classify(path, fam):
    toks = load(path)
    ats = split_decls(toks, atoms(toks))
    texts = [norm(toks, a, b) for a, b in ats]
    first = [toks[a + 1][2] if toks[a][2] == ";" and a < b else toks[a][2] for a, b in ats]
    n = len(ats)
    cls = [None] * n
    info = [None] * n
    # structure: depth and procedure context
    proc = ["main"] * n
    kind = [None] * n
    depth = 0
    stack = []  # (procname, depth at body start, single)
    pending = None
    dep = [0] * n
    for idx in range(n):
        f = first[idx]
        t = texts[idx]
        if f == "procedure" or (f in ("integer", "Boolean", "boolean") and t.split()[1:2] == ["procedure"]):
            kind[idx] = "proc"
            name = t.split()[t.split().index("procedure") + 1]
            proc[idx] = name
            pending = name
            dep[idx] = depth
            continue
        if f == "begin":
            kind[idx] = "begin"
            if pending:
                stack.append((pending, depth, False)); pending = None
            depth += 1
        elif f == "end":
            kind[idx] = "end"
            depth -= 1
        elif pending:
            stack.append((pending, depth, True)); pending = None
        dep[idx] = depth
        proc[idx] = stack[-1][0] if stack else "main"
        if f == "end" and stack and not stack[-1][2] and depth == stack[-1][1]:
            stack.pop()
        if f == "if" or t.startswith("else if"):
            kind[idx] = kind[idx] or "if"
        elif f == "else":
            kind[idx] = "else"
        elif f == "for":
            kind[idx] = "for"
        # single-statement bodies end at the next ';' atom at their depth
        if stack and stack[-1][2] and idx + 1 < n and toks[ats[idx + 1][0]][2] == ";" and depth == stack[-1][1]:
            stack.pop()
    ov = OV.get(fam, {})
    for idx in range(n):
        if kind[idx] in ("begin", "end", "else"):
            continue
        p, t, f = proc[idx], texts[idx], first[idx]
        toklist = t.split()
        key = (p, t)
        if key in ov:
            cls[idx], c, r = ov[key]; info[idx] = (c, r); continue
        if ("main", t) in ov and p == "main":
            cls[idx], c, r = ov[("main", t)]; info[idx] = (c, r); continue
        if kind[idx] == "proc":
            if p in ADAPTERS:
                cls[idx] = "H"; info[idx] = ("output adapter procedure " + p, "13"); continue
            if p in HOLDING:
                cls[idx] = "R"; info[idx] = ("heading of the holding code " + p, "19"); continue
            cls[idx] = "P"; info[idx] = ("heading of " + p + " (transcription / encoding operation)", "3/15"); continue
        if p in ADAPTERS:
            cls[idx] = "H"; info[idx] = ("body of output adapter " + p, "13"); continue
        if any(w in OUTPUT or w in ADAPTERS for w in toklist):
            cls[idx] = "H"; info[idx] = ("printing a tag or the state held", "13; harness README 2.7.3"); continue
        if p == "propagate":
            cls[idx] = "R"; info[idx] = ("propagation loop of the holding code", "19"); continue
        # declarations
        if f in ("integer", "Boolean", "boolean") or (toklist and toklist[0] == ","):
            names = [w for w in toklist if re.match(r"^[A-Za-z]\w*$", w) and w not in ("integer", "Boolean", "boolean", "array")]
            nm = names[0]
            c = DECL_COMMON.get(nm)
            if c is None:
                c = "P"
            cls[idx] = c; info[idx] = ("declaration of " + nm, {"H": "harness README 2.7.5", "R": "19", "P": "1"}[c]); continue
        # counters
        m = re.match(r"^(\w+) := (\w+) \+ 1$", t)
        if m and m.group(1) in COUNTERS:
            cls[idx] = "H"; info[idx] = ("counter", "harness README 2.7.4"); continue
        if re.match(r"^(x1|x2|x3)( := (x1|x2|x3))* := 0$", t):
            cls[idx] = "H"; info[idx] = ("counters initialised", "harness README 2.7.4"); continue
        if t.startswith("held :="):
            cls[idx] = "H"; info[idx] = ("count of held relations, for observe", "13"); continue
        # reads
        mr = re.match(r"^ininteger \( 0 , (.+) \)$", t) or re.match(r"^(.+) := read$", t)
        if mr:
            v = mr.group(1)
            if v in HARNESSVARS or v.startswith("ord"):
                cls[idx] = "H"; info[idx] = ("reading a harness word", "harness README 2.7.1")
            else:
                cls[idx] = "P"; info[idx] = ("reading the stage's constants (stage information)", "harness README 2.7, Not H")
            continue
        if p == "main":
            if f == "for" and ("until m do" in t or "while true do" in t):
                cls[idx] = "H"; info[idx] = ("harness loop (codes / messages)", "harness README 2.7.1-2"); continue
            if re.match(r"^(else )?if k = \d+ then$", t):
                cls[idx] = "H"; info[idx] = ("message dispatch by stage", "harness README 2.7.2"); continue
            if t == "propagate":
                cls[idx] = "R"; info[idx] = ("call of the holding code", "19"); continue
            if re.match(r"^[a-z0-9]+k( := \w+)* := false$", t) or re.match(r"^(r\d|q\d)( := \w+)* := true$", t) or re.match(r"^\w+( := \w+)* := false$", t):
                cls[idx] = "R"; info[idx] = ("initial holding state (known flags, held flags)", "19"); continue
            if re.match(r"^(q\d|defined|concdef|rev1def|rev2def) := true$", t):
                cls[idx] = "R"; info[idx] = ("the stage's relation (or definition) recorded as held/arrived", "19"); continue
            if t == "for j := 1 step 1 until 3 do" or t == "ek [ j ] := false":
                cls[idx] = "R"; info[idx] = ("x, y, z marked unknown", "19"); continue
        if p in PPROCS:
            cls[idx] = "P"; info[idx] = ("body of " + p, "3/15"); continue
        if p == "propagate":
            cls[idx] = "R"; info[idx] = ("propagation loop of the holding code", "19"); continue
        if p in HOLDING or p == "main":
            if kind[idx] == "if":
                cond = toklist[2:-1] if toklist[0] == "else" else toklist[1:-1]
                names = [w for w in cond if re.match(r"^[A-Za-z]\w*$", w)]
                if names and all(w in FLAGS or w in ("e", "f", "true", "false") for w in names) and not any(w in ("≠", "=", "<", ">", "≥", "≤") for w in cond):
                    cls[idx] = "R"; info[idx] = ("test of which places are known / verdict to wait", "19")
                else:
                    cls[idx] = "P"; info[idx] = ("test of a fully known relation", "19")
                continue
            ma = re.match(r"^(\w+)( \[ [^\]]+ \])? := (.*)$", t)
            if ma:
                tgt = ma.group(1)
                if tgt in FLAGS:
                    cls[idx] = "R"; info[idx] = ("records a place as known / relation as no longer held / a change", "19")
                else:
                    cls[idx] = "P"; info[idx] = ("computes a place from the others / gives the verdict of a test", "19")
                continue
            if t.startswith("equal ("):
                cls[idx] = "P"; info[idx] = ("the equation between two elements applied", "19"); continue
            if f == "for":
                cls[idx] = "P"; info[idx] = ("loop over the encoding (++ decomposition or construction, or x's values)", "15"); continue
            if re.match(r"^examine\d$", t):
                cls[idx] = "R"; info[idx] = ("call of an evaluator", "19"); continue
        cls[idx] = "?"; info[idx] = ("UNCLASSED", "")
    # structural atoms
    # if/else header controlled region classes for adapters in main: header H if all controlled are H
    def region(idx):
        """atoms controlled by header idx (if/else/for): until statement ends."""
        j = idx + 1
        if j >= n:
            return []
        if kind[j] == "begin":
            d = 0
            k = j
            while True:
                if kind[k] == "begin":
                    d += 1
                elif kind[k] == "end":
                    d -= 1
                    if d == 0:
                        break
                k += 1
            return list(range(j, k + 1))
        if kind[j] in ("if", "for"):
            r = [j] + region(j)
            return r
        return [j]
    for idx in reversed(range(n)):
        if kind[idx] in ("if", "for") and proc[idx] == "main" and cls[idx] in ("P", "R"):
            reg = [r for r in region(idx) if kind[r] not in ("begin", "end", "else")]
            if reg and all(cls[r] == "H" for r in reg):
                cls[idx] = "H"; info[idx] = ("guard of printing only", "13")
    # begin: class of preceding header if any, else of next atom
    match = {}
    st = []
    for idx in range(n):
        if kind[idx] == "begin":
            st.append(idx)
        elif kind[idx] == "end":
            match[idx] = st.pop()
    lastif = {}
    for idx in range(n):
        k = kind[idx]
        if k == "begin":
            prev = idx - 1
            if prev >= 0 and kind[prev] in ("if", "for", "proc", "else"):
                cls[idx] = cls[prev]; info[idx] = ("begin of the construct introduced before it", "10")
            elif prev < 0:
                cls[idx] = "P"; info[idx] = ("the program block (frame of the transcription)", "1")
            else:
                # bare compound: class of first inner atom
                q = idx + 1
                while kind[q] in ("begin",):
                    q += 1
                cls[idx] = cls[q]; info[idx] = ("compound statement", "10")
        elif k == "else":
            # nearest preceding if-header at same depth
            q = idx - 1
            while q >= 0 and not (kind[q] == "if" and dep[q] == dep[idx]):
                q -= 1
            cls[idx] = cls[q]; info[idx] = ("else of the conditional", "10")
        elif k == "end":
            b = match[idx]
            cls[idx] = cls[b]; info[idx] = ("end of the compound", "10")
        if k == "if" and texts[idx].startswith("else if"):
            pass
    # the outermost program begin/end: H? They enclose everything; class by convention
    spans = []
    for idx, (a, b) in enumerate(ats):
        spans.append({"from": a, "to": b, "class": cls[idx], "construct": info[idx][0] + ": " + texts[idx][:60], "rule": info[idx][1]})
    return toks, ats, texts, cls, info, proc


def merge(spans):
    out = []
    for s in spans:
        out.append(s)
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else None
    toks, ats, texts, cls, info, proc = classify(TOK + which, FAMILY[os.path.basename(which)[:4]])
    for idx, (a, b) in enumerate(ats):
        print(f"{toks[a][1]:4d} {cls[idx]} {proc[idx]:10s} {texts[idx][:90]}  | {info[idx][0][:50]}")
