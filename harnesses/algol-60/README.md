# The ALGOL 60 harness

*Phase 4, wave 1, against `spec-1.0`. The per-system part of the harness for
ALGOL 60 (`systems/algol-60/README.md`), written to the common contract in
[`../README.md`](../README.md). Where the contract or the specification could
not be implemented as written for ALGOL 60, the reading taken is in
[`QUESTIONS.md`](QUESTIONS.md) (entries A1–A17).*

| file | what it is |
|---|---|
| `run` | the harness: `run CONFIGURATION PROBLEM INSTANCE MODE PROGRAM OUTDIR` |
| `check` | the syntax check, which executes nothing: `check CONFIGURATION PROGRAM` |
| `README.md` | this file: the program contract, per configuration, and how the harness works |
| [`S-mechanisms.md`](S-mechanisms.md) | the S mechanisms of each configuration (none) |
| [`QUESTIONS.md`](QUESTIONS.md) | what could not be implemented as written, and the reading taken |
| [`qualification/`](qualification) | the evidence that the harness does what this file says: `qualify.py`, its output, its made-up programs and stages file, and the records it wrote |

Both scripts are **Python 3.11, standard library only**, as the image
`cp-agent-systems:spec-1.0` provides it (`/usr/bin/python3`). They install
nothing. They run inside the image, from the repository root mounted at
`/work`:

    container run --rm --platform linux/amd64 --volume REPO:/work --workdir /work \
        cp-agent-systems:spec-1.0 harnesses/algol-60/run report P07 P07c behaviour PROGRAM OUTDIR

---

## 1. Configurations

| configuration | system run | modes | budget | stages received |
|---|---|---|---|---|
| **report** | `/usr/local/bin/algol60` (`6e8740c`); storage mode `/usr/local/bin/algol60-measure` (`151cdff`) with `--measure` | behaviour, cost, storage | enforced, `--max-steps` | incremental or reposed, as the program declares (section 2.2) |
| **x1** | the same, with `--x1` | behaviour, cost, storage | enforced, `--max-steps` | as report |
| **x1sim** | `/usr/local/bin/x1sim` (`938fa03`), which compiles with `x1algc` and simulates | **behaviour only** | **not enforced** (`budget_enforced: false`): x1sim has no step count | incremental (one live process) or reposed |

The step unit is the interpreter's tick as `--max-steps` counts it
(`systems/algol-60/README.md`, Units). `run` refuses `cost` and `storage` for
x1sim (exit 2). The configuration never chooses incremental or reposed
posing from a result: the program declares it before it is run.

**Can a configuration continue after budget?** No, in report and x1: when
`--max-steps` fires the interpreter stops the program with an error and the
process ends, so there is no computation to pose stage k+1 into. Stage k+1
is reposed (`reason: "after-budget"`). x1sim has no budget.

---

## 2. The program contract

An author who cannot run the program before its results are taken writes it
to this section, and may use only `check` (section 6) before it is fixed.

### 2.1 File layout

- **One file**, the whole program: one ALGOL 60 program (a block or compound
  statement). Any extension; the harness copies it as `prog.a60` for x1sim.
- **Constants** (common contract, section 11.6): every constant of every stage
  is in **one input file**, beside the program, with the same name and the
  extension `.constants` (`P07c.alg` → `P07c.constants`). The verifier
  substitutes a hidden variant by passing another file in the environment
  variable `ALGOL60_CONSTANTS` (and its id in `ALGOL60_VARIANT`); the program
  is not touched. **Every line of the file is tagged with the stage that
  first uses it**: `k: v1 v2 …`, where k is a stage of the instance (1..K)
  and the values are integers in the problem's encoding
  (`systems/algol-60/README.md`, Values), separated by spaces, in a layout the
  program states in a comment. A stage may have several lines, or none;
  blank lines are ignored; any other line is refused (exit 2). The harness
  sends stage k's lines **only with the message that poses or replays stage
  k** (2.2): no stage's constants are on the program's input before that
  stage is posed (`PROTOCOL.md`, "Writing a program", rule 5, no
  anticipation). A constant a later stage uses again is kept by the program
  from the stage that first gave it. The program must stay correct for other
  constants: give lengths in the file, never in the program. A sub-problem with no constants has no file (`constants.how =
  "none"`). The program holds nothing else of the stages.
- **Representation**:
  - *report*: as `algol60` reads it: reserved words in lower case
    (`begin`, `if`), or quote-stropped, or underlined; strings `"..."` (with
    `\n`) or `` `...' ``. The procedures `ininteger`, `outinteger`,
    `outstring` are IFIP's, and are external mechanisms in report
    (systems file, Configurations).
  - *x1sim*: as the X1 compiler reads it: **underlined reserved words**
    (each letter followed by U+0332, `b̲e̲g̲i̲n̲`), strings only `` `...' ``,
    the operators as symbols (`¬ ∧ ∨ ⊃ ≡ ≠ ≤ ≥ × ÷`; underlined `not` or `and`
    are refused), and the X1 system's procedures `read`, `print`,
    `PRINTTEXT`, `NLCR`, `SPACE`, `TAB` (no `ininteger` or `outstring`).
    Characters in strings: letters, digits, space and `[ ] / = : , . ( ) + -`
    (the X1 code has no `#`, `@`, `<` inside text is risky). The X1 system
    breaks a line at 144 positions: print `NLCR` between answers so that
    no tag is split.
  - *x1*: `algol60 --x1` reads both forms and has both sets of procedures.
    A program in the x1sim form runs unchanged in x1 (the qualification does
    this); a program in the report form runs in x1 too.
- **Declarations, in comments** (comments are not tokens). An ALGOL 60
  comment ends at the first `;`, so none of these may contain `;`:

      comment HARNESS POSING incremental;          (or: reposed — exactly one, required)
      comment PROVENANCE author: ...;
      comment PROVENANCE precursor seen: yes|no;
      comment PROVENANCE idioms: <each idiom and its source>;
      comment CONSTANTS <the layout of the constants file>;

  `run` and `check` read the posing declaration from the program's bytes,
  and refuse a program without exactly one (exit 2).

### 2.2 How the program learns which stage to handle: its input

The harness writes everything on the program's **standard input**, as lines
of integers, read with the configuration's input procedure
(`ininteger(0, v)` in report and x1; `v := read` in x1 and x1sim):

1. **The instance line**, first: `n a m c1 … cm`
   - `n` the instance's size (`stages.json` parameter `n`), else 0;
   - `a` its answer cap where the instance gives one (P12: 20 for `all`,
     1 for `any-one`), else 0;
   - `m` the number of codes that follow, and `c1 … cm` the instance's
     `order` or `spawn_order`, each as its code (table below), else `m = 0`.
2. **Messages**, one per line, each **followed by the constants lines of
   the stage it poses or replays** (the lines of the file tagged `k:`, in
   file order, with the tag removed and the values verbatim; nothing if the
   stage has none). The program reads exactly that stage's constants after
   reading the message's words:

   | message | meaning |
   |---|---|
   | `1 k` | **pose stage k**: stage k's information arrives (in an incremental program, into the computation that holds stages 1..k−1; in a reposed run, the stage posed after the replay) |
   | `2 j` | **replay stage j** (reposed run only): carry out stage j again, as when it was posed, replacements and withdrawals included |
   | `3 j` then a line `v` | **replay commit stage j as the information x = v** (P11, reposed run): `v` is the commit stage's first answer, verbatim as it was printed (the text between `[answer]` and `[/answer]`), then stage j's constants lines. Print P11 answers so that they can be read back (as integers) |
   | `4 k c` | **spawn computation c of stage k** (P09a, P09b): start computation c and run it to its end; stage k's constants follow each spawn message |

   The program answers **every message with exactly one `[end]`** (2.3),
   printed when it has finished with that message, and then reads its next
   message. It never reads input beyond the message it is handling: in an
   incremental run the next message is written only after `[end]`, so a read
   beyond it waits forever (and the stage ends at the safety limit). After the
   last stage the harness closes the input; the program's next read then
   fails with the interpreter's "the input is exhausted" (x1sim: "No input"),
   which ends the process. That is expected, not an error of the stage.

   No message says how many stages follow (no anticipation).

**Incremental program** (`HARNESS POSING incremental`; the systems file's
"read each stage with ininteger or insymbol as it arrives, which counts as
the same computation"): a loop that reads a message, handles it, prints the
stage's answers and observe block, prints `[end]`, and reads the next. It
must also accept `2 j` and `3 j` (handled as `1 j`, and as x = v): the
harness reposes an incremental program after a budget, error or safety stop.
Stage 1 arrives as `1 1`.

**Reposed program** (`HARNESS POSING reposed`; "otherwise each stage is
posed by rerunning with stages 1 to k"): for stage k the harness starts the
program afresh and writes, at once, `2 1` … `2 k−1` (with `3 j` + `v` for a
commit stage) and then `1 k`. The program reads messages until it reads a
`1`, printing `[end]` after each replayed one, then computes stage k, prints
its answers and observe block and a final `[end]`, and may end.

Codes of `order`, `spawn_order` and computations (by first appearance in
`stages.json`; structure, not constants):

| instance or stage | what | codes |
|---|---|---|
| P02b | `order` | R1 = 1, R2 = 2, R3 = 3 |
| P07a | `order` | 1 = 1, 2 = 2, 3 = 3 |
| P09a, P09b | `spawn_order` | A = 1, B = 2 |
| P09a, P09b stage 1 | computation `c` of `4 1 c` | A = 1, B = 2 |
| P16a | `order` | ascending = 1, descending = 2, interleaved = 3 |
| P16b, P16c, P16d, P16d2 | `order` | ascending = 1 |
| P16b stage 1 | computations C1–C4 | **not spawned**: posed as `1 1` to `main` (`spawn_fallback`, QUESTIONS.md A3) |

So `P12c.n16.any` gives the line `16 1 0`, `P09a.BA` gives `0 0 2 2 1`
followed by `4 1 2` and later `4 1 1`, and `P16a.n100.descending` gives
`100 0 1 2`.

### 2.3 How the program reports: tags in its output

Answers reach the harness through the system's standard mechanism, the values
the program prints (systems file; `PROTOCOL.md`). The program prints them,
with `outstring`/`outinteger` (report) or `PRINTTEXT`/`print` (x1sim), between
these tags. The harness keeps the text between tags **verbatim** (the
padding of `outinteger` and of the X1 `print` included):

| tag | meaning |
|---|---|
| `[answer]TEXT[/answer]` | one answer to the query of the computation now running. In order; the first `cap` are collected (`stages.json` gives the cap of each query), any more stay in `stdout` and `print` |
| `[observe]TEXT[/observe]` | the state for `observe()` at the end of the stage (2.4). Print it once, after the answers |
| `[emit]TEXT[/emit]` | the effect stub `emit(TEXT)` (P11, 2.5) |
| `[end]` | the program has finished with the current message. Print a newline *before* it, nothing after it before the next read |

The text of a tag must not contain the tags themselves.

### 2.4 observe() and the execution state

ALGOL 60 has no unknowns, alternatives or suspension of its own, so
`observe()` reads what the program prints in its observe block, and the
execution state is read from it. Inside `[observe]…[/observe]`, any text
(the held relations, a residual, the program's named structures) is kept
verbatim in `observe.raw`; these tags are also read mechanically:

| inside observe | recorded as |
|---|---|
| `[bind NAME]VALUE[/bind]` | `observe.bindings[NAME] = VALUE` |
| `[alternatives NAME COUNT]` | `alternatives.by_type[NAME]`; `at_boundary` is their sum; a sum above 0 is the state **alternatives pending** |
| `[held-as all-live]` (`backtracking`, `mixed`) | `alternatives.held_as` (else `unknown` if alternatives are reported, `none` if not) |
| `[problem-alternatives NAME COUNT]` | `alternatives.problem_defined[NAME]` (METRICS.md: P05's values of x, P12's partial sequences, P15a's interleavings) |
| `[suspended NAME COUNT]` | `suspended.items[NAME]`; `at_boundary` their sum; a sum above 0 is the state **suspended** |
| `[operations NAME COUNT]` | `problem_operations[NAME]`: applications of each case of each relation (`conc/1`), counted by the program **since the computation started** |
| `[candidates COUNT]` | `candidates_examined` (P12) |

COUNT is an integer, printed with `outinteger` or `print` (a leading `+` and
spaces are accepted). A stage that ends with `[end]` (or with the program's
normal end) and reports neither alternatives nor suspended work is
**finished**. **budget**: the interpreter reported `stopped after N steps`.
**error**: the process ended otherwise before `[end]`; `error_verbatim` is
the interpreter's message (its last line of standard error; for x1sim all of
standard error). **timeout**: the safety limit. When a stage ends by budget,
error or timeout, the program cannot print an observe block at that moment;
whatever it printed in the stage before the stop is what is recorded.

`print()` is the stage's output, verbatim, from its message to its `[end]`.

### 2.5 emit and commitments (P11)

`emit(m)` is bound as printing `[emit]m[/emit]`. The harness appends `m`,
verbatim, to the effects log when it reads it, with the run, stage, attempt
and (in a reposed run) the stage being replayed (`during_replay_of`). The
log is `OUTDIR/<instance>.effects.jsonl` in behaviour mode, and
`OUTDIR/<instance>.effects-observation.jsonl` in cost and storage mode; it
is never reset. The interpreter holds its output until it next reads input
(or ends), so an emit is logged by the end of its stage at the latest.

At a commit stage the program selects one outcome and prints it as the
stage's answer. That answer, verbatim, is v: a later reposed run sends
`3 j` and then v on its own line, and the program takes it as x = v without
selecting again.

### 2.6 spawn (P09a, P09b)

ALGOL 60 has no separate computations. A spawned computation is a part of
the one program (a procedure, typically), started by the message `4 k c`.
It runs to its end, budget or error, and prints `[end]`; then the harness
spawns the next, in the instance's `spawn_order` (`side_by_side: false`).
They share the program's variables. Each has its own budget (report, x1). If
one ends the process (budget, error, timeout), the ones after it in the stage
are recorded as not started (QUESTIONS.md A3).

### 2.7 H tokens

These constructs are **H** (`METRICS.md`, class H, rule 13), every token of
each:

1. each statement that reads a harness word: the instance line
   (`ininteger(0, n)`, `n := read`, the loop that reads the codes), a message
   word (code, stage number, computation code), and the statement that reads
   the replayed value v (turning v into the information x = v is classed by
   METRICS.md, not H);
2. the message loop: its `for … while …` header (or label and `go to`), and
   the tests and connectives that select by the message code, by k (which
   stage's code to run) and by c (which computation): the dispatch, not the
   stage code it selects;
3. every output statement whose only effect is to print a tag or the text
   inside a tag (`[answer]`, `[observe]` and its inner tags, `[emit]`,
   `[end]`, and the `NLCR` that separate them), and procedures whose only
   effect is to print answers or state the program already holds (output
   adapters);
4. counters that only count (problem operations, candidates): their
   declarations and increments;
5. declarations of variables that hold only harness words (the message code,
   the stage number k, the computation code c, a loop variable of the message
   loop).

Not H: the variables holding instance parameters as the program uses them
(n, an order, the cap), reading the constants (that is the stage
information, P), holding information between stages, and any pending or
suspension structure (R or S by METRICS.md rule 19).

### 2.8 A complete minimal example

Made-up problem **X01** (not one of P01–P16): one unknown integer x; stage 1
gives x ≥ c1, stage 2 gives x ≤ c2, stage 3 gives x ≠ c3; the query is every
x. Program `qualification/programs/x01-incremental.alg`, configuration
report:

```
begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (the harness README's example, for the made-up problem X01, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the input and output procedures of the interpreter (IFIP 1964, Modified Report 1976);
  comment X01 (made up). One unknown integer x. Stage 1: x >= c1. Stage 2: x <= c2. Stage 3: x differs from c3. Query: every x. Constants file: a line 1: c1, a line 2: c2, a line 3: c3, each read when its stage is posed;
  integer n, cap, m, i, code, k, c1, c2, c3, lo, hi, ex, x, tested, held;
  Boolean haslo, hashi, hasex;

  comment harness words: the instance parameters;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  haslo := hashi := hasex := false; tested := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage to pose, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then begin ininteger(0, c1); lo := c1; haslo := true end
    else if k = 2 then begin ininteger(0, c2); hi := c2; hashi := true end
    else if k = 3 then begin ininteger(0, c3); ex := c3; hasex := true end;

    comment the query: every x, when the relations bound it on both sides;
    if haslo and hashi then
      for x := lo step 1 until hi do
      begin
        tested := tested + 1;
        if not (hasex and x = ex) then
        begin outstring(1, "[answer]x = "); outinteger(1, x); outstring(1, "[/answer]\n") end
      end;

    comment observe: the relations held, and how many wait for more information;
    held := (if haslo then 1 else 0) + (if hashi then 1 else 0) + (if hasex then 1 else 0);
    outstring(1, "[observe]");
    if haslo then begin outstring(1, "x >= "); outinteger(1, lo) end;
    if hashi then begin outstring(1, "x <= "); outinteger(1, hi) end;
    if hasex then begin outstring(1, "x <> "); outinteger(1, ex) end;
    if not (haslo and hashi) then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]") end;
    outstring(1, "[operations x-tested "); outinteger(1, tested); outstring(1, "]");
    outstring(1, "[/observe]\n[end]")
  end
end
```

Its constants file `x01-incremental.constants` is

    1: 3
    2: 9
    3: 5

The harness writes `0 0 0` and `1 1` with `3`; after the first `[end]`,
`1 2` with `9`; after the second, `1 3` with `5`; then it closes the input. It records: stage 1, no
answers, state suspended (`held-relations 1`); stage 2, the seven answers
`x = 3 ` … `x = 9 `, finished; stage 3, six answers. H here: the reads of
`n, cap, m`, the code loop, the message reads, the `for i := 1 while true`
header, the `if k = …` tests and connectives, every `outstring`/`outinteger`
of a tag, the counter `tested` and its statement, and the declarations of
`code, k, i, tested, held`; the rest (the reads of `c1`, `c2`, `c3`
included: they are the stage information) is classed by METRICS.md. The same
problem, posed by rerunning, is `x01-reposed.alg`; in the X1 form, for x1 and
x1sim, `x01-x1.a60` and `x01-x1-reposed.a60`.

---

## 3. How the harness drives the system

### 3.1 report and x1: a process per stage, re-created

`--max-steps` is fixed when the interpreter starts and counts from the start
of the process, and the interpreter reports its count only when the limit
stops it. So, to give every stage and every spawned computation its own
budget of exactly 10⁶ steps (10⁸ for P12, P13, P16), the harness runs each
in its own process: for stage k of an incremental program it starts the
interpreter with `--max-steps R(k−1) + budget`, writes the instance line and
constants and `1 1`, waits for `[end]`, writes `1 2`, … and finally `1 k`.
The program receives every stage as it first arrived, one after another,
into one computation; the earlier stages are re-created, not replayed, and
the record says `posed.how = "incremental"` with nothing replayed (QUESTIONS.md
A2). **Every such attempt is marked**: its `notes` begin with a line

    recreated_for_budget: true; computation: main; prefix_messages: 2; prefix_stages: [1, 2]; prefix_steps: 103; prefix_commit_stages_carried_out_again: []

(the schema has no field for it, so it is a note in this fixed form).
`prefix_steps` is R(k−1), the steps of the re-created prefix: they are **not
charged to the stage** (`steps.stage` and the budget count from the end of
the prefix; `restart_cost` is null; `steps.restated` includes them, as
"from nothing"). A commit stage in the re-created prefix is carried out
again by the program, deterministically, and listed in
`prefix_commit_stages_carried_out_again`; its output (v included) is checked
byte-identical to the first time. This relies on the interpreter being deterministic (it has no clock and
no random numbers): the earlier stages' output in the new process must be
byte-identical to what was recorded for them, or the run has a harness fault.
Their output is not repeated in the attempt's `stdout`, and their emits are
not logged again.

**Steps** are read only through `--max-steps`, by bisection: R(k), the steps
until the program asks for input after stage k (or ends), is the least limit
at which a run of stages 1..k, its input closed after stage k's `[end]`, is
not stopped with `stopped after N steps`. Each probe is a run of the program
(their number is in the record's notes). The stage's incremental cost is
R(k) − R(k−1), its restated cost R(k).

**A reposed stage** (a reposed program; or an incremental one after budget,
error or timeout, and every safety rerun after stage 1): one new process,
all messages written at once. Its restart cost is measured as a separate run
(`restart_cost_method: "separate-run"`): the least limit at which stages
1..k−1 alone (their messages, then the input closed) are not stopped. The
budget is that plus 10⁶ (10⁸). The replay as a whole has at most the sum of
its stages' budgets (QUESTIONS.md A6).

### 3.2 x1sim: one live process

No step count, no limit. An incremental program runs in **one x1sim
process** for the whole run: the harness writes each message after the
previous `[end]`, and the computation is genuinely the same. A reposed stage
starts a new process with all its messages. x1sim writes its object file
beside the program, so it runs in a fresh temporary directory with a copy
`prog.a60`, `HOME` set there and `X1ALGOL_LIB` unset, so the library is
`/usr/local/lib/x1algol.lib`.

### 3.3 Safety limit

60 s per attempt (600 s for P12, P13, P16), as `stages.json` gives. For an
incremental attempt it runs from writing the stage's message to its `[end]`
(the re-created earlier stages are not inside it: they are guarded at 900 s
as a harness fault); for a reposed attempt it covers the whole run (Q13).
The harness stops the system with **SIGKILL to its process group**
(`how_stopped`), keeps what had been printed, and reruns once at the raised
limit (reposed; for stage 1, fresh) where the problem allows, else the stop
is final (`fixed-limit-timeout`). The interpreter flushes its output at every
read of input, at an error and at the step limit, but not when killed:
output printed but not yet flushed when the safety limit kills it is lost.

### 3.4 Modes

| mode | report, x1 | x1sim |
|---|---|---|
| behaviour | `algol60` with the budget's `--max-steps`; steps are measured only where a later budget needs them | `x1sim`, no budget |
| cost | as behaviour, plus R(k) at every stage, `steps_at` for each collected answer (the least limit at which the answer's `[/answer]` is in the output), `to_first_answer`, `between_answers`, `to_end`; repeated work from one extra run of `algol60-measure --measure` per computation | refused |
| storage | `algol60-measure --measure` for the attempt (its steps, under `--max-steps`, are the baseline's: systems file) | refused |

**Store** (storage mode): `--measure` reports at the end of the process,
after the interpreter has unwound. The totals (`frames_made`, `calls`,
`name_uses`, `name_evaluations`, `name_first_evaluations`,
`name_repeat_evaluations`) are read as the stage boundary's, since the
process ends there; the live quantities (`frames`, `slots`, `arrays`,
`array_elements`, `names`, `call_depth`) have `boundary: null`, and their
peak over the process (stages 1..k) is recorded as the stage's (`exact`)
only where it exceeds the peak at the end of stage k−1, else `null`; a
reposed stage's peak is its run's. **Repeated work** is
`name_repeat_evaluations` (with first and all evaluations) between the
boundaries, or over the whole reposed run. **P13**: `cpu_time_s` and
`max_rss_kb` are the attempt process's, from `wait4`, in behaviour and cost
mode (not storage, which is instrumented).

### 3.5 Confounds

Everything the harness does beyond passing stages in, collecting answers and
reading state (copied into every record's `run.confounds`):

1. the re-creation of the computation in report and x1 (3.1): an attempt
   in a fresh process, re-created for its budget, recorded as incremental
   and marked `recreated_for_budget: true` with its `prefix_steps`, which
   are not charged to the stage; its determinism check; a commit stage in
   the re-created prefix is carried out again by the program,
   deterministically, its output (v included) checked identical, and listed
   in the mark;
2. the bisection probes, extra runs of the program, for every step count;
3. closing the input after the stage under test, which ends the process with
   the interpreter's "input is exhausted" error after `[end]`;
4. the safety limit of an incremental attempt excludes the re-created stages;
5. output still in the interpreter's buffer at a safety-limit kill is lost;
6. store and repeated work read from the end-of-process report of the
   measurement build, with the peak attribution of 3.4;
7. the instance line and messages written on standard input, each message
   followed by its stage's constants lines with their `k:` tag removed;
8. answers, observe state, emits and stage ends read from printed tags by
   pattern matching; answers beyond the cap left uncollected;
9. spawned computations are parts of one program, run one after another;
10. x1sim: run in a temporary directory on a copy of the program, and no
    budget.

---

## 4. Records

`run` writes `OUTDIR/<instance>.<mode>.<UTC>.json`, then validates it with
`harnesses/validate.py`; an invalid record is kept as `….INVALID.json` and
`run` exits 3. Exit 0 whatever the outcome of the stages; 2 for a usage error
(unknown configuration, instance or mode, a mode x1sim does not have, no
posing declaration), with no record. `PROGRAM` and `OUTDIR` are relative to
the repository root. `system_build.commit` is read from `/opt/src/COMMITS`;
the image digest from `HARNESS_IMAGE` if the launcher passes it, else null.
`HARNESS_PURPOSE` sets `run.purpose` (`primary` by default); `HARNESS_STAGES`
another stages file (only the qualification uses it).

---

## 5. check

`harnesses/algol-60/check CONFIGURATION PROGRAM`:

| configuration | what it runs |
|---|---|
| report | `algol60 --check PROGRAM`: parses and compiles, reports errors and warnings, runs nothing |
| x1 | `algol60 --x1 --check PROGRAM`, the same in the X1 dialect |
| x1sim | `x1algc prog.a60 /usr/local/lib/x1algol.lib` on a copy, in a temporary directory: the X1 compiler alone; the object code is discarded and the simulator is never started. On failure the compiler's report (which it writes on standard output) is printed |

It also reports whether the posing declaration is present and whether a
constants file is beside the program. Messages are printed verbatim; exit 0
if none is an error, 1 otherwise. It poses no stage and prints nothing the
program would compute. The X1 compiler finds fewer errors than `algol60
--check` (it accepted `k := 1 +;`, which then stopped at run time); an x1sim
author may also check the program in x1. The qualification (E1–E2) shows a
program whose only effect is to print a marker leaves no marker and no file
when checked, in all three configurations.

---

## 6. Qualification

`qualification/qualify.py`, run in the image from the repository root,
reruns all of it on made-up programs and problems (X01–X09,
`qualification/stages-made-up.json`) and writes its records to
`qualification/records/<UTC>/`. Its output is `qualification/output.txt`.
It shows: (A) the system run directly and the harness agree on each stage's
output and answers, the harness's step counts agree with `--max-steps`
itself (R passes, R−1 stops), the systems file's step examples (3, 3, 5, 1)
are reproduced as stage-step differences, and the storage figures equal
`--measure` run directly; (B) incremental and reposed programs give the same
answers in all three configurations, a commitment is replayed verbatim, the
modes agree, spawn follows the instance's order; (C) budget, error, safety
rerun, final and fixed-limit timeouts and usage errors; (D) every record
passes `validate.py`; (E) `check` executes nothing; (F) from a trace of
every write the harness made to the system's input (`HARNESS_INPUT_TRACE`,
qualification only), no stage's constants were on the input before its
message, in every process (attempts and probes), and every re-created stage
is marked with its `prefix_steps`.
