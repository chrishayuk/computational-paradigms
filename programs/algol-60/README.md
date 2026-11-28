# ALGOL 60 programs, wave 1: batch 1A (P01–P03), batch 1B (P04–P08), batch 1C (P09–P12) and batch 1D (P13–P16)

*Batches 1B, 1C and 1D have their own sections, [below](#batch-1b-p04p08), [after it](#batch-1c-p09p12) and [last](#batch-1d-p13p16). What follows up to batch 1B is batch 1A's, unchanged.*

*Phase 5 (`PROTOCOL.md`, "Phases"), against `spec-1.0.1`. Written to the
program contract of `harnesses/algol-60/README.md`, section 2. Every program
was fixed before any was run. The only thing run on them is the harness's
`check`, which executes nothing, and it reports no error or warning for any
of them.*

**Author of every program:** `implementation-algol-60`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`). **Precursors:** the author had not
seen any precursor program: not the absys experiments E01–E09, not the
calibration programs, not any earlier program of this study.

**S mechanisms used:** none, in any program (`harnesses/algol-60/S-mechanisms.md`
lists none for any configuration). The code that holds a relation until its
places are known is written for each problem's own relations, so it is R in
the core configuration (`METRICS.md`, rule 19), not S.

## Layout

    programs/algol-60/<configuration>/<instance>.<ext>        the program
    programs/algol-60/<configuration>/<instance>.constants    its constants, tagged by stage

`<instance>` is the instance id of `harnesses/stages.json`, so that `run`
finds the constants file beside the program with no setting
(`ALGOL60_CONSTANTS` is left for the verifier). `<ext>` is `.alg` for
*report* and `.a60` for *x1* and *x1sim*. Run each as, for instance:

    harnesses/algol-60/run report P02 P02b.R3R1R2 behaviour programs/algol-60/report/P02b.R3R1R2.alg OUTDIR
    harnesses/algol-60/run x1sim  P03 P03f        behaviour programs/algol-60/x1sim/P03f.a60          OUTDIR

### Which configurations share a text

- **x1 and x1sim share one text.** Every file in `x1/` is byte-identical to
  the file of the same name in `x1sim/`. It is written in the X1 compiler's
  representation (underlined reserved words, the operator symbols, strings in
  `` `...' ``) with the X1 system's `read`, `print`, `PRINTTEXT` and `NLCR`,
  which is the natural program for both: x1 is the X1 system "as its
  documents describe it", and the harness README recommends that form for x1
  (2.1; `QUESTIONS.md`, A14).
- **report has its own text**, because the Revised Report's configuration
  has only the IFIP procedures `ininteger`, `outinteger`, `outstring`, and the
  X1 procedures are not in it. Line by line it is the same program: the X1
  text was made from the report text by a fixed substitution (reserved words
  underlined; `not`, `and`, `or` and `not (a = b)` written `¬`, `∧`, `∨`,
  `a ≠ b`; `ininteger(0, v)` written `v := read`; `outinteger(1, v)` written
  `print(v)`; `outstring(1, "t\n")` written ``PRINTTEXT(`t'); NLCR``), with
  the comment on idioms changed to name the X1 procedures. Same
  algorithm, same structure, same constants files.
- **P02b's six instances share one text.** The six files
  `P02b.R1R2R3` … `P02b.R3R2R1` in each folder are byte-identical; only
  their constants files differ (ambiguity 1).

## Programs, per sub-problem

All of them are **primary**. No named variant was written: no sub-problem was
judged not expressible, and for each one program was chosen before any was
run. The expressibility below is the author's reading, for the classifiers to
confirm.

| sub-problem | report | x1, x1sim | posing | expressibility |
|---|---|---|---|---|
| P01a | `report/P01a.alg` | `x1/P01a.a60` = `x1sim/P01a.a60` | incremental | expressible with reformulation |
| P01b | `report/P01b.alg` | `x1/P01b.a60` = `x1sim/P01b.a60` | incremental | expressible with reformulation |
| P01c | `report/P01c.alg` | `x1/P01c.a60` = `x1sim/P01c.a60` | reposed (one stage) | expressible with reformulation |
| P02a | `report/P02a.alg` | `x1/P02a.a60` = `x1sim/P02a.a60` | incremental | expressible with reformulation |
| P02b (six orders) | `report/P02b.<order>.alg` | `x1/P02b.<order>.a60` = `x1sim/…` | incremental | expressible with reformulation |
| P02c | `report/P02c.alg` | `x1/P02c.a60` = `x1sim/P02c.a60` | reposed (one stage) | expressible with reformulation |
| P03a | `report/P03a.alg` | `x1/P03a.a60` = `x1sim/P03a.a60` | reposed (one stage) | expressible |
| P03b | `report/P03b.alg` | `x1/P03b.a60` = `x1sim/P03b.a60` | reposed (one stage) | expressible with reformulation |
| P03c | `report/P03c.alg` | `x1/P03c.a60` = `x1sim/P03c.a60` | reposed (one stage) | expressible with reformulation |
| P03d | `report/P03d.alg` | `x1/P03d.a60` = `x1sim/P03d.a60` | reposed (one stage) | expressible with reformulation |
| P03e | `report/P03e.alg` | `x1/P03e.a60` = `x1sim/P03e.a60` | reposed (one stage) | expressible |
| P03f | `report/P03f.alg` | `x1/P03f.a60` = `x1sim/P03f.a60` | reposed (one stage) | expressible with reformulation |

The expressibility is the same in all three configurations: they share the
algorithm, and nothing in these problems uses a feature one configuration has
and another lacks.

### The design shared by P01 and P02: holding relations

ALGOL 60 has no unknowns and no relations. Each unknown is a Boolean (`xk`:
has it a value?) and a variable that holds its value. Each relation of a
stage is held, as posed, by a Boolean (`r1`: posed and not yet decided). Its
**evaluator** decides it from the places known: with enough places known it
gives the remaining place its value, or tests it when all are known; else it
waits. After every stage, `propagate` examines every held relation, in the
order posed (the problem's presentation order), again and again until a whole
pass gives no unknown a value. By `METRICS.md` rule 19, the evaluators'
computing of a place and testing are P; the tests of which places are known,
the waiting, `propagate` and the flags are R (holding code written for the
problem's own relations). That is why P01 and P02 are *expressible with
reformulation*: their definitions are transcribed, but holding an undecided
relation needs code the problem does not give.

Each stage prints **one answer** (unless the relations held are known to be
inconsistent, when it prints none and the observe block says `no solution`):
every unknown as its value, or `held` (it occurs in a relation still held), or
`free`; then `where` and the relations still held, with known values put in
their places. For example P02b.R2R3, stage 2:
`u = 2, v held, w held, where w . 2 = v`. The observe block gives the same
relations, a `[bind …]` for every unknown with a value, `[suspended
held-relations N]` while N relations wait, and counters (below). The product
is printed as `.`, because the X1 code has no `×` or `*` in strings (harness
README, 2.1); the report text prints the same for parity.

- **P01a.** Three integer unknowns; stage 1 holds x = y, stage 2 y = z,
  stage 3 z = k (k from the constants). One evaluator, `equation`, serves both
  equations between unknowns, the unknowns' state passed **by name** (Revised
  Report 4.7.3.2), so the same code reads and assigns x, y or z; z = k has its
  own evaluator. Stage 3 sets z, then y, then x, over three passes.
- **P01b.** Sequences are cells (below). Stage 1 holds conc(a, s, t); stage
  2 holds s = b. When s is known, t is computed by conc's cases, as a
  function (rule 3: the direction the stage uses).
- **P01c.** x = a ++ x is held. Its evaluator would test it if x were known,
  computing a ++ x by conc's cases; nothing gives x a value, so the stage
  ends with the equation held (`[suspended held-relations 1]`). The program
  has no unification, so it has no occurs check, and it makes no cyclic value.
  It neither detects that no finite x exists nor builds the rational
  solution: either would need a further reformulation (an argument on
  lengths, or a cyclic cell), which the problem does not give and was not
  written.
- **P02a, P02b, P02c.** Integer unknowns u, v, w. R1 (u + v = c) computes
  either place from the other. R2 (w · u = v) computes v from w and u, and w
  from u and v (or u from w and v) by integer division where the divisor
  divides v, with no solution where it does not; with a zero factor it holds
  for every value of the other factor when v = 0, and for none otherwise.
  R3 (u + a = b) gives u = b − a. P02b poses at stage k the relation the
  instance's order gives in place k, read as codes (R1 = 1, R2 = 2, R3 = 3)
  from the instance line. P02c poses R1, R2 and R3, in that order, as one
  stage. Counters `[operations R1-examined N]` (and R2, R3) give how many
  times each relation's evaluator was entered since the computation started:
  R1–R3 are not defined by cases, so these are the observation P02 asks for
  ("how many times each is examined"), not applications of cases.

After R1 and R2 only, the program holds both relations and does not
enumerate the ten triples: no evaluator can act with no place known. That is
the transcription; solving the pair (u divides c) would be an algorithm the
problem does not state.

### The design of P03, and of P01b and P01c: sequences as cells

A sequence is an index into two integer arrays `hd` and `tl`, 0 being ⟨⟩ and a
cell c being ⟨hd[c]⟩ ++ tl[c] (the systems file's "parallel arrays of heads and
tail indices", `systems/algol-60/README.md`, Values: encoding, P; its
construction, decomposition and equality are P by rule 15). `cons` makes a
cell, `readseq` reads a sequence, `same` tests equality, and `printseq` and
`printpath` are output adapters (H).

- **P03a** (conc forward) and **P03e** (rev forward): conc and rev are
  integer procedures with one branch per case, in order, computing their last
  place from the others: mode-faithful transcriptions (rule 3), P. rev's case
  2 takes its conjuncts in order: `q := rev(l)`, then `conc(q, ⟨h⟩)`.
  *Expressible.*
- **P03b** (conc(a, b, ⟨1,2⟩)): a separate procedure `split`, written from
  conc's cases in order: case 1 reports a = ⟨⟩, b = c; case 2, when c is
  ⟨h⟩ ++ c₁, recurses on c₁ with h appended to `path`, an extra argument
  holding a so far. Reports the three answers in the order of the cases, then
  finishes. *Expressible with reformulation* (rules 3 and 14: a separately
  written direction is R, with the extra argument, rule 5).
- **P03c** (conc(⟨1⟩, b, ⟨1,2,3⟩)): `strip`, from conc's cases: case 1 when a
  is ⟨⟩ reports b = c; case 2 when a and c begin with the same head recurses
  on both tails. *Expressible with reformulation.*
- **P03d** (conc(a, ⟨3⟩, ⟨1,2,3⟩)): `prefix`, from conc's cases: case 1 when
  c equals b reports a (from `path`); case 2 as in `split`. It tries every
  case, so it reports every a there is. *Expressible with reformulation.*
- **P03f** (rev(a, ⟨1,2,3⟩)): `unrev`, from rev's cases: case 1 when r is ⟨⟩
  reports a (from `path`); case 2 takes its two conjuncts in the other order
  (one **move**, rule 4), since r is known and q is not: `lastsplit`, written
  from conc's cases for conc(q, ⟨h⟩, r) with r known, gives q and h, and then
  `unrev` recurses on q with h appended to `path`. Both of `lastsplit`'s cases
  are tried; at most one can succeed. Reports the one answer and finishes.
  *Expressible with reformulation.*

Each P03 program counts the applications of each case of each relation it
uses (`[operations conc/1 N]`, `conc/2`, `rev/1`, `rev/2`), H counters: a case
is counted when its head's conditions hold and the case is taken. In the
reversed directions those are the cases of the direction procedure, which
transcribes conc's or rev's. If a P03 stage has no answer, the observe block
says `no solution`. Every P03 program ends with *finished*: nothing is held.

The arrays are sized from the lengths read at the stage (Revised Report
5.2.4.2), so a P03 or P01c program serves sequences of any length: the
constants list the lengths first, then the elements. P01b cannot do this:
stage 2's sequence arrives after the cells must exist, so its store is fixed
at 1000 cells (ambiguity 5).

## Constants files

Each line is `k: values`, tagged by the stage that first uses it, its layout
stated in the program's `CONSTANTS` comment. Sequences are given as a length
and then the elements (integers; an atom would be its integer code).

| instance | file contents | layout |
|---|---|---|
| P01a | `3: 2` | stage 3: k of z = k |
| P01b | `1: 2 1 2`, `2: 1 3` | stage 1: a of conc(a, s, t); stage 2: b of s = b |
| P01c | `1: 1 1` | a of x = a ++ x |
| P02a | `1: 16`, `3: 10 12` | R1's c; R3's a b |
| P02b.R1R2R3 | `1: 16`, `3: 10 12` | the stage posing R1 has c, the stage posing R3 has a b, R2 has none |
| P02b.R1R3R2 | `1: 16`, `2: 10 12` | the same |
| P02b.R2R1R3 | `2: 16`, `3: 10 12` | the same |
| P02b.R2R3R1 | `2: 10 12`, `3: 16` | the same |
| P02b.R3R1R2 | `1: 10 12`, `2: 16` | the same |
| P02b.R3R2R1 | `1: 10 12`, `3: 16` | the same |
| P02c | `1: 16 10 12` | c, then a b |
| P03a | `1: 2 1 1 2 3` | La Lb, a, b |
| P03b | `1: 2 1 2` | Lc, c |
| P03c | `1: 1 3 1 1 2 3` | La Lc, a, c |
| P03d | `1: 1 3 3 1 2 3` | Lb Lc, b, c |
| P03e | `1: 3 1 2 3` | La, a |
| P03f | `1: 3 1 2 3` | Lb, b |

No stage's code reads another stage's constants, and nothing in a program
depends on a later stage (rule 5). P02b's order and every program's handling
of a message depend only on the instance line and the message.

## Idioms and their sources

Cited in each program's `PROVENANCE idioms` comment:

- the Revised Report on ALGOL 60 (1962): blocks; arrays with bounds computed
  at run time (5.2.4.2); procedures and function designators with value and
  name parameters, recursion (4.7, 5.4); name parameters to share one
  evaluator (P01a) and to return results (P03f's `lastsplit`) (4.7.3.2); the
  `for` statement with `step … until` and `while` elements (4.6);
  conditional statements and expressions (3.3, 4.5); integer division
  (3.3.4.2);
- *report*: the input and output procedures `ininteger`, `outinteger`,
  `outstring`, IFIP 1964, as the interpreter gives them (systems file);
- *x1, x1sim*: the X1 system's `read`, `print`, `PRINTTEXT`, `NLCR`, and the
  X1 compiler's representation, as the harness README gives them (2.1). The
  programs also cite "Kruseman Aretz 2003, chapter 7" for them, taken
  second-hand from the harness's own X1 qualification programs: the author
  did not read that source (see "What the author read");
- sequences as parallel arrays of heads and tail indices: the systems file,
  Values;
- the message loop, the reading of the instance line and the observe block:
  the harness README's example X01 (2.8);
- holding each relation until its places are known, and the propagation
  loop: no period source; written for these problems (`METRICS.md`, rule 19).

The X1 manual's rule that declarations come in the order scalars, arrays,
procedures (`algol60 --x1 --check` reports it as "property 15") is kept in
all three configurations' texts.

## Ambiguities, and the reading taken

1. **P02b's constants depend on the order.** The contract has one constants
   file per program, every line tagged by "the stage that first uses it",
   but in P02b which stage first uses R1's constant depends on the instance's
   order, and no single file can be tagged for all six without giving a stage
   constants of a later one (rule 5). *Reading:* one program per instance,
   six byte-identical texts named by instance id, each with its own constants
   file. The verifier will need one variant constants file per P02b instance
   (or one tagged per order, passed with `ALGOL60_CONSTANTS`).
2. **What an imperative program reports for a stage whose outcomes are a
   relation or infinite.** *Reading:* one answer holding the values known and
   the relations still held, and the same state in the observe block, read
   from the program's own structures, so that it is state the program acts
   on at a later stage, not the posed information printed back. In single
   stage problems (P01c) nothing comes later; the held equation is reported
   anyway, and it is identical to the posed information.
3. **The values an unknown ranges over.** P01a's unknowns range over all
   values, but every stage of P01a gives only an integer (`stages.json`:
   `<k>`); P02's are integers. *Reading:* each unknown is held as an integer.
   Sequences (P01b, P01c, P03) are taken as flat sequences of integers, an
   atom being its integer code (systems file, Values); a sequence with
   sequences as elements is not handled.
4. **P01c under the two readings.** Neither ALGOL 60 configuration has an
   occurs-check setting, unknowns or terms. *Reading:* the equation is held,
   undecided; the program neither reports "no solution" (finite reading) nor
   a cyclic value (rational reading).
5. **P01b's fixed store.** 1000 cells, set in one place (`cells := 1000`).
   A variant whose sequences need more than that (about 500 elements in all)
   would stop with an index error, not a wrong answer. The P03 and P01c
   programs size their store from the input and have no such limit.
6. **Single-stage problems** (P01c, P02c, P03) are declared `reposed`. With
   one stage, incremental and reposed posing send the same input; the
   program reads its one message, answers, and ends.
7. **Problem operations where relations are not defined by cases** (P02):
   counted as examinations of each relation, named `R1-examined` and so on.
   P01a counts nothing: it uses only equality.
8. **Expressibility of the holding code.** By rule 19 the holding code is R,
   so P01 and P02 are given here as *expressible with reformulation*, not
   *expressible*; a classifier who reads "the problem's definitions can be
   transcribed" as covering the evaluators alone would call them
   *expressible*.
9. **x1's input and output.** `algol60 --x1` accepts both the X1 and the IFIP
   procedures (harness `QUESTIONS.md`, A14). *Reading:* the X1 system's own,
   as the X1 documents describe it, which also makes the x1 text the x1sim
   text.

## What the author read and ran

Read: `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
`AMENDMENTS.md`, `problems/README.md` and the files of P01, P02 and P03,
`systems/algol-60/README.md`, `harnesses/README.md`, `harnesses/stages.json`
(the entries of P01–P03 and its preamble), and `harnesses/algol-60/` (the
README, `S-mechanisms.md`, `QUESTIONS.md`, `check`, parts of `run`, the
qualification programs and part of their records). By mistake, also a part of
`harnesses/QUESTIONS.md` (the common harness's questions Q1–Q5, on stage
descriptions, instance ids and P09/P16 queries), which is outside the brief's
list; it holds no program and no outcome. **Not read:** the image's own
documentation and examples (`/opt/src/algol-60`, `/opt/src/x1sim`): the one
attempt to list them in the image was refused by the permission system, so
no idiom is cited from them.

Ran: only `harnesses/algol-60/check`, on every program in its
configuration (the X1 texts in both x1 and x1sim), and once on a scratch
program with a deliberate error, deleted afterwards, to see that `check`
reports errors. On the host, `python3` was used once to print the P01–P03
entries of `stages.json`, and once with an empty input by mistake; neither ran
any program of the study or the system.

---

# Batch 1B (P04–P08)

*Phase 5, against `spec-1.0.1`, written to the program contract of
`harnesses/algol-60/README.md`, section 2. Every program was fixed before any
was run. The only thing run on them is the harness's `check`, which executes
nothing. It reports no error or warning for any of them, in any configuration
(the X1 texts checked in both x1 and x1sim).*

**Author of every program:** `implementation-algol-60`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`). This batch's author has its own context
and had not seen any earlier work on the study except what is listed under
"What the author read and ran" below. That includes this README's batch 1A
section and the batch 1A programs, which the brief allows and which hold no
outcome. **Precursors:** the author had not seen any precursor program: not
the absys experiments E01–E09, not the calibration programs, and no program of
this study other than the batch 1A ALGOL 60 programs.

**S mechanisms used:** none, in any program. Every procedure that holds a
relation, decides it, or passes its solutions on is written for that problem's
own relations, so by `METRICS.md` rule 19 it is R in the core configuration,
not S. Ambiguity 5 below says where a classifier could read P04 another way.

**Named variants:** none. No sub-problem was judged not expressible. For each
sub-problem one program was chosen before any was run, and it is the primary.

## Layout, and which texts are shared

The layout is batch 1A's: `programs/algol-60/<configuration>/<instance>.<ext>`
with its `.constants` beside it, `.alg` for report and `.a60` for x1 and x1sim.
A sub-problem with no constants (P04d, P04f, P08b) has no constants file
(`constants.how = "none"`).

- **x1 and x1sim share one text**, as in batch 1A: every `.a60` file in `x1/`
  is byte-identical to the file of the same name in `x1sim/`, and so are the
  constants files.
- **The X1 text is made from the report text by a fixed substitution**, the
  one batch 1A describes, carried out by a short Python script that only
  rewrites text (it executes no ALGOL, and is not part of the study): reserved
  words underlined outside comments and strings; `ininteger(0, v)` written
  `v := read`; `outinteger(1, e)` written `print(e)`; `outstring(1, "t")`
  written ``PRINTTEXT(`t')``, a `\n` in it written `NLCR`, and the statements
  that one call becomes wrapped in `begin … end` when there are more than one;
  and the comment on idioms changed to name the X1 procedures. The report
  texts of this batch already write `¬ ∧ ∨ ≠ ≥ × ÷` as symbols, so nothing
  else changes. Same algorithm, same structure, same constants.
- **Identical texts within a configuration:** `P06a` = `P06c` (the same stages,
  other constants); `P06e1` = `P06e2` (the query's atom is a constant);
  `P07d` = `P07e` (the problem gives them as one relation with two sets of
  constants); `P08a` = `P08b` (P08b is P08a's stages 1 to 3; it has no
  constants file, since P08a's only constants are stage 6's).
- **P07a: one program for all six instances.** Its constants do not depend on
  the order (one stage, the three relations' integers in the order written),
  so `P07a.alg` (`P07a.a60`) and its constants serve `P07a`, `P07a.132`,
  `P07a.213`, `P07a.231`, `P07a.312` and `P07a.321`; the order comes from the
  instance line. Run it as, for instance,

      harnesses/algol-60/run report P07 P07a.231 behaviour programs/algol-60/report/P07a.alg OUTDIR

## Programs, per configuration and sub-problem

Every program below is **primary**, and exists in all three configurations:
`report/<id>.alg`, and `x1/<id>.a60` = `x1sim/<id>.a60`. The expressibility is
the author's reading, for the classifiers to confirm; it is the same in all
three configurations, which share the algorithm, and nothing in these
problems uses a feature one configuration has and another lacks.

| sub-problem | file | posing | expressibility |
|---|---|---|---|
| P04a | `P04a` | reposed (one stage) | expressible with reformulation |
| P04b | `P04b` | reposed (one stage) | expressible with reformulation |
| P04c | `P04c` | reposed (one stage) | expressible with reformulation |
| P04d | `P04d` (no constants) | reposed (one stage) | expressible with reformulation |
| P04e | `P04e` | reposed (one stage) | expressible with reformulation |
| P04f | `P04f` (no constants) | reposed (one stage) | expressible with reformulation |
| P05a | `P05a` | incremental | expressible with reformulation |
| P05b | `P05b` | incremental | expressible with reformulation |
| P05c | `P05c` | incremental | expressible with reformulation |
| P06a | `P06a` | incremental | expressible with reformulation |
| P06b | `P06b` | incremental | expressible with reformulation |
| P06c | `P06c` (= `P06a`) | incremental | expressible with reformulation |
| P06d | `P06d` | reposed (one stage) | expressible |
| P06e1 | `P06e1` | reposed (one stage) | expressible |
| P06e2 | `P06e2` (= `P06e1`) | reposed (one stage) | expressible |
| P06e3 | `P06e3` | reposed (one stage) | expressible |
| P07a (six orders) | `P07a` | reposed (one stage) | expressible with reformulation |
| P07b | `P07b` | reposed (one stage) | expressible with reformulation |
| P07c | `P07c` | reposed (one stage) | expressible with reformulation |
| P07d | `P07d` | reposed (one stage) | expressible with reformulation |
| P07e | `P07e` (= `P07d`) | reposed (one stage) | expressible with reformulation |
| P07f | `P07f` | reposed (one stage) | expressible with reformulation |
| P07g | `P07g` | reposed (one stage) | expressible with reformulation |
| P08a | `P08a` | incremental | expressible with reformulation |
| P08b | `P08b` (= `P08a`, no constants) | incremental | expressible with reformulation |
| P08c | `P08c` | incremental | expressible with reformulation |

Single-stage sub-problems are declared `reposed`, as in batch 1A: with one
stage both posings send the same input. Incremental programs handle a replay
message `2 j` as `1 j` (the harness reposes an incremental program after a
budget, error or safety stop).

### P04: each relation a procedure that passes on its solutions

ALGOL 60 has no unknowns and no alternatives. Each relation is transcribed as
a procedure with one branch per case, in the order written, that passes each
of its solutions to a parameterless procedure `found` and returns when it has
no more; a disjunction calls its alternatives one after the other, in the
order written. An unknown is a Boolean that says whether it has a value and a
variable that holds it, both passed by name; a value given to an unknown is
taken back when `found` returns. The continuation `found` is often a procedure
declared in an inner block of the caller, which is the way Knuth's man or boy
test passes its procedure `B` (1964; `examples/man-or-boy-1964.alg` in the
image). Sequences are batch 1A's cells; the atom ᴀ is the code 1.

- **P04a, P04b.** `loop(x)` is its one case, a procedure that calls itself.
  P04a calls `loop` and then `x = k`; P04b the other way round. In P04a `loop`
  never returns, so `x = k` is never reached; in P04b `x = k` is reported
  first. Neither finishes: in report and x1 the expectation is the budget, in
  x1sim (no budget) the safety limit or the X1's stack.
- **P04c, P04d (alist-left).** Case 1 is tried first, with its conjuncts in the
  order written: `alist(m)` is called with m unknown, and only then is
  `s = ⟨ᴀ⟩ ++ m` decided (`conseq`, which gives m from s, or s from m, or
  tests it). So the recursion on case 1 comes first, at every depth, whether s
  is known (P04c) or not (P04d). No reordering was made to avoid it: it is the
  presentation order the problem fixes.
- **P04e, P04f (alist-right).** Case 1, s = ⟨⟩, first; then case 2. With s
  known (P04e) the head of case 2 gives m from s, and then `alist(m)` is
  called. With s unknown (P04f) the head cannot give s a value before m has
  one (there are no partial values), so `alist(m)` is called first and the
  head then gives s: **one move** (rule 4), in both texts, since both contain
  the procedure. The test of whether s is known, which chooses between the two
  orders, is R. P04f prints ⟨⟩, ⟨ᴀ⟩, ⟨ᴀ,ᴀ⟩, … until it is stopped; the harness
  collects the first 20.
- Counters `[operations alist/1 N]`, `alist/2`, `loop/1` (H) count a case when
  it is taken. A stage that never ends prints no observe block.
- R, by the author's reading: the known-flags and the parameter `found` (extra
  arguments, rule 5), the taking back of a value after `found` returns, the
  test of which places are known, and P04f's move. Giving back the cell made
  for a value (`top := top - 1`) only lets store be reused: C (rule 16).

### P05: the values of x held all at once

`pick(x)` is its facts, read from the constants: when it is posed each fact,
in order, gives x one value, and the values are held all at once, each with a
Boolean that says whether it is still a solution. Each comparison or equation
is held as posed until x has values, and is then tested on each value
(testing a fully known relation is P); a value that fails is dropped and not
kept. Before `pick` (P05b, stage 1), the comparison is held, and the answer is
`x held, where x gt 1`. Each stage prints one answer per value still held, or
none and `no solution` in the observe block. The observe block lists the values
held, `[problem-alternatives x N]` (the problem-defined alternatives,
`METRICS.md`), the held relations with `[suspended held-relations N]` while one
waits, and `[operations pick/i 1]` for each fact applied. It does not print
`[alternatives …]`, since nothing is left for a request for more answers to
resume: every value held is printed (ambiguity 7). Comparisons are printed in
words (`x gt 1`, `not (x = 2)`), since the X1 code has no `>` in strings.

### P06: negation

- **P06a, P06c, P06b.** As P01 and P02 in batch 1A: x is a Boolean and an
  integer; `not (x = c)` is held while x is unknown, and is tested with the
  negation of the language, `¬(x = c)`, once x is known; `x = c` gives x its
  value or is tested. The answer before x is known is
  `x held, where not (x = 1)`. P06c's stage 2 makes the held negation false,
  and the program reports no answer and `no solution`.
- **P06d.** `mem` is a Boolean procedure testing mem(e, s) with both known, its
  cases in order: case 1 when the head is e, else case 2 on the tail (once
  case 1 has made it true, case 2 is not tried: a test needs one derivation).
  `setdiff` computes d from s1 and s2 as a function, the direction the query
  uses, by its three cases in order, case 3 testing its own conjunct
  `¬mem(h, s2)` (so mem is evaluated again there). Mode-faithful (rule 3):
  *expressible*.
- **P06e1, P06e2, P06e3.** The facts of the closed world are arrays read from
  the constants, atoms as codes (ʙʀᴏᴡɴ 1, ꜱᴍɪᴛʜ 2, ᴄ101 101, ᴄ301 301).
  `nonmajor` is its one case, its conjuncts in order: `student(p)` is tested
  on each fact (p known, P06e1 and P06e2) or gives p each fact's value (P06e3),
  `maths(k)` gives k each fact's value, and `takes(p, k)`, both known, is a
  Boolean procedure over its facts, negated with `¬`. So p and k are always
  known when the negation is decided, as the observe block says. Each
  derivation is one answer (`true`, or `p = brown`). Each program uses one
  direction only: *expressible*.

### P07: one relation at a time

Batch 1A's design for P02: each relation held as posed, its evaluator
giving the remaining place its value when enough are known or testing it,
and a loop examining the held relations in the order posed until a pass gives
no unknown a value. x + y + z = 12 has one evaluator for the three-place sum
(writing it compound or decomposed is a transcription, `SPECIFICATION.md`).

- **P07a** solves z, then y, then x, in every order; the order changes only
  the number of passes, which the counters `[operations R1-examined N]` show.
- **P07b, P07c, P07f** have no relation with a known place, so nothing is
  given a value: the relations are held and reported as such
  (`x held, y held, where x + y = 10, x - y = 4`). P07f's inconsistency is
  not detected. Solving P07b by elimination would be an algorithm the problem
  does not state (and, written generally, a solver over relations, S); it was
  not written (ambiguity 9).
- **P07d, P07e.** w · u = v, as P02's R2: w from v and u where u divides v,
  `no solution` where it does not (P07e: 15 is not a multiple of 2).
- **P07g.** x · x = c has one unknown in both its factors, and c known, so its
  evaluator gives x its values: r = entier(sqrt(c) + 0.5) and, if r · r = c,
  r and −r (one value if r = 0), and none if c is negative or not a square.
  Two answers, `x = 3` and `x = -3`, and the values held all at once in the
  observe block. That this is computing a place of the relation (P, rule 19)
  and not a changed algorithm is the author's reading (ambiguity 10).

### P08: a definition that arrives

ALGOL 60 has no definitions that arrive while a program runs: every procedure
is in the text before the program starts. So the procedures `rev` and `conc`
(transcribed as in batch 1A's P03, each computing its last place by its cases
in order) are in the text, and a Boolean for each definition, or each case,
says whether it has arrived. The stage that brings a definition sets it. An
application of `rev` before its definition has arrived is held as posed,
neither true nor false, and examined again at each later stage: **the fourth
of the problem's four states, a computation awaiting its definition**, which is
the open reading. The observe block says which definitions have arrived, shows
the application as `rev((x, y, z), b) awaiting its definition`, and gives
`[suspended pending-applications 1]` while it is held.

- **P08a, P08b.** The elements of a sequence are indices into a table of
  elements, each a Boolean and an integer: 1 is x, 2 is y, 3 is z, and the
  elements of stage 6's sequence are further entries with their values.
  `rev` and `conc` only move elements, so they work on elements with no value:
  at stage 4, b = (z, y, x). x = y and y = z are held until one side is known,
  as P01a's equations. b = s ++ c, with b known, equates each element of s
  with the element of b in its place, which gives z its value, and c is the
  rest of b; then y = z and x = y give y and x theirs. Answers name every
  unknown, as its value, `held` or `free`, with the relations held, for
  example after stage 4:
  `a = (x, y, z), b = (z, y, x), c free, x held, y held, z free, where x = y`.
  P08b stops after stage 3 with the application still held, which the
  observe block tells apart from failure.
- **P08c.** conc's definition arrives at stage 1, rev's case 1 at stage 3, as
  the two sequences of the stage's constants (ambiguity 2), and rev's case 2 at
  stage 4. `rev` and `conc` say whether they found their result (1), found
  there is none (0), or could not tell because a case they would need has not
  arrived (2). At stage 3, case 1 does not apply to ⟨1, 2⟩ and case 2 has not
  arrived, so the application is still held; at stage 4 it is decided,
  b = (2, 1). The application is held until the whole of rev and conc has
  arrived, even after a case that has arrived gives a solution.
- R, by the author's reading: the holding of the application and of the
  equations, the flags that say a definition has arrived, and the tests of
  them (ambiguity 3 asks whether those tests are C instead, by rule 11).
- Integers in P08's answers are printed by an output adapter, digit by digit,
  so that an answer with many values stays inside the X1 system's line of 144
  positions, where `print` takes a column of its own for each value; the
  report text does the same, for parity.

## Constants files (batch 1B)

| instance | file contents | layout |
|---|---|---|
| P04a, P04b | `1: 1` | k of x = k |
| P04c, P04e | `1: 2 1 1` | L, then s (ᴀ is 1) |
| P04d, P04f | none | |
| P05a | `1: 3 1 2 3`, `2: 1`, `3: 2` | F and pick's facts; c of x > c; c of x ≠ c |
| P05b | `1: 1`, `2: 3 1 2 3` | c of x > c; F and pick's facts |
| P05c | `1: 3 1 2 3`, `2: 4`, `3: 3` | F and pick's facts; c of x = c; c of x = c |
| P06a | `1: 1`, `2: 2` | c of not (x = c); d of x = d |
| P06c | `1: 1`, `2: 1` | the same |
| P06b | `1: 2`, `2: 1` | c of x = c; d of not (x = d) |
| P06d | `1: 4 3 1 2 3 4 2 4 6` | L1 L2, s1, s2 |
| P06e1 | `1: 1 2 1 2 2 101 301 3 1 101 2 101 2 301` | q; S, student's facts; M, maths's; T, takes's pairs |
| P06e2 | `1: 2 2 1 2 2 101 301 3 1 101 2 101 2 301` | the same |
| P06e3 | `1: 2 1 2 2 101 301 3 1 101 2 101 2 301` | the facts only |
| P07a (all six) | `1: 12 7 3` | c1 c2 c3, in the order written |
| P07b | `1: 10 4` | c1 c2 |
| P07c | `1: 10` | c1 |
| P07d | `1: 2 14` | u's c, v's c |
| P07e | `1: 2 15` | the same |
| P07f | `1: 10 11` | c1 c2 |
| P07g | `1: 9` | c |
| P08a | `6: 1 42` | L, then s of b = s ++ c |
| P08b | none | |
| P08c | `2: 2 1 2`, `3: 0 0` | L, then s of rev(s, b); L1 L2, then p and r of rev(p, r) |

No stage's code reads another stage's constants, and nothing in a program
depends on a later stage (rule 5). A definition's text is in the program from
the start, as every stage's relations are; only its arrival is a stage
(ambiguity 3).

## Idioms and their sources (batch 1B)

Cited in each program's `PROVENANCE idioms` comment:

- the Revised Report on ALGOL 60 (1962): as in batch 1A, and also procedures
  as actual parameters and parameterless formal procedures (4.7.5, 5.4.4),
  Boolean procedures and the negation `¬` (3.4), and the standard functions
  `sqrt` and `entier` (3.2.4–3.2.5, P07g);
- a parameterless procedure declared in an inner block and passed as an
  actual parameter: Knuth's man or boy test (Algol Bulletin 17, 1964), as the
  image has it (`examples/man-or-boy-1964.alg`, read). Wirth's backtracking
  eight queens (`examples/queens.alg`, read) shows the period's depth-first
  search by recursive procedure, though the programs here follow the
  problem's cases rather than it;
- *report*: `ininteger`, `outinteger`, `outstring` (IFIP 1964, systems file);
  *x1, x1sim*: `read`, `print`, `PRINTTEXT`, `NLCR` and the X1 compiler's
  representation (harness README, 2.1), cited, as in batch 1A, after
  Kruseman Aretz 2003, chapter 7, second-hand from the harness's own X1
  programs and the image's `docs/x1.md`; the X1 line of 144 positions and
  `print`'s columns from `docs/x1.md` and the x1sim library manual;
- sequences as parallel arrays of heads and tails, facts as arrays of codes:
  the systems file, Values;
- the message loop, instance line and observe block: the harness README's
  example X01;
- holding a relation, or an application awaiting its definition, until it can
  be decided: no period source; written for these problems (rule 19).

The X1 manual's rules followed in all three texts: declarations in the order
scalars, arrays, procedures (property 15); no conditional statement straight
after `do` (property 12); identifiers unique in their first nine characters
(property 3); every formal parameter specified (property 19). Since neither
dialect stops evaluating `∧` and `∨` early, no subscript is guarded by `∧`.

## Ambiguities, and the reading taken (batch 1B)

1. **P08 says "rev and conc are as in P03",** and P03's file is not in this
   batch's reading list. *Reading:* the definitions as batch 1A's P03 programs
   transcribe them (conc: conc(⟨⟩, b, b); conc(⟨h⟩ ++ a, b, ⟨h⟩ ++ c) if
   conc(a, b, c). rev: rev(⟨⟩, ⟨⟩); rev(⟨h⟩ ++ l, r) if rev(l, q) and
   conc(q, ⟨h⟩, r)), which agree with P08c's own statement of case 1.
2. **P08c stage 3's case 1 has constants.** `stages.json` writes it
   `rev(<seq>, <seq>)`. *Reading:* the two sequences are read from stage 3's
   constants, and case 1 is rev(p, r) for them. If a variant made case 1
   overlap case 2 (p not empty), the program, which computes rev as a
   function, would report case 1's solution and not try case 2.
3. **What a definition's arrival is, in ALGOL 60.** The definitions are in the
   text from the start and a flag marks their arrival; the code of the stages
   before it does not depend on their content. *Reading:* this is how every
   program here holds a stage's information (its relations are in the text;
   the stage's message makes them hold), so it is not anticipation, and P08 is
   *expressible with reformulation*. A classifier who holds that a definition
   which cannot arrive at run time cannot be transcribed would call P08 *not
   expressible*; and the tests of the flags, which decide that an undefined
   relation's application is held rather than false, might be classed C by
   rule 11 rather than R.
4. **P08c with part of a definition.** *Reading:* the application is tried
   with the cases that have arrived, and is held until the whole definition
   is there, since the program cannot know (rule 5) that the missing case
   adds nothing. A solution found by the arrived cases would be reported and
   the application still held.
5. **P04: is passing solutions on a search mechanism?** The procedures follow
   the problem's cases and the order of the language's own calls; nothing in
   them is general over relations. *Reading:* R in the core configuration
   (rule 19), and P04 *expressible with reformulation*. A classifier who reads
   the solution-passing procedures and the taking back of values as a
   depth-first search mechanism would class them S, making P04 *not
   expressible* in the configurations as listed and these programs named
   variants. The natural imperative alternatives (a Boolean test that takes s
   apart before recursing, a loop over lengths) change the order or the
   algorithm, and were not written.
6. **P04's presentation order.** *Reading:* kept, cases and conjuncts, even
   where it makes the program run until it is stopped (P04a, P04c, P04d); the
   one move is P04f's, forced by the absence of partial values.
7. **P05: are the values held "alternatives pending"?** They are all printed
   at every stage, so nothing waits for a request for more. *Reading:* they
   are reported as the problem-defined alternatives
   (`[problem-alternatives x N]`, held all at once, as the observe text says),
   not as `[alternatives …]`, which the harness would read as *alternatives
   pending*.
8. **P06e: one answer per derivation.** A student missing two maths courses
   would be reported twice (`true`, `true`; `p = …` twice), as the definition's
   cases derive it; the set of solutions is the same. No deduplication was
   written.
9. **P07b, P07f: solved one relation at a time.** *Reading:* as batch 1A's
   P02, the relations are held and nothing is eliminated; P07f's inconsistency
   goes undetected.
10. **P07g.** *Reading:* giving x its values from c by a square root is the
    evaluator computing a place from the others (rule 19, P); a classifier
    who reads it as a changed algorithm would class it R.
11. **The values unknowns range over.** As batch 1A: integers, an atom being
    its code, sequences flat sequences of integers. P06a's x ranges over all
    values; the program can hold only an integer in it, though its residual,
    `not (x = 1)`, restricts nothing.
12. **Fixed store.** Facts of P05 at most 1000; P08a's cells and elements 1000;
    P08c's cells 10000; P04's cells for the sequences made during the search
    20000 beyond the input (report and x1 reach far fewer within the budget;
    x1sim, with no budget, may meet the X1's stack first). A variant needing
    more would stop with an index error, not a wrong answer.
13. **X1 line length.** P05's case names and P08's values are printed digit by
    digit, so that no tag is split at the X1's 144 positions; elsewhere
    answers are short enough for `print`.

## What the author read and ran (batch 1B)

Read: `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
`AMENDMENTS.md`, `problems/README.md` and the files of P04–P08,
`systems/algol-60/README.md`, `harnesses/README.md`, `harnesses/stages.json`
(its preamble, and its lines from P03e to the first line of P09), `harnesses/algol-60/README.md`,
`QUESTIONS.md`, `S-mechanisms.md`, `check`, a few lines of `run` (its tag
patterns), and the list of its qualification programs and the first part
of one of them (`x01-x1.a60`); this README and the batch 1A programs `P01c` (report), `P02a` (report and
x1) and `P03e` (report, and the head of x1), and a few lines of `P03b`
(report). In the image: the listings of
`/opt/src/algol-60` (top level, `docs/`, `examples/`, `historical/`) and
`/opt/src/x1sim` (top level, `doc/`, `examples/`); `/opt/src/algol-60/README.md`,
`docs/x1.md`, `examples/queens.alg`, `examples/man-or-boy-1964.alg`;
`/opt/src/x1sim/examples/README.md` and the first part of
`doc/library-procedures.md`. The top-level listing of `/opt/src/algol-60`
shows the name of the `compare/` directory; nothing in it was listed or read,
and no `.out` file was read.

Ran: `harnesses/algol-60/check` on every program in its configuration (the X1
texts in x1 and in x1sim), in the brief's form, one container run each,
from a small host shell loop that filters the output; and, in the image,
`ls` and `cat` to read the documentation above. On the host, `python3` (with
heredocs and a scratch script) only to edit text: to derive programs from one
another, to make the X1 texts from the report texts, and to measure the length
of one answer line. Nothing else executed a program, the system, or an
interpreter on a program.

---

# Batch 1C (P09–P12)

*Phase 5, against `spec-1.0.1`, written to the program contract of
`harnesses/algol-60/README.md`, section 2. Every program was fixed before any
was run. The only thing run on them is the harness's `check`, which executes
nothing. It reports no error and no warning for any of them, in any
configuration: the report texts in report, and the X1 texts in both x1 and
x1sim.*

**Author of every program:** `implementation-algol-60`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`). This batch's author has its own context
and had not seen any earlier work on the study except what is listed under
"What the author read and ran" below. That includes the batch 1A and 1B
sections of this README and some of their programs, which the brief allows and
which hold no outcome. **Precursors:** the author had not seen any precursor
program: not the absys experiments E01–E09, not the calibration programs, and
no program of this study other than the batch 1A and 1B ALGOL 60 programs.

**S mechanisms used:** none, in any program. Every procedure that holds a
relation, decides it, or passes its solutions on is written for that problem's
own relations, so by `METRICS.md` rule 19 it is R in the core configuration,
not S. Ambiguity 12 below says where a classifier could read P12 another way.

**Named variants:** none. No sub-problem was judged not expressible. For each
sub-problem one program was chosen before any was run, and it is the primary.

## Layout, and which texts are shared

The layout is that of batches 1A and 1B: `programs/algol-60/<configuration>/<instance>.<ext>`
with its `.constants` beside it, `.alg` for report and `.a60` for x1 and x1sim.
Every sub-problem of this batch has constants, so every program has a
constants file.

- **x1 and x1sim share one text**, as before: every `.a60` file in `x1/` is
  byte-identical to the file of the same name in `x1sim/`, and so are the
  constants files.
- **The X1 text is made from the report text by the fixed substitution of
  batch 1B**, carried out by a short Python script that only rewrites text (it
  executes no ALGOL, and is not part of the study): reserved words underlined
  outside comments and strings (`Boolean` written `boolean`, `go to` written
  as the one word `goto`); `ininteger(0, v)` written `v := read`;
  `outinteger(1, e)` written `print(e)`; `outstring(1, "t")` written
  ``PRINTTEXT(`t')``, a `\n` in it written `NLCR`, the statements one call
  becomes wrapped in `begin … end` when there are more than one; and the
  comment on idioms changed to name the X1 procedures. Before it was used, the
  script was checked by converting eight report texts of batches 1A and 1B:
  for the five of batch 1B (P04f, P05a, P06d, P07b, P08a) its output is
  byte-identical to the X1 texts committed for them. The report texts of this
  batch write `¬ ∧ ∨ ≠ ≤ ≥ × ÷` as symbols, so nothing else changes. Same
  algorithm, same structure, same constants.
- **Identical texts within a configuration:**
  - `P09a.AB` = `P09a.BA`, and their constants files: the spawn order comes
    from the instance line, and the program runs whichever computation the
    harness's message names.
  - **P12: one text for all 24 instances** (`P12a`–`P12d` × `n8`, `n12`,
    `n16` × `all`, `any`). n and the answer mode come from the instance line.
    The facts of accept depend on n (`stages.json`), so the constants
    differ between n and between sub-problems, and each instance has its own
    constants file (ambiguity 14). The files of the same sub-problem and n
    (`.all` and `.any`) have the same constants.
  - P11a and P11b differ only in the order of two conjuncts; P11c and P11d
    only in which stage commits and which poses x ≠ c.

## Programs, per configuration and sub-problem

Every program below is **primary**, and exists in all three configurations:
`report/<id>.alg`, and `x1/<id>.a60` = `x1sim/<id>.a60`, each with its
`<id>.constants`. The expressibility is the author's reading, for the
classifiers to confirm. It is the same in all three configurations, which
share the algorithm, and nothing in these problems uses a feature one
configuration has and another lacks.

| sub-problem | files (`<id>`) | posing | expressibility |
|---|---|---|---|
| P09a (both orders) | `P09a.AB`, `P09a.BA` (identical) | incremental (spawn messages) | expressible with reformulation |
| P09b | `P09b` | incremental (spawn messages) | expressible with reformulation |
| P09c | `P09c` | reposed (one stage) | expressible |
| P09d | `P09d` | reposed (one stage) | expressible (ambiguity 4) |
| P09e | `P09e` | reposed (one stage) | expressible with reformulation |
| P10a | `P10a` | incremental | expressible |
| P10b | `P10b` | incremental | expressible with reformulation |
| P10c | `P10c` | incremental | expressible |
| P10d | `P10d` | incremental | expressible with reformulation |
| P11a | `P11a` | reposed (one stage) | expressible |
| P11b | `P11b` | reposed (one stage) | expressible |
| P11c | `P11c` | incremental | expressible with reformulation |
| P11d | `P11d` | incremental | expressible with reformulation |
| P12a, P12b, P12c, P12d (each at n = 8, 12, 16, all and any) | `P12<x>.n<n>.<mode>` (24 identical texts) | reposed (one stage) | expressible with reformulation (ambiguity 12) |

Single-stage sub-problems are declared `reposed`, as in batches 1A and 1B:
with one stage both posings send the same input. Incremental programs handle a
replay message `2 j` as `1 j`, since they dispatch on the stage number; P11c
and P11d also handle `3 j` (a replayed commitment, below).

### P09: computations one after another

ALGOL 60 has one computation. A spawned computation is a part of the one
program, run by the message `4 1 c` to its end before the program reads the
next message (harness README, 2.6): `side_by_side: false`. The computations
share the program's variables (the "one database").

- **P09a.** A is `loop(xk, x, found)`, batch 1B's P04 procedure, by loop's one
  case: it calls itself and never returns. B is `rev` computing b from a by its
  cases, in order, with `conc` computing its third place, batch 1A's P03e
  transcription, mode-faithful. In the order A, B, A never ends: in report and
  x1 it is stopped by its budget, which ends the process, so B is not started
  (harness `QUESTIONS.md`, A3); in x1sim it runs until the safety limit or the
  X1's stack. In the order B, A, B reports `b = (3, 2, 1)` and finishes, and
  then A starts. That the order matters is the result the problem asks to
  record; no scheduler was written to interleave them (it would be S, and
  ALGOL 60 has no coroutines to build one from).
- **P09b.** Each equation is a procedure, batch 1B's `equals`, that tests its
  unknown when known and otherwise gives it the value for as long as `found`
  runs. A is `x = c1` and then, in `found`, `x = c2`; it reports nothing and
  its observe block says `no solution`. B is `y = c3`, which reports `y = 3`.
  A's failure only ends A's procedure; B runs as if A had not.
- **P09c.** `gen` computes s from n by its two cases, in order, as a function
  (the direction the query uses), and `sum3` computes total from s by its one
  case: s must have at least three elements p, q, r, and total is p + q + r.
  The conjuncts run in order, so `gen` has finished before `sum3` starts; the
  observe block says so. One answer, `total = 6, s = (1, 2, 3, 4, 5)`.
  *Expressible*: both are mode-faithful transcriptions (rule 3).
- **P09d.** `genu` is its one case as a function: the sequence of n followed by
  the s of `genu(n + 1)`. It never returns, so no cell is made and `sum3` is
  never reached. In report and x1 the expectation is the budget; in x1sim the
  safety limit or the X1's stack. Nothing is reported (ambiguity 4).
- **P09e.** Batch 1B's P07b design: each relation held as posed, with an
  evaluator that gives the other place its value when one is known, or tests
  the relation when both are. Neither x nor y is known, so neither relation
  acts: the answer is `x held, y held, where x = y + 1, y = x - 1`, and the
  observe block gives `[suspended held-relations 2]`, which tells the state
  apart from completion. No deadlock is reported as such; the program has no
  notion of one. The holding code is R (rule 19).
- Counters (H): `loop/1`, `rev/1`, `rev/2`, `conc/1`, `conc/2`, `gen/1`,
  `gen/2`, `genu/1`, `sum3/1`, `R1-examined`, `R2-examined`. Integers inside
  P09a's and P09c's sequences are printed digit by digit (an output adapter),
  so that a longer sequence in a variant does not run past the X1's seven
  `print` columns on a line.

### P10: named quantities as variables

- **P10a, P10c.** A named quantity is an integer variable, with a Boolean that
  says whether it has a value yet. "b becomes e" is an assignment, its right
  side taken at the values before the stage, which is what the assignment
  statement does (Revised Report 4.2). In P10c, "d becomes 2 · b" is an
  assignment too, so d keeps 20 when b is replaced. Earlier values are not
  kept, and cannot be retrieved; the observe block says so. *Expressible*: the
  replacement is native.
- **P10b.** The standing relation d = f · b is held, as posed, by a Boolean.
  After every stage its evaluator is examined: while b has no value it waits
  (`[suspended held-relations 1]`); once b has one it gives d the value f · b,
  again after every stage, whatever d was. The answer at stage 1 is
  `b held, d held, where d = 2 . b` (the product printed as `.`, as in batch
  1A); then `b = 10, d = 20`, `b = 15, d = 30`, `b = 7, d = 14`. The counter
  `[operations d-recomputed N]` gives how many times d has been recomputed
  since the computation started: once per stage after b has a value. The
  holding is R (rule 19); computing d from b is P.
- **P10d.** pick's facts are read at stage 1 and held as given. Each
  comparison is held as posed by a Boolean that says it is in force; a
  withdrawal sets it out of force, and the observe block lists it as
  withdrawn. After every stage the values of x are those facts that pass every
  comparison in force, tested again from the facts. So at stage 3 the value
  1 comes back, all values of x are held at once, and nothing is restated.
  The holding is R. `[problem-alternatives x N]` and the counters `pick/i`
  and `x-gt-tested` as in batch 1B's P05 (ambiguity 8).

### P11: effects, one outcome at a time

`emit(m)` is bound as printing `[emit]m[/emit]` (harness README, 2.5). An
answer, and an entry emitted, is x alone, printed digit by digit with no
spaces, so that a replayed commitment v can be read back with `ininteger` or
`read` (ambiguity 11). Every P11 query is for any one outcome.

- **P11a, P11b.** pick's facts are tried in order, one at a time: a fact gives
  x its value, and the conjuncts after pick are carried out on it in the order
  written, `x ≥ c` and then `emit(x)` in P11a, `emit(x)` and then `x ≥ c` in
  P11b. The loop over the facts stops at the first x that passes the whole
  conjunction (`for … while ¬ok ∧ cur < nf`): the query asks for one answer.
  P11a emits only 2; P11b emits 1, then 2. No deferral is arranged: emit is
  carried out where the conjunction places it. The stop in the loop's
  condition is C, the construct that ends the search at the answer
  (`problems/11-irreversible-effects.md`, Rules; the end of the query is where
  commitment happens, in ALGOL 60's terms).
- **P11c, P11d.** The same, held between stages. The program keeps pick's
  facts, the position reached in them, and every relation posed after
  `pick(x) and emit(x)`, in the order posed. At stage 1 the first fact gives x
  = 1, `emit(1)` is carried out, and x = 1 is reported. When a later stage's
  relation refutes the outcome held, the next facts are tried in the same way:
  each gives x its value, `emit(x)` is carried out again (it is stage 1's
  conjunct, after pick), and the relations posed so far are tested. Commit
  selects the outcome held, v, reports it, and adds the information x = v,
  held as one more relation (ambiguity 9). A replayed commitment (`3 j`, then
  v) adds x = v in the same way, without selecting. So:
  - P11c: stage 1 emits 1; stage 2's x ≠ 1 refutes it, and 2 is emitted and
    reported; stage 3 commits to 2. L = ⟨1, 2⟩.
  - P11d: stage 1 emits 1; stage 2 commits to 1; stage 3's x ≠ 1 refutes it,
    the remaining facts are tried, 2 and 3 are emitted and fail x = 1, and no
    solution is reported. L = ⟨1, 2, 3⟩.

  These are the author's expectations from the text, not results. The holding
  of the relations and of the position is R (rule 19). The observe block
  gives `[bind x]`, the relations held, the commitment, the facts tried and
  untried, `[held-as backtracking]` and `[problem-alternatives x N]` (the
  outcome held and the untried facts), and the counters `pick/i`
  (ambiguity 10).

### P12: choice by its cases, depth first

`choice(n, s)`, with s unknown, is a procedure with its two cases in order,
passing each solution to the parameterless procedure `found` (batch 1B's P04
design): case 1 sets s to ⟨⟩ and calls `found`; case 2, if n > 0, makes the
cell of s with its head e and its tail t still to come, and for e = ʟ and then
e = ʀ calls `choice(n − 1, t)` with t the tail of that cell, passed by name
(Revised Report 4.7.3.2), so that the recursive call gives the tail its value
in place. s is then complete whenever `found` runs, with no reordering of the
head (no move). `found` is `accept`: a closed world of facts, read from the
constants as sequences, each tested against s in order by the equality of
sequences; each fact equal to s is one solution, reported as
`s = (l, l, r)`. The candidates come in the order of the problem's
depth-first reference (⟨⟩ first, ʟ repeated n times the n + 1st, ⟨ʀ⟩ the
2ⁿ + 1st, ʀ repeated n times the last).

- **all** (cap 20): the whole space is covered and every solution printed,
  and the program finishes; the harness collects the first 20.
- **any** (cap 1): at the first solution, a `go to` statement leaves the
  recursion at once for the label `done` before the observe block (Revised
  Report 4.3; `examples/exits.alg` in the image shows the same exit from a
  deep recursion). That `go to` is C. Which mode applies is read from the
  instance line's cap (1 for `any-one`).
- After each answer the program prints, outside any tag, `candidates
  examined so far: N`, so the candidates before each solution are in the
  stage's print. The observe block gives `[candidates N]` (accept evaluated),
  `[operations choice/1 N]` and `choice/2` (each application of case 2 with
  one e), the peak length of the partial sequence held and the peak number of
  alternatives e = ʀ kept for backtracking (H counters, as text), and
  `[problem-alternatives partial-sequences 0]`: at the end of the stage the
  program holds no partial sequence, in either mode.
- R and C, by the author's reading: the parameter `found` (an extra argument,
  rule 5) is R; giving back the cell made for s (`top := top - 1`) is C
  (rule 16); the `go to` of the any mode is C. Making the cell of s and
  setting its head and tail are operations on the encoding (rule 15), P.
- Store: the facts' cells are fixed at 2000 in one place, and the search uses
  n + 1 more (ambiguity 15).

## Constants files (batch 1C)

| instance | file contents | layout |
|---|---|---|
| P09a.AB, P09a.BA | `1: 3 1 2 3` | L, then the sequence of B's rev(⟨…⟩, b); A reads the line and does not use it |
| P09b | `1: 1 2 3` | c1 c2 of A (x = c1 and x = c2), c3 of B (y = c3) |
| P09c | `1: 1` | g of gen(g, s) |
| P09d | `1: 1` | g of genu(g, s) |
| P09e | `1: 1 1` | c1 of x = y + c1, c2 of y = x − c2 |
| P10a | `1: 10`, `2: 5`, `3: 7` | e of b becomes e; e of b becomes b + e; e of b becomes e |
| P10b | `1: 2`, `2: 10`, `3: 5`, `4: 7` | f of d = f · b; then P10a's three |
| P10c | `1: 10`, `2: 2`, `3: 5`, `4: 7` | e of b becomes e; f of d becomes f · b; e of b becomes b + e; e of b becomes e |
| P10d | `1: 3 1 2 3`, `2: 1` | F and pick's facts; c of x > c (stage 3 has none) |
| P11a, P11b | `1: 3 1 2 3 2` | F and pick's facts, then c of x ≥ c |
| P11c | `1: 3 1 2 3`, `2: 1` | F and pick's facts; c of x ≠ c (stage 3, commit, has none) |
| P11d | `1: 3 1 2 3`, `3: 1` | F and pick's facts; (stage 2, commit, has none); c of x ≠ c |
| P12a.n`N`.* | `1: 2 1 2 N 1 … 1` | F, then each fact as its length and atoms: ⟨ʀ⟩, then ʟ repeated N times (ʟ is 1, ʀ is 2) |
| P12b.n`N`.* | `1: 1 1 2` | ⟨ʀ⟩ |
| P12c.n`N`.* | `1: 1 N 2 … 2` | ʀ repeated N times |
| P12d.n`N`.* | `1: 1 N 1 … 1` | ʟ repeated N times |

In P09a and P09b the harness sends stage 1's line after each spawn message, so
each computation reads all of it (ambiguity 1). No stage's code reads another
stage's constants, and nothing in a program depends on a later stage (rule 5).

## Idioms and their sources (batch 1C)

Cited in each program's `PROVENANCE idioms` comment:

- the Revised Report on ALGOL 60 (1962): as in batches 1A and 1B, and also the
  assignment statement as replacement (4.2, P10), a subscripted variable given
  as an actual parameter called by name and assigned to (4.7.3.2, P12's tail),
  and the go to statement leaving procedures (4.3, P12's any mode);
- a parameterless procedure passed as an actual parameter for each solution:
  Knuth's man or boy test (1964, `examples/man-or-boy-1964.alg` in the image,
  read by batch 1B; cited after it, not reread);
- the depth-first enumeration of a space by a recursive procedure: Wirth's
  eight queens (`examples/queens.alg` in the image, read), for P12;
- leaving a deep recursion at once by a `go to`: `examples/exits.alg` in the
  image (read), for P12;
- *report*: `ininteger`, `outinteger`, `outstring` (IFIP 1964, systems file);
  *x1, x1sim*: `read`, `print`, `PRINTTEXT`, `NLCR` and the X1 compiler's
  representation (harness README, 2.1), cited after Kruseman Aretz 2003,
  chapter 7, second-hand, as batches 1A and 1B did; the X1's line of 144
  positions and at most seven `print` columns on a line from `docs/x1.md` in
  the image (read); `goto` written as one underlined word, as the x1sim
  examples write it (seen in a search of them);
- sequences as parallel arrays of heads and tails, facts as arrays of codes:
  the systems file, Values;
- the message loop, instance line and observe block: the harness README's
  example X01; the spawn message (2.2, 2.6) and its qualification program
  `x03-spawn.alg`; emit and the replayed commitment (2.5) and the
  qualification program `x02-incremental.alg`, whose answer is the integer
  alone so that v can be read back;
- holding a relation, a standing relation, or the position reached in pick's
  facts, until it can be decided or is refuted: no period source; written for
  these problems (rule 19).

The X1 manual's rules followed in all three texts, as in batch 1B:
declarations in the order scalars, arrays, procedures (property 15); no
conditional statement straight after `do` (property 12); identifiers unique in
their first nine characters (property 3); every formal parameter specified
(property 19). Neither dialect stops evaluating `∧` and `∨` early, so no
subscript is guarded by `∧` (P09's `sum3` tests the length by nested `if`s).

## Ambiguities, and the reading taken (batch 1C)

1. **P09a, P09b: the constants of a spawning stage.** The harness sends all of
   stage 1's lines after each spawn message (README 2.2). *Reading:* both
   computations read the whole line; each uses its own part. In P09a, A reads
   B's sequence and does not use it; in P09b, A and B each read c1 c2 c3.
2. **P09a, P09b: is running side by side part of the problem?** ALGOL 60 has no
   separate computations; the harness spawns them one after another
   (`side_by_side: false`). *Reading:* the definitions are transcribed, and the
   sequential running is the configuration's behaviour, a result, not a
   matter of expressibility. P09a and P09b are *expressible with
   reformulation* only because of the `found` parameter (batch 1B's reading of
   P04). A classifier who takes concurrent running as part of what the problem
   asks to be expressed would call P09a *not expressible*; a hand-written
   scheduler would be S, and was not written.
3. **P09c, P09d: which numbers are constants.** `stages.json` writes the stage
   as `gen(<k>, s)` and `genu(<k>, s)`. *Reading:* only that k is a stage
   constant, in the constants file; gen's bound 5 and sum3's three elements
   belong to the definitions and are in the program text. A variant that
   changed the bound would need the program changed.
4. **P09d under its two readings.** The transcription is eager: `genu` must
   return before `sum3` can look at s, and it never returns. *Reading:* that
   is the transcription, and P09d is *expressible* (mode-faithful). Under the
   finite reading P09d1 nothing is reported, which is the valid outcome; under
   the stream reading P09d2 total = 6 is never computed. A demand-driven
   producer (sum3 asking a generator procedure for three elements, by call by
   name) would change the order of the conjuncts and genu's form, a
   reformulation the problem does not give; it was not written.
5. **P09e.** *Reading:* as batch 1B's P07b, the relations are held and nothing
   is solved; the program reports the residual with both relations held, and
   neither enumerates the pairs nor reports a deadlock.
6. **P10b: the standing relation.** *Reading:* its evaluator gives d from b,
   the direction the problem defines ("d is defined by a relation that must
   hold whenever b has a value"); it does not give b from d, since d is never
   given a value by a stage. While b has no value the relation is reported as
   suspended. After that it is re-examined after every stage, but it is not
   tagged as suspended, since it has been decided for the value b has; the
   observe block names it as a standing relation. A classifier may read a
   standing relation as held work at every stage.
7. **P10: what a named quantity without a value is.** *Reading:* a Boolean per
   quantity; P10a's and P10c's answers say `has no value` (P10c's d before
   stage 2), and P10b's say `held` while the relation waits, as batch 1A's
   answers do.
8. **P10d: holding pick's facts, and no anticipation.** Batch 1B's P05
   programs drop a value that fails a test and do not keep it. P10d's program
   keeps pick's facts as given at stage 1 and recomputes the values of x from
   them at every stage, from the comparisons in force. *Reading:* that is how
   a closed world of facts is held, and stage 2's code (it sets its comparison
   in force) does not depend on stage 3, so it is not anticipation (rule 5);
   but the author wrote it knowing that a withdrawal follows, and a classifier
   may weigh that. The withdrawn value comes back without restating.
9. **P11: what commit is.** The problem says commit selects v and adds the
   information x = v. *Reading:* exactly that: x = v is held as one more
   relation, tested in the order posed. Nothing discards pick's untried
   facts. So in P11d, when stage 3 refutes the committed outcome, the program
   tries the remaining facts, and the conjunct `emit(x)`, which comes before
   the relations in the order written, is carried out for each: L gets
   entries for outcomes that were never committed. A program that discarded
   the untried alternatives at commit (a cut, C) would avoid them; it was not
   written, since nothing in the problem's statement of commit removes
   alternatives.
10. **P11c, P11d: the untried facts.** They are kept and are resumed if a
    later stage refutes the outcome held, which is neither a request for more
    answers (*alternatives pending*) nor quite work waiting for information
    (*suspended*). *Reading:* as batch 1B's ambiguity 7, they are reported as
    problem-defined alternatives with `[held-as backtracking]`, not as
    `[alternatives …]` or `[suspended …]`, so the harness will read the
    execution state as *finished*. A classifier may class it otherwise from
    the observe block.
11. **P11: the form of an answer.** The harness passes the commit stage's
    answer back verbatim as v, to be read as an integer. *Reading:* an answer
    is x alone, its digits printed with no padding, in all three texts, since
    the X1's `print` pads and signs an integer in a column.
12. **P12: "a search written by hand is supporting code".** ALGOL 60 has no
    search of its own. *Reading:* `choice` is its two cases transcribed, in
    order, as a procedure that passes on its solutions, and the order in
    which they come is the language's own order of procedure calls, depth
    first; nothing in it is general over relations, it keeps no queue or
    stack of its own, and accept is its facts. So it is R in the core
    configuration (rule 19, batch 1B's reading of P04), and P12 is
    *expressible with reformulation*. A classifier who reads the problem's
    rule as covering any program that enumerates choice's solutions would
    class `choice` S, making P12 *not expressible* in the configurations as
    listed, and these programs named variants.
13. **P12: the two answer modes.** *Reading:* *all* covers the whole space and
    prints every solution (the space is finite, so the program finishes);
    *any* stops at the first, by a `go to` (C). The mode is read from the
    instance line's cap, which `stages.json` sets to 1 for `any-one` and 20
    for `all`.
14. **P12: constants that depend on n.** `stages.json` says accept's facts
    depend on n. *Reading:* one constants file per instance, each giving the
    facts in full, ʟ and ʀ as the codes 1 and 2; the program text is the same
    for all 24. The verifier will need one variant constants file per
    instance, or per sub-problem and n.
15. **Fixed store.** P12's facts at most 2000 cells in all, and at most 2000
    facts; P09d's 1000 cells (never used, since genu never returns); pick's
    facts at most 1000 in P10d and P11. P09a's and P09c's store is sized from
    the input. A variant needing more would stop with an index error, not a
    wrong answer.
16. **The values unknowns range over.** As before: integers, an atom being its
    code, sequences flat sequences of integers.

## What the author read and ran (batch 1C)

Read: `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
`AMENDMENTS.md`; `problems/README.md` and the files of P09, P10, P11, P12, and
of P03, P04 and P05 for the definitions; `systems/algol-60/README.md`;
`harnesses/README.md`; `harnesses/stages.json` (its preamble, lines 1–40, the
lines naming each sub-problem's id, and lines 318–520, P09 to the start of
P12d's instances); `harnesses/algol-60/README.md`, `QUESTIONS.md`,
`S-mechanisms.md` and `check`, the lines of `run` that mention spawn or
observe, the list of the qualification programs and records, the
qualification programs `x03-spawn.alg` and `x02-incremental.alg` with its
constants, and the lines of `qualification/stages-made-up.json` about X02 and
X03; this README; the batch 1B programs `report/P04a.alg`, `report/P04f.alg`,
`report/P05a.alg`, `report/P07b.alg` and `x1/P05a.a60`, and the batch 1A
program `report/P03e.alg`; and, through the converter's check, the differences
between its output and the committed X1 texts of P01b, P02a, P03e, P04f, P05a,
P06d, P07b and P08a. In the image: the listings of `/opt/src/algol-60` (top
level, `docs/`, `examples/`, `historical/`) and `/opt/src/x1sim` (top level,
`doc/`, `examples/`); `/opt/src/algol-60/docs/x1.md`, `examples/exits.alg`,
`examples/queens.alg` and `examples/own.alg`; the lines of
`/opt/src/x1sim/doc/library-procedures.md`, `README.md` and
`examples/README.md` that mention read or print; and the lines of the
`/opt/src/x1sim/examples/*.a60` files that write `goto`, `own` or `label`. The
top-level listing of `/opt/src/algol-60` shows the name of the `compare/`
directory; nothing in it was listed or read. The examples' listing shows
their `.out` files; none was read.

Ran: `harnesses/algol-60/check` on every program in its configuration (the X1
texts in x1 and in x1sim), in the brief's form, one container run each, from
a small host shell loop that filters the output. Also, beyond the brief's
list: in the image, `ls`, `cat` and `grep` to read the documentation above
(four container runs); on the host, `python3` only to edit text (to derive
P11b from P11a and P11d from P11c, to rename variables in the P12 text, to
make the instance copies and constants files, and the converter to the X1
texts, with its check against batch 1B's texts), and `git`, `ls`, `cat`,
`sed`, `grep`, `diff`, `cmp`, `wc` and `cp`. Nothing executed a program of the
study, the system, or an interpreter on a program.

---

# Batch 1D (P13–P16)

*Phase 5, against `spec-1.0.1`, written to the program contract of
`harnesses/algol-60/README.md`, section 2. Every program was fixed before any
was run. The only thing run on them is the harness's `check`, which executes
nothing. It reports no error and no warning for any of them, in any
configuration: the report texts in report, and the X1 texts in both x1 and
x1sim.*

**Author of every program:** `implementation-algol-60`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`). This batch's author has its own context
and had not seen any earlier work on the study except what is listed under
"What the author read and ran" below. That includes the batch 1A–1C sections
of this README and some of their programs, which the brief allows and which
hold no outcome. **Precursors:** the author had not seen any precursor
program: not the absys experiments E01–E09, not the calibration programs (which
hold programs for P13), and no program of this study other than the batch
1A–1C ALGOL 60 programs.

**S mechanisms used:** none, in any program. Every procedure that holds a
relation, decides it, or passes its solutions on is written for that problem's
own relations, so by `METRICS.md` rule 19 it is R in the core configuration,
not S. Ambiguity 14 says where a classifier could read P16 another way.

**Named variants:** none. No sub-problem was judged not expressible. For each
sub-problem one program was chosen before any was run, and it is the primary.

## Layout, and which texts are shared

The layout is that of batches 1A–1C: `programs/algol-60/<configuration>/<file>.<ext>`
with its `.constants` beside it, `.alg` for report and `.a60` for x1 and x1sim.

- **One file per sub-problem, for all its instances.** n and the arrival order
  come from the instance line, and no constant depends on them, so (as batch
  1B's `P07a`) one program and one constants file serve every instance of a
  sub-problem: `P13a` serves `P13a.n100` … `P13a.n100000`, `P16a` its nine
  instances (three sizes, three orders), and `P16b`, `P16c`, `P16d`, `P16d2`
  their three sizes. Run them as, for instance,

      harnesses/algol-60/run report P13 P13c.n1000 behaviour programs/algol-60/report/P13c.alg OUTDIR
      harnesses/algol-60/run x1sim  P16 P16a.n100.interleaved behaviour programs/algol-60/x1sim/P16a.a60 OUTDIR

  Every other sub-problem has one instance, of its own name.
- **No constants file** for `P13e`, `P13f` and `P16d2`: their stages have no
  constant (ambiguities 3 and 16).
- **x1 and x1sim share one text**, as before: every `.a60` file of this batch
  in `x1/` is byte-identical to the file of the same name in `x1sim/`, and so
  are the constants files.
- **The X1 text is made from the report text by the fixed substitution of
  batches 1B and 1C** (reserved words underlined outside comments and strings,
  `Boolean` written `boolean`, `go to` written `goto`; `ininteger(0, v)` written
  `v := read`; `outstring(1, "t")` written ``PRINTTEXT(`t')``, a `\n` in it
  written `NLCR`, the statements one call becomes wrapped in `begin … end`; the
  comment on idioms changed to name the X1 procedures). This batch carried it
  out with a `sed` script, which only rewrites text, and checked that no string
  in a report text holds a reserved word (which the substitution would
  underline). The report texts write `¬ ∧ ≠ ≤ ≥ × ÷` as symbols and print every
  integer with the digit-by-digit output adapter `num` (no `outinteger`), so
  nothing else changes. Same algorithm, same structure, same constants.
- **Identical texts within a configuration:** `P14a` = `P14c` (P14c is P14a's
  stages and two more). Nearly identical: `P15a1` and `P15a2` differ only in
  the `go to` that leaves at the first answer; `P15b` and `P15b2` only in the
  order of merge's arguments; `P16d` and `P16c` only in stage 3's relation.

## Programs, per configuration and sub-problem

Every program below is **primary**, and exists in all three configurations:
`report/<file>.alg`, and `x1/<file>.a60` = `x1sim/<file>.a60`. The
expressibility is the author's reading, for the classifiers to confirm. It is
the same in all three configurations, which share the algorithm, and nothing
in these problems uses a feature one configuration has and another lacks (but
see ambiguity 1 on the X1's store and integers).

| sub-problem | file | instances | posing | expressibility |
|---|---|---|---|---|
| P13a | `P13a` | n = 10², 10³, 10⁴, 10⁵ | reposed (one stage) | expressible |
| P13b | `P13b` | the same | reposed (one stage) | expressible |
| P13c | `P13c` | the same | reposed (one stage) | expressible |
| P13d | `P13d` | the same | reposed (one stage) | expressible |
| P13e | `P13e` (no constants) | the same | reposed (one stage) | expressible (native) |
| P13f | `P13f` (no constants) | the same | reposed (one stage) | expressible (native) |
| P14a | `P14a` | one | incremental | expressible |
| P14b | `P14b` | one | reposed (one stage) | expressible |
| P14c | `P14c` (= `P14a`) | one | incremental | expressible |
| P15a1 | `P15a1` | one | reposed (one stage) | expressible with reformulation |
| P15a2 | `P15a2` | one | reposed (one stage) | expressible with reformulation |
| P15b | `P15b` | one | reposed (one stage) | expressible with reformulation (ambiguity 10) |
| P15b2 | `P15b2` | one | reposed (one stage) | expressible with reformulation (ambiguity 10) |
| P15c | `P15c` | one | reposed (one stage) | expressible with reformulation |
| P15d | `P15d` | one | incremental | expressible |
| P16a | `P16a` | three sizes × three orders | incremental | expressible with reformulation |
| P16b | `P16b` | three sizes | incremental (stage 1 by the spawn fallback) | expressible with reformulation |
| P16c | `P16c` | three sizes | incremental | expressible with reformulation |
| P16d | `P16d` | three sizes | incremental | expressible with reformulation |
| P16d2 | `P16d2` (no constants) | three sizes | incremental | expressible with reformulation |

Single-stage sub-problems are declared `reposed`, as before: with one stage
both posings send the same input. The incremental programs handle a replay
message `2 j` as `1 j`: P16's programs dispatch on the stage number, and P14's
and P15d's do not look at it at all (ambiguity 6).

### P13: the definitions as functions, and arrays for the native tasks

- **Representation (prescribed).** A sequence is batch 1A's cell: an index into
  the integer arrays `hd` and `tl`, 0 being ⟨⟩ and a cell c being ⟨hd[c]⟩ ++
  tl[c], so taking the tail is one subscript, in constant time, as the problem's
  section "Representation" requires of ALGOL 60 ("arrays with an index for the
  tail"). `cons` makes a cell. No cell is ever given back: ALGOL 60 has no
  reclaiming of store. The arrays are sized from the stage's k and n, for the
  cells the definitions make.
- **P13a.** `range(m, n)` computes s by its two cases, in order, as a function
  (the direction the query uses): case 1 when m > n gives ⟨⟩; case 2 computes
  t := range(m + 1, n) and then makes the cell ⟨m⟩ ++ t. A mode-faithful
  transcription (rule 3): *expressible*. The recursion is n deep.
- **P13b.** `range`, then `sum(s)` by its two cases in order, case 2 taking its
  conjuncts in order: j := sum(tl[s]), then k := hd[s] + j. The answer is
  `k = …, s = (…)`.
- **P13c.** `range`, then `rev` and `conc` exactly as batch 1A's P03e
  transcribes them (rev's case 2: q := rev(l), then conc(q, ⟨h⟩)); quadratic,
  n(n+1)/2 applications of conc's cases. The store is sized for the n cells of
  s, the n cells ⟨h⟩ and the n(n−1)/2 cells conc copies (ambiguity 1).
- **P13d.** `range`, then `revacc(s)` by its one case, `racc(s, ⟨⟩)`, and
  `racc(a, c)` by its two cases: case 1 when a = ⟨⟩ gives c; case 2 gives
  racc(tl[a], ⟨hd[a]⟩ ++ c). Linear: 2n cells. ALGOL 60 has no tail calls, so
  racc's recursion is n deep too.
- **P13e, P13f (native).** The algorithm: the sequence ⟨1, …, n⟩ is built in an
  integer array `s[1:n]` by a `for` statement (`s[i] := i`) and held there until
  the answer is printed; P13e then adds its elements in order into `total` by a
  second `for` statement, P13f copies them in reverse order into a second array
  (`r[i] := s[n + 1 − i]`). Both linear in steps, n (P13e) or 2n (P13f)
  elements of store. This is the systems file's "integer array with a length"
  and the Revised Report's `for` statement over an array (4.6), the period's
  own idiom; rule 18 makes its tokens P.
- **Answers.** The whole of s and r is printed, ten elements to a line, so that
  no line of the X1 passes its 144 positions (the tags are kept whole; the
  harness reads answers across lines). The unknown the problem calls k is
  `total` in the program, since `k` there is the stage number; it is printed
  and bound as `k`.
- **Observe.** The cells (or elements) held after the answer, which the
  program keeps until it ends, and `[operations …]` counters (H) for each case:
  `range/1`, `range/2`, `sum/1`, `sum/2`, `rev/1`, `rev/2`, `conc/1`, `conc/2`,
  `revacc/1`, `racc/1`, `racc/2`. Nothing is suspended and no alternative is
  held: every stage is *finished* if it ends. The native programs count the
  elements built and added (or moved) in plain text, since they apply no case
  of a defined relation.
- **Recursion at n = 10⁵.** The systems file lists no flag that raises the
  interpreter's depth of recursion, so none is set; if the depth is exceeded,
  the error is the result (`problems/13-deterministic-scale.md`,
  Representation).

### P14: the counter as the running program

- **P14a, P14c.** The counter is implemented as a process holding its count,
  which the problem allows as a transcription: the incremental program itself,
  which reads each message as it arrives (the systems file's "same
  computation") and answers before reading the next. The count is one integer
  variable, 0 at first (run(m, 0)). Each message is taken by run's case for
  its head: INC (case 2) adds one; READ(r) (case 3) gives the next unknown,
  r1, r2, …, the count. Case 1 would close the stream, and no stage closes it.
  A message with no case of run makes run false from then on (`no solution`).
  Each stage answers with every unknown bound so far (`r1 = 2, r2 = 3`), or
  `no unknowns` before the first READ (the stage's one, empty, solution). r₁ is
  reported at stage 3, before later messages arrive. The observe block gives
  the count held, `[bind r1]`, … and `[operations run/2 …]`, `run/3`.
- **P14b.** `run(s, c)` transcribed by its three cases, in order, as a recursive
  Boolean procedure over the sequence of the stage (read as cells), with the
  count passed down as its second place: P, the relation as the problem
  defines it. Answer `r1 = 2, r2 = 3`.
- **How the count is held** (P14's observation): as a variable of the running
  program between messages, which waits on its next read. The harness re-creates
  that process for each stage's budget in report and x1 (its `QUESTIONS.md`,
  A2), and keeps one live process in x1sim. The waiting is not tagged
  `[suspended …]` (ambiguity 7).

### P15: merge, fairness, and a resource

- **P15a1, P15a2.** `merge(a, b, m, found)` is its four cases, in order, as a
  procedure that passes each solution to `found` (batch 1B's P04 design and
  batch 1C's P12): case 1 sets m := b; case 2, when a ≠ ⟨⟩ and b = ⟨⟩, m := a;
  cases 3 and 4 make the cell of m with its head and its tail still to come,
  and pass the tail by name to the recursive merge, which gives it its value
  in place (batch 1C's P12 idiom), and give the cell back when done (C,
  rule 16). Interleavings come depth first, in the order of the cases:
  ⟨1,2,3,4⟩, ⟨1,3,2,4⟩, ⟨1,3,4,2⟩, ⟨3,1,2,4⟩, ⟨3,1,4,2⟩, ⟨3,4,1,2⟩, the same at
  every run (the interpreter is deterministic). P15a2 prints all six and
  finishes; P15a1 prints the first and leaves the recursion by a `go to` (C, as
  P12's any mode). `[problem-alternatives interleavings 0]`: nothing is held
  after the stage, in either. R: the parameter `found` (rule 5).
- **P15b, P15b2.** The conjuncts in order: `zeros` by its one case, as a
  function, as batch 1C's P09d transcribes genu: it must have z's tail before
  it can make z's cell, and before merge can begin, and it never returns. So
  merge (P15a's) and `position` (its two cases, in order, as a function,
  0 for no solution) are never reached, in either argument order, and nothing
  is reported: the expectation is the budget (or the interpreter's limit on the
  depth of recursion) in report and x1, and the safety
  limit or the X1's stack in x1sim. No fair merge was written: merge's cases in
  order take from z first, and fairness is a requirement the problem says the
  definition does not give (ambiguity 10).
- **P15c.** `grant(p, q, g, found)` is its two facts, in order. The query asks for
  one answer: `found` reports g = p (`g = 1`, ᴀ being 1) and leaves by a `go to`
  (C), so the second fact is never tried, and nothing is kept that could
  revisit the choice: the choice is the order of the facts, and it is
  committed. `[operations grant/1 1]`, `grant/2 0`.
- **P15d.** holder and queue are named quantities, each one variable (batch 1C's
  P10a), replaced by assignment at each stage by the problem's cases: a
  request gives holder p if it is none, else queue becomes queue ++ ⟨p⟩ (++ by
  conc's cases, copying); a release by the holder gives holder none if queue is
  empty, else holder becomes queue's head and queue its tail. Answers:
  `holder = 1, queue = ()`, `holder = 1, queue = (2)`, `holder = 2, queue = ()`.
  ʙ's waiting is held as an element of queue, a value, and stage 3's release
  grants it: ʙ's request is not posed again. A grant is never withdrawn by a
  later request. `[bind holder]`, `[bind queue]`, and counters for the cases of
  request, release and conc.

### P16: relations held on lists of their unknowns

ALGOL 60 has no unknowns. Each unknown is a Boolean (has it a value?) and an
integer, in arrays sized from n: x_i is unknown i, y_i (P16c, P16d) unknown
n + i, total (P16b) the last. Each relation is held as posed in arrays of its
kind and places, with a Boolean that says it is still held. Its **evaluator**
(rule 19) decides it from the places known: succ(a, b) gives b the value a + 1
when a is known, or a the value b − 1 when b is known, or tests b = a + 1 when
both are; an equation x = k gives x its value or tests it; P16b's total
relation gives its sixth place when five of its six are known, or tests it;
P16d2's x_n = x_1 gives either place the other's value, or tests it. Otherwise
it waits.

**Unlike batches 1A–1C**, which examine every held relation in order, again and
again, until a pass gives nothing, these programs keep for each unknown the
list of the relations it occurs in (in arrival order) and a queue of the
unknowns given values: a relation is examined when it arrives, and again only
when one of its places is given a value; after each relation is posed the
queue is emptied. So each succ relation is examined at most twice (on arrival,
and once when its first place becomes known, when it is decided), the work
after a value arrives is confined to what that value reaches, and P16c's stage
2 examines no y relation. This design was chosen before any program was run,
because the passes of batch 1A would examine every held relation again for
every unknown given a value along a chain followed against the arrival order,
about n²/2 examinations at stage 2 (ambiguity 14). Both are written for the
problem's own relations.

- **P16a.** Stage 1 poses succ(x_i, x_i+1), i = 1 … n − 1, in the order the
  instance line gives (ascending, descending, or odd i ascending then even i
  ascending); nothing is known, so each waits. Stage 2 poses x_j = k,
  j = ⌈n/2⌉ (computed as (n + 1) ÷ 2), and the values spread outward from x_j.
- **P16b.** ALGOL 60 has no separate computations sharing unknowns, so stage 1
  is posed to `main` as one conjunction (the harness's `spawn_fallback`,
  `QUESTIONS.md` A3): the four contributions in the order of the contributors,
  each ascending, n relations over x_1 … x_{n+1}. Stage 2 poses
  total = x_1 + x_{m+1} + x_{2m+1} + x_{3m+1} + x_{4m+1}, which waits; stage 3,
  x_1 = k, and then total = 10m once the fifth of its places is known.
- **P16c.** Both chains in one computation: the x relations, then the y
  relations, ascending. Stage 2 x_1 = k; stage 3 y_1 = k. Counters
  `[operations succ-x-examined N]` and `succ-y-examined` give each chain's
  examinations since the computation started.
- **P16d.** As P16c, with stage 3 x_n = k: x_n is known from stage 2, the test
  fails at once, and no answer is printed; the observe block says `no
  solution`. Nothing held is withdrawn or changed: the x values and the y
  relations stay as they were, and the observe block shows them.
- **P16d2.** Stage 2 (the problem's stage 3) poses x_n = x_1, with no value known:
  it waits, like every succ, and the contradiction (x_n = x_1 + n − 1) is not
  found, since nothing combines two waiting relations. That is batch 1B's P07f
  reading, for the same reason (elimination is not written).
- **Answers.** Every unknown with a value (`x1 = 0, x2 = 1, …`), or `no unknown
  is known`, then `where` and every relation still held, in arrival order
  (`succ(x1, x2), …`), five to a line for the X1's 144 positions. With n = 10⁴
  an answer is long (tens of thousands of items); it is printed in full.
- **Observe.** The held relations again (state the program acts on), a
  `[bind …]` for every unknown with a value, `[suspended held-relations N]`
  while any relation waits, and counters (H) since the computation started:
  `succ-examined`, `succ-decided`, `succ-waited` (examinations that ended with
  the relation still waiting), `equation-examined` (or `total-examined`,
  `equality-examined`), and the most examinations of any one succ relation.
  succ is not defined by cases, so these count examinations, the observation
  P16 asks for, as batch 1A's P02 does.

## Constants files (batch 1D)

| file | contents | layout |
|---|---|---|
| P13a, P13b, P13c, P13d | `1: 1` | k of range(k, n, s); n from the instance line |
| P13e, P13f | none | |
| P14a | `1: 1`, `2: 1`, `3: 2`, `4: 1`, `5: 2` | each stage's message: 1 INC, 2 READ |
| P14c | as P14a, and `6: 1`, `7: 2` | the same |
| P14b | `1: 5 1 1 2 1 2` | L, then the messages of the sequence |
| P15a1, P15a2 | `1: 2 1 2 2 3 4` | La, a, Lb, b of merge(a, b, m) |
| P15b, P15b2 | `1: 1 9 9` | L, then the known sequence of merge, then e of position(e, m, i) |
| P15c | `1: 1 2` | p q of grant(p, q, g): ᴀ 1, ʙ 2 |
| P15d | `1: 1 1`, `2: 1 2`, `3: 2 1` | r p: r 1 a request, 2 a release; p the atom, ᴀ 1, ʙ 2 |
| P16a | `2: 0` | k of x_j = k; stage 1 from n and the order |
| P16b | `3: 0` | k of x_1 = k; stages 1 and 2 from n |
| P16c | `2: 0`, `3: 5` | k of x_1 = k; k of y_1 = k |
| P16d | `2: 0`, `3: 0` | k of x_1 = k; k of x_n = k |
| P16d2 | none | both stages from n |

No stage's code reads another stage's constants, and nothing in a program
depends on a later stage (rule 5). The lists and queue of P16 are built for
whatever relations arrive, not for the stages to come.

## Idioms and their sources (batch 1D)

Cited in each program's `PROVENANCE idioms` comment:

- the Revised Report on ALGOL 60 (1962): blocks and arrays with bounds computed
  at run time (5.2.4.2), Boolean arrays (5.2), recursive procedures and
  function designators with value and name parameters (4.7, 5.4), a
  subscripted variable as an actual parameter called by name and assigned to
  (4.7.3.2, P15's tail of m), procedures as actual parameters (4.7.5, 5.4.4),
  the `for` statement with `step … until` and `while` elements, and over the
  subscripts of an array (4.6, P13e and P13f), conditional statements and
  expressions (3.3, 4.5), the assignment statement as replacement (4.2, P15d),
  and the `go to` statement leaving procedures (4.3, P15a1, P15b, P15c);
- a parameterless procedure passed as an actual parameter for each solution:
  Knuth's man or boy test (1964, `examples/man-or-boy-1964.alg` in the image),
  cited after batch 1B's reading of it, not reread; leaving a deep recursion by
  a `go to`: `examples/exits.alg` in the image, cited after batch 1C's reading
  of it, not reread;
- *report*: `ininteger` and `outstring` (IFIP 1964, systems file); *x1, x1sim*:
  `read`, `PRINTTEXT`, `NLCR` and the X1 compiler's representation (harness
  README, 2.1). This batch's programs do not cite Kruseman Aretz 2003, which
  its author did not read;
- sequences as parallel arrays of heads and tails, an array with a length,
  atoms as codes: the systems file, Values, and P13's "arrays with an index
  for the tail";
- rev and conc as batch 1A's P03e transcribes them (P13c); genu's transcription
  in batch 1C's P09d (P15b's zeros); named quantities as batch 1C's P10a
  (P15d);
- the message loop, instance line and observe block: the harness README's
  example X01;
- holding a relation until it can be decided, on lists of its unknowns with a
  queue of the unknowns given values: no period source; written for P16
  (rule 19).

The X1 manual's rules, as batches 1B and 1C state them, followed in all three
texts: declarations in the order scalars, arrays, procedures; no conditional
statement straight after `do`; identifiers unique in their first nine
characters; every formal parameter specified. Neither dialect stops evaluating
`∧` early, so no subscript is guarded by `∧` (P15's merge tests a ≠ ⟨⟩ and
b ≠ ⟨⟩ by nested `if`s).

## Ambiguities, and the reading taken (batch 1D)

1. **P13c's store, and the X1's.** Without reclaiming, rev makes n(n+1)/2 + n
   cells, all declared when the stage's block is entered: 5·10⁷ in each of two
   arrays at n = 10⁴, 5·10⁹ at n = 10⁵. *Reading:* the arrays are sized for the
   cells the definitions make, and nothing gives a cell back (a free list would
   be C, rule 16, and was not written). At n = 10⁴ the interpreter may fail to
   allocate them (an *error*) before the budget is reached; that is the cost of
   having no dynamic store, and is recorded as whatever happens. The X1 had a
   small store and 26-bit integers: in x1sim P13c (and the larger n of the
   others) is expected to stop on store, and n(n+1) overflows at n = 10⁴, before
   any step of rev. The x1 configuration runs on the interpreter, with its store.
2. **P13: recursion depth.** The prescribed definitions are recursive, and each
   is transcribed recursively, n deep (racc too: ALGOL 60 has no tail calls).
   No flag raises the depth (none is in the systems file), so an error at
   n = 10⁵ is the result, as the problem says.
3. **P13e, P13f have no constants.** `stages.json` gives their stage no
   constant, so the sequence ⟨1, …, n⟩'s first element, 1, is in the program,
   and n comes from the instance line. P13a–d read range's first place k from
   the constants.
4. **P13: printing the answer.** The valid outcomes include s (and r), so the
   whole sequence is printed, 10⁵ elements at the largest n. The output
   adapter's steps (H) are in the stage's steps.
5. **P14: the message is a constant of every stage.** `stages.json` writes
   P14a's INC stages as `message <atom>`, a constant, and its READ stages as
   `message READ(r1)`, without one. *Reading:* every stage's line gives its
   message as a code (INC 1, READ 2), READ included, and the program takes each
   message by its content, as a counter receiving messages does, not by the
   stage's number. A variant constants file must give a line for every stage,
   in this layout.
6. **P14, P15d: dispatch on the message, not the stage.** Both programs read
   the stage number and do not use it: a replay (`2 j`) and a first posing
   (`1 j`) carry the same constants and are carried out alike. P15d's stage
   kind (request or release) is in its constants for the same reason
   (ambiguity 5).
7. **P14: is the waiting counter *suspended*?** The program holds its count and
   waits on its next read, in every stage; so does every incremental program of
   batches 1A–1C, and none tags that waiting. *Reading:* it is not tagged
   `[suspended …]`, so the harness will record each stage as *finished*; the
   observe block says the count is held by the running program, which waits on
   its next message. A classifier may read P14c's question ("suspended waiting
   for messages, or finished and restarted") as answered *suspended* in x1sim,
   which keeps one live process, and as re-created in report and x1.
8. **P14: an answer with no unknowns.** Before the first READ the stage has one
   solution, with no unknowns. *Reading:* it is reported as one answer,
   `no unknowns`.
9. **P15a: what an interleaving held is.** *Reading:* after the stage nothing is
   held (`[problem-alternatives interleavings 0]`); during it, the recursion
   holds the cases not yet tried, as P12's did, and the observe block gives its
   peak depth.
10. **P15b, P15b2: the stream reading and fairness.** ALGOL 60 has no infinite
    values and no lazy ones, and the transcription of zeros in the order of the
    conjuncts never returns. *Reading:* as batch 1C's P09d (its ambiguity 4),
    the eager transcription is the program of record, and the stream reading is
    not reached: nothing is reported, in both argument orders. The
    expressibility is *expressible with reformulation* only for merge's `found`
    parameter. A classifier who holds that the greatest relation, or the
    fairness the problem adds, cannot be transcribed in ALGOL 60 would call
    P15b *not expressible*. A demand-driven zeros (a procedure called by name
    for the next element) and a merge that alternates its inputs would be a
    reformulation of zeros' form, of the conjuncts' order and of merge's cases
    (and the alternation a fairness construct, C); it was not written.
11. **P15b: which numbers are constants.** `stages.json` writes merge(z,
    `<seq>`, m) and position(`<k>`, m, i). *Reading:* ⟨9⟩ and 9 are the
    constants; zeros' 0 belongs to its definition, in the program.
12. **P15c: committed choice.** *Reading:* the any-one query stops at the first
    fact's solution by a `go to` (C); the second fact is never tried, and the
    choice is fixed by the order of the facts, the same at every run.
13. **P15d: a release by someone who is not the holder.** The problem defines a
    release only "where holder = p". *Reading:* any other release (or an
    unknown stage kind) is not defined: the program reports no answer, says
    `no solution` in the observe block, and leaves holder and queue as they
    were. ʙ's waiting is a value of queue, not tagged `[suspended …]`.
14. **P16: lists of each unknown's relations, and a queue.** *Reading:* this is
    holding code written for the problem's own relations (succ, the equations,
    the total), so it is R in the core configuration (rule 19), and P16 is
    *expressible with reformulation*. A classifier who reads the occurrence
    lists and the queue as a propagator general over relations would class them
    S, making P16 *not expressible* in the configurations as listed and these
    programs named variants. The design departs from batches 1A–1C's passes
    over every held relation; that was chosen before any run, and the passes
    were not written for P16.
15. **P16: the relations of stage 1 are generated from n and the order.** They
    have no constants (`stages.json`). *Reading:* the program poses them from
    the instance line, in the order the problem fixes; j = ⌈n/2⌉ is computed
    from n. P16b's m is n ÷ 4 (`q` in the program, since `m` there is the
    instance line's count of codes); if n were not a multiple of 4 the four
    contributions would cover 4m relations.
16. **P16d2's stages.** `stages.json` numbers them 1 and 2; the problem file 1
    and 3. *Reading:* `stages.json`'s numbering, and x_n = x_1 has no constant,
    so there is no constants file.
17. **P16: the size of answers and observe blocks.** Every value, every held
    relation and a bind tag for every unknown with a value are printed, in
    full, at every stage: at n = 10⁴, tens of thousands of items, twice.
    *Reading:* that is what the program holds and the problem's outcomes name;
    the output adapters' steps (H) are in the stage's steps.
18. **Fixed store.** P14a and P14c hold at most 1000 READ unknowns; P15a's cells
    2000; P15b's and P15d's 10000. P13, P14b and P16 size their store from the
    input. A variant needing more would stop with an index error, not a wrong
    answer.
19. **The values unknowns range over.** As before: integers, an atom being its
    code, sequences flat sequences of integers.

## What the author read and ran (batch 1D)

Read: `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
`AMENDMENTS.md`; `problems/README.md` and the files of P13, P14, P15 and P16;
of P07 the lines about P07f (a search), of P09 its section P09d and its
observations, and of P10 its first 60 lines (to P10d's heading);
`systems/algol-60/README.md`; `harnesses/stages.json` (its top-level keys,
the lines that name P13–P16, and lines 520–740, P13 to the end);
`harnesses/algol-60/README.md`, `S-mechanisms.md`, `QUESTIONS.md`, the first
80 lines of `check`, and the lines of `run` that hold its tag patterns; this
README in full; the batch 1A–1C programs `report/P03e.alg`, `report/P09e.alg`
and part of `x1/P09e.a60`, `report/P09d.alg`, part of `report/P09c.alg` and
of `x1/P09c.a60` (the output adapter `num`), `report/P12a.n8.any.alg`,
`x1/P10a.a60`, and the lines of `report/P08a.alg`, `x1/P08a.a60` and
`x1/P12a.n8.any.a60` that a search for procedure headings and `goto` showed,
and the names of the batch 1B programs that declare a `Boolean array`. Not
read: `harnesses/README.md` (allowed, not needed), and nothing in the image:
no command was run in it but `check`, so no idiom is cited from the image
except through the earlier batches' reading, as said above. No file outside
the brief's list was read.

Ran: `harnesses/algol-60/check` on every program in its configuration (the X1
texts in x1 and in x1sim), in the brief's form, one container run each, from a
small host shell loop that filters the output; once by mistake with the
arguments not split (the check printed its usage and ran nothing). On the host:
`python3 -c` once, to print the top-level keys of `harnesses/stages.json` (it
read the JSON file and ran no program of the study or the system); `sed` to
edit the report texts and to make the X1 texts from them, `grep` to check
that no string holds a reserved word or a character the X1 code lacks, and
`git`, `ls`, `cat`, `cp`, `cmp`, `diff`. Nothing executed a program of the
study, the system, or an interpreter on a program.
