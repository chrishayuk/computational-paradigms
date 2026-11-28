# Classifier A (Claude): algol-60, batch 1B, P04-P06

Working copy: `~/cp-roles/classifier-1B-A` at 3c7c778, read only.
Output: `algol-60.json`, made by `build.py` from `specs.py`, `engine.py` and `run.py`.
`compact.py` and `summarize.py` extract records, and `residual_check.py` checks the residuals.

## Texts

I classed the 28 distinct texts of `TEXTS-1B-P04-P06.tsv`, each under its first path. The
report and x1 texts of each program have the same line layout and differ only in their
input and output calls, which are H in both, so one per-line spec (`specs.py`) serves both.
A script checked that both texts get the same classes on every line. Every token of every
text is covered exactly once (`build.py` asserts this). No text needed separate classes for
a second configuration: no configuration has an S mechanism, and the x1sim texts are byte
for byte the x1 texts. Semicolons and commas take the class of the construct that follows
them (rule 20), or of the one before them where `end` or `else` follows.

## Constructs that were hard to class

1. **The success continuation (`found`, `answer`, `second`, `body`, `head`) in P04.** Each
   relation is a procedure that passes each solution to a procedure parameter. I classed the
   parameter, its specifier, its actual arguments and the calls `found` as R (rules 3 and 5:
   an extra argument the problem does not give), and the wrapper procedures `second`, `body`
   and `head` as R too. The calls they wrap are P. This choice is what makes every P04
   sub-problem *expressible with reformulation*. Another reading is that the continuation is
   the search, and so C. I did not take it, because the continuation is an argument the
   relation does not have, not an order or a directive.
2. **Taking a binding back (`xk := false`, `sk := false`, `mk := false` after `found`)** is C,
   by rule 2. It restores the state that the next alternative runs in, which is the
   backtracking. Removing it changes what is held and, in P04d and P04f, the solutions.
   **`top := top - 1`** is C by rule 16.
3. **Mode tests and unused directions in P04.** ALGOL 60 has no unification, so `conseq`,
   `alist` and `equals` test whether each place is known and branch. I classed these tests R
   (by analogy with rule 19's split). I classed a branch P if it is a direction the query
   uses, and R if it is not (rule 3). Directions were found statically from each program's
   own query and its recursion, not from which branches a run reached:
   - P04c uses s = <a> ++ m with both known and with s unknown;
   - P04d and P04f use only s unknown;
   - P04e uses only s known and m unknown.

   So the same procedure text has different classes in different programs. `same` is R in
   P04d to P04f, where it serves only an unused direction (rules 14 and 15 by analogy). This
   is the main source of R in P04, and it is where I expect most disagreement.
4. **P04f, alist-right with s unknown,** calls the body alist(m) before deciding the head
   s = <a> ++ m. I count this as one move (rule 4), with its tokens classed by content. No
   other move or omission was found in this batch.
5. **Holding code in P05 and P06 (rule 19).** The following are R:
   - the flags `picked`, `r1` to `r3`, `changed` and `pass`;
   - the procedures `test` and `propagate`;
   - the evaluators' tests of whether x is known, and their releases of a relation (`r := false`).

   The evaluators' tests and computations of a fully known relation are P, in every
   direction, including the branch of P06's `x = c` evaluator that tests a known x. The
   arrays of pick's values (`xv`, `xa`) are P, as the stated facts (rule 6). I classed the
   loop over the held values inside `test` as R, as part of the holding. That loop could
   instead be read as the conjunction of each comparison with pick's disjunction, which
   would make it P. The holding code is specific to the problem's relations, so the core
   configuration holds and there is no S.
6. **Mixed declarations.** `integer n, cap, m, i, ...` declares harness words, constants and
   counters in one statement. The declarator keyword takes the class of its first
   identifier, and each identifier takes its own. In P06e the loop variable `i` also reads
   the facts, so it is P there. Elsewhere it is H.
7. **The program block's `begin`/`end`, and the inner blocks that size the arrays,** are P
   (rule 10, as the frame of the transcription). One could argue they are H, since the
   harness contract requires one block.
8. **Output adapters with logic.** These are H by rule 13:
   - `if ¬inconsistent then` around the printed answer in P06;
   - the loop that prints the surviving values in P05;
   - `printatom` in P06e3, which writes the problem's atom names into the adapter;
   - the counter `found` in P06e.

## Outcomes that were hard to class

- **x1sim P04a and P04b** were killed by SIGKILL at about 59 s. The record has
  `safety_limit.hit: false` and gives no error text, so I classed the state as *error*, as
  the record does. The likely cause is unbounded recursion exhausting the simulator, but the
  record does not show it. A reviewer may prefer to treat it as an unrecorded safety stop.
  P04b's answer x = 1 had already been printed, so it is *complete*.
- **x1sim P04e and P04f** stopped with "Unknown descriptor of formal argument". In P04e this
  happened before any answer (*none reported*). In P04f it happened after one answer
  (*partial*). It looks like a fault of the reconstructed X1 run-time with procedure
  parameters, and I did not count it against expressibility.
- **P04f** is classed *partial*: 20 answers were collected and 301 printed, out of an
  infinite valid set, and every solution would be reached. For **P04c and P04d** (alist-left)
  no answer is ever produced: *none reported*, then budget.
- **P06c stage 2.** The program reports no answer and "no solution", but its observe block
  still prints `[bind x]1`. I classed it *complete*, since the report denotes the empty set.
  Under a literal reading of SPECIFICATION's "a binding that the system holds is reported if
  observe() can read it", x = 1 would count as reported, and the result would be *unsound*.
  The two readings should be settled.
- **P06a and P06c stage 1.** The held `not (x = 1)` is a residual, *complete* and *reduced*,
  and identical to the posed information. The program's x is an integer variable, but the
  residual it reports does not restrict x, and atoms are integer codes under the systems
  file's encoding. So I did not class it *partial* under P06's note on integer restriction.
  This is open to dispute.
- **P05b stage 1.** `x > 1` is held as a residual: *complete*, *reduced*, identical to the
  posed information. It is *suspended*, with 1 held relation.
- **Empty outcomes** are classed *complete* / *explicit*. These are P05c stages 2-3, P06c
  stage 2 and P06e2. No answers were printed, and "no solution" is in observe.
- **Withdrawn conclusions** (P05a stages 2-3, P05c stage 2) are shown only by their absence.
  No explicit withdrawal is printed.

## Rules I think ambiguous

- Rule 3's "a direction the queries do not use" and rule 19's "which branches a run reaches
  never decides a class" pull in opposite directions for P04's evaluator-like procedures.
  P04 is not staged, so I applied rule 3. A rule for multi-mode procedures in query problems
  would help.
- Nothing says how to class a continuation argument in imperative backtracking: R (extra
  argument) or C (search).
- The empty outcome has no representation class of its own. I used *explicit*.
- How does a binding read by observe interact with an explicit "no solution"? (P06c above.)

## Mode comparison

I compared all 96 cost and storage records with their behaviour runs. Answers, `ended_by`,
states, errors, observe text, problem-defined alternatives and suspended counts agree in
every stage, so `mode_differences` is empty. There are no `*.INVALID.json` records and no
`raw-rerun-m2/` folders for these problems. `results/algol-60/rerun-m2-log.tsv` does not
exist at this commit.

## Late definition and S

There is no P08 in this batch, so `late_definition` is empty. No program uses or supplies
an S mechanism (`S-mechanisms.md` lists none). Each program has one `s_mechanisms` entry,
`none`, with 0 tokens.

## Files read outside the list

- The brief itself, at `~/cp-roles/briefs/`.
- My own tool-output overflow files, under the session's `tool-results` folder. These hold
  only output from my own commands on allowed files.
- No forbidden file was opened. I listed `results/algol-60/` to find the records, which
  showed the name `classes/`, but I did not enter it.
- I wrote one temporary file outside the output folder by mistake:
  `/private/tmp/claude-501/x.txt`, an x1 program with its underlines stripped, used for a
  diff. It has been deleted.

## Summary

**Tokens** (28 texts, 16483 tokens): P 5141, C 108, R 2204, S 0, H 9030.

| program (report / x1) | P | C | R | H |
|---|---|---|---|---|
| P04a, P04b | 92 / 89 | 4 / 4 | 31 / 31 | 155 / 134 |
| P04c | 388 / 382 | 14 / 14 | 63 / 63 | 153 / 138 |
| P04d | 184 / 184 | 14 / 14 | 170 / 170 | 250 / 223 |
| P04e | 299 / 293 | 4 / 4 | 207 / 207 | 147 / 132 |
| P04f | 185 / 185 | 14 / 14 | 209 / 209 | 249 / 222 |
| P05a, P05c | 114 / 102 | 0 | 73 / 73 | 665 / 588 (P05c: 658 / 583) |
| P05b | 87 / 78 | 0 | 59 / 59 | 598 / 529 |
| P06a (= P06c), P06b | 73 / 67 | 0 | 93 / 93 | 409 / 359 |
| P06d | 363 / 354 | 0 | 0 | 319 / 288 |
| P06e1 (= P06e2) | 293 / 269 | 0 | 0 | 265 / 248 |
| P06e3 | 272 / 251 | 0 | 0 | 345 / 316 |

**Outcomes** (72 behaviour stages: 24 per configuration):

- **Semantic:** complete 59, none reported 10, partial 3. Nothing is unsound or
  undetermined.
- **Execution state:** finished 47, suspended 9, budget 10, error 6 (all x1sim P04).
- **report and x1** agree everywhere:
  - P04a, P04c and P04d: none reported, then budget;
  - P04b: x = 1, then budget;
  - P04e: true, finished;
  - P04f: partial, an enumeration that would reach every solution, then budget;
  - all of P05 and P06: complete.
- **Residuals** (P05b stage 1; P06a and P06c stage 1): all *reduced* and identical to the
  posed information.
- **x1sim** matches report on P05 and P06. On P04 it errs:
  - P04a and P04b: SIGKILL, with no text;
  - P04c and P04d: stack overflow;
  - P04e: descriptor fault before any answer;
  - P04f: descriptor fault after one answer.

**Expressibility:**

- Every P04, P05 and P06a-c sub-problem is *expressible with reformulation*:
  - P04: the continuation argument, mode tests and unused directions; P04f also has one move;
  - P05 and P06a-c: holding code by rule 19.
- P06d and P06e1-e3 are *expressible*, with no R tokens.
- The same holds in all three configurations.

**Cost and storage:** no differences from the behaviour runs. **S:** none.
