# SWI-Prolog programs, wave 1, batch 1A (P01–P03)

*Phase 5 (`PROTOCOL.md`, "Implementation"), against `spec-1.0.1` and the
program contract in `harnesses/swi-prolog/README.md`. Every program here was
fixed before any of them was run. None has been run: the only command run on
them is the harness's `check`, which executes nothing, and every file passes
it with no errors and no warnings in its own configuration.*

## Author and provenance

- **Author of every program:** `implementation-swi-prolog`, an agent (Claude
  Opus 5.5, model id `claude-opus-5-5`), working from the public repository
  at `spec-1.0.1` only.
- **Precursor seen:** no. I had not seen the absys E01–E09 programs, the
  `research/e07/` programs, the calibration programs, or any other program
  for these problems.
- **Read:** `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
  `AMENDMENTS.md`, `problems/README.md`, the problem files for P01, P02 and
  P03, `systems/swi-prolog/README.md`, `harnesses/README.md`,
  `harnesses/stages.json`, and `harnesses/swi-prolog/` (its README,
  QUESTIONS, S-mechanisms, `check`, the start of `lib/check.pl`, and two
  of its qualification programs). The SWI-Prolog documentation is cited
  from memory, by section name. I did not open it in the image, since
  that would have meant running a command other than `check` there.
- **S mechanisms used:** none, in any configuration. *session* loads its
  wait-for-definition code (`harnesses/swi-prolog/S/session-wait.pl`) in
  every run. These programs never call an undefined procedure, and never
  call `h_wait/0`, so that code is loaded but never used.

## Layout

One file per configuration and instance, at
`programs/swi-prolog/<configuration>/<instance>.pl`. The instance ids
come from `stages.json` (`P01a`, `P02b.R2R3R1`, `P03f`). Every file follows
the contract: no module, a `PROVENANCE` comment, one `CONSTANTS` block
tagged by stage, `unknowns/2`, `stage/3` and `query/2`.

P02b has one file per order. A relation's constants have to be tagged
with the stage that brings them (contract 2.5), and that stage depends on
the order. Within a configuration, the six P02b files and P02a differ only
in their `CONSTANTS` block and their `stage/3` clauses. Their relation
definitions are the same text.

The named variant `P01c-occurs-check.pl` is the recorded variant that the
systems file asks for ("Flags": P01c is also run with `occurs_check`
`true`). It is the primary P01c text with one added directive. It is in
every configuration's folder.

## Shared texts

Where the same text is the natural program in several configurations, it
is copied byte for byte into each folder:

| sub-problems | plain | tabling | coroutines | constraints | session |
|---|---|---|---|---|---|
| P01a | **A** | A | A | A | A |
| P01b, P01c (+ variant), P03a–P03f | **B** | **B + table** | B | B | B |
| P02a, P02b (6), P02c | **C** | C | **C + when** | **D** | D |

- **A**: plain unification. No relation to table, delay or constrain.
- **B**: conc/3 (and rev/2) transcribed as clauses, and unification.
- **B + table**: B with `:- table conc/3.` (and `rev/2` in P03e and P03f).
  Nothing else changes.
- **C**: each primitive relation a + b = c and a · b = c written as integer
  arithmetic. It computes whichever single place is unknown from the
  other two, or tests the relation when all three are known.
- **C + when**: C, with each relation delayed by `when/2` until two of its
  places are known.
- **D**: library(clpfd) `#=/2` constraints over the unbounded integers,
  with no labeling.

## Per configuration and sub-problem

Every program below is the **primary**, except `P01c-occurs-check.pl`,
which is a **named variant** in every configuration. No sub-problem was
judged *not expressible* in any configuration.

### P01 (unknown equality)

| config | sub-problem | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| all five | P01a | `P01a.pl` (text A) | expressible | memberchk/2 (to read the constant) |
| plain, coroutines, constraints, session | P01b | `P01b.pl` (B) | expressible | memberchk/2 |
| tabling | P01b | `P01b.pl` (B + `:- table conc/3`) | expressible | `:- table`; memberchk/2 |
| plain, coroutines, constraints, session | P01c | `P01c.pl` (B); variant `P01c-occurs-check.pl` | expressible, under both readings (finite: the variant; rational: the primary) | memberchk/2; the variant sets the `occurs_check` flag |
| tabling | P01c | the same, with `:- table conc/3` | expressible | `:- table`; memberchk/2 |

Idioms and their sources:

- Equality is unification, `=/2` (ISO/IEC 13211-1, 8.2.1; SWI-Prolog
  manual, "Comparison and Unification of Terms").
- Sequences are lists, and conc/3 is the two clauses of append/3
  (Clocksin and Mellish, *Programming in Prolog*, 1981, chapter 3;
  Sterling and Shapiro, *The Art of Prolog*, 1986, chapter 3).
- A cyclic term is a rational tree (Colmerauer, "Prolog and infinite
  trees", 1982; SWI-Prolog manual, "Rational trees (cyclic terms)").
- The `occurs_check` flag: SWI-Prolog manual, "Environment Control
  (Prolog flags)".
- `:- table`: SWI-Prolog manual, "Tabled execution (SLG resolution)".
- Constants are read with memberchk/2, as in the contract's example
  (`harnesses/swi-prolog/README.md` 2.7).

### P02 (late information)

| config | sub-problem | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, tabling | P02a, P02b ×6, P02c | `P02a.pl`, `P02b.<order>.pl`, `P02c.pl` (C) | expressible. Each relation is computed by its own arithmetic. The tests of which places are known are R by the reading of `METRICS.md` rule 19 (see ambiguity 4). Where fewer than two places of a relation are known, `is/2` raises its instantiation error. Plain Prolog cannot hold the relation | memberchk/2 |
| coroutines | the same | the same files (C + when) | expressible. `when/2` is C, the knowns tests are R | `when/2`; memberchk/2 |
| constraints, session | the same | the same files (D) | expressible: a direct transcription | library(clpfd); memberchk/2 (in *session*, engines are the harness's, not the program's) |

Idioms and their sources:

- Arithmetic by `is/2` and `=:=/2` (ISO 8.6 and 8.7; SWI-Prolog manual,
  "Arithmetic").
- A three-place integer relation that computes any one place from the
  other two follows SWI-Prolog's own `plus/3` ("Special purpose integer
  arithmetic": at least two arguments must be instantiated). It
  dispatches on `nonvar/1` with the cut.
- Delay until computable, by `when/2` with a disjunction of `nonvar/1`
  conditions (SWI-Prolog manual, "Coroutining"). This follows the delaying
  arithmetic of MU-Prolog and NU-Prolog (Naish, *Negation and Control in
  Prolog*, LNCS 238, 1986).
- `#=/2` in place of `is/2` for integer arithmetic in every direction
  (SWI-Prolog manual, "library(clpfd)"; Triska, FLOPS 2012).

### P03 (reversible relations)

| config | sub-problem | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, coroutines, constraints, session | P03a–P03d | `P03a.pl` … `P03d.pl` (B) | expressible. One definition of conc serves every direction by unification | memberchk/2 |
| plain, coroutines, constraints, session | P03e, P03f | `P03e.pl`, `P03f.pl` (B, with rev/2 as naive reverse) | expressible, in both directions, with the definition and its conjunct order unchanged | memberchk/2 |
| tabling | P03a–P03f | the same, with `:- table conc/3` (and `rev/2` in P03e and P03f) | expressible | `:- table`; memberchk/2 |

Idioms are as for P01. rev/2 is naive reverse by append/3 (Sterling and
Shapiro, chapter 3; Warren's naive-reverse benchmark for DEC-10 Prolog).

## Choices made before any run (rule 4), and alternatives not written

1. **Tabling tables the problem's recursive relations.** In the tabling
   configuration, the primary tables every relation the problem defines
   (conc, rev). Tabling is the mechanism that sets this configuration
   apart. P03 asks "whether the system knows when it has found every
   answer", and SLG completion is SWI-Prolog's mechanism for that. The
   alternative is the untabled plain text. It was not written as a
   variant, because its results would be those of *plain*. P01a and P02
   define no relation, so there is nothing to table, and tabling uses the
   plain text.
2. **P02 in plain.** There were two candidates:
   - the literal `U + V =:= K`, which raises an instantiation error
     whenever any place is unknown;
   - generate-and-test over an enumeration of all integers, which needs a
     generator the problem does not state (C) and goes on to the budget
     on every infinite stage.

   I chose neither. The primary is the plus/3-style relation (text C). It
   computes the one unknown place and holds nothing. Neither alternative
   was written.
3. **P02 in coroutines.** The relation waits until two places are known,
   and is then computed. A simpler candidate, `when(ground(...),
   U + V =:= K)`, which only tests once everything is known, was not
   chosen: it would never derive u = 2 from R3. It was not written.
4. **P02 in constraints and session.** The solver is clpfd, not clpq. clpq
   would solve over the rationals, and the problem is over the integers
   (the systems file). No domain is imposed (`AMENDMENTS.md` 3.4), and
   there is no labeling, since labeling an infinite domain is an error in
   clpfd and the problem does not ask for it.

## Ambiguities, and the readings taken

1. **"conc(⟨⟩, b, b), for every sequence b".** conc's first case is
   restricted to sequences. The transcription `conc([], B, B).` does not
   test that B is a list, which is the standard idiom. I read the
   restriction as carried by the encoding. In P01b stage 1, the answer
   T = [1,2|S] is t = ⟨1,2⟩ ++ s, and ++ is defined only on sequences, so
   s is a sequence by the solved-form reading of `SPECIFICATION.md`,
   "Representation". If the classifiers read the restriction as a guard,
   its absence is one omission (R) in every program that uses conc. The
   alternative is a `seq/1` guard. It would enumerate s in P01b and was
   not written.
2. **P01c, "x = ⟨1⟩ ++ x".** The constant is a sequence (`stages.json`:
   `<seq> ++ x`), so the right-hand side is built by the problem's own
   conc: `conc(P, X, X)`, which says "x is p followed by x". I read this
   as a transcription. The alternative is to write the term `[1|X]`
   directly, but that does not stay generic when the constant changes.
3. **The constants.** Each sequence or integer in a stage's information is
   an entry of the block, under a descriptive name (`conc_first([1, 2])`,
   `r3_addend(10)`), read with memberchk/2. The `[H]` inside rev's
   definition is part of the definition, not a constant.
4. **Rule 19 for a declarative program.** `METRICS.md` rule 19 is written
   for imperative programs. Under it, computing a place from the others
   is P, and the tests of which places are known are R. I applied the
   same reading to the `nonvar/1` dispatch in texts C and C + when, and
   expect the classifiers to decide. If they class that dispatch as more
   than R, P02 in plain, tabling and coroutines becomes "expressible with
   reformulation". The arithmetic itself would still not change meaning
   on any input.
5. **Integers in P02.** The problem says all unknowns are integers. In
   texts C and C + when, integrality comes from integer arithmetic on
   integer constants (`//` only after `mod` gives 0). An unknown that
   stays free, such as w when u = 0 and v = 0 in R2, or a place held by a
   `when/2` goal, is not typed as an integer. I read the problem's
   statement as giving the domain, not as a relation to post. In text D,
   clpfd's domain is the integers.
6. **R2's argument order.** "w · u = v" is written `product(W, U, V)` and
   `W * U #= V`, in the problem's order.
7. **P02b's file names.** Instances are named as `stages.json` names them,
   so the program for `P02b.R2R3R1` is `P02b.R2R3R1.pl`.

## Commands run

- Only `harnesses/swi-prolog/check` was run on the programs, in the pinned
  image, once per configuration and file. All 90 files passed with no
  errors and no warnings.
- No program, interpreter or Prolog system was run on any program or
  fragment.
- File work used the shell, git, and bash/awk/sed scripts that wrote and
  edited these files' text.
- Once, early on, I ran `python3 -c` on the host to list the top-level
  keys of `harnesses/stages.json`. It read the file and executed nothing
  of the study. It is disclosed because the brief allows only `check`.
