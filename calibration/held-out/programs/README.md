# Held-out calibration programs: P02, Python core and ALGOL 60 report

These are development examples for testing the token-classification rules
(`METRICS.md`, Calibration). They are not results.

## Author

Claude (Opus 5.5, model id `claude-opus-5-5`), as an agent, in the role of
implementation author. Written on 27 November 2026, against draft 0.6.

## What the author read

- `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`.
- `problems/02-late-information.md`, `problems/01-unknown-equality.md`,
  `problems/README.md`.
- `systems/python/README.md`, `systems/algol-60/README.md`.
- For the ALGOL 60 interpreter, as the system's manual: its `README.md`,
  `docs/decisions.md`, `algol60 --help`, `examples/average.alg` and
  `average.in` (the manual's example of reading input), and, in `src/`,
  the list of built-in procedures and the code of `ininteger` and
  `outinteger` (how input is split and how integers are printed).

Not read: anything else under `calibration/` or `reviews/`, the absys
repository's `research/` and `examples/`, and any other program written for
this study.

## Exposure to precursors

The author has not seen any precursor program (the absys experiments
E01–E09), or any other program for this study, in this session or, as far
as the author knows, before it.

## Versions and commands

| system | version | command |
|---|---|---|
| Python core | CPython 3.13.7, macOS arm64 (uv build) | `PYTHONHASHSEED=0 .../cpython-3.13.7-macos-aarch64-none/bin/python3.13 p02.py > p02.out` |
| ALGOL 60 report | `algol60` 0.1.1, repository at commit `6e8740c` | `algol60 p02.alg < p02.in > p02.out` |

The report dialect is the interpreter's default: there is no flag for it,
only `--x1` for the other dialect. `--check p02.alg` was run before the
first run. Both runs exited 0 with nothing on standard error.

## Files

| file | what it is |
|---|---|
| `python/p02.py` | P02a, P02b in all six orders, and P02c, each as its own computation, in one file |
| `python/p02.out` | its output |
| `algol-60/p02.alg` | the same, in one file |
| `algol-60/p02.in` | the stages, read with `ininteger`: the one place the ALGOL program's stage constants are kept |
| `algol-60/p02.out` | its output |

One file per system suffices: each sub-problem and each order is a fresh
computation within the one run.

## The two programs

Both programs are the same design, chosen before either was run, and
there is one variant per configuration (the primary).

- **Unknowns.** u, v, w, with a record of which are known (Python: a
  dict from name to value; ALGOL 60: three integers and three Booleans).
- **Relations.** R1, R2 and R3 are each a function (Python) or an integer
  procedure (ALGOL 60) of their own. Each transcribes its relation in
  every direction the stages need, and returns a verdict: it binds one
  unknown, it holds for every value of the unknowns it still has (decided),
  it fails, or it waits, naming the unknowns it waits for.
- **Holding and taking up again.** A stage's relations are appended to the
  held relations, in arrival order, and every held relation is examined
  again, in arrival order, pass after pass, until a whole pass decides
  nothing new. A decided relation is dropped. This is the problem's central
  difficulty, and it is written by hand for this problem's three relations,
  not as a general constraint store.
- **The report.** After each stage: the unknowns bound and unbound; each
  relation still held, with known values put in, and what it waits for;
  and the outcome. The held relations are the program's own state, the
  same state the next stage acts on.
- **Infinite outcomes.** Reported as bindings plus held relations: *solved
  form* where nothing is held (R3 alone: u = 2, v and w free; R1, R3:
  u = 2, v = 14, w free), *residual* where something is (R1 alone:
  u + v = 16; R2 alone: w · u = v; R2, R3: w · 2 = v, with u = 2). The
  R1-alone and R2-alone residuals are identical to the posed information:
  nothing is done with them until more arrives.
- **The finite case.** Where R1 and R2 alone are held with nothing known,
  the solutions are enumerated and printed as values (explicit), derived
  as u · (w + 1) = c₁ and u a divisor of c₁, positive or negative. If c₁
  were 0 the solutions would be infinite, and the residual is reported
  instead. The relations stay held either way; the enumeration is computed
  for the report and not kept.
- **Observation output.** Each examination of a relation is printed as a
  trace line, and the number of examinations per relation per stage.

### Python core

- No imports. Generators, exceptions and classes are not used; dicts,
  lists, tuples and `%` formatting only.
- The stages are posed by a stand-in for the harness at the end of the
  file, which calls `take` with each stage's relation names, in one process
  per run of the file. The constants are in the marked block
  `THE STAGE CONSTANTS` at the top (`R1_SUM`, `R3_ADDEND`, `R3_SUM`).
- Idioms: a dict as a store of bindings, tagged tuples as verdicts, and a
  dispatch table from names to functions, from the Python Language
  Reference and Tutorial (3.13), sections on dictionaries, tuples and
  functions as objects. The fixpoint loop ("repeat a pass until nothing
  changes") is the ordinary iterative-relaxation idiom; I cite no
  published source for it.

### ALGOL 60 report

- The Revised Report language as the interpreter takes it, written with
  the reference symbols `∧ ¬ × ÷ ≠`. `iabs` (Modified Report) is not used;
  the absolute value is a conditional expression. `÷` is the Report's
  integer division (3.3.4.2), truncating towards zero, so
  `v ÷ u × u = v` tests divisibility for either sign.
- Input and output are the Modified Report's `ininteger`, `outinteger` and
  `outstring`, external mechanisms in *report*. `outinteger` prints a space
  after each number, which is why the output has spaces before `:` and
  after numbers.
- The stages are read from `p02.in` as they arrive, into the running
  computation (`systems/algol-60/README.md`, "The same computation"). Its
  encoding is in the program's opening comment: R1 as `1 c`, R2 as `2`,
  R3 as `3 a b`. The relations held are kept in parallel integer arrays
  (kind, constants) with a Boolean array `alive`, in arrival order, as the
  systems file's encoding of values suggests.
- Idioms: integer procedures returning a result code through their name
  (Revised Report 5.4.4), global variables for the binding a verdict makes,
  a labelled `go to` for the repeated pass, and `for s := d, -d` as a
  for list (4.6). Sources: the Revised Report itself; the interpreter's
  `examples/average.alg` for reading input until a condition holds.

## What is reformulation, and why

Both programs, same constructs:

1. **Keeping unknowns and held relations.** Neither language has unknowns
   or suspended relations, so the program holds them itself (the known
   flags, the list or arrays of held relations, the verdicts, the pass
   loop). Rule 19: written for this problem's relations, so R in the core
   configuration, unless a classifier judges the pass loop general enough
   to be S.
2. **Verdict codes and their extra results** (`which`, `val` in ALGOL 60;
   the tagged tuples in Python). Not in the problem.
3. **The joint solution of R1 and R2** (`r1_and_r2_solutions`,
   `solutions12`): a derivation not in the problem file, and a loop over
   candidate divisors the problem does not state.
4. **Each relation as directions.** The problem states R1–R3 as
   relations with any place unknown; the programs compute each in the
   directions the stages can need. I wrote every direction, so none is
   left out, but whether that is P (rule 3, mode-faithful) or R (rule 8)
   is for the classifiers.

No definition case or conjunct was moved: R1, R2 and R3 are held and
examined in the order they arrive, and P02c poses them in the order R1,
R2, R3.

## Fixes

- **Python:** none. It ran correctly the first time.
- **ALGOL 60:** two fixes, both before the first run, found by
  `algol60 --check`, not by running:
  1. The opening comment contained two semicolons ("number of runs;",
     "number of stages;"). A comment ends at its first semicolon (Report
     2.3), so they would have ended it early. Changed to commas.
  2. The comment before `solutions12` contained "v = c - u; put in". Same
     reason. Changed to "v = c - u.  Put in". `--check` reported this one
     as "line 175, column 42: '.' is not a basic symbol".

No fix was made after any run.

## Whether the outputs give the valid outcomes

Every stage of every run, in both systems, gives the problem's valid
outcomes. The two outputs report the same verdicts in the same order.

| relations so far | reported | valid |
|---|---|---|
| R1 | held: u + v = 16; u, v, w unbound | yes (residual, identical to posed) |
| R2 | held: w · u = v; u, v, w unbound | yes (residual, identical to posed) |
| R3 | u = 2; v, w unbound; nothing held | yes (solved form) |
| R1, R2 | both held; ten triples listed | yes: the ten triples of the problem file, in another order |
| R1, R3 | u = 2, v = 14; w unbound; nothing held | yes (solved form) |
| R2, R3 | u = 2; held: w · 2 = v | yes (residual) |
| R1, R2, R3 | u = 2, v = 14, w = 7 | yes (explicit) |

P02a, all six orders of P02b, and P02c end in u = 2, v = 14, w = 7. The
traces show how many times each relation was examined; for example, in
the order R2, R1, R3, the last stage examines R1 3 times, R2 4 times and
R3 twice.

A check with changed constants, on scratch copies and not saved here
(R1: u + v = 0, and R3: u + 1 = 4), gave a residual at the R1, R2 stage
and "no solutions" where R3 makes u = 3, which does not divide 16.

## Points the specification leaves open, for this problem

- **The R1, R2 stage.** Holding the two relations alone is *complete* but
  *reducible*. Reaching the ten triples needs a derivation the problem does
  not give. I printed both the held relations and the triples. Which one is
  "the report" for classification is not said, and the triples are computed
  for printing, not held.
- **Rule 19's boundary.** The pass loop takes up relations through a table
  of relation functions. Whether that is "written for the problem's own
  relations" (R) or "general over relations" (S, extended) is a judgement
  the rule does not settle for code this small.
- **Solved form and products.** Solved form allows terms built from values,
  unknowns, ⟨⟩ and ++. So v = 2w (R2, R3) has to be a residual, though the
  problem file writes it like a binding.
- **The divisor loop.** As an enumeration the problem does not state, it
  could be C (rule 6, generators of values). As part of a derivation the
  problem does not give, it could be R.
- **Cap.** With other constants, R1 and R2 can have more than 20 solutions.
  The programs print them all; `answers(cap)` would stop at 20.
