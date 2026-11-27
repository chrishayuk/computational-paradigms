# Brief for a held-out calibration classifier

You are one of two independent classifiers in a research study. Do not
look for, or read, any other classifier's classes. Do not read
`calibration/README.md`, `calibration/programs/`, `calibration/classes/`,
`calibration/round-2/`, `calibration/agreement.txt`,
`calibration/held-out/programs/README.md` (the author's notes),
`calibration/held-out/classes/` or `reviews/`. Do not modify any file in
the repository.

Read `SPECIFICATION.md`, `METRICS.md` (above all "Tokens", "Classing by
construct" and "Rules"), `PROTOCOL.md`, the problem file
`problems/02-late-information.md`, and `systems/python/README.md` and
`systems/algol-60/README.md` for their cores.

The programs are `calibration/held-out/programs/python/p02.py` and
`calibration/held-out/programs/algol-60/p02.alg` (with its input
`p02.in`), and their outputs beside them (`.out`). For each, the file
`calibration/held-out/tokens/<system>/<file>.tokens.tsv` lists its tokens,
numbered from 0, as one fixed tokenizer cut them. Class those tokens: do
not re-tokenize. Comments are already excluded.

## 1. Tokens

For every program, cover **every** token index exactly once with spans,
each span one construct, given one class from METRICS.md:

- **P** problem; **C** control; **R** reformulation; **S** supporting
  code; **H** harness.

Class by construct (rule 10 for nested constructs). Where a rule decides
the class, name it.

## 2. Outcomes

For each program, and for each sub-problem and order it runs (P02a, the
six orders of P02b, P02c), classify the reported outcome after **every
stage** on the semantic axis and the representation axis of
`SPECIFICATION.md`, against the problem file's valid outcomes, with the
simplification flag where it applies. Name the rule or section you used.

## Output

Write one JSON object to the output path you are given:

    {
      "tokens": {
        "python/p02.py": [{"from": 0, "to": 12, "class": "P", "construct": "R1", "rule": "3"}, ...],
        "algol-60/p02.alg": [...]
      },
      "outcomes": {
        "python/p02.py": [{"run": "P02a", "stage": 1, "semantic": "...", "representation": "...", "simplification": "...", "rule": "..."}, ...],
        "algol-60/p02.alg": [...]
      }
    }

`from` and `to` are inclusive token indices. For P02b, name each run by
its order, as `P02b R3,R1,R2`. Write valid JSON only. Then write, beside
it, a short notes file (same name, `.notes.md`) listing the constructs and
outcomes you found hard to class, and why, and any rule you think is
ambiguous or wrong.
