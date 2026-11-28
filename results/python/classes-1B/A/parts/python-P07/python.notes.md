# Classifier A (Claude): python, batch 1B, P07. Notes

Output: `python.json`, beside this file. Scripts, all in this folder: `show.py`
(loads a token file), `lines.py` (lists the distinct code lines), `classify.py`
(the line-by-line classing that produced `tokens.json`), `view.py` (prints a
text with each token's class), `summ.py` (pulls the fields of every record
into `summary.json`), `equiv.py` (brute-force check of each residual), and
`build.py` (puts together `python.json` and checks that every token is covered
exactly once). Run with `python3 -B`.

## What I read

Only files on the brief's list: README.md, SPECIFICATION.md, METRICS.md,
PROTOCOL.md (phases to the end), AMENDMENTS.md, problems/README.md,
problems/07, systems/python/README.md, harnesses/stages.json (the P07 entry
and the start of P08), harnesses/python/README.md, S-mechanisms.md,
S/suspend.py, the 21 P07 programs, the 108 P07 raw records (read with
scripts), batch-log.tsv (its P07 lines), and the P07 token files and
TEXTS-1B-P07.tsv. To check whether the holding code is reused across
problems (rule 19), I also read the code of `programs/python/core/P02a.py`
and grepped the core and extended programs for `def decide` and
`class Relation`. Those are programs, so they are on the list. I read
nothing in calibration/, reviews/, variants/, transcripts/,
results/python/classes/, the author's notes, or the other classifier's
folder. I did not read systems/python/measurement.md,
harnesses/README.md (the common contract), or record.schema.json: I did not
need them. `results/python/rerun-m2-log.tsv` does not exist, and P07 has no
`raw-rerun-m2/` folder and no `*.INVALID.json` record.

## Texts

All 21 texts in TEXTS-1B-P07.tsv are distinct, and none is shared between
configurations, so each is classed once under its own path. Within each
configuration the seven programs share one body: the four evaluators
(equal, plus, minus, times), the holding code, and the reporting code. They
differ only in the constants, the names of the unknowns, and the stage block.

## Conventions I adopted

- **Layout.** NEWLINE belongs to the statement it ends. An INDENT or DEDENT
  belongs to the compound statement whose block it opens or closes (rule 10:
  the tokens that introduce and close a construct take its class). So a
  DEDENT at the start of a line may differ in class from the rest of the line.
- **Harness reads inside P constructs.** `s.constants["…"]` and
  `s.params["order"]` are split out as H (harness README s.7 item 3), even
  inside a relation tuple. The tuple around them stays P.
- **Constants block entries** are P: they are the stage's information
  (harness README s.7).

## Constructs that were hard to class

1. **The holding code (rule 19): R or S.** Core's `held` list, `place()`,
   `EVALUATOR` and `decide()`, stdlib-concurrency's `hold()` (its non-thread
   parts), and extended's `Relation` goal wrapper are R by the first bullet
   of rule 19 ("written for the problem's own relations … R, in the core
   configuration"). But `decide()` is word for word the same in core P01a–c,
   P02a–c, P06a–c and P07, and `Relation` is the same in extended's P02 and
   P06 programs. Only the EVALUATOR table is specific to a problem. That
   reuse fits the second bullet ("general over relations, reusable from one
   problem to another … S, and the program belongs to *extended*").
   - I kept R because each copy is written against its own program's
     representation (places as str or int, the module-level `known`, `held`
     and `failed`) and dispatches only on that problem's relations.
   - The S reading would move core's P07 programs into extended. It is
     **classification-sensitive**: about 186 tokens per core program, 230 per
     stdlib-concurrency program and 216 per extended program (the
     decide/place/EVALUATOR/hold/Relation constructs).
   - The rule does not say whether "reusable" means that it *can* be reused
     or that it *is* reused across problems. I think it should say.
2. **Evaluators of relations a sub-problem does not use.** Every program
   carries all four evaluators: equal, plus, minus and times. P07c, for
   instance, uses only plus. Rule 19 makes an evaluator P "in every
   direction". It says nothing about a relation that the sub-problem does not
   have at all. By rule 1, removing such an evaluator changes no reported
   value, so it is not P. It changes no operational behaviour either, so it
   is not C. I classed it R (rule 3, "cases the problem does not give").
   This is the largest single choice in the P totals: 220 to 355 R tokens per
   program. Another classifier may well class it P, and I would expect a
   dispute there.
3. **The evaluator split (rule 19).**
   - **R:** the guards `if a is not None and b is not None:` and
     `if c is None:` (tests of which places are known), and `return None`
     (the verdict that the relation must wait).
   - **P:** every `return` that computes a place or tests a fully known
     relation, and times()'s `if a != 0:`. That test is part of computing
     the other factor (division, or "any value" when c = 0), not a test of
     what is known.
   - **P:** the header `def plus(a, b, c):`, as the relation's own construct.
4. **Freeze calls against rule 19's "verdict to wait".** In extended,
   `q.wait(self, *vars)` inside `Relation.__call__` is both the program's
   record of what the relation waits for (R by rule 19) and a freeze call (C
   by the class table, and S-mechanisms.md says a freeze call is C). I classed
   it **C** and the `if outcome is None:` test around it **R**. In the stage
   block, `q.wait(Relation(...))` and stdlib-concurrency's `pose(...)` are C
   wrappers around a P relation (rule 10). Core's `held.append(...)` and
   `held.extend(...)` are R wrappers (rule 19 holding).
5. **Binding a computed value.** `known.setdefault(p, x)` (core),
   `known[p] = x` (stdlib-concurrency) and `q.bind(p, v)` (extended) store a
   value that the evaluator computed. I classed them R, as the holding code's
   write. Rule 19 counts "gives an unknown its value" as part of the
   evaluator, but here the computation is in the evaluator, which is P, and
   the store happens outside it.
6. **Thread bookkeeping (stdlib-concurrency).**
   - **C:** the `changed` condition, the `count` busy/news counters, the
     `new` flag, `told()`, `pose()` and `settle()`.
   - **R:** `waiting.append`, `waiting.clear` and the evaluation loop in
     `hold()`.
   - The `import threading` line is C. threading is an external mechanism,
     not S.
7. **`from S.suspend import …`** is S (11 tokens): it is the program's only
   code whose role is to supply the listed mechanism. One could argue for C,
   since everything it brings in is used by C calls. `q = Queue()` is C.
   `x = Var("x")` is P: it declares a problem unknown, and the fresh `t` of
   the decomposition counts as transcription.
8. **report() and its extended equivalent** are H by rule 13, the test
   `if failed:` included. That test chooses how to render a verdict already
   computed (printing "no solution" or answering the bindings). It does not
   choose another derivation. `UNKNOWNS` and extended's `unknowns` dict are
   H, because they only name objects for the harness and the answer.
9. **Presentation order.** `for position in s.params["order"]:`, and the
   inner loop over a position's conjuncts, are P: the instance's order is part
   of the problem. Only the `s.params[...]` read is H.

## Outcomes that were hard to class

- **P07e: how "none" is reported.** The program reports none with `print`,
  not `cp.answer`, so the record's answers list is empty. Python's standard
  mechanism for answers is "the values the program prints" (PROTOCOL.md),
  and the failed relation is held in a registered structure. So I classed it
  *complete / explicit* (the empty set, stated) / *finished*, with the
  inconsistency detected. If only `cp.answer` counted, it would be
  *none reported*.
- **P07g: reducible or reduced?** The residual x * x = 9 has 1 relation and 2
  occurrences of x. The explicit "x = 3 or x = -3" has no relation left to
  decide, so I classed it *reducible*. By a literal count of relations, a
  disjunction of two equalities is not obviously smaller. I think the
  definition of "smaller" should say how it treats a disjunction of explicit
  solutions.
- **Reported residuals.** P07b, c, f and g are residuals that count as
  reported (SPECIFICATION, "reported"). Each is held in a registered
  suspended structure, which the program would act on at a later stage:
  decide() runs at every stage, and the queue and threads wake on bindings.
  Each is *identical to the posed information*.
- **Residual equivalence.** Every residual is the posed relations unchanged,
  so equivalence is immediate. equiv.py also checks each one by brute force
  over [-200, 200].
- **Cost and storage runs.** I compared all 72 against their behaviour runs:
  same answers, states, suspended counts, observe.raw, stdout and step
  counts. No stage's classification differs, so `mode_differences` is empty.
- **Harness faults.** None: there is no INVALID record, `harness_faults` is
  empty in every record, and every run is a single fresh attempt.

## Rules I think ambiguous

- Rule 19 against the class table on freeze calls (item 4 above).
- Rule 19's "reusable from one problem to another" (item 1 above).
- How an evaluator of a relation the sub-problem does not use is classed
  (item 2 above).
- The definition of "smaller" for a disjunction of explicit solutions (P07g).

## Summary

**Tokens** (20,363 in 21 texts):

| configuration | P | C | R | S | H | total |
|---|---|---|---|---|---|---|
| core (7) | 989 | 0 | 4,016 | 0 | 1,202 | 6,207 |
| extended (7) | 1,167 | 324 | 3,710 | 77 | 1,443 | 6,721 |
| stdlib-concurrency (7) | 1,000 | 1,474 | 3,759 | 0 | 1,202 | 7,435 |
| **all** | 3,156 | 1,798 | 11,485 | 77 | 3,847 | 20,363 |

R is dominated by two things: the unused evaluators (220 to 355 per
program) and the holding code (186 to 230 per program).

**Outcomes** (36 behaviour runs, each with one stage; the configurations agree on every instance):

| instance | classification |
|---|---|
| P07a, all six orders | complete / explicit / finished. x = 5, y = 4, z = 3, by local propagation one relation at a time |
| P07b | complete / residual / reducible / identical to the posed information / suspended (2 held) |
| P07c | complete / residual / reduced / identical / suspended (1 held) |
| P07d | complete / explicit / finished. w = 7 |
| P07e | complete / explicit (none) / finished. The inconsistency is detected; no 15/2 |
| P07f | complete / residual / inconsistency undetected / identical / suspended (2 held) |
| P07g | complete / residual / reducible / identical / suspended (1 held). Neither ±3 found |

**Other sections.**

- Mode differences: none (72 compared).
- Expressibility: *expressible with reformulation* for every sub-problem in
  every configuration. The relations are P evaluators, but they can be
  stated only with R holding code.
- Late definition: not applicable (no P08 in this batch).
- S mechanisms: extended uses the listed suspension queue (537 tokens,
  listed at phase 4; 11 import tokens in each program). Core and
  stdlib-concurrency use none.
