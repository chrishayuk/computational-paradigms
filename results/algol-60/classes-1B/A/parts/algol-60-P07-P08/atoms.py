"""Segment a token file into atoms (small constructs) for classing.

An atom is a run of tokens forming one construct at the finest grain used:
a simple statement, a conditional's header (if ... then), an else, a for
header (for ... do), a begin, an end (with its end-comment), a procedure
heading with its value and specification parts, a declaration item.
A separator ';' starts the atom after it (METRICS.md rule 20).
"""
import csv, sys

TYPEKW = {"integer", "Boolean", "boolean", "real"}


def load(path):
    toks = []
    with open(path, newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            toks.append((int(row[0]), int(row[1]), row[2]))
    for i, t in enumerate(toks):
        assert t[0] == i
    return toks


def atoms(toks):
    """Return list of (start, end) inclusive index ranges."""
    out = []
    n = len(toks)
    i = 0
    cur = None

    def close(upto):
        nonlocal cur
        if cur is not None and cur <= upto:
            out.append((cur, upto))
        cur = None

    while i < n:
        t = toks[i][2]
        if t in ("if", "then", "else") and cur is not None and any(toks[q][2] == ":=" for q in range(cur, i)):
            seg = [toks[q][2] for q in range(cur, i)]
            first_assign = seg.index(":=")
            after = seg[first_assign:]
            open_ifs = after.count("if") - after.count("else")
            if t == "if" or open_ifs > 0:
                i += 1
                continue
        if t == ";":
            close(i - 1)
            cur = i
            i += 1
            continue
        if t == "begin":
            # a pending lone ';' joins begin
            if cur is not None and toks[cur][2] == ";" and cur == i - 1:
                out.append((cur, i)); cur = None
            else:
                close(i - 1); out.append((i, i))
            i += 1
            continue
        if t == "end":
            if cur is not None and toks[cur][2] == ";" and cur == i - 1:
                # empty statement before end: attach ';' to end
                start = cur; cur = None
            else:
                close(i - 1); start = i
            j = i + 1
            while j < n and toks[j][2] not in (";", "end", "else"):
                j += 1
            out.append((start, j - 1))
            i = j
            continue
        if t == "else":
            close(i - 1)
            if i + 1 < n and toks[i + 1][2] == "if":
                j = i + 1
                while toks[j][2] != "then":
                    j += 1
                out.append((i, j)); i = j + 1
            else:
                out.append((i, i)); i += 1
            continue
        if t == "if" and (cur is None or toks[cur][2] == ";" and cur == i - 1 or cur is not None):
            # if a statement is in progress and is an assignment with a
            # conditional expression (x := if ...), keep it in the statement
            if cur is not None and any(toks[k][2] == ":=" for k in range(cur, i)):
                i += 1
                continue
            start = cur if (cur is not None and cur == i - 1 and toks[cur][2] == ";") else None
            close(i - 1) if start is None else None
            if start is None:
                start = i
            cur = None
            j = i
            depth = 0
            while toks[j][2] != "then" or depth:
                if toks[j][2] == "if" and j != i:
                    depth += 1
                if toks[j][2] == "then" and depth:
                    depth -= 1
                j += 1
            out.append((start, j)); i = j + 1
            continue
        if t == "for":
            start = cur if (cur is not None and cur == i - 1 and toks[cur][2] == ";") else None
            if start is None:
                close(i - 1); start = i
            cur = None
            j = i
            while toks[j][2] != "do":
                j += 1
            out.append((start, j)); i = j + 1
            continue
        if t == "procedure" or (t in TYPEKW and i + 1 < n and toks[i + 1][2] == "procedure"):
            start = cur if (cur is not None and cur == i - 1 and toks[cur][2] == ";") else None
            if start is None:
                close(i - 1); start = i
            cur = None
            j = i
            while toks[j][2] != ";":
                j += 1
            # value and specification parts
            while j + 1 < n and (toks[j + 1][2] == "value" or (toks[j + 1][2] in TYPEKW and toks[j + 2][2] != "procedure" and toks[j + 2][2] != "array")):
                j += 1
                while toks[j][2] != ";":
                    j += 1
            out.append((start, j)); i = j + 1
            continue
        if cur is None:
            cur = i
        i += 1
    close(n - 1)
    # check cover
    seen = []
    for a, b in out:
        seen.extend(range(a, b + 1))
    assert seen == list(range(n)), "atoms do not cover"
    return out


if __name__ == "__main__":
    toks = load(sys.argv[1])
    for k, (a, b) in enumerate(atoms(toks)):
        print(k, toks[a][1], " ".join(t[2] for t in toks[a:b + 1]))
