# Print a program's source lines with the token index range of each line.
import sys, csv
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
cfgfile = sys.argv[1]  # e.g. core/P10a.py
toks = {}
with open(f"{REPO}/results/python/tokens/{cfgfile}.tokens.tsv") as f:
    r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    next(r)
    for row in r:
        i, line = int(row[0]), int(row[1])
        toks.setdefault(line, []).append(i)
src = open(f"{REPO}/programs/python/{cfgfile}").read().split("\n")
for n, text in enumerate(src, 1):
    if n in toks:
        t = toks[n]
        print(f"{t[0]:5d}-{t[-1]:<5d} {n:4d}| {text}")
    elif text.strip() and not text.strip().startswith("#"):
        print(f"{'':11s} {n:4d}| {text}")
