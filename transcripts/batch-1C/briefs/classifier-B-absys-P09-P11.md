# Brief: classifier for absys, batch 1C (P09, P10, P11)

You are one of two independent classifiers (`PROTOCOL.md`, "Roles") for
absys in batch 1C of wave 1, problems P09, P10 and P11. The other classifier is of a different
origin, and you must not look for, or read, its classes. You did not
write any of the programs. You are working in ~/cp-roles/classifier-1C-B, a clone of the public
repository at commit bd43b8d. Do not modify any file in it. Write only to
~/cp-roles/classes-1C-B/absys-P09-P11.

## What you may read

- `README.md`, `SPECIFICATION.md`, `METRICS.md` (above all "Tokens",
  "Classing by construct", "Rules" and "Two classifiers"), `PROTOCOL.md`,
  `AMENDMENTS.md`;
- `problems/README.md` and `problems/09-concurrent-goals.md`, `problems/10-state-replacement.md`, `problems/11-irreversible-effects.md`, `problems/03-reversible-relations.md` (P09 uses loop, rev and conc as in P03), `problems/04-unbounded-alternative.md` (loop as in P04), `problems/05-late-contradiction.md` (P10 uses pick as in P05) (their valid outcomes are the
  standard you judge against);
- `systems/absys/` in full;
- `harnesses/README.md`, `harnesses/stages.json`, `harnesses/record.schema.json`,
  and `harnesses/absys/` in full (the contract, and the S mechanisms
  listed at phase 4);
- the programs, `programs/absys/<configuration>/`, except the author's
  notes (`programs/absys/README.md` and the audits `programs/AUDIT-*.md`);
- the raw run records of these problems,
  `results/absys/<configuration>/<problem>/raw/`, the labelled
  measurement reruns beside them (`raw-rerun-m2/`, where there are any),
  and the logs: `results/absys/batch-log.tsv` (to batch 1B),
  `results/absys/logs/` (one log per job, from batch 1C) and
  `results/absys/rerun-m2-log.tsv`;
- the tokens, `results/absys/tokens/`.

## What you may not read

Anything else, in particular `calibration/`, `reviews/`, `variants/`,
`transcripts/`, any earlier batch's classes and results
(`results/absys/classes/`, `results/absys/classes-*/`, `results/*/*/*.md`, `results/BATCH-*.md`), the
author's notes above, other systems' folders, anything outside ~/cp-roles/classifier-1C-B
except ~/cp-roles/classes-1C-B/absys-P09-P11 (above all `~/cp-roles`, `~/cp-private`, `~/.claude`,
`~/.codex`, `~/chris-source`), and the web. If you come across any of
these by accident, stop reading and say so in your notes.

You may run read-only commands (`cat`, `grep`, `jq`, `python3` on the
records and token files) and write your own checking scripts in ~/cp-roles/classes-1C-B/absys-P09-P11. Do
not run any program or the system itself. Some records are large (hundreds of
MB, mostly verbatim output): read them with tools, not whole. Records
over 50 MB are committed gzip-compressed, as `.json.gz`; read them with
`zcat` or Python's `gzip`.

## 1. Tokens

`results/absys/tokens/<configuration>/<file>.tokens.tsv` lists each
program's tokens, numbered from 0, as the study's frozen tokenizer
(`calibration/tools/tokens.py`; you need not read it) cut them, with
comments excluded. Class those tokens; do not re-tokenize.
`results/absys/tokens/TEXTS-1C-P09-P11.tsv` lists the distinct texts of this batch: class each
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

Every behaviour run of P09, P10 and P11 in the logs has a record. For each one, every
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
  script you write in ~/cp-roles/classes-1C-B/absys-P09-P11;
- the observations of "Observations common to every problem" that the
  record lets you state (unknowns' representation, alternatives held,
  suspended work and its count, any conclusion withdrawn, manual actions).

**Harness faults.** A record named `*.INVALID.json` is one the harness
wrote but that failed its own validation. These are faults of the
harness's step accounting. Classify its stages from it as from any other
record, and set `"harness_fault": true` on each of its entries. Where a
stage was posed by reposing and the record says the replay did not reach
it, the stage is *not reached* (the run stopped at the earlier stage that
failed), whatever its other fields say.

**Measurement reruns.** A record in `raw-rerun-m2/` reruns a cost or
storage run, labelled in its notes, with a fixed measurement build. The
original record beside it stands. Compare both with the behaviour run.

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

## 4. Late definition (P08, where in this batch)

For each P08 program, say which of these it does when a procedure is
applied before its definition has arrived, with the evidence (the
constructs, by token range, and what the records show):

- **code awaited**: the application waits for the definition itself to
  become known, and the definition is information that arrives at its
  stage;
- **permission awaited**: the code is already in the program, and the
  application waits for a condition (a flag, a test) saying that it may
  run;
- **neither**: the application errs, fails, or is otherwise not held.

## 5. Supporting code

For each program, list every supporting mechanism (S) it uses: whether it
is one listed before any program was written (`harnesses/absys/S-mechanisms.md`)
or one the program supplies itself, its name, and its tokens by your
classes.

## Output

Write one JSON object to `~/cp-roles/classes-1C-B/absys-P09-P11/absys.json`:

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
      ],
      "late_definition": [
        {"configuration": "...", "program": "<file>", "kind": "code awaited|permission awaited|neither", "evidence": "..."}
      ],
      "s_mechanisms": [
        {"configuration": "...", "program": "<file>", "mechanism": "...", "listed_at_phase_4": true, "tokens": 0}
      ]
    }

`from` and `to` are inclusive token indices. Use `null` where a field
does not apply. Write valid JSON only, and check that every token of every
text is covered exactly once. Then write, beside it, `~/cp-roles/classes-1C-B/absys-P09-P11/absys.notes.md`:
the constructs and outcomes you found hard to class, and why; any rule you
think ambiguous or wrong; every file you read outside the list above, if
any. End with a short summary of totals by class and of the outcomes.
