# Brief for a calibration classifier

You are one of two independent classifiers in a research study. Do not
look for, or read, any other classifier's classes. Do not read
`calibration/programs/README.md` (the author's notes), `calibration/classes/`
or `reviews/`. Do not modify any file in the repository.

Read `SPECIFICATION.md`, `METRICS.md` (above all "Tokens", "Classing by
construct" and "Rules"), `PROTOCOL.md`, the problem files
`problems/01-unknown-equality.md`, `problems/03-reversible-relations.md` and
`problems/13-deterministic-scale.md`, and each system's
`systems/<system>/README.md` for its core.

The programs are in `calibration/programs/<system>/`. For each, the file
`calibration/tokens/<system>/<file>.tokens.tsv` lists its tokens, numbered
from 0, as one fixed tokenizer cut them. Class those tokens: do not
re-tokenize. Comments are already excluded.

For every program, cover **every** token index exactly once with spans,
each span one construct, given one class from METRICS.md:

- **P** problem: the definitions as the problem gives them, the stage
  information, connectives, the query; mode-faithful transcription (rule 3);
- **C** control;
- **R** reformulation;
- **S** supporting code;
- **H** harness: posing queries, printing, collecting answers, budgets.

Class by construct (rule 10 for nested constructs). Where a rule decides
the class, name it.

Write one JSON object to the output path you are given, mapping each
program's path relative to `calibration/programs/` (for example
`"python/p03.py"`) to a list of spans:

    {"from": 12, "to": 30, "class": "P", "construct": "conc case 2", "rule": "3"}

`from` and `to` are inclusive token indices. Write valid JSON only. Then
write, beside it, a short notes file (same name, `.notes.md`) listing
the constructs you found hard to class, and why, and any rule you think is
ambiguous or wrong.
