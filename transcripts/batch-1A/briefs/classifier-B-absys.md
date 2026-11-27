# Brief: classifier for absys, batch 1A (P01–P03)

You are one of two independent classifiers (`PROTOCOL.md`, "Roles") for
absys in batch 1A of wave 1. The other classifier is of a different
origin, and you must not look for, or read, its classes. You did not
write any of the programs. You are working in ~/cp-roles/classifier-B, a clone of the public
repository at commit 628a324. Do not modify any file in it. Write only to
~/cp-roles/classes-B/absys.

## What you may read

- `README.md`, `SPECIFICATION.md`, `METRICS.md` (above all "Tokens",
  "Classing by construct", "Rules" and "Two classifiers"), `PROTOCOL.md`,
  `AMENDMENTS.md`;
- `problems/README.md`, `problems/01-unknown-equality.md`,
  `problems/02-late-information.md`, `problems/03-reversible-relations.md`
  (their valid outcomes are the standard you judge against);
- `systems/absys/` in full;
- `harnesses/README.md`, `harnesses/stages.json`, `harnesses/record.schema.json`,
  and `harnesses/absys/` in full (the contract, and the S mechanisms
  listed at phase 4);
- the programs, `programs/absys/<configuration>/`, except the author's
  notes (`programs/absys/README.md` and `programs/AUDIT-1A.md`);
- the raw run records, `results/absys/<configuration>/P0?/raw/`, and the
  run log `results/absys/batch-log.tsv`;
- the tokens, `results/absys/tokens/`.

## What you may not read

Anything else, in particular `calibration/`, `reviews/`, `variants/`, the
author's notes above, other systems' folders, anything outside ~/cp-roles/classifier-B
except ~/cp-roles/classes-B/absys (above all `~/cp-roles`, `~/cp-private`, `~/.claude`,
`~/.codex`, `~/chris-source`), and the web. If you come across any of
these by accident, stop reading and say so in your notes.

You may run read-only commands (`cat`, `grep`, `jq`, `python3` on the
records and token files) and write your own checking scripts in ~/cp-roles/classes-B/absys. Do
not run any program or the system itself. Some records are large (up to
40 MB, mostly verbatim output): read them with tools, not whole.

## 1. Tokens

`results/absys/tokens/<configuration>/<file>.tokens.tsv` lists each
program's tokens, numbered from 0, as the study's frozen tokenizer
(`calibration/tools/tokens.py`; you need not read it) cut them, with
comments excluded. Class those tokens; do not re-tokenize.
`results/absys/tokens/TEXTS.tsv` lists the distinct texts: class each
text once, under its first path. A text shared by several configurations
is classed once for all of them, unless a token's class would differ
between them (an S mechanism present in one and not another, for
instance). Then also class it separately under that configuration's path,
and say why in your notes.

For every text, cover **every** token index exactly once with spans, each
span one construct, given one class from `METRICS.md`: **P** problem,
**C** control, **R** reformulation, **S** supporting code, **H** harness.
Class by construct (rule 10 for nested constructs). Where a rule decides
the class, name it.

## 2. Outcomes

Every behaviour run in `batch-log.tsv` has a record. For each one, every
configuration, instance and program (named variants included), classify
**every stage** against the problem file's valid outcomes for that
instance:

- **semantic** (`SPECIFICATION.md`, Outcomes, 1);
- **representation** (2), and for a residual the **simplification**
  (*reduced*, *reducible*, *inconsistency undetected*), the flag
  **identical to the posed information** (true or false), and the
  residual's size beside the input's;
- **execution state** (3): one or more classes;
- **residual equivalence**: for a residual or solved form, whether it is
  equivalent to the valid outcomes, and your reasoning, by hand or by a
  script you write in ~/cp-roles/classes-B/absys;
- the observations of "Observations common to every problem" that the
  record lets you state (unknowns' representation, alternatives held,
  suspended work and its count, any conclusion withdrawn, manual actions).

Apply `AMENDMENTS.md` 3: a stage never reached is *not reached*, with
what stopped the run, not a failure of its own; a missing measurement is
unavailable, not 0. Judge a finite domain the program imposes against the
problem's own domain (3.4).

For the cost and storage runs, do not class every stage again. Compare
each with the behaviour run of the same configuration, instance and
program, and list only the stages whose classification differs, with
both.

## 3. Expressibility

For each configuration and sub-problem (and direction, for a relation
used in several), give your own judgement of expressibility
(`SPECIFICATION.md`, Outcomes), from the programs and your R tokens:
*expressible*, *expressible with reformulation*, or *not expressible*,
with the reason.

## Output

Write one JSON object to `~/cp-roles/classes-B/absys/absys.json`:

    {
      "tokens": {
        "<configuration>/<file>": [{"from": 0, "to": 12, "class": "P", "construct": "...", "rule": "..."}, ...]
      },
      "outcomes": [
        {"configuration": "...", "instance": "P01a", "program": "<file>", "record": "<path of the record>",
         "stage": 1, "reached": true, "semantic": "complete", "representation": "residual",
         "simplification": "reduced", "identical_to_posed": false, "residual_size": "...",
         "execution_state": ["suspended"], "residual_equivalence": "...", "observations": "...", "rule": "..."}
      ],
      "mode_differences": [
        {"configuration": "...", "instance": "...", "program": "...", "mode": "cost", "record": "...",
         "stage": 2, "behaviour": {...}, "this_mode": {...}, "note": "..."}
      ],
      "expressibility": [
        {"configuration": "...", "subproblem": "P01a", "direction": null, "expressibility": "...", "reason": "..."}
      ]
    }

`from` and `to` are inclusive token indices. Use `null` where a field
does not apply. Write valid JSON only, and check that every token of every
text is covered exactly once. Then write, beside it, `~/cp-roles/classes-B/absys/absys.notes.md`:
the constructs and outcomes you found hard to class, and why; any rule you
think ambiguous or wrong; every file you read outside the list above, if
any. End with a short summary of totals by class and of the outcomes.
