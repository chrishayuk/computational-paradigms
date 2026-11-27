# Classifier A, swi-prolog, batch 1A (P01-P03): notes

Output: `swi-prolog.json` (made by `build.py`, checked by `verify.py`; the
P02 equivalence check is `check_p02.py`; `summarize.py` and `modediff.py`
are reading aids). The scripts read only the token files, `TEXTS.tsv`,
`batch-log.tsv` and the raw records. Nothing was run but these scripts.

## What I read

Inside the allowed list: `README.md`, `SPECIFICATION.md`, `METRICS.md`,
`PROTOCOL.md`, `AMENDMENTS.md`, `problems/README.md`, `problems/01-03`,
`systems/swi-prolog/README.md` and the first 200 lines of
`measurement.md`, `harnesses/swi-prolog/README.md` and
`S-mechanisms.md`, the programs (their comments included, since they are
in the program files), the raw records (with tools), `batch-log.tsv`,
and the token files.

Outside the list: nothing. I did not read `harnesses/README.md`,
`stages.json`, `record.schema.json`, `S/session-wait.pl` or the
qualification files. The program files' comments point to
`programs/swi-prolog/README.md`, and I did not open it. I did run
`ls` on the repository root, which lists folder names (`calibration`,
`reviews`, `variants`, and others) without their contents. My brief is in
`~/cp-roles/briefs/`, which I was told to read. Nothing else under
`~/cp-roles` (other than `classifier-A` and `classes-A/swi-prolog`) and
nothing under `~/cp-private`, `~/.claude`, `~/.codex` or `~/chris-source`
was opened, apart from the harness writing one long tool output to its own
scratch file, which I then read back (it held `S-mechanisms.md` and the
harness README).

## Tokens: how the classes fall

Every token of the 43 distinct texts (9,980 tokens) is covered once.
`TEXTS.tsv` groups were confirmed token for token. No token's class
differs between the configurations that share a text, so nothing is
classed twice. *session* loads the S mechanism `session-wait.pl`, but none
of these programs calls an undefined procedure, so no program token
depends on it. No program has S tokens.

- **H**: the `unknowns/2` facts, the `stage/3` heads with their `:-`, and
  the `query(_, _).` facts (harness README section 12).
- **P**: the CONSTANTS block entries (the stages' information); the
  transcriptions of conc and rev; the R1-R3 clauses; the stage bodies; the
  clpfd constraints; the `is/2`, `=:=/2` and `mod` evaluations of the
  primitive relations; the clause heads of `sum/3`, `product/3`,
  `sum_known/3`, `product_known/3` and `factor/3`.
- **C**: `:- table` (tabling declaration), cuts (rule 2), the `when/2`
  calls and their conditions (coroutine call; rule 10 puts the goal inside
  in P), `:- set_prolog_flag(occurs_check, true)`.
- **R**: the `nonvar/1` mode tests in `sum/3`, `product/3`,
  `sum_known/3` and `product_known/3` (26 tokens per P02 text in *plain*,
  *tabling* and *coroutines*).

## Hard constructs, and rules I found ambiguous

1. **The nonvar/1 mode tests in P02 (R).** The problem's primitive
   relations have no cases, so rule 2's head-test exemption has nothing to
   attach to, and rule 3 ("mode-faithful transcription") assumes a fixed
   direction. Rule 19 settles exactly this split (each direction's
   computation is P, the tests of which places are known are R), but it is
   written "in imperative programs". I applied it by analogy to Prolog,
   because `sum/3` here is just such an evaluator. The other reading is C
   by rule 1 (removing the tests changes only errors). This is the
   construct most likely to be disputed: 26 tokens per P02 text in plain,
   tabling and coroutines, 208 per configuration. It also decides whether
   coroutines' P02 is *expressible* or *expressible with reformulation*.
   **Rule 19 should say whether it covers declarative mode-dispatching
   code.**
2. **The cuts after the mode tests (C)**, by rule 2. They commit to one
   direction's clause. Without them the clauses also re-test and give
   duplicate solutions.
3. **`:- use_module(library(clpfd))` (P).** No rule classes an import. I
   put it with the constraints it makes meaningful (rules 1 and 12):
   without it, `#=` does not exist. C would also be arguable. 8 tokens per
   constraints/session P02 text.
4. **`:- set_prolog_flag(occurs_check, true)` (C).** Rule 1 would make it
   P, since it changes the solution set. Rule 11 makes the parallel
   declaration (`unknown`, `dynamic`) C because it chooses a reading, and
   that is what this flag does for P01c. I followed rule 11 by analogy. A
   rule for flags that choose a problem's reading is missing.
5. **`memberchk(k(X), Cs)` reading a constant (P).** Under the harness
   contract this is the only way a stage's constant reaches the program,
   and with the following goal it states the stage's information. I class
   it P. memberchk/2 is from library(lists), outside plain's core, and is
   listed (rules 9 and 12).
6. **CONSTANTS entries (P).** The tokenizer counts them, although the
   harness never loads them as program text. They are the stages'
   information.
7. **P01c written as `conc(P, X, X)` (P).** It uses the problem's own
   vocabulary for `<1> ++ x`. Writing `X = [1|X]` would also be P.
8. **Clause full stops.** In a clause whose last body construct is C (the
   coroutines `when/2` wrappers), I gave the `.` the clause's class (P,
   rule 10).

## Outcomes I found hard to class

1. **Bindings read at an exception (plain and tabling P02, R2 first;
   R3R2R1 stage 2).** The stage errs. In the exception hook observe()
   reads `U = 0` (a binding that factor/3's head `factor(C, 0, _)` makes
   when the divisor is unbound) or `U = 2` (from R3), and no relation is
   held. SPECIFICATION 1 counts a binding observe() reads at the end of
   the stage as reported, and names the budget case explicitly. Taking that
   literally, the report is the binding with the other unknowns free, which
   admits invalid assignments, so I classed these **unsound** (6 stages).
   Read as an aborted derivation instead, they would be **none reported**.
   Where observe() read `true` (R1 first), I classed **none reported**.
   **The specification should say whether the "reported at the budget" rule
   also covers errors, and covers tentative bindings of a backtracking
   derivation.**
2. **P03f at the budget.** After the one answer, the search for another
   runs to the budget, and observe() then reads `A` bound to a 182-element
   list of fresh variables. Under the literal rule in 1, that binding would
   make the report unsound. problems/03 states this case outright ("reports
   it and then runs out of budget is *complete* with *budget*"), and I
   followed the problem file, since it is the more specific text. That
   makes my readings in 1 and 2 not quite uniform. I chose to follow the
   letter in each place rather than make them uniform.
3. **Tabling P01c.** Tabling cannot store a cyclic answer (type error in
   `'$tbl_reset'/6`). No answer is delivered, but observe() read
   `X = [1|X]` in the exception hook. By the same rule as 1, the binding
   counts as reported: complete under the rational reading and unsound
   under the finite one, with state *error*. The alternative is none
   reported.
4. **The occurs-check variant reports `false`.** I classed it
   representation *explicit* (an empty set of solutions, no residual),
   complete under the finite reading and unsound under the rational
   reading. The two readings are given in `semantic` and in
   `semantic_by_reading`.
5. **R1 with R2 held (ten triples).** Both clpfd and when/2 hold the two
   relations untouched. I classed them as equivalent (`check_p02.py`:
   u(w+1) = 16 bounds u, and the solutions in the box are exactly the ten)
   and *reducible*, because ten explicit triples leave no relation to
   decide ("fewer relations left to decide"). Whether a ten-way disjunction
   of values counts as "smaller" than two relations is open. *reduced*
   would be the other reading.
6. **when/2 residuals.** Their wait conditions are not simplified (e.g.
   `nonvar(2)`). I treated the condition as control, so it does not count
   toward the residual's size or simplification. *identical to the posed
   information* is true wherever the held goal is the posed relation with
   its constant.
7. **P01b `T = [1, 2|S]`.** The Prolog variable S is not restricted to
   lists. I read the solved form `<1,2> ++ s` as defining s as a sequence,
   which makes it complete.
8. **Not reached (22 stages, plain and tabling P02).** After a stage-1 or
   stage-2 error, each later stage is reposed, and the replay errs again
   before that stage is posed. The record files this as state *error*.
   Following AMENDMENTS 3.2, I classed these *not reached*, naming what
   stopped the run. The record's `restart_cost_source` says "the replay was
   stopped by budget", which is wrong: `budget_exhausted` is false and the
   state is error. This is a wording fault in the harness.
9. **Storage-mode faults.** In plain, coroutines, constraints and session
   P03f, the storage record has state *error* ("HARNESS FAULT: no end event
   for the computation"), because the harness could not parse its own
   at_exception event. That event reads `why: budget` at 1,000,009 steps.
   The answer is the same, so the semantic result agrees. These are the
   only mode differences (4). They are faults of the instrumentation, and
   the storage figures for those stages are unavailable, not 0. A
   measurement discrepancy that is not a classification difference: plain
   P02b.R3R1R2 stage 2 reports 99 steps in storage mode against 7 in the
   behaviour and cost modes, although the harness claims that storage steps
   equal behaviour steps.
10. **Expressibility of P02 in plain and tabling.** I judged it *not
    expressible* for P02a, P02c and five P02b orders, from the programs:
    their only reformulation errs where a relation arrives with fewer than
    two known places. Rule 19 would allow a hand-written holding layer
    for these relations as R in the core, which would make it *expressible
    with reformulation*. No program here has one, and I do not claim that
    one is impossible. R3R1R2 works in plain and tabling for any constants,
    so I judged it *expressible with reformulation*.

## External mechanisms listed

memberchk/2 (library(lists)) in every program; library(clpfd) (`#=`) in
constraints and session P02; when/2 in coroutines P02; `:- table` in
tabling; the occurs_check flag in the P01c variant.

## Summary

**Tokens.** 43 distinct texts, 9,980 tokens:

| class | tokens |
|---|---|
| P | 7,131 |
| H | 1,667 |
| C | 766 |
| R | 416 |
| S | 0 |

Counting each configuration's texts in full (P / C / R / S / H):

| configuration | P | C | R | S | H | total |
|---|---|---|---|---|---|---|
| plain | 2,887 | 80 | 208 | 0 | 687 | 3,862 |
| tabling | 2,887 | 142 | 208 | 0 | 687 | 3,924 |
| coroutines | 3,191 | 624 | 208 | 0 | 687 | 4,710 |
| constraints | 1,831 | 8 | 0 | 0 | 687 | 2,526 |
| session | 1,831 | 8 | 0 | 0 | 687 | 2,526 |

The R tokens are all the P02 nonvar/1 mode tests. The C tokens are cuts,
when/2 calls, table directives and the occurs_check flag.

**Outcomes.** There are 175 behaviour stages (35 per configuration).

- **constraints, coroutines and session:** every P01-P03 stage is complete,
  except P01c, which is complete under one reading and unsound under the
  other in every configuration.
  - P02's undecided stages are held residuals (clpfd or when/2):
    suspended, equivalent, reduced, or reducible for the ten-triple stage.
  - Every P02b order ends in u = 2, v = 14, w = 7.
  - P03f is complete with budget.
- **plain and tabling, P02:** only order R3R1R2 succeeds.
  - In every other order, the first relation that arrives with fewer than
    two known places raises an instantiation error. That gives 9 *none
    reported* in all (4 in plain, 5 in tabling, counting tabling P03f) and
    6 *unsound* (bindings read at the error).
  - 22 later stages are *not reached*.
- **tabling** also errs on P01c (it cannot table a cyclic answer) and on
  P03f (out of table space; *none reported*).

The mode differences are 4 P03f storage records with a harness fault.
