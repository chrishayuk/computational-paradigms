"""Cut a calibration program into numbered tokens, the same for every
classifier, so that classes can be compared token by token.

    python3 tokens.py PROGRAM > PROGRAM.tokens.tsv

Each line: index, line number, token. Comments and whitespace are not
tokens. Python is cut by its own tokenize module, with NEWLINE, INDENT and
DEDENT kept as significant layout (METRICS.md, Tokens). Other languages are
cut by one shared lexical rule: identifiers and keywords, numbers, quoted
strings, the multi-character operators listed below, and single
characters otherwise.
"""
import io
import re
import sys
import tokenize

OPS = sorted("""
:- --> -> \\+ =.. == \\== =:= =\\= =< >= <= := ++ ** // /\\ \\/ << >> => != ≠ ≤ ≥ ⊃ ≡ ¬ ∧ ∨ ↑ ×
""".split(), key=len, reverse=True)

COMMENT = {
    ".pl": [r"%[^\n]*", r"/\*.*?\*/"],
    ".abs": [r"%[^\n]*"], ".ab1": [r"%[^\n]*"], ".ab2": [r"%[^\n]*"],
    # ALGOL 60: `comment ... ;` and the text after `end` up to ; end or else
    ".alg": [r"\bcomment\b[^;]*;"],
}


def python_tokens(text):
    skip = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER}
    prev = tokenize.NEWLINE
    toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    for k, t in enumerate(toks):
        if t.type in skip:
            continue
        # a docstring: a string standing alone as a statement (METRICS.md, rule 17)
        nxt = next((u.type for u in toks[k + 1:] if u.type not in skip), None)
        if t.type == tokenize.STRING and prev in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT) and nxt == tokenize.NEWLINE:
            continue
        prev = t.type
        name = {tokenize.NEWLINE: "<NEWLINE>", tokenize.INDENT: "<INDENT>",
                tokenize.DEDENT: "<DEDENT>"}.get(t.type, t.string)
        yield t.start[0], name


def generic_tokens(text, ext):
    for pat in COMMENT.get(ext, []):
        text = re.sub(pat, lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    ops = "|".join(re.escape(o) for o in OPS)
    rx = re.compile(r"""
        (?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\\n]|\\.)*'|`[^']*')
      | (?P<num>\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)
      | (?P<id>[A-Za-z_][A-Za-z0-9_]*'*)
      | (?P<op>""" + ops + r""")
      | (?P<ch>\S)
    """, re.X)
    line = 1
    pos = 0
    for m in rx.finditer(text):
        line += text.count("\n", pos, m.start())
        pos = m.start()
        yield line, m.group(0)


def main(path):
    text = open(path, encoding="utf-8").read()
    ext = path[path.rfind("."):]
    toks = python_tokens(text) if ext == ".py" else generic_tokens(text, ext)
    print("index\tline\ttoken")
    for i, (ln, tok) in enumerate(toks):
        # a token may hold a newline or a tab (a multi-line string): escape them
        tok = tok.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
        print(f"{i}\t{ln}\t{tok}")


if __name__ == "__main__":
    main(sys.argv[1])
