"""Size of each S mechanism, by METRICS.md "Tokens": lexical tokens from
Python's tokenize, with comments, docstrings (rule 17), non-significant line
ends (NL), the encoding and the end marker not counted; NEWLINE, INDENT and
DEDENT, which are significant layout, are counted as one token each.
Lines: all lines of the file, and the code lines (lines holding a counted
token other than layout)."""
import io
import os
import tokenize

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER}
LAYOUT = {tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT}


def measure(path):
    src = open(path, encoding="utf-8").read()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    counted, prev = [], tokenize.NEWLINE
    for i, t in enumerate(toks):
        if t.type in SKIP:
            continue
        nxt = next((u for u in toks[i + 1:] if u.type not in SKIP), None)
        # a docstring: a string that is a whole statement
        if t.type == tokenize.STRING and prev in LAYOUT and nxt is not None and nxt.type == tokenize.NEWLINE:
            prev = "docstring"
            continue
        if t.type == tokenize.NEWLINE and prev == "docstring":
            prev = tokenize.NEWLINE
            continue
        counted.append(t)
        prev = t.type
    lines = {t.start[0] for t in counted if t.type not in LAYOUT}
    return len(src.splitlines()), len(lines), len(counted)


def main():
    print("%-14s %6s %11s %7s" % ("mechanism", "lines", "code lines", "tokens"))
    for f in ("search.py", "suspend.py", "propagate.py"):
        print("%-14s %6d %11d %7d" % ((f,) + measure(os.path.join(S, f))))


if __name__ == "__main__":
    main()
