# Questions for the ALGOL 60 harness, and the readings implemented

*Harness author, ALGOL 60, wave 1, against `spec-1.0`. No frozen file and no
file outside `harnesses/algol-60/` was changed. Each entry says what could not
be implemented as written for ALGOL 60, or was open, and the reading this
harness implements. The common part's readings (`harnesses/QUESTIONS.md`,
Q1–Q19) are implemented as written, except where an entry here says so.*

## A1. The systems file's probes are not files

The brief asks to qualify on "the systems file's probes", and
`systems/algol-60/` holds only `README.md`. Its Units section gives four step
examples ("`i := 1; i := 2` in a block is 3 steps", a procedure statement
whose body is one assignment is 3, `for i := 1 step 1 until 3 do ;` is 5,
`for i := 1, 2, 3 do ;` is 1) and says they "were checked against
`--max-steps` on ten small programs", which are not in the repository.

**Implemented:** the four examples are written as made-up probe programs
(`qualification/programs/x08-*.alg`), and the qualification checks that the
harness's stage-step counts differ from a base probe by exactly 3, 3, 5 and
1. The ten programs themselves were not available.

## A2. A per-stage budget, when the step limit is fixed at process start

`PROTOCOL.md` gives each stage (and each spawned computation) its own budget
of 10⁶ steps, and the systems file says an ALGOL 60 program that reads each
stage as it arrives "counts as the same computation". The interpreter's only
step mechanism, `--max-steps N`, is set when the process starts, counts from
the start, and reports the count only when it stops the program. One
process cannot give stage 1 a budget of 10⁶ and stage 2 a budget of
R(1) + 10⁶.

**Implemented** (report, x1): each stage, and each spawned computation, is
run in a **fresh interpreter process** that receives the earlier stages'
messages exactly as they first arrived (each after the previous `[end]`),
with `--max-steps R(k−1) + budget`, R(k−1) measured by bisection. The record
says `posed.how = "incremental"`, `replayed = []`, no restart cost, budget
10⁶: from the program's side the computation receiving stage k holds stages
1..k−1, received one by one, and its budget for stage k is exactly 10⁶. The
harness relies on the interpreter being deterministic, checks that the
re-created stages' output is byte-identical to their recorded output (else a
harness fault), does not repeat their output in `stdout`, and does not append
their emits to the effects log again. Every such attempt is **marked
explicitly**: its notes begin with `recreated_for_budget: true; …;
prefix_steps: R(k−1); prefix_commit_stages_carried_out_again: […]` (a note in
fixed form, since `record.schema.json` has no field for it and the common
schema is not changed here; a field `posed.recreated_for_budget` with
`steps.prefix_steps` would be the natural amendment). The prefix's steps are
recorded there and not charged to the stage. Listed as confound 1. *Why:* the
alternative readings were worse: charging an incremental program a restart
cost it does not have (calling every stage *reposed*), or one live process
whose stage budgets cannot be enforced. x1sim has no budget, so there it is
one live process.

**Open:** at a commit stage inside the re-created prefix, the program
carries out the commit again (deterministically, its output checked to be
identical, so v is the same). `PROTOCOL.md` says a reposed run must not "ask
the system to select again"; this is not a reposed run, but the classifiers
may wish to know it, and it is recorded in the attempt's notes.

## A3. spawn, and sharing unknowns (P09, P16b)

ALGOL 60 has no separate computations, no concurrency and no unknowns.

**Implemented:**
- *P09a, P09b*: a spawned computation is a part of the one program, started
  by the message `4 k c`, that runs to its end (or budget, or error) before
  the next is spawned, in the instance's `spawn_order`: `side_by_side:
  false`. They share the program's variables (the "one database"). In report
  and x1 each has its own budget (A2). If one ends the process (budget,
  error, timeout), there is no instance left to start the next in; the next
  is recorded as not started (`execution_state.determined: false`, no
  states, the reason in `basis`), not run in a separate instance.
- *P16b*: ALGOL 60 configurations do **not** allow separate computations to
  share unknowns (they have no unknowns), so stage 1 is posed to `main` as
  one conjunction (`1 1`), the `spawn_fallback`, with its `fallback_queries`.
  This is the harness's statement for all three configurations, made before
  any program is run, as the common Q4 asks.

## A4. After budget, error or timeout, the replay repeats the stop

An incremental ALGOL 60 program cannot continue past `--max-steps` or an
error (the process ends), so stage k+1 is reposed (`PROTOCOL.md`). The
program is deterministic, so the replay of stage k ends the same way, and
stage k+1 is never reached; every later stage is then recorded as *budget*,
*error* or *timeout* during the replay (the attempt's notes say which stage
of the replay stopped). After a final timeout each later stage again takes
the full limit and its rerun.

**Implemented:** exactly that; the harness does not skip, shorten or work
around those stages (`harnesses/README.md` section 3: `run` never decides
from a result to skip a stage).

## A5. Restart cost: never in-run

The default method (Q6) reads the step count "at the moment stage k is first
posed". The interpreter cannot report its count at a moment of the harness's
choosing.

**Implemented:** `restart_cost_method: "separate-run"` always: stages 1..k−1
alone (their messages written at once, then the input closed), the least
`--max-steps` at which the interpreter does not stop, found by bisection.

## A6. Replayed stages' budgets in one process

Q6 says each replayed stage has, during the replay, the budget it had when
first posed. In one process a single limit bounds the whole run.

**Implemented:** the bisection for the restart cost searches up to the sum
of the replayed stages' budgets; the replay as a whole therefore has that sum,
not each stage its own. Where the replay does not end within the sum (it
replays a stage that ran out of budget, A4), the sum is recorded as
`restart_cost`, with a `restart_cost_source` saying the replay was not
measured to its end, and the run's limit is that plus the budget (so that
`budget = restart_cost + 10⁶`, as `validate.py` requires). A replayed stage
can therefore get more than its own budget in a reposed run; for a stage
that does not terminate that changes nothing but the step count at which it
is stopped.

## A7. Store at the stage boundary

The measurement build reports its quantities once, at the end of the
process, after the interpreter has returned and dropped every frame and
array, so the live quantities' "end" is 0, not their value at the stage
boundary.

**Implemented:** live quantities (`frames`, `slots`, `arrays`,
`array_elements`, `names`, `call_depth`) have `boundary: null`; their peak
over the process (stages 1..k, as re-created) is the stage's `exact` peak
only where it exceeds the peak at the end of stage k−1 (from the previous
stage's storage run), else `null`. Totals are read at the boundary (the
process ends there). Confound 6.

## A8. What a stage stopped by budget, error or timeout can observe

`observe()` is to read state "including at the moment a budget runs out".
An ALGOL 60 program cannot print anything at that moment; the interpreter
stops it.

**Implemented:** observe records what the program printed in the stage
before the stop (often nothing). The process is gone; nothing more can be
read.

## A9. Steps in behaviour mode

**Implemented:** in behaviour mode the harness measures R(k) only where a
later stage's budget needs it, and records it (Q17: incidental). The last
stage's steps, and those of a reposed program, are left null in behaviour
mode, with a note; the cost run gives them.

## A10. `ended_by` for printed answers

The program prints all it computes; there is no mechanism to ask for more.

**Implemented:** `no-enumeration` when the stage ended with no more than cap
answers; `cap` when it printed more than cap (the first cap are collected,
the rest stay in `stdout` and `print`); `budget`, `error`, `timeout` when the
stage ended so.

## A11. Constants and parameters on one input, without anticipation

The interpreter has one input stream, and the contract wants constants read
"from a constants file the harness passes", the parameters n, order, answer
mode passed by the harness, and stages posed by the harness; and no stage's
information may reach the program before the stage is posed (`PROTOCOL.md`,
"Writing a program", rule 5).

**Implemented** (revised before merge, at the coordinator's request): every
line of the constants file is tagged with the stage that first uses it
(`k: values…`). Standard input carries one line of instance parameters
(`n a m c1 … cm`), and then messages; each message that poses or replays
stage k (`1 k`, `2 k`, `3 k` + v, `4 k c`) is followed by stage k's lines, in
file order, with the tag removed. So no stage's constants are on the input
before that stage is posed, structurally, and a reposed run carries each
replayed stage's constants with its replay. The harness reads only the
tags, never the values. The verifier still substitutes only the constants
file (`ALGOL60_CONSTANTS`), which must keep the tags. String-valued
parameters (`order`, `spawn_order`) are passed as integer codes by their
first appearance in `stages.json` (README, 2.2). The qualification (F1)
traces every write to the system's input and checks it. Earlier version:
the whole file was sent before stage 1; the program's discipline alone kept
it from anticipating.

## A12. The image's name

The brief names the image `cp-agent-systems:spec-1.0`; `harnesses/README.md`
names `cp-systems:spec-1.0`. The harness ran in the former. It cannot read
the image digest from inside; `system_build.image` is taken from
`HARNESS_IMAGE` when the launcher passes it, else null.

## A13. The X1 compiler as `check`

`x1algc` compiles without running anything, but it accepts some programs
that are wrong (it accepted `k := 1 +;`, which x1sim then stopped at run
time with "Cannot pop empty stack"), and it writes its error report on
standard output, where the object code goes.

**Implemented:** `check x1sim` runs only `x1algc` on a copy in a temporary
directory, discards the object code, prints the compiler's report on
failure, and says that the X1 compiler detects fewer errors than `algol60
--check`. An author may also check the X1-form program in x1.

## A14. Input and output in x1

`algol60 --x1` provides both the X1 system's procedures (`read`, `print`,
`PRINTTEXT`, …) and the Modified Report's (`ininteger`, `outstring`, …),
which the X1 did not have; the systems file lists only the IFIP procedures,
as external mechanisms of *report*.

**Implemented:** the harness accepts either in x1, since it only reads
text. Which procedures count as core or external in x1 is for the
classifiers; the README recommends the X1 form, which also runs in x1sim.

## A15. Exit status of an incremental attempt

After the stage under test the harness closes the input, and the program's
next read ends the process with the interpreter's error (exit status 1).

**Implemented:** `exit` records that status verbatim; the stage's execution
state is decided by its `[end]`, not by the exit status, and a note says so.
In x1sim the live process continues, so `exit` is null until the last stage,
and its final status is in the record's notes.

## A16. A program that ends its own computation

An incremental program that terminates (instead of reading its next
message) leaves no computation for the next stage.

**Implemented:** the next stage is reposed, with `reason: "configuration"`
and a stage note saying the process had ended.

## A17. Replaying a spawning stage

`PROTOCOL.md` reposes every stage 1..k. No stage after a spawning stage
exists in `stages.json` except in P16b, whose spawning stage ALGOL 60 poses
by its fallback (A3).

**Implemented:** replaying a spawning stage is not implemented; the harness
would record a harness fault if a stages file needed it.
