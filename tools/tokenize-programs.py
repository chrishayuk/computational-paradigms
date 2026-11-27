#!/usr/bin/env python3
"""Cut every program of a system into numbered tokens for the classifiers.

    tools/tokenize-programs.py SYSTEM

Runs the frozen tokenizer, calibration/tools/tokens.py, unchanged, on each
program under programs/SYSTEM/ and writes
results/SYSTEM/tokens/<configuration>/<file>.tokens.tsv.

One mapping is applied first, to ALGOL 60's x1 and x1sim texts (.a60) only:
the combining low line (U+0332) that underlines their reserved words is
removed, so that b̲e̲g̲i̲n̲ is cut as the word begin, and c̲o̲m̲m̲e̲n̲t̲ ... ; is
excluded as a comment, as the tokenizer does for the report's .alg texts.
No line is added or removed, so line numbers are the file's own. ALGOL 60
constants files are input read by the program, like the held-out P02's
p02.in, and are not tokenized.
"""
import os, subprocess, sys, tempfile

system = sys.argv[1]
EXT = {".ab1", ".ab2", ".abs", ".pl", ".py", ".alg", ".a60"}
for cfg in sorted(os.listdir(f"programs/{system}")):
    d = f"programs/{system}/{cfg}"
    if not os.path.isdir(d):
        continue
    out = f"results/{system}/tokens/{cfg}"
    os.makedirs(out, exist_ok=True)
    for f in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(f)
        if ext not in EXT:
            continue
        src = f"{d}/{f}"
        if ext == ".a60":
            text = open(src, encoding="utf-8").read().replace("̲", "")
            tmp = tempfile.NamedTemporaryFile("w", suffix=".alg", delete=False, encoding="utf-8")
            tmp.write(text); tmp.close()
            src = tmp.name
        r = subprocess.run([sys.executable, "calibration/tools/tokens.py", src],
                           capture_output=True, text=True, check=True)
        open(f"{out}/{f}.tokens.tsv", "w", encoding="utf-8").write(r.stdout)
