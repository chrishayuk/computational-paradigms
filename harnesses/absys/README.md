# The Absys harness

*Phase 4, wave 1, against `spec-1.0`. Written by the Absys harness author
(an agent, `harness-absys`), from `harnesses/README.md` (the common
contract), `systems/absys/README.md` and the pinned sources in the image
(`/opt/src/absys`, `/opt/src/absys-measure`). It changes no frozen file.
Where the contract could not be implemented as written, the reading taken
is in [`QUESTIONS.md`](QUESTIONS.md).*

| file | what it is |
|---|---|
| `run` | the harness: `run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR` |
| `check` | `check CONFIGURATION PROGRAM`: syntax and static errors, executing nothing |
| `absys_harness.py` | the code of both |
| `README.md` | this file: how the harness works, and **the contract a program for Absys must meet** |
| [`S-mechanisms.md`](S-mechanisms.md) | the S mechanisms of each configuration (none) |
| [`QUESTIONS.md`](QUESTIONS.md) | what could not be implemented as written, and the reading implemented |
| [`qualification/`](qualification) | made-up programs, the script that reruns every test, its output and its records |

## 1. Running it

Inside the pinned image, from the repository root mounted at `/work`:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \
        cp-agent-systems:spec-1.0 \
        harnesses/absys/run absys P01 P01a behaviour PROGRAM results/absys/absys/P01/raw

and for P12, P13 and P16 add `--memory 16g` (or more) after `container run`
(see **Memory** below).

The harness is Python 3.11, standard library only (`/usr/bin/python3` of
the image). It runs the pinned builds in `/usr/local/bin` and installs
nothing. Exit status, as the common contract says: 0 when a valid record
was written, whatever the outcome; 2 for a usage error, with no record; 3
when the record does not validate, kept as `<run_id>.INVALID.json`.

Environment variables it reads, none of which changes what the system
computes:

| variable | what |
|---|---|
| `CP_IMAGE_DIGEST` | the image digest, for `system_build.image`; the launcher may pass it (the harness cannot read it from inside). Otherwise `null` |
| `ABSYS_HARNESS_PURPOSE` | `primary` (default), `variant` (the verifier's) or `qualification` |
| `ABSYS_HARNESS_VARIANT` | the hidden variant's id, with `variant` |
| `ABSYS_HARNESS_STAGES` | another stages file; used only by the qualification, for its made-up problems |
| `ABSYS_HARNESS_POSING=reposed` | qualification only: every stage after the first is posed by reposing, so that the two ways can be compared |

**Memory.** The machine keeps every event of a run in memory, whether or
not the trace is shown (`Ctx.events`): about 85 bytes a step, measured in
the image. Under the container's default of 1 GiB, a computation is killed
by the kernel near 10⁷ steps, well before a budget of 10⁸ (P12, P13, P16).
The harness records that as *error*, with the signal (qualification,
X21a). **Run P12, P13 and P16 with `container run --memory 16g`** or more
(10⁸ steps is about 8.5 GB in one assertion).

## 2. Configurations

| configuration | flags the harness passes | alternatives held as |
|---|---|---|
| `absys` | none | `all-live` |
| `absys-depth-first` | `--search depth-first` | `mixed`: every derivation is held at once, but only the first running one is elaborated until it hibernates or fails (systems file, Units) |
| `absys-wake-back` | `--wake back` | `all-live` |

Every run also passes `--notation N` (from the program's file name, below)
and `--steps B`, the problem's budget. All three modes are allowed for
every configuration. Every configuration is incremental
(`run.posing: "incremental"`).

**The binary.** Every mode runs `absys-measure` (branch `measure`,
`5450449`, which is the pinned `efd5203` with `--measure` and `--full`
added). Behaviour runs pass `--full` and not `--measure`: `--full` only
prints lists and derivations without cutting them short, so that
`observe()` and `answers()` read every answer (systems file, Output). The
qualification shows its output identical to the baseline `absys`'s on
every test (QUESTIONS, A2). `system_build.commit` is `5450449…`, read from
`/opt/src/COMMITS`, and `instrumented: true`. Absys has no version option,
so `version_output` is `null`.

## 3. The program contract

A program author cannot run the program before its results are taken, so
everything below is exact. Only `check` may be used before the program is
fixed.

### 3.1 The file

One file, UTF-8. **Its extension fixes the notation**, as the system's own
rule does (`src/session.rs`, `notation_for`): `.ab1` is the 1969 notation
(Absys 1, with arithmetic), `.ab2` the 1982 notation, anything else (use
`.abs`) the 1990 notation. Lines beginning with `%` are comments in all
three; the harness's markers are comments, so they are not tokens.

The file is divided by marker lines (each on its own line; leading spaces
allowed; exact patterns):

| marker | pattern | meaning |
|---|---|---|
| `% STAGE k` | `^\s*%\s*STAGE\s+(\d+)\s*$` | the text of stage *k* starts here |
| `% PART name` | `^\s*%\s*PART\s+(\S+)\s*$` | the text of the part *name* starts here (3.5); a program has STAGE sections or PART sections, not both |
| `% SPAWN c` | `^\s*%\s*SPAWN\s+(\S+)\s*$` | inside a stage's section: the text of the spawned computation *c* starts here (3.6) |
| `% PARAMETERS n order …` | `^\s*%\s*PARAMETERS\b(.*)$` | in the prelude: the instance parameters the program wants (3.4) |
| `% CONSTANTS BEGIN` / `% CONSTANTS END` | a comment line containing the words | the constants block (3.9), in the prelude: a table the harness reads, never given to the system |

Everything before the first STAGE or PART marker is the **prelude**: the
definitions of the problem's relations and the constants block. A section
runs to the next STAGE or PART marker (a SPAWN subsection to the next
SPAWN, STAGE or PART marker). Marker lines are given to the system with
the section they begin; they are comments.

### 3.2 How a stage is given to the system

**Behaviour runs** start one `absys-measure repl` process and keep it for
the whole run: every stage is received into the same session, as the
systems file says ("The same computation"). The harness writes to its
standard input, in this order:

1. at stage 1: one assertion per declared parameter (3.4), then the
   prelude's lines (without the constants block), then stage 1's section;
2. at stage *k*: stage *k*'s section, as the file has it but with each
   constant's name replaced by its value (3.9), line by line, **only when
   stage *k* is posed**. No line of a later section is
   ever written before its stage (no anticipation), and the program is
   never told how many stages follow.

After each section, and after each piece of 1 (the parameters, the
prelude), the harness writes a line `.help`. The repl's reply to it is a
fixed text, which tells the harness that the system has finished with
everything before it (QUESTIONS, A3). The repl takes each line in turn and
does everything that can be done before it reads the next (each
assertion is elaborated until every derivation hibernates or fails, or the
budget runs out).

**The repl reads a text line by line**, and that is the one constraint it
puts on layout (`src/main.rs`, `repl`). After each line it parses what it
has read since the last complete assertion:

- if that parses, it is accepted at once, as one or more assertions;
- if it fails to parse only because it ends too soon, the repl reads on;
- otherwise it reports `error at L:C: message` and drops it.

So, **a program must keep these rules**, which `check` enforces:

1. **An assertion that spans several lines must not be complete at the
   end of any of its lines but the last.** End a line with `or`, `,`,
   an open `{` or `[`, or `=`, never at a point where the assertion could
   end. `colour = lambda C {C = 'red'} or` followed by `{C = 'green'}` is
   right; `colour = lambda C {C = 'red'}` followed by a line
   `or {C = 'green'}` is two assertions to the repl, the second a syntax
   error.
2. **Every section ends with a complete assertion.** Otherwise the repl
   reads the harness's `.help` as the assertion's continuation and
   reports a syntax error (``error at L:1: `.` is not in the notation``),
   which the harness records as the stage's error.
3. **No line, outside an unfinished assertion, may begin with `?` or
   `.`.** The repl takes such a line as a command (`.quit` ends it).

**Cost and storage runs** cannot use the repl, which reports no step
count and no store: the system reports them only for a whole text,
`absys-measure FILE --measure`. So each stage *k* is one new process on a
text the harness writes: the parameters' assertions, the prelude and the
sections of stages 1 to *k*, in order, exactly as above. Its session takes
the assertions one at a time, as the repl's does, and the qualification
shows that its states and step counts at every stage are those of the
incremental behaviour run. These records show every stage after the first
as `reposed` (`reason: "configuration"`), with the steps of stages 1 to
*k*−1 as restart cost, which the behaviour run does not pay (QUESTIONS,
A4).

### 3.3 What the program writes in a stage's section

The stage's information, as Absys assertions: equations, applications,
`or`, `not`, `set`, `tout`, procedure definitions (a stage may define a
procedure, P08 for instance). A replacing or retracting stage (P10, P15d)
is whatever assertions the program uses to carry it out; the harness
gives the section as written, every one of them, on every replay.

**Identifiers.** As the reconstruction decides (`docs/decisions.md`, rule
6): outside any lambda every identifier is shared by the whole text, so a
name given a value in the prelude, the constants block or an earlier
stage is the same variable in every later stage. In the 1990 notation,
inside a lambda an identifier with a capital that the lambda does not
bind is local, and one with a small letter is shared; in the 1969
notation a primed name is local; in the 1982 notation, a name the body
uses but never applies, and the lambda does not bind, is local. So a
constant used inside a lambda must be written with a small letter (1990)
or not be primed (1969).

**Name each unknown as `stages.json` names it** (`x`, `total`, …), where
the notation allows it: `observe()` asks the system for each unknown by
that name (3.8). Every identifier of the text that is not a procedure is
printed in every derivation, so the parameters' names appear in the
answers too. The constants' names do not: the system never sees them
(3.9).

### 3.4 Instance parameters

A program that needs an instance's parameters (n, an order, a spawn
order, the answer mode) names them on one line of the prelude:

    % PARAMETERS n order

For each name, in that order, the harness gives the system, at stage 1,
before the prelude, one assertion `NAME = VALUE`, in the program's
notation:

| value | 1990 (`.abs`) | 1969 (`.ab1`) | 1982 (`.ab2`) |
|---|---|---|---|
| `"n": 1000` | `n = 1000` | `n = 1000` | `n = 1000` |
| `"order": ["R2", "R1", "R3"]` | `order = ['R2', 'R1', 'R3']` | `order = ['R2';'R1';'R3']` | `order = ['R2','R1','R3']` |
| `"answers": "all"` | `answers = 'all'` | `answers = 'all'` | `answers = 'all'` |
| `"spawn_order": ["A", "B"]` | `spawn_order = ['A', 'B']` | `spawn_order = ['A';'B']` | `spawn_order = ['A','B']` |

The names are `n`, `order`, `answers`, `cap` and `spawn_order`, and only
those the instance has (`stages.json`). A program that declares none gets
none. The record lists what was passed (`posed.instance_parameters_passed`).
The harness never passes a constant of a problem.

The answer mode needs nothing from the program: the harness's cap does it
(3.7). The spawn order needs nothing either (3.6).

### 3.5 Arrival orders of written relations: PART sections (P02b, P07a)

Where an instance's `order` names the stage's relations (`P02b.R2R1R3`:
R2, then R1, then R3; `P07a.312`: the third relation written, then the
first, then the second), a program may give each relation as a part,
named as the order names it:

    % PART R1
    ...
    % PART R2
    ...

At stage *k* the harness gives part `order[k-1]`. A program for the
instance in the written order (`P07a`, order `["1","2","3"]`) is the same
program. Orders that do not name stages (P16's `ascending`, …) are passed
only as the parameter `order` (3.4), and the program must use it itself.

### 3.6 Spawned computations (P09a, P09b, P16b)

A stage that spawns computations has, in its section, one SPAWN
subsection per computation, named as `stages.json` names them:

    % STAGE 1
    % SPAWN A
    ...
    % SPAWN B
    ...

Text in the section before the first SPAWN is given first. Then, for each
computation in the instance's `spawn_order` (or the order of the stage's
`spawns`), the harness gives its subsection, waits until the system has
done everything it can (every derivation hibernates or fails, or the
budget runs out), reads that computation's answers and state, and then
gives the next (`side_by_side: false`).

**Absys has no separate computations**: one session holds one
computation, whose derivations every assertion is added to. A spawned
computation's text is accepted into that one computation, conjoined with
everything already there, and so it shares every unknown with the others
(QUESTIONS, A5). P16b's contributors are therefore spawned, not posed by
the fallback. Whether P09a ("not conjoined") is expressible in Absys is
for the program author and the classifiers; the harness does nothing to
separate them.

### 3.7 Answers: the system's standard mechanism

Absys reports a computation as its **derivations**, every one at once,
each with its bindings, the processes it suspends and its outputs, by
printing its state. That is the standard mechanism, and the program needs
nothing to use it. `answers(cap)` is the first `cap` derivations of the
state the system prints at the end of the stage (the repl's `?`), each
derivation's block verbatim, from its line `  derivation #N (…)` to the
next. Under `--full` every derivation is printed.

| ended_by | when |
|---|---|
| `exhausted` | the system printed at most `cap` derivations (none, when no derivation survives) |
| `cap` | it printed more than `cap`; the rest are in `observe.raw` |
| `budget` | its state reports derivations still elaborating when the budget ran out |
| `error` | the system reported an error for the stage's text |
| `timeout` | the safety limit stopped the attempt |

Absys elaborates every derivation before it reports any, so there is no
request for "more answers": a stage never ends *alternatives pending*
(QUESTIONS, A8). In cost mode each answer's `steps_at` is the stage's
steps, when the mechanism gave every answer at once.

### 3.8 What `observe()` and `print()` read

At the end of each stage (and for each spawned computation, after its
section) the harness writes the repl's own commands:

- `?`: the state, every derivation with its status (`hibernating` or
  `still elaborating`), its outputs, its procedures, every identifier's
  value (with `(suspended: …)` where only suspended equations constrain
  it), its suspended processes, and what is still to do. This is
  `print`, and the start of `observe.raw`;
- `? NAME`, for each unknown of the sub-problem in `stages.json` written
  as a plain identifier: the system's value of NAME in each derivation
  (`#3: x = 2`), or `NAME does not occur`. These are `observe.bindings`,
  by unknown, verbatim, and follow in `observe.raw`.

Both read and change nothing. In cost and storage runs, `print` and
`observe.raw` are the state `absys FILE` prints at the end of the text of
stages 1 to *k* (with `--each` in a stage that spawns, the state after
each assertion, from which each computation's is read).

### 3.9 The constants block

Every constant of every stage is in **one block in the prelude**, between
a comment line containing `CONSTANTS BEGIN` and one containing
`CONSTANTS END`. The block is a **table, never given to the system**: one
constant per line, `NAME = VALUE`, the value on that line (comment lines
and blank lines are allowed; a `%` ends the value):

    % CONSTANTS BEGIN
    c1 = 41
    c2 = 'red'
    facts = [[1, 'a'], [2, 'b']]
    % CONSTANTS END

The program's text refers to the constants by name (`pr = [c1, d]`).
**When the harness gives a section to the system, it replaces each name
of the table, in that section's text, by its value**, so that what the
system receives is `pr = [41, d]`. A constant therefore reaches the system
only with the section that uses it: a constant of stage 3 is not in the
system, as information or as a name, before stage 3 is posed (no
anticipation, `PROTOCOL.md`, "Writing a program", rule 5). A name used in
the prelude (in a definition) is given with the prelude, at stage 1.

What is replaced, exactly: an identifier (the system's: a letter or `_`,
then letters, digits and `_`, and, after a small letter, `-` between
letters, as in `math-course`) equal to a name of the table. Nothing is
replaced inside a quoted constant (`'…'`, `"…"`), inside a comment, or in
a name written with a prime (1969: a new local name). The value is put in
as written in the table, with no change. So:

- name constants with identifiers that the program uses for nothing else;
- a constant used inside a lambda is replaced like any other (the value,
  not the name, reaches the system, so the scoping rules of 3.3 do not
  arise).

The verifier replaces only the lines between the markers. The harness
records `constants.how: "block"` when the markers are present, else
`"none"`. `check` parses each section after the replacement, as the
system will receive it, and reports a line of the block that is not
`NAME = VALUE`. Absys reads no input, so there is no `input` form.

### 3.10 Effects (P11): emit

The harness's `emit(m)` is written, in Absys,

    tout("emit", M)

with the term to emit as its second argument. `tout` is the system's own
output assertion (Elcock 1990, note 11): it waits until its term has no
uninstantiated variable, and then performs one output, `emit = VALUE`, in
the derivation it is in. In P11 runs the harness switches the system's
trace on (`.trace`, or `--trace`), and every `output` event of the trace
whose text begins `emit = ` becomes one entry of the log, `entry` being
the rest of it, the system's rendering of the term (`'red'`, `[1,2]`), in
the order the trace shows them. An output performed in a derivation that
later fails stays in the log: nothing the system does removes an entry.
Entries made while a reposed run replays an earlier stage carry
`during_replay_of`. Behaviour runs write to
`OUTDIR/<instance>.effects.jsonl`; the separate run that measures a
restart cost, and every cost and storage run, write to
`OUTDIR/<instance>.effects-observation.jsonl`. Neither is ever reset.

**Commit stages** (P11c stage 3, P11d stage 2): Absys keeps every
derivation live and selects none. The section may be empty (comments
only). `answers(1)` reports the first derivation printed, as for any
any-one query; no commitment is recorded, and none is replayed when a
later stage is reposed (QUESTIONS, A6).

### 3.11 Provenance

At the top of the file, in comments, the lines `% AUTHOR: …`,
`% PRECURSOR-SEEN: yes|no` (whether its author had seen the E01–E09
programs) and `% IDIOM: …` (the source of each idiom). `check` warns if
there is no `AUTHOR` line.

### 3.12 H tokens

`METRICS.md`, class H: the harness's own calls as they appear in a
program. In an Absys program they are:

| construct | H tokens |
|---|---|
| the emit stub's binding, `tout("emit", T)` | `tout`, `(`, `"emit"`, `,` and `)`; the term `T` is classed on its own (rule 10) |

Nothing else in a program is H. The markers are comments; the parameter
assertions are written by the harness, not the program; answers are
collected from what the system prints by itself, with no call in the
program, so there is no output adapter. A program's uses of a parameter's
name (`n`), its constants block and its definitions are classed by the
rules of `METRICS.md`.

### 3.13 A complete minimal example

A made-up problem, not one of P01–P16 (`qualification/stages-qualification.json`, X10):

> **X10a.** `pair(A, B, P)` holds when P is the list `[A, B]`.
> Stage 1: `pair(a, b, pr)`. Stage 2: `pr = [⟨k⟩, d]`. Stage 3: `d = ⟨atom⟩`.
> Unknowns a, b, pr, d. Constants: ⟨k⟩ = 41, ⟨atom⟩ = `'red'`.

The program, `qualification/programs/x10-pair.abs`:

```
% AUTHOR: harness-absys (an agent), for the harness's qualification. MADE UP: not a problem program.
% PRECURSOR-SEEN: no. IDIOM: a lambda procedure, as in Elcock 1990 p. 8.
% CONSTANTS BEGIN
c1 = 41
c2 = 'red'
% CONSTANTS END
pair = lambda A, B, P {P = [A, B]}
% STAGE 1
pair(a, b, pr)
% STAGE 2
pr = [c1, d]
% STAGE 3
d = c2
```

What the system receives, in one session, and what the harness collects
(from the qualification's behaviour record):

| stage | written to the repl | `answers(20)`: the one derivation | state |
|---|---|---|---|
| 1 | the prelude without the block (lines 1, 2 and 7), `.help`, `% STAGE 1` and `pair(a, b, pr)`, `.help`, then `?` and `? a`, `? b`, `? pr`, `? d` | `a  uninstantiated`, `b  uninstantiated`, `pr = [a,b]` | finished |
| 2 | `% STAGE 2`, `pr = [41, d]`, `.help`, `?`, … | `a = 41`, `b = d   (suspended: b = d)`, `pr = [41,b]`, `suspended   b = d` | suspended |
| 3 | `% STAGE 3`, `d = 'red'`, `.help`, `?`, … | `a = 41`, `b = 'red'`, `pr = [41,'red']`, `d = 'red'` | finished |

41 is not in the system before stage 2, nor `'red'` before stage 3.

Its H tokens: none. Snippets for the other forms are in
`qualification/programs/`: SPAWN (`x17-spawn.abs`), PART with a parameter
(`x19-parts.abs`), emit (`x18-emit.abs`), the 1969 notation
(`x20-arith.ab1`).

## 4. Modes

| mode | process | what is of record |
|---|---|---|
| behaviour | one `absys-measure repl --full` for the run (a new one only to repose) | answers, `observe`, `print`, execution state, the effects log. No step count: the repl reports none |
| cost | per stage, `absys-measure FILE --measure --full` on stages 1..k; `--trace` too where the budget is 10⁶ | `steps.stage` (the steps of stage k's assertions: the incremental cost), `steps.restated` (all of the run), `restart_cost` (stages 1..k−1, in-run), `to_end`, `repeated_work` |
| storage | the same command, with `--trace` only in P11 | the store vector, `alternatives.peak` (derivations, exact), the state's suspended processes |

- **Steps** are the system's (one step of the machine, as `--steps`
  counts them), read only from `--measure`'s table, the systems file's
  qualified measurement. Sampling the store adds time, not steps
  (systems file). Cost and storage records both keep what `--measure`
  gave; the figure of record is the mode's. Behaviour records have
  `steps.stage: null`.
- **Store** (`store.quantities`): the ten quantities of `--measure`, each
  with `boundary` (after the stage's last assertion) and `peak` (the
  largest value after any step of the stage's assertions, or when each
  was added), `kind: "exact"` (exact at the granularity of steps). A stage
  with no assertion has the boundary of the last assertion before it and
  no peak.
- **Suspended work** (`suspended`) is what the system prints as suspended,
  in every mode, counted by kind under `--measure`'s names
  (`susp_equations` for an equation between unknowns, `susp_applications`
  for "waits for a definition" or "for its key", `susp_relations` for
  "waits for two of its numbers" or "for its term", `susp_negations` for
  "waits for its variables" or "cannot be decided yet"), summed over
  derivations. The printer shows only processes still waiting on an
  uninstantiated variable; `--measure`'s `susp_*` in the store also count
  equations and arithmetic relations that stay associated with their
  variables after every one is bound (`docs/decisions.md`, rule 10), so
  the two may differ.
- **Repeated work** (cost mode, budget 10⁶): `reactivating_events`, the
  number of trace events of the stage's assertions that reactivated
  suspended processes (`… reactivated …`: a variable was bound and the
  processes waiting on it went back to the goal). Not measured (`null`)
  where the budget is 10⁸, whose traces would be too large to keep.
- **P13**: `cpu_time_s` and `max_rss_kb` of the behaviour run's process
  (`getrusage` through `os.wait4`), for growth only.

## 5. Budget, safety limit, reposing

- **Budget.** `--steps B`, B the problem's budget, is the system's own
  budget, and it counts **per assertion**: each assertion is elaborated
  for at most B steps. A stage of several assertions can therefore spend
  more than B in all before the system reports budget (QUESTIONS, A1);
  cost records say so in a note when it happens. A stage is *budget* when
  the system's state reports derivations "still elaborating when the
  budget ran out".
- **Continuing after budget: yes, in every configuration.** The derivations
  still elaborating stay in the session, and the next assertion accepted
  goes on elaborating them, with a new budget. So after *budget* the next
  stage is posed into the same session, `continued_after_budget: true`.
- **Safety limit.** For an incremental stage, from writing its first line
  to reading the last reply; for a reposed one, the whole run, replay
  included. When it is reached the harness sends **SIGKILL** to the
  system's process (`safety_limit.how_stopped`), records what it had read,
  and, where the problem allows, reruns the stage once with the raised
  limit, by reposing (the session is gone). P12, P13 and P16: no rerun.
- **Reposing** (after *error*, after a final *timeout*, a safety rerun):
  a new session, into which the harness writes the parameters, the
  prelude and every section of stages 1 to *k*−1 in order, each followed
  by `.help`, replacements and withdrawals included, then stage *k* as
  usual. The repl gives no step count, so the restart cost is measured on
  a **separate run** of that same text with `absys-measure json`, which
  reports each assertion's steps (the same count as `--measure`'s, as the
  qualification shows) without sampling the store
  (`restart_cost_method: "separate-run"`). It stops at a syntax error,
  where the repl goes on, so after an error it may undercount, and the
  record says so in `harness_faults`.
- **Error.** The repl reports a syntax or static error and goes on; the
  harness records the stage as *error* with the message verbatim, and
  poses the next stage by reposing, as `PROTOCOL.md` says. A system
  process that ends on its own (a crash, or killed by the kernel) is
  *error* too, with its exit status or signal.
- **When a reposed stage's replay itself cannot finish** (the replay is
  killed for lack of memory), no restart cost can be measured, and the
  record does not validate: it is kept as `.INVALID.json`, exit 3
  (QUESTIONS, A12).

## 6. `check`

    harnesses/absys/check CONFIGURATION PROGRAM

Absys has no parse-only mode. `absys lsp` cannot serve: its diagnostics
*run* the text (`src/lsp.rs`, `analyse`, with a budget of 20 000 steps).
So `check` does this, the same for every configuration (the flags change
nothing a parser sees):

1. It reads the program's bytes and finds its sections, as `run` does
   (3.1); it reports misplaced markers, numbering, and a missing `AUTHOR`
   line (a warning).
2. For each section, as the harness would give it, it does what the repl
   does line by line (3.2): after each line, it gives the text read since
   the last complete assertion to `absys-measure json FILE --steps 0`.
   That command parses the text and compiles each assertion and adds it
   to the goal, with **a budget of zero steps**: no step of the machine
   is taken, so no equation, application, `or`, `not`, `set` or `tout` is
   elaborated. `check` reads only the error (with its line and column)
   and the number of assertions, and stops if the system reports any step
   or event at all.
3. It prints each error verbatim, with its line in the program, each line
   that the repl would take as a command, and each section that ends in
   an unfinished assertion. Exit 0 when there is none, 1 otherwise.

It never prints anything the program would compute. The qualification
shows it on a program whose only effect, run, is to output a marker: the
marker is not in `check`'s output, while running the program prints it.
Absys has no means of writing a file, so no file test is possible.

## 7. Confounds

Everything the harness does beyond passing stages in, collecting answers
through the system's mechanism and reading state (copied into every
record's `run.confounds`):

1. Behaviour runs use the measurement build with `--full` (printer only),
   not the baseline build (2).
2. The `.help` line after each section, to know where the system's output
   for it ends; a section ending inside an unfinished assertion turns it
   into a syntax error (3.2).
3. `?` and `? NAME` to read the state (3.8).
4. The parameters' assertions, written by the harness (3.4).
5. PART sections chosen by the instance's order (3.5).
6. Spawned computations accepted one after another into the one session,
   each read right after its section (3.6).
7. The budget is per assertion (5).
8. Cost and storage runs are a new process per stage, on stages 1..k (3.2).
9. The restart cost of a reposed behaviour stage is measured on a separate
   `json` run (5).
10. The trace is switched on in P11 runs and in cost runs with the 10⁶
    budget (3.10, 4).
11. `answers(cap)` takes the first `cap` derivations of the printed state (3.7).
12. Each constant's name is replaced by its value in the section that uses
    it, when that section is given; the block itself is never given (3.9).

## 8. Qualification

`qualification/run-qualification` reruns everything; its output is
`qualification/output.txt`, and its records are in
`qualification/records/`. See [`qualification/README.md`](qualification/README.md).
