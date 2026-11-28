"""Print a tokens.tsv one source line per row: line, first index, tokens."""
import sys

rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])][1:]
cur, start, toks = None, None, []
for i, ln, t in rows:
    if ln != cur:
        if cur is not None:
            print(f"{cur:>4} {start:>4}-{int(start)+len(toks)-1:<4} {' '.join(toks)}")
        cur, start, toks = ln, i, []
    toks.append(t)
print(f"{cur:>4} {start:>4}-{int(start)+len(toks)-1:<4} {' '.join(toks)}")
