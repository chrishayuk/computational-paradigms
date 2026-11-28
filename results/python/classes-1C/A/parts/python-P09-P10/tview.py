# Print each source line with its tokens and their indices (read-only).
import sys, csv
REPO = "."
cfgfile = sys.argv[1]
lines = {}
with open(f"{REPO}/results/python/tokens/{cfgfile}.tokens.tsv") as f:
    r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    next(r)
    for row in r:
        lines.setdefault(int(row[1]), []).append((int(row[0]), row[2]))
for n in sorted(lines):
    t = lines[n]
    print(f"L{n} [{t[0][0]}-{t[-1][0]}] " + " ".join(f"{i}:{s}" for i, s in t).replace("<NEWLINE>", "NL").replace("<INDENT>", "IN").replace("<DEDENT>", "DE"))
