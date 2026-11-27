# SWI-Prolog programs, wave 1, batches 1A (P01–P03) and 1B (P04–P08)

The sections up to "Batch 1B" are batch 1A's, unchanged. Batch 1B's are
in "Batch 1B (P04–P08)" below.

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

---

# Batch 1B (P04–P08)

*Phase 5, against `spec-1.0.1` (repository at `651a55b`). Every program of
this batch was fixed before any was run. None has been run: the only
command run on them is the harness's `check`, which executes nothing.
All 145 files pass it with no errors. The only warnings are in P08 (40,
listed under "check" below).*

## Author and provenance (1B)

- **Author of every program:** `implementation-swi-prolog`, an agent (Claude
  Opus 5.5, model id `claude-opus-5-5`), working from the public repository
  only, with no context from earlier work.
- **Precursor seen:** no. I had not seen the absys E01–E09 programs, the
  `research/e07/` programs, the calibration programs, or any other program
  for P04–P08. The only programs I read were this system's batch 1A
  programs (`P01c.pl`, `P02a.pl`, `P02b.R2R3R1.pl`, `P02c.pl`,
  `tabling/P03e.pl`) and one harness qualification program
  (`x09-count.pl`).
- **Read:** `README.md`, `PROTOCOL.md`, `SPECIFICATION.md`, `METRICS.md`,
  `AMENDMENTS.md`, `problems/README.md`, the problem files of P04–P08,
  `systems/swi-prolog/README.md`, `harnesses/README.md` (in part),
  `harnesses/stages.json` (P01 and P04–P08), and from
  `harnesses/swi-prolog/`: `README.md`, `QUESTIONS.md`, `S-mechanisms.md`,
  `S/session-wait.pl`, `check`, and parts of `run` and `lib/harness.pl`
  found by grep (instance lookup, term quoting, `h_param/2`). I opened no
  SWI-Prolog documentation in the image. It is cited from memory, by
  section name.
- **Seen by accident:** once, a listing of the file *names* at the top of
  the session's scratchpad directory, which holds files of other sessions
  (names such as `classifier-a`, `p12.pl`). I opened none of them and
  worked from then on in a subdirectory of my own.
- **S mechanisms used:** only in *session* P08, where the configuration's
  wait-for-undefined-procedure code (`harnesses/swi-prolog/S/session-wait.pl`)
  is what an application of a relation not yet defined meets. The programs
  call no S of their own, and never call `h_wait/0` directly. No other
  program of this batch calls an undefined procedure.

## Layout (1B)

One file per configuration and sub-problem, at
`programs/swi-prolog/<configuration>/<id>.pl`, with the same contract as in
1A. The exceptions:

- **P07a**: one file, `P07a.pl`, serves all six instances (`P07a`,
  `P07a.132`, `P07a.213`, `P07a.231`, `P07a.312`, `P07a.321`). All of its
  constants come in its one stage, so (unlike P02b) the order does not
  change the CONSTANTS block, and the harness contract says orders come
  from `h_param/2` (harness README 2.5; common contract 11.3). The program
  reads `h_param(order, Order)` and poses the relations in that order.
- **P08**: each sub-problem also has the named variant
  `<id>-unknown-fail.pl` in every configuration folder: the systems file's
  recorded variant ("Flags": "P08 records the result, and a variant with
  `fail`, which corresponds to the closed reading"). It is the primary
  text plus one directive, `:- set_prolog_flag(unknown, fail).`
- P04d, P04f and P08b have no CONSTANTS block, as `stages.json` and the
  contract say (`constants.how = none`).

## Shared texts (1B)

Copies are byte for byte. **Bold** marks where a text is defined.

| sub-problems | plain | tabling | coroutines | constraints | session |
|---|---|---|---|---|---|
| P04a–P04f | **E** | **E + table** | E | E | E |
| P05a, P05b | **F** | F | **F + freeze/dif** | **G** | G |
| P05c | **H** | H | H | H | H |
| P06a, P06b, P06c | **I** | I | **J** | J | J |
| P06d, P06e1–P06e3 | **K** | **K + table** | K | K | K |
| P07a–P07g | **C** | C | **C + when** | **D** | D |
| P08a, P08b, P08c (+ variants) | **L** | L | L | L | L |

- **E**: loop/1 and alist/1 transcribed as clauses, the disjunction by
  `;/2` in the order written.
- **E + table**: E with `:- table loop/1.` (P04a, P04b) or
  `:- table alist/1.` (P04c–P04f).
- **F**: pick by `member(pick(X), Cs)` over the facts; x > k by `>/2`;
  x ≠ k by `\=/2`.
- **F + freeze/dif**: x > k by `freeze(X, X > K)`; x ≠ k by `dif(X, K)`.
- **G**: x > k by `X #> K` (clpfd, no domain, no labeling); x ≠ k by
  `dif(X, K)`.
- **H**: P05c has only pick and equality (unification), so one text serves
  every configuration.
- **I**: not (x = k) by `\+ X = K`. **J**: by `dif(X, K)`.
- **K**: mem/2, setdiff/3 and nonmajor/1 transcribed as clauses, not R by
  `\+`. P06e asserts its closed world (below).
- **K + table**: K with `:- table mem/2, setdiff/3.` (P06d) or
  `:- table nonmajor/1.` (P06e).
- **C, C + when, D**: as in 1A (P02), with the same sum/product/factor text
  and a diff/3 relation for a − b = c written the same way.
- **L**: definitions asserted, clause by clause, by the stage that brings
  them. No declaration of rev or conc before then.

## Per configuration and sub-problem (1B)

Every file is the **primary** for its configuration and sub-problem,
except `P08a-unknown-fail.pl`, `P08b-unknown-fail.pl` and
`P08c-unknown-fail.pl`, which are **named variants** in every
configuration. I judged no sub-problem *not expressible* in any
configuration.

### P04 (unbounded alternative)

| config | sub-problems | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, coroutines, constraints, session | P04a–P04f | text E | expressible: a transcription of loop, both alists and the disjunctions, in the presentation order | memberchk/2 (P04a, b, c, e: to read the constant) |
| tabling | P04a–P04f | text E + table | expressible | `:- table`; memberchk/2 |

Idioms: clauses read as the least relation (ISO 7.5; Clocksin and
Mellish, ch. 1); `;/2` tried in order (ISO 7.8.6); lists for sequences, and
`[a|M]` for ⟨ᴀ⟩ ++ m (Clocksin and Mellish, ch. 3; Sterling and Shapiro,
ch. 3); `:- table` (SWI-Prolog manual, "Tabled execution (SLG
resolution)"). Coroutines and constraints have nothing to delay or
constrain here, so they use the plain text.

### P05 (late contradiction)

| config | sub-problems | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, tabling | P05a, P05b | text F | expressible. With x unknown (P05b stage 1), `>/2` raises an instantiation error: that is the configuration's result, not a reformulation | member/2, memberchk/2 |
| coroutines | P05a, P05b | text F + freeze/dif | expressible | freeze/2, dif/2; member/2, memberchk/2 |
| constraints, session | P05a, P05b | text G | expressible | library(clpfd) `#>/2`; dif/2; member/2, memberchk/2 |
| all five | P05c | text H | expressible | member/2, memberchk/2 |

Idioms: a closed-world relation as facts, enumerated by backtracking with
member/2 over the stage's constants (the contract's example, README 2.7);
`>/2` (ISO 8.7); `\=/2` (ISO 8.2.3); freeze/2 and dif/2 (SWI-Prolog
manual, "Coroutining"; dif after Prolog II, Colmerauer 1982); clpfd `#>`
(SWI-Prolog manual, "library(clpfd)"; Triska 2012).

### P06 (negation)

| config | sub-problems | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, tabling | P06a, P06b, P06c | text I | expressible: not is transcribed as negation as failure, the core's negation (whether it is sound with x unknown is the result) | memberchk/2 |
| coroutines, constraints, session | P06a, P06b, P06c | text J | expressible | dif/2; memberchk/2 |
| plain, coroutines, constraints, session | P06d | text K | expressible | memberchk/2 |
| tabling | P06d | text K + table | expressible | `:- table`; memberchk/2 |
| plain, coroutines, constraints, session | P06e1, P06e2, P06e3 | text K | expressible | `:- dynamic` (C by rule 11, listed), assertz/1, forall/2, member/2; memberchk/2 (P06e1, P06e2) |
| tabling | P06e1–P06e3 | text K + table | expressible | the same, and `:- table` |

Idioms: `\+/1` (ISO 8.15.1; Clark, "Negation as failure", 1978); dif/2 as
the sound negation of equality (SWI-Prolog manual, "Coroutining"); mem/2
as member/2 (Sterling and Shapiro, ch. 3); a closed world as facts in
the database by assertz/1 with a dynamic declaration (contract 2.5; ISO
8.9.2); `:- table`.

### P07 (simultaneous constraints)

| config | sub-problems | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, tabling | P07a (×6 orders), P07b–P07g | text C | expressible, under the same reading of rule 19 as P02 in 1A (ambiguity 4 there): computing a place is P; the `nonvar/1` tests are R. Where fewer than two places of a relation are known, `is/2` raises an instantiation error | memberchk/2; P07a also `h_param/2` (H) |
| coroutines | the same | text C + when | expressible (the same reading) | when/2; memberchk/2; `h_param/2` |
| constraints, session | the same | text D | expressible: a direct transcription | library(clpfd); memberchk/2; `h_param/2` |

Idioms are as for P02 in 1A: plus/3-style relations dispatching on
`nonvar/1` (SWI-Prolog manual, "Special purpose integer arithmetic");
when/2 delaying arithmetic (Naish 1986); `#=/2` with no domain or
labeling (Triska 2012). There is no relation the problem defines, so
tabling uses the plain text, as for P02.

### P08 (late definition)

| config | sub-problems | program | expressibility (my view) | mechanisms beyond the core |
|---|---|---|---|---|
| plain, tabling, coroutines, constraints | P08a, P08b, P08c | text L, primary | expressible: the definitions are transcribed and arrive by assertz/1 in their stage. An application before its definition is a call of an undefined procedure, which raises an existence error (unknown = error), state 3 of the problem's four | memberchk/2 (P08a, P08c) |
| session | the same | text L, primary | expressible. The call waits in the engine through the configuration's S mechanism, state 4 | memberchk/2; **S: session-wait** (the configuration's, not the program's) |
| all five | P08a, P08b, P08c | `<id>-unknown-fail.pl`, **named variant** | the closed reading's flag (state 1) | the `unknown` flag (C, rule 11) |

Idioms: assertz/1 "for posing definitions" (the systems file, "The core of
plain"; ISO 8.9.2); conc and rev as in P03 (append/3 and naive reverse);
the `unknown` flag left at its ISO default (ISO 7.11.2; SWI-Prolog manual,
"Environment Control (Prolog flags)").

## Choices made before any run (rule 4), and alternatives not written (1B)

1. **Tabling tables the relations the problem defines** (as in 1A): loop,
   alist, mem, setdiff, nonmajor. Facts given as constants (pick, student,
   maths, takes) are not tabled. P05, P06a–c and P07 define no relation,
   so tabling uses the plain text. P06's tabled programs keep `\+` and do
   not use tabled negation, `tnot/1`. That alternative was not written.
2. **Tabling in P08 uses the plain text.** rev and conc arrive as clauses
   that a stage asserts. Tabling them would need `:- table` (and, for
   dynamic clauses, `incremental`) declarations made at load, before the
   stage that brings the definition. Such a declaration names a relation
   that has not arrived, which is the anticipation rule 5 forbids, and it
   would also give rev a declaration before its definition, changing how
   its undefined application behaves (rule 11). Calling `table/1` at run
   time, from the stage that brings the definition, was not written.
3. **P08 has no primary that waits outside session.** In plain,
   coroutines and constraints, a pending application could only be held
   by code the program writes: a list of pending goals run by the
   defining stage, or a `freeze/2` on a variable that the defining stage
   binds. That is a wait-for-definition layer (S, METRICS.md's own
   example), and it would also add an unknown the problem does not have.
   It was not written.
4. **The unknown-fail variant is in every configuration**, session
   included, as the occurs-check variant was in 1A. In session, how the
   flag interacts with the S hook is the system's behaviour, and I did not
   predict it.
5. **≠ and not (x = k)**: `\=/2` and `\+ X = K` in plain and tabling (the
   core). dif/2 wherever coroutines are available, constraints and
   session included. I did not use clpfd's `#\=`, because the problem's ≠
   and not hold of every value, and `#\=` would restrict x to integers
   (P06, "a representation that restricts x to integers is *partial*").
   x > k is clpfd `#>` in constraints and session, since > holds only of
   integers (SPECIFICATION.md, "Arithmetic").
6. **x > k in coroutines** waits by `freeze/2` until x is known. The
   alternative, `when(nonvar(X), ...)`, is the same here and was not
   written.
7. **P06d and P06e in coroutines** use the plain text, with no delay of
   the negations (`when(ground(G), \+ G)`). With the conjuncts in the
   order written, the negated goals are ground whenever they are reached,
   on every input of the problem's domain (both sequences are given; p and
   k are bound by student and maths first). A delay would add control that
   changes nothing. It was not written.
8. **P07a's order**: one program, which reads the order and walks it
   (`relations/3`, `relation/3`). Six files, each with the conjunction
   written in its order, were not written.
9. **P07's compound x + y + z = k**, in texts C and C + when, is (x + y) + z
   = k with a fresh t, the two primitive relations in the order written:
   `sum(X, Y, T), sum(T, Z, K)`. In text D it is one constraint,
   `X + Y + Z #= K` (SPECIFICATION.md allows either). In plain, the
   decomposition decides which orders can compute. x + (y + z) was not
   written.
10. **P07b's x − y = k** is its own relation, diff/3, written like sum/3.
    It is not rewritten as y + k = x.
11. **P05's problem-defined alternatives**: the programs do not call
    `h_held/2`. A backtracking program holds one value of x at a time and
    has no count of the others without computing one (an aggregation the
    problem does not ask for, which would add steps and alternatives). The
    held alternatives are left to the harness's choicepoint count, and in
    constraints to the clpfd domain shown in the residual.

## Ambiguities, and the readings taken (1B)

1. **What is a constant.** I followed `stages.json`'s placeholders. P04c
   and P04e's sequence ⟨ᴀ,ᴀ⟩, P04a and P04b's 1, the pick facts, the
   comparisons' integers, P06's values, sequences and closed world with
   the queried atom, P07's integers, P08a's ⟨42⟩, and P08c's ⟨1,2⟩ and
   stage 3's `rev(<seq>, <seq>)` are constants. The atom ᴀ inside alist's
   definition, and ⟨⟩ and ⟨h⟩ inside rev and conc in P08a stage 4 and P08c
   stage 4, are parts of definitions (P04d, P04f and P08b have no
   constants at all). Reading P08c stage 3's ⟨⟩, ⟨⟩ as constants is
   unusual, but `stages.json` writes them as placeholders, so they are in
   the block as `rev_case_1([], [])`, and stage 3 asserts
   `rev(S, T)` from them.
2. **"s = ⟨ᴀ⟩ ++ m" in alist** is written as the term `[a|M]`: ⟨ᴀ⟩ is a
   one-element sequence of the definition, and ⟨ᴀ⟩ ++ m is a solved-form
   term (SPECIFICATION.md, "Representation"). Where the prefix is a
   **constant** (P08a stage 6, b = ⟨42⟩ ++ c; P01c in 1A), it is built by
   the problem's own conc, `conc(P, C, B)`, so that it stays generic for
   other prefixes. In P08a this means stage 6 calls conc, defined at
   stage 4.
3. **P05's pick facts** are the constants of the stage that first uses
   them (P05b: stage 2), and the relation is `member(pick(X), Cs)` over
   the stage's constant list, as in the contract's example. They are not
   asserted as clauses. Every entry in that list that is not a pick fact
   fails to match.
4. **P06e's closed world** is asserted as clauses by stage 1
   (`forall(member(F, Cs), assertz(F))`), because nonmajor's definition
   calls student, maths and takes as relations. The queried atom's entry,
   `queried(brown)` or `queried(smith)`, is asserted too, as a fact
   nothing calls. `:- dynamic student/1, maths/1, takes/2.` keeps check
   free of undefined-procedure warnings, and makes a relation with no
   facts fail. That is the closed world the problem states, but it is a
   declaration that changes how an undefined relation behaves, so by
   rule 11 it is C, and is listed.
5. **P06 not R** is the core's `\+` in plain and tabling, which the problem
   names as the thing being probed. dif/2 is a transcription of
   "not (x = k)" only. The negations of mem and takes stay `\+` in every
   configuration (choice 7).
6. **P07a's order dispatch** (`relations/3`, `relation/3` and its first
   argument) is code the problem does not give. I expect the classifiers
   to class it as R (or C, as scheduling by the instance's order), and the
   `h_param/2` call as H. Each relation's body is P.
7. **P07's integers**: as in 1A (ambiguity 5 there). Texts C and C + when
   compute with integer arithmetic on integer constants. Text D uses
   clpfd, whose domain is the integers. clpq is not used.
8. **P08's undefined relation.** The primary declares nothing (no
   `:- dynamic`, flag at its default), since either is control that
   chooses a reading (P08, rule 11). The definition's clauses are asserted
   in the stage that brings them, rev's before conc's in P08a stage 4
   ("the definitions of rev and conc"), case by case in the order written.
   `check` warns that stage/3 calls rev/2 (and, in P08a, conc/3) with no
   definition. That is the subject of the problem. In a reposed
   configuration, each stage runs in a fresh process, so stage 2's call
   comes before stage 4's assertions on every replay. What that does is
   the configuration's result, and I did not anticipate it in the program.
9. **Stages that assert** (P06e stage 1; P08a stage 4; P08c stages 1, 3,
   4) are deterministic. In session, if backtracking re-entered such a
   stage, it would assert its clauses again. This is a property of the
   text, recorded here; I made no attempt to guard against it, because a
   guard would test the database for a definition, which is more than the
   problem states.
10. **P08b's unknowns** are a, b, x, y, z (`stages.json`), without c.

## check (1B)

All 145 files of this batch (29 per configuration: P04a–f, P05a–c,
P06a–d, P06e1–3, P07a–g, P08a–c, and the three P08 variants) were checked
in their own configuration's folder, in the pinned image, with
`harnesses/swi-prolog/check <configuration> <file>`. Every one reports
`check: no errors`. The 40 warnings are all in P08 and its variants: in
each configuration, `stage/3 calls rev/2, which nothing defines` (P08a,
P08b, P08c and their variants) and `stage/3 calls conc/3, which nothing
defines` (P08a and its variant). Those definitions arrive by assertz/1 at
a stage, which a static check cannot see. There are no warnings for the
other files.

## Commands run (1B)

- `harnesses/swi-prolog/check`, in the pinned image, once on five P04
  files, then once on every file of this batch. Nothing else in the image.
- No program, interpreter or Prolog system was run on any program or
  fragment.
- File work used the shell, git, and bash, perl and sed scripts (kept
  outside the repository) that wrote these files' text and copied the
  shared texts.
- On the host, `python3` was run once with a here-document to list
  `harnesses/stages.json`'s top-level keys (reading the file, executing
  nothing of the study).
