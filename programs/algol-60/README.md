# ALGOL 60 programs, wave 1: batch 1A (P01–P03) and batch 1B (P04–P08)

*Batch 1B has its own section, [below](#batch-1b-p04p08). What follows up to it is batch 1A's, unchanged.*

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
