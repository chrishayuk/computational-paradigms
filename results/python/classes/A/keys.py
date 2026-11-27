# List distinct (scope, stripped source line) keys of the token-bearing lines of every text.
import csv, os, collections
REPO = "/Users/christopherhay/cp-roles/classifier-A"
TOK = REPO + "/results/python/tokens"
def texts():
    rows = list(csv.reader(open(TOK + "/TEXTS.tsv"), delimiter="\t"))[1:]
    return [r[0] for r in rows]
def scopes(src_lines):
    sc, cur = {}, "<top>"
    for i, l in enumerate(src_lines, 1):
        if l and not l[0].isspace() and not l.startswith("#"):
            if l.startswith("def ") or l.startswith("class "):
                cur = l.split()[1].split("(")[0].rstrip(":")
            else:
                cur = "<top>"
        sc[i] = cur
    return sc
def load(text):
    src = open(REPO + "/programs/python/" + text, encoding="utf-8").read().split("\n")
    toks = list(csv.reader(open(TOK + "/" + text + ".tokens.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))[1:]
    toks = [(int(a), int(b), c) for a, b, c in toks]
    return src, toks
def linekey(toks, ln):
    return " ".join(tk for _, l, tk in toks if l == ln and tk not in ("<INDENT>", "<DEDENT>", "<NEWLINE>"))
if __name__ == "__main__":
    keys = collections.Counter()
    for t in texts():
        src, toks = load(t); sc = scopes(src)
        lines = sorted({ln for _, ln, tk in toks if tk not in ("<INDENT>", "<DEDENT>")})
        for ln in lines:
            keys[(sc[ln], linekey(toks, ln))] += 1
    print(len(keys))
    for k, v in sorted(keys.items()): print(v, k)
