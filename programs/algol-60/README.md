# ALGOL 60 programs, wave 1, batch 1A (P01–P03)

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
