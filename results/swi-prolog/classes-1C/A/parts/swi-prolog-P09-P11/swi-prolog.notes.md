# Classifier 1C-A, swi-prolog, P09-P11: notes

Classifier A (Claude, an agent). I wrote none of the programs. I did not look
for the other classifier's classes. Nothing was run except read-only Python
over the token files and records. My scripts are in this folder:

- `spec.py`: the token classes, written as construct segments;
- `build_tokens.py`: resolves the segments to token ranges and checks coverage;
- `outcomes.py`: the outcome classes, each checked against its record's answers and states;
- `assemble.py`: writes `swi-prolog.json` and checks coverage again;
- `summarize.py`, `compact.py`, `modecmp.py`: read-only views of the records.

## Files read outside the brief's list

- **`~/.claude/.../tool-results/*.txt` (three files).** These are outside the
  repository, under `~/.claude`, which the brief rules out. The tool harness
  saved the output of three of my own `cat` commands there because they were
  long, and I read them back from there. They held only allowed files:
  `PROTOCOL.md` with the problem files, `systems/swi-prolog/README.md` with
  `measurement.md`, and `harnesses/swi-prolog/README.md`. I read nothing else
  under `~/.claude`.
- I did **not** read `problems/01-unknown-equality.md`, although P03 says "conc,
  as in P01". I took conc to be the usual two cases of append (conc(<>, b, b);
  conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)), which is how the programs write
  it.
- Nothing else. I came across no forbidden file by accident. The
  `qualification/` folder is part of `harnesses/swi-prolog/`, which the brief
  allows, but I only listed it and did not read it.

## Texts

The brief gives 32 distinct texts with 4,794 tokens. I classed each once, and
every token is covered exactly once (checked twice, by two scripts). Each shared
text has the same classes in every configuration that uses it. I checked the one
case where the S mechanism could make a difference: the `:- dynamic`
declarations in the texts that *session* shares with *constraints*. In
*session* an undefined procedure would wait (S/session-wait.pl) rather than
raise an error. The declaration is C by rule 11 either way, so no text needed
separate classes for one configuration.

## Constructs that were hard to class, and the readings I took

1. **The clause terminator `.`.** The harness README makes a `stage/3`,
   `query/2` or `spawned/4` head H "with its `:-`", but says nothing about the
   final `.`. Rule 20 does not apply, because no construct follows it. I gave it
   the class of the clause's head, by rule 10 (the tokens that introduce and
   close a construct take its class): H for stage, query and spawned clauses, P
   for the problem's definition cases, and R for the reformulated
   `sum`/`diff` clauses. That puts 1 H token per stage clause.
2. **`memberchk(const(K), Cs)`, reading a stage's constant.** I classed it P,
   as the stage's information reaching the goal (harness README 2.5). memberchk
   is a library predicate, listed as an external mechanism (rule 12). Someone
   could argue for H as part of the constants contract, but README section 12
   does not list it as H. The same reading covers `member(pick(X), Cs)`: P for
   pick over its closed world (rules 6 and 9).
3. **`:- use_module(library(clpfd))`.** I classed it P. It supplies the
   problem's arithmetic connectives (`#=`, `#>`, `#>=`), and without it the
   program does not mean anything (rule 1). It is listed as an external
   mechanism. C would be a defensible alternative. This choice moves 9 tokens
   in each of 7 constraints texts.
4. **emit is P, not H.** `problems/11` "Rules" says that "emit and commit are
   problem tokens". The harness README section 12 lists every `emit/1` call as
   H. I followed the frozen problem file and say so in each rule field. Taking
   the README's reading would move 5 tokens to H per emit call, in 8 P11 texts.
   **This looks like a conflict between the two documents**, and I think it needs
   an adjudication or an amendment.
5. **The commit stage, `( h_commitment(V) -> committed_value(V, X) ; true )`,
   and `committed_value/2`.** `h_commitment(V)` is H. I classed the rest P,
   since commit is a problem token. This includes `committed_value/2`, which
   parses the harness's verbatim answer into x = v. It is not an output adapter
   under rule 13, because it computes information the report depends on. It is
   input-side adaptation code, which no rule names. R ("a definition the
   problem does not give") would be the main alternative, and would move 35 + 10
   tokens per P11c/P11d text.
6. **P09e plain and coroutines: arithmetic that dispatches on mode.** Rule 19
   is written for imperative programs, but its split of the evaluator is the
   closest rule, so I applied it by analogy. The `is/2` computations are P in
   every direction. The `nonvar/1` tests are R. The cuts are C (the class table
   lists cuts as C, and rule 2 applies). The clause heads of `sum`, `diff`,
   `sum_known` and `diff_known` are R, as cases the problem does not give: the
   problem's `+` is primitive. In coroutines the `when/2` call with its
   condition is C, since it is a coroutine call. The `sum_known(A,B,C)` call
   inside it is R, as part of the holding code. Rule 14 would make the whole
   definition R; I did not apply it, because the definition is not written for
   one direction. **This is the construct I am least sure of** (86 R tokens in
   plain, 124 in coroutines).
7. **A quantity with no value yet (P10b, P10c): `( q(V) -> Q = V ; true )`.**
   I classed the if-then-else frame and `true` R, as a case the problem does
   not give (rule 3), and its contents (`q(V)`, `Q = V`) P. One could read it as
   C (rule 2, `->` commits), but the construct changes the meaning (without it,
   stage 1 of P10b fails) and does not change the order. So I took R over C.
8. **P10d, `held(Y, Rel)` and `forall(held(X, R), call(R))`.** These store a
   stage's relation as data so that a later stage can withdraw it. I classed the
   `held/2` wrappers and the query's interpreter R: holding written for this
   problem's relation, by analogy with rule 19's first bullet. The
   `assertz`/`retract` frames are P, since the systems file names them as core
   "for posing definitions and replacing state". The relation inside (`Y #> K`
   or `Y > K`) is P, and the `freeze` wrapper in coroutines is C. Someone could
   class the mechanism S, since it is general over relations. I did not, because
   it is three small constructs written into the program for one relation, not a
   reusable mechanism the configuration lacks. If it were S, P10d would belong
   to an extended configuration.
9. **P10a/P10b/P10c replacement by `retractall`/`assertz`.** I classed these P,
   as native replacement of a named quantity (systems file core; problems/10
   says only indexing written for the purpose is R). The `:- dynamic`
   declarations are C by rule 11, and are listed. In P10a the declaration
   changes no read (b always has a fact when it is read), so it is C by rule 1 as
   well.
10. **Freeze closers.** In `freeze(Rest, gen(N1, Rest))`, the tokens
    `freeze ( Rest ,` and the closing `)` are C, and the inner goal is P
    (rule 10). The comma before `freeze` is C (rule 20).

## Outcomes that were hard to class

- **P09d1 in coroutines/constraints/session.** The answer is
  `S = [1,2,3|_A], Total = 6, freeze(_A, genu(4,_A))`, in state *suspended*.
  The problem says that reporting total = 6 "as a finished outcome" is unsound.
  This report is not finished: it is conditional on a held producer goal. Under
  the finite reading that goal has no instance, so the whole answer denotes the
  empty set. I classed it *complete / residual / inconsistency undetected*
  (SPECIFICATION separates correctness from simplification). If the held goal
  is ignored and total = 6 is read alone, it would be *unsound*. **This
  outcome is classification-sensitive.**
- **P09d in plain/tabling.** The producer never ends, and sum3 is never called.
  I classed both readings *none reported / budget*. The prefix of s held at the
  budget (1,000,004 elements in plain, 83,333 in tabling, with a free tail) is
  recorded as an observation, not as a report of total.
- **Empty outcomes reported as `false.`** (P09a A in tabling, P09b A, P11d
  stage 3 in the reposed configurations). I classed these *complete /
  explicit*, the empty set given explicitly. SPECIFICATION has no
  representation class for "none".
- **P11d in session (the one unsound outcome).** The commit stage's answer was
  collected on a separate run (QUESTIONS S4), so the selection v = 1 was made
  there. In the incremental engine the commit stage, when first posed, adds
  nothing: `h_commitment/1` succeeds only on replay. At stage 3 the engine
  backtracked through the commit into pick and answered x = 2. Against the
  committed v = 1 the valid outcome is none, so the answer is *unsound*, and the
  effects are *extra* (2 was emitted after commitment). In the reposed
  configurations, commitments replayed as x = v keep the commitment. **This
  looks like a gap between the harness's way of selecting on a separate run
  and the program contract**, and someone should look at it.
- **P11 effects timing.** In one-stage problems I recorded an entry emitted in
  the derivation of the reported answer as "at commitment". Entries emitted
  while the stage-3 run replays stage 1 in P11d come after the commitment of
  stage 2, for outcomes never committed (2, 3), so P11d is *extra* in every
  configuration. Without reposing duplicates, L would be ⟨1, 2, 3⟩.

## Rules I think ambiguous

- **emit as H (harness README 12) versus emit as P (problems/11, Rules).** See
  construct 5 above.
- **Rule 19 applies to "imperative programs" only.** The same question, holding
  or dispatch code for primitive relations, arises in Prolog (P09e). There the
  rule's split is the natural reading, but it is not stated.
- **Nothing classes input adapters** (code that turns a harness value such as a
  commitment string into the program's information). Rule 13 covers output
  only.
- **The terminating `.` of a clause whose head is H** is not covered by README
  section 12 or by rule 20.
- **Representation for an empty outcome** is not defined.

## Mode differences and harness faults

There are no `*.INVALID.json` records and no `raw-rerun-m2/` folders for these
problems. The cost runs agree with the behaviour runs everywhere.

Six storage runs carry a `harness_faults` entry: P09a.BA in plain,
coroutines, constraints and session, P09a.AB in session, and P09d in plain.
They give 8 entries in `mode_differences` (session P09a.AB has two
computations, and P09d is listed once per reading). In each, the budget's at-exception event was
interleaved with another write and could not be parsed. The harness then
recorded the computation as *error* ("HARNESS FAULT: no end event for the
computation") with steps null. In session P09a.AB it also lost B's answer.
These are instrumentation faults, listed in `mode_differences` with
`harness_fault: true`. The steps are unavailable, not 0 (AMENDMENTS 3.1). Other
storage differences (steps null at A's budget in P09a.AB, variable numbers in
error texts) change no class.

## Late definition

There is no P08 in this batch, so `late_definition` is empty.

## Summary

**Tokens (32 texts, 4,794 tokens):**

| class | tokens |
|---|---|
| P | 2,889 |
| H | 1,330 |
| C | 269 |
| R | 306 |
| S | 0 |

Most of the R tokens are in P09e (plain 86, coroutines 124) and P10d (25 in
each of three texts). The rest are in P10b (5) and P10c (6). The C tokens are
freeze/when, tabling and dynamic declarations, and cuts.

**Outcomes: 160 behaviour entries** (per stage and computation; P09d counted
once per reading):

| class | entries |
|---|---|
| complete | 143 |
| none reported | 16 |
| unsound | 1 (session P11d stage 3) |

- **Representation:** 129 explicit, 15 residual, 16 none.
- **Execution state:** 93 finished, 36 alternatives pending, 15 suspended, 12
  budget, 4 error.
- **Effects:** 5 exact (P11a in each configuration) and 15 extra (P11b, P11c and
  P11d in each configuration).
- **Mode differences:** 8 entries from 6 storage runs, all harness faults.

**S mechanisms.** session-wait.pl is loaded in each of the 13 session programs
but never exercised. No program supplies S of its own.
