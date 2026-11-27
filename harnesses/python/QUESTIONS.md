# Questions: the Python harness

*Where the common contract (`harnesses/README.md`, `harnesses/QUESTIONS.md`),
the specification or `systems/python/` could not be implemented as written
for Python, or left a choice open, and the reading implemented. No file
outside `harnesses/python/` was changed. An amendment can settle any of
them.*

*Settled by the coordinator after phase 4's first report: the recursion
limit stays at CPython's default, recorded (Q1); S mechanisms for
extended will be written, problem-independent, by a separate author before
any program (Q3).*

## Q1. The recursion limit has no value

`systems/python/README.md` says "the recursion limit is a configuration
flag, fixed per configuration", and `measurement.md` gives two coherent
choices (the default 1000, or one large limit such as 10⁷), but the
configurations table names no flag and no value.

**Implemented:** no flag. Every configuration runs with CPython 3.13.7's
default recursion limit, 1000, which the harness does not change; a
`RecursionError` is *error*. *Why:* the harness must not set a flag the
systems file does not name; the default is what the pinned image gives. A
program may not raise it itself for one problem (`measurement.md`, 5: that
would be an intervention or a control tailored to a stage); if it calls
`sys.setrecursionlimit`, that is an import of `sys` (an external mechanism)
and a construct for the classifiers. Because the program is `exec`'d under
the runtime's frames, about three fewer levels are available than in a
plain script (README.md, confounds).

## Q2. Whether extended includes stdlib-concurrency's modules

The configurations table lists core, stdlib-concurrency ("adds threading,
queue and asyncio") and extended ("adds mechanisms written for the
experiment"), without saying whether each row adds to the one before.

**Implemented:** extended is **core plus S mechanisms**, without
`threading`, `queue` or `asyncio`; `check` rejects them there, and `spawn()`
runs computations one after another, as in core. *Why:* extended's class is
"modern, extended", without stdlib-concurrency's "with external
mechanisms", so it does not carry those modules.

## Q3. No S mechanism is defined for extended

`systems/python/README.md` names a backtracking search, a suspension queue
and a constraint propagator *for instance*, and `PROTOCOL.md` requires every
configuration's S mechanisms to be listed with their size at phase 4. None
is defined, and the brief forbids writing problem programs here.

**Implemented:** [`S-mechanisms.md`](S-mechanisms.md) lists **none** for
every configuration. A program for extended therefore has no listed
mechanism to use; code a program writes that is general over relations is
S by `METRICS.md` rule 19 and is classed so by the classifiers. *Why:* a
mechanism invented now by the harness author would be a choice of the
study's design, not of the harness; it needs an amendment, or a listing
before programs are written.

## Q4. A budget, an error or a timeout during the replay of a reposed run

A reposed run of stage k replays 1 … k−1, each with the budget it had when
first posed. If the program's set-up (its code before it first calls
`cp.stage()`) or a replayed stage ends in *budget* (it did when first
posed, in a program that reposes every stage), *error*, or the safety limit
stops the run, stage k is never given to the program, and its restart
cost cannot be read "at the moment stage k is first posed" (common Q6).

**Implemented:** the attempt for stage k records the replay's outcome as
stage k's state (*budget*, *error* or *timeout*), with a note that stage k
was never posed, and its restart cost is the whole instruction count of the
replay as far as it went (`in-run`), so that its budget is still restart
cost + 10⁶ as `validate.py` requires. *Why:* the harness may not skip the
replayed stage or give it more budget than it had; recording what happened
is the only reading that supplies nothing. In such a configuration every
later stage of the run ends the same way, which is a result about it.

## Q5. Continuing after budget

The systems file says that "where a stage must be continued after its
budget, the computation's thread is instead blocked at B and resumed with a
new budget".

**Implemented:** every configuration can continue, and does: the program's
computation is always paused at its budget (never stopped by an
exception), and an incremental program's next stage is posed into that
same process with a new budget of 10⁶ (`continued_after_budget: true`). The
resumed computation carries on with what it was doing when it was paused,
and receives stage k+1 when it next calls `cp.stage()`. Answers it reports
before receiving stage k+1 are collected as stage k+1's (they were reported
while k+1 was posed), with a note saying so. A spawned computation paused
at its budget stays paused: no later stage is posed to it.

## Q6. Which answers a cap keeps, when nothing can be asked for more

The contract's `ended_by` values assume a mechanism that is asked for
answers one at a time. A Python program reports what it computes; the
harness cannot stop asking.

**Implemented:** the harness collects a computation's answers in the order
reported until the cap; any reported after it are not collected (they stay
in `stdout`, and the attempt's notes count them), and `ended_by` is `cap`.
With fewer answers than the cap, `ended_by` is the state that ended the
computation (`budget`, `timeout`, `error`) if any, else `no-enumeration`. The
harness never stops a program because the cap was reached. Programs are not
told the cap, except as P12's instance parameter.

## Q7. When a computation's part of a stage has ended

Python has no notion of a stage. The contract says the program "printed
what it computed for the stage and the stage ended".

**Implemented:** `main`'s part ends when it calls `cp.stage()` again, or its
module ends, or its budget runs out; a spawned computation's when its
function returns or its budget runs out; and any running computation's when
all running computations are quiescent: alive, and executing no
instruction for 0.5 s (README.md, section 6). A quiescent computation is
recorded `suspended` with `determined: false`. *Why:* without quiescence, a
thread waiting for information that never comes (stdlib-concurrency) could
only end at the safety limit, and would be misreported as *timeout*; the
harness reports quiescence and does nothing else to the thread. The sampling
is by wall clock, which the README lists as a confound.

## Q8. A program that ends before the last stage

An incremental program whose module ends (normally, or by `SystemExit`)
before the harness has posed every stage cannot receive the later stages.

**Implemented:** each later stage is recorded as posed incrementally, with a
note that the program had ended and nothing was sent; no answers, and the
state read from its registrations as they were left (*finished* if they are
empty). If the program ended in an error, the next stage is reposed
(`after-error`) as always. If a replay ends with no instruction count to
read (the process died, or the safety limit stopped it), the restart cost
is recorded as 0 and that is listed in `harness_faults`. *Why:* the harness may not
restart a computation that ended normally to give it a stage.

## Q9. problem_operations are per relation, not per case

The schema's example names a case (`conc/1`), and `METRICS.md` counts
"applications of each case of each relation". The systems file's
measurement is a PY_START count of the function that transcribes a
relation, which counts applications of the relation, one case per call.

**Implemented:** `problem_operations` is keyed by the name the program gives
the relation in `cp.relations(name=function)`, and counts calls of that
function: applications of the relation, all cases together. *Why:* the
systems file qualifies only that count; splitting by case would need
counters in the program (method A, which changes the step count) or a trace
of which branch ran.

## Q10. The program declares its own posing

`stages.json` and the contract leave posing to "the configuration's systems
file", and Python's allows both ways in every configuration.

**Implemented:** the program declares it, statically, in one comment line
`# CP-POSING: incremental` or `# CP-POSING: reposed`, read from its bytes
before it runs; the harness never chooses from results. The record's
`run.posing` is the declaration.

## Q11. P16b's fallback

Whether a configuration lets separate computations share unknowns is "the
system harness's statement".

**Implemented:** all three Python configurations do (spawned computations
are threads of one interpreter and share every object), so P16b's
contributors are always spawned and `spawn_fallback` is never used.

## Q12. What print() is, for Python

**Implemented:** `print` is what the program wrote to standard output while
stage k was posed, after any replay, verbatim: its own `print()` output
and the lines `cp.answer()` writes. For a continued stage it starts where
stage k was posed, so it includes what the resumed computation printed
before it received stage k. `stdout` is everything written during the
attempt, replay included.

## Q13. Where the step window of stage 1 starts

**Implemented:** at the program's first instruction, so a program's set-up
before its first `cp.stage()` (definitions, registrations, building tables)
counts in stage 1's steps and budget, and, in a reposed run, in the restart
cost. *Why:* that code runs before any stage and must be under some budget;
it is part of the computation that first receives stage 1.

## Q14. Constants delivered with their stage

The common contract (section 11, point 6) puts every constant in one marked
block, and `PROTOCOL.md` rule 5 forbids stage k's code to depend on any
later stage. A block of assignments that the program executes when it
starts puts every stage's constants in the program's namespace at stage 1,
so no anticipation would rest only on the author's discipline.

**Implemented** (at the coordinator's request, for all four systems): the
block is divided by `# stage k` lines, each entry tagged with the stage that
first uses it; `run` parses it and never lets the program execute it (the
program's process receives the text with the block's lines emptied and
never reads the file); `cp.stage()` gives stage k's entries as
`s.constants` when stage k is posed, and again when it is replayed. The
verifier still replaces only the block. The qualification scans the whole
memory of the program's process, from outside, at stage 1 and at stage 2:
stage 2's constant is absent at stage 1 and present at stage 2. What
remains outside the harness's reach: a program that opened its own file
from disk could read the block; `check` rejects every way of doing so it
can see statically (`open`, `__file__`, `linecache`, `inspect`, ...), and
the program's file is not otherwise in the process.
