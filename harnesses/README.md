# Harnesses: the common contract

*Phase 4 (`PROTOCOL.md`, "Phases"), wave 1, written against `spec-1.0`.
This is the part every per-system harness shares. It changes no frozen
file. Where the specification could not be implemented as written, or was
ambiguous, the reading taken here is in [`QUESTIONS.md`](QUESTIONS.md).*

| file | what it is |
|---|---|
| `README.md` | this contract: what every per-system harness implements, and what every program is written against |
| [`stages.json`](stages.json) | the structure of every problem: sub-problems, instances (sizes, orders, answer modes), and per stage its number, description, queries and caps, commit and spawn, and the problem file's line. **No constants, no valid outcomes** |
| [`record.schema.json`](record.schema.json) | the JSON Schema of a raw record, the same for every system |
| [`validate.py`](validate.py) | checks raw records against the schema and the rules below (Python 3, standard library only) |
| [`QUESTIONS.md`](QUESTIONS.md) | what the specification leaves open, and the reading implemented |
| [`examples/`](examples) | **made-up** records and a made-up stages file, written by hand to test `validate.py`. Not runs, not results |
| `<system>/` | one per system, written by that system's harness author: `run`, `check`, its `README.md`, `S-mechanisms.md`, `qualification/` |

Words in this file: *must*, *never* and *only* are requirements; a
per-system harness that cannot meet one says so in its own `QUESTIONS.md`
and README.

## 1. The first principle

**A harness observes what the system computes. It never supplies it.**

A harness passes stages in, collects answers through the system's
standard mechanism for answers, reads state for `observe()`, enforces the
budget and the safety limit, and writes the record. It does not, on the
system's or the program's behalf:

- suspend a computation, or wait for information;
- search, backtrack, or enumerate values;
- schedule, interleave or arbitrate between computations, or run
  computations concurrently itself (`PROTOCOL.md`: concurrency is a
  mechanism of the configuration);
- propagate constraints, or simplify, reconstruct, complete or combine
  answers;
- combine stages, work out the net information of a reposed run, or skip
  a replayed stage;
- order, choose, retry or re-pose goals on its own.

Where a configuration lacks a mechanism, the harness does not make up for
it. The program must, as S code counted against that configuration, or
the problem is *not expressible* there. Everything a harness does beyond
passing stages in, collecting answers and reading state is listed in its
README as a possible confound, and copied into each record's
`run.confounds`.

## 2. Terms

| term | meaning |
|---|---|
| **instance** | one thing a harness runs: a sub-problem at one size, in one arrival or spawn order, in one answer mode. Its id comes from `stages.json` (`P01a`, `P02b.R2R1R3`, `P12c.n16.any`, `P13d.n10000`, `P16a.n1000.interleaved`). A sub-problem with one instance has the sub-problem's own id |
| **run** | one invocation of `harnesses/<system>/run`: one configuration, one instance, one mode, every stage of the instance in order. It writes one raw record |
| **stage** | as the problem file numbers it (`stages.json` gives the line). Stage k's information is held by the program, never by the harness |
| **computation** | `main`, the instance's one computation (or its top level); or a computation started with `spawn()` (P09a, P09b, P16b), named as `stages.json` names it |
| **attempt** | one try at a stage under the safety limit. A stage has one attempt, or two when the first was stopped by the safety limit and the problem allows a rerun |
| **query** | one call of `answers(cap)` on one computation at the end of a stage. Each stage of `stages.json` lists its queries with their caps |

The query of a stage is always about all the information of stages 1 to k
(`SPECIFICATION.md`, "Stages and monotonicity"), over the sub-problem's
unknowns. `stages.json` lists those unknowns by name; their values are
for the classifiers.

## 3. How a run is driven

    harnesses/<system>/run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR

| argument | value |
|---|---|
| CONFIGURATION | a configuration of `systems/<system>/README.md`, by its name there (`absys-depth-first`, `plain`, `core`, `x1sim`, ...) |
| PROBLEM | `P01` … `P16` |
| SUBPROBLEM | an **instance id** from `stages.json`, which for a sub-problem with one instance is the sub-problem id (`P07c`), and otherwise names its parameters (`P12a.n8.all`). See `QUESTIONS.md`, Q2 |
| MODE | `behaviour`, `cost` or `storage` (section 8) |
| PROGRAM | the program's path, relative to the repository root |
| OUTDIR | where the raw record is written: `results/<system>/<configuration>/<problem>/raw/` (section 10) |

Exit status: **0** when a valid record was written, whatever the run's
outcome (an *error*, *budget* or *timeout* stage is a result, not a
failure of the harness); **2** for a usage error (unknown configuration,
instance or mode; a mode the systems file does not allow for that
configuration, such as `cost` for *x1sim*), with no record written;
**3** when the harness itself failed and could not write a valid record.
A harness fault that still allows a record is written into
`harness_faults` and exits 0.

**The harness runs inside that system's pinned Linux image**
(`sandbox/README.md`, `PINS.md`): `cp-systems:spec-1.0` (Absys, ALGOL 60,
x1sim), the pinned `swipl:11.0.1` image, the pinned `python:3.13.7`
image. It assumes nothing of the host. It needs only what the image has,
plus the repository mounted at a path it is given or finds from its own
location. It records the system build it ran (section 9). The launcher
outside the container (whatever starts it) is not part of the harness and
may not change what it does; it may pass the image digest in, by an
environment variable the system harness names, since the harness cannot
always read it from inside.

What `run` does, in this order, and nothing else:

1. Read `harnesses/stages.json`; find the instance; take its stages, its
   queries and caps, its commit and spawn stages, and its limits (a
   problem's `limits`, else `default_limits`).
2. Check the program with nothing but reading its bytes (SHA-256) and,
   where the systems file needs it, the constants input (section 11).
3. For k = 1 … K: **pose** stage k (section 4); for each spawned
   computation of the stage, **spawn** it; for each query of the stage,
   **answers(cap)**; then **observe()** and **print()**; then record the
   attempt. Apply the safety limit (section 7); after a stop, rerun once
   where allowed.
4. Write the record, then validate it with `validate.py`. A record that
   does not validate is a harness fault (exit 3), kept beside the output
   under the name `<run_id>.INVALID.json`, never silently dropped.

`run` never decides, from what a stage returned, to pose a different
stage, to skip one, or to stop early. The only things that change how the
next stage is posed are the ones `PROTOCOL.md` names: *budget*, *error*,
and (`QUESTIONS.md`, Q7) *timeout*. P13's rule that larger n are not run
after a limit stop is applied by whoever runs the batch, across runs, not
by `run` (Q10).

## 4. The operations

These are `PROTOCOL.md`'s, made concrete. A per-system harness implements
exactly these and nothing that orders, chooses or re-poses goals on its
own.

### pose(stage)

Gives the system the information of stage k, in one of two ways, chosen
by the configuration's systems file ("The same computation"), never by
the harness from results:

- **incremental**: stage k is received into the computation that holds
  stages 1 to k−1 (an Absys session, a SWI-Prolog *session* engine, a
  Python or ALGOL 60 program that reads each stage from its input as it
  arrives). Recorded `posed.how = "incremental"`.
- **reposed**: a new computation is started, and stages 1 to k are
  replayed into it **in order, every one of them, replacements and
  withdrawals included** (P10, P15d). The program carries them out. The
  harness never works out the net information itself, never drops a
  stage that a later one replaced or withdrew, and never merges stages.
  Recorded `posed.how = "reposed"`, `posed.replayed = [1, …, k−1]`.

Stage 1 is always `fresh`. What the harness gives the program is only:
which stage to pose (k), for a reposed run the list of stages to replay
(1 … k−1) and any replayed commitments (below), and the instance's
parameters (n, order, answer mode, as `stages.json` gives them). The
program holds the stage information. The harness never passes a constant
of a problem.

**No anticipation** (`PROTOCOL.md`, "Writing a program", rule 5): the
harness tells the program about stage k only when stage k is posed, and
never tells it how many stages follow.

### spawn(computation)

P09a, P09b and P16b. Starts a separate computation **in the same
instance of the system**, sharing one database, never in a separate
operating system process (`PROTOCOL.md`). `stages.json` lists the
computations a stage spawns (`spawns`) and, for P09a, the order
(`spawn_order`).

- Where the configuration can run computations side by side, `spawn`
  returns at once (`side_by_side: true`).
- Where it cannot, the first runs to its end or its budget, and then the
  next (`side_by_side: false`).
- Each spawned computation has its own budget and its own execution
  state, recorded separately.
- P16b only: where the configuration does not allow separate
  computations to share unknowns, the four contributions are posed as one
  conjunction in `main` (`spawn_fallback`), with `fallback_queries`, and
  that is recorded. Which configurations allow it is the systems file's
  and the system harness's statement, not the harness's judgement on a
  run.

The harness may use the configuration's own mechanism for starting a
computation (an engine, a thread, a program's own spawn), as the program
asks for it. It may not interleave computations itself.

### answers(cap)

Collects the answers the system reports, **through its standard mechanism
for enumerating them** (each systems file says what it is; for Python and
ALGOL 60 it is the values the program prints), until the mechanism is
exhausted, the budget runs out, or `cap` answers have been collected.
`cap` is 1 for an *any one* query and 20 otherwise, as `stages.json`
gives it per query. The harness never asks for an answer the mechanism
did not offer, never filters or deduplicates answers, and never stops
early because the answers look complete. Each answer is recorded
**verbatim**, as the mechanism produced it, with `ended_by`:

| ended_by | when |
|---|---|
| `exhausted` | the mechanism reported no more answers |
| `cap` | `cap` answers were collected; the mechanism was not asked again |
| `budget` | the budget ran out while collecting |
| `timeout` | the safety limit stopped the attempt |
| `error` | the system stopped with an error |
| `no-enumeration` | the configuration has no mechanism for asking for more: the program printed what it computed for the stage and the stage ended (Python, ALGOL 60) |

The execution state is classified **after** the call (section 5).

### observe()

Records the state the common observations need (`SPECIFICATION.md`,
"Observations common to every problem"), **verbatim**, as the system or
the program holds it at the end of the stage, including at the moment a
budget runs out: bindings held (`SPECIFICATION.md`, "reported": a binding
is reported if `observe()` can read it), residual relations, suspended
work, alternatives held. `observe.raw` is what was read, unedited;
`observe.bindings` splits it by unknown only where that can be done
mechanically. A residual counts as reported only if it is state that the
system or program holds and acts on later; printing the posed information
back is not observing it, and the harness never makes a residual up from
the posed information.

### print()

The system's own rendering of what it holds at the end of the stage (an
Absys assertion's printed derivations, a Prolog toplevel's bindings, the
program's printed values), recorded verbatim in `print`. The harness
never reformats it.

### Observing must not consume the computation

In a configuration where collecting answers or observing would end or
alter the computation that the next stage extends (exhausting a
backtracking search in a SWI-Prolog *session* engine, for instance),
`answers()` and `observe()` for stage k are taken on a **separate run of
stages 1 to k**, and the incremental computation is left as it was. The
record marks each such query `collected_on: "separate-run"`, and the
observation `taken_on: "separate-run"`, and keeps the separate run's
stdout, stderr and steps under `separate_run`. Its P11 effects go to the
observation log (section 6). In a reposed configuration every stage's run
is already separate, and nothing more is needed.

## 5. Execution state

Recorded per computation, per attempt, in the vocabulary of
`SPECIFICATION.md` ("Execution state"), **as far as the harness can tell
it mechanically**:

| state | what the harness reads to say so |
|---|---|
| `budget` | its budget mechanism fired (Absys `--steps`, `call_with_inference_limit/3`, the `sys.monitoring` callback, `--max-steps`) |
| `timeout` | the safety limit stopped the attempt |
| `error` | the system stopped with an error; the error is copied verbatim to `error_verbatim` |
| `alternatives pending` | the system's own report that a request for more answers would resume it (a nondeterministic exit, open choicepoints, hibernating derivations), or, for Python and ALGOL 60, the program's named pending structure, read by `observe()` |
| `suspended` | the system's own report of held work that later information may resume (suspended equations, attributed variables with goals, a blocked engine, a program's named queue) |
| `finished` | the system stopped and reports none of the above |

`alternatives pending` and `suspended` may both hold. `finished` excludes
the others; at most one of `budget`, `timeout` and `error` holds. Where
the harness cannot tell mechanically, it says so (`determined: false`),
lists what it could tell, and gives its basis. **The harness never
classifies the semantic axis, the representation, the simplification or
the effects class**: those are the classifiers' (`PROTOCOL.md`, "Roles"),
from the record.

## 6. Commitments and the effects log (P11)

**Commitments are preserved when a run is reposed.** At a commit stage
(`stages.json`, `commit: true`: P11c stage 3, P11d stage 2), the system
selects one of its current outcomes, v, and reports it through its
answers mechanism (`answers(1)`). The harness keeps that answer verbatim.
When a later stage is reposed, the commit stage is replayed **as the
information x = v**, with v passed to the program verbatim as first
selected, and recorded in `posed.replayed_commitments`. The harness never
asks the system to select again, and never parses or rewrites v beyond
taking the answer as the system gave it. Where the system did not select
(one that keeps every alternative live), nothing is replayed as a
commitment, and that is recorded; the classifiers judge it as P11 says.
In P11a and P11b, which have one stage, the outcome is committed when it
is reported (`committed_when_reported`).

**The effects log.** The harness provides L and emit: one stub, with the
same behaviour and the same log format in every system (the binding of
emit into each language is the system harness's).

- `emit(m)` appends one entry, m as the program passed it, rendered as
  the system renders m, to the log, and returns. It does nothing else: it
  does not fail, defer, buffer past the end of the stage, deduplicate, or
  read the log. Nothing the system does can remove an entry.
- The log is a file of JSON lines, one entry per line, with the fields of
  `effect_entry` in the schema: `seq` (position, from 1, never reused),
  `entry`, `run_id`, `stage`, `attempt`, `during_replay_of` (the earlier
  stage being replayed when emit was called, in a reposed run, else
  null), and `log`.
- **One classification log per configuration and instance**, at
  `results/<system>/<configuration>/P11/raw/<instance>.effects.jsonl`,
  **never reset**, across every behaviour run the harness makes, reposed
  runs and safety reruns included. The record copies the entries this run
  appended into each attempt's `effects`, and the whole log after the run
  into `effects.log_after_run`, with `entries_before_run`.
- **Separate observation runs** (section 4) and **every cost and storage
  run** write to `<instance>.effects-observation.jsonl` in the same
  folder, which is not judged (Q8).
- Entries emitted while replaying an earlier stage carry
  `during_replay_of`, so that entries duplicated only by reposing can be
  counted separately. The harness marks when an entry was made; whether it
  is a duplicate, and whether it was before, at or after commitment, is
  for the classifiers.

## 7. Budget and safety limit

| | P12, P13, P16 | every other problem |
|---|---|---|
| budget | 10⁸ steps per stage and computation | 10⁶ steps per stage and computation |
| safety limit | 600 s per stage, **fixed, no rerun** | 60 s per stage, then **one rerun at 600 s** |
| source | the problem file (`stages.json`, `limits`) | `PROTOCOL.md`, "Running" |

- **Steps** are in the systems file's unit (Absys steps, SWI-Prolog
  inferences, Python bytecode instructions, ALGOL 60 interpreter ticks).
  The budget is a classification within a system, never compared across
  systems. Each spawned computation has its own budget; P16b stages 2
  and 3 have one for the whole.
- **A reposed run** has a budget of its **restart cost plus 10⁶** (10⁸
  where the problem says). The restart cost is the measured steps of
  running stages 1 to k−1 alone (`METRICS.md`), taken as the restated
  steps of this run's own run of stages 1 to k−1, that is, stage k−1's
  final attempt (Q6). It is recorded in `steps.restart_cost`, with
  `restart_cost_source`.
- **After budget.** If stage k ends in *budget* and the configuration can
  keep its computation and continue it, stage k+1 is posed into that same
  computation, with a new budget (`continued_after_budget: true`). Only
  where it cannot are stages 1 to k+1 reposed (`reason: "after-budget"`),
  counted under restart cost. Whether a configuration can continue is the
  system harness's statement, in its README.
- **After error.** Stage k+1 is posed by reposing stages 1 to k+1
  (`reason: "after-error"`), counted under restart cost, in every
  configuration, incremental ones included.
- **After timeout.** As after error: the stopped computation cannot be
  continued, so stage k+1 is reposed (`reason: "after-timeout"`), Q7.
- **Safety limit.** It protects the harness; it is not a measurement.
  It covers one attempt of one stage: for an incremental stage, from
  posing stage k to the end of `print()`; for a reposed stage, the whole
  run of stages 1 to k. When it stops an attempt, the harness stops the
  system by the means its README gives (`safety_limit.how_stopped`),
  records the attempt with what it had collected, and, where the problem
  allows, **reruns the stage once** with the limit raised tenfold
  (attempt 2, `reason: "safety-rerun"`). An incremental configuration's
  rerun is reposed, since the stopped computation is gone. If the rerun
  also stops, *timeout* is final for that stage (`final-timeout`). Under
  a fixed limit (P12, P13, P16) the first stop is final
  (`fixed-limit-timeout`). **Both attempts are recorded.** Answers
  collected before a stop are kept and classified on the semantic axis;
  only the execution state is *timeout*.
- A run that hits the safety limit only because it is instrumented (cost
  or storage, where the behaviour run finished) is recorded as such; it
  is not evidence about the model (`PROTOCOL.md`, "Modes of running").
  The classifiers read that from the records of the two modes.
- **ALGOL 60 x1sim** has no step count, so no budget can be enforced;
  only the safety limit stops it, and its records say
  `budget_enforced: false` (Q12).

## 8. Modes

Each program is run in up to three modes, one run each. A run's record
says its mode, and each figure is taken from the mode that gives it:

| mode | instrumentation | gives |
|---|---|---|
| **behaviour** | none beyond the harness (its budget counter included) | answers, observe(), print(), the execution state, the effects log. **The semantic result and the execution state are taken from this run** |
| **cost** | step counting only | steps per stage (incremental and restated), restart cost, answer latency (steps to the first answer, between answers, to the end), problem operations, repeated work where the systems file names a source, candidates examined (P12) |
| **storage** | the systems file's storage measurement | store vector (boundary and peak), retained alternatives (at answers, at boundaries, at budget, peak), suspended state (at boundaries and peak), P13's maximum resident set size where the systems file takes it from a separate run |

- **A sampled measurement is never taken from the run that gives the step
  count or the classification.** A sampled maximum (`peak.kind =
  "sampled"`) may appear only in a storage record; `validate.py` rejects
  one in a behaviour or cost record. Exact peaks may appear in any mode
  whose instrumentation gives them.
- A field a mode does not measure is `null`, or `{}` for the store
  vector. Figures that a mode records incidentally (the budget counter's
  steps in a behaviour run) are kept, but the figure of record is the one
  from the mode in this table.
- Where two modes can be compared, their answers must agree; a
  disagreement is reported as a fault of the instrumentation, by the
  classifiers, from the records.
- The systems file says which modes a configuration has (x1sim:
  behaviour only). P13's process CPU time and maximum resident set size
  are recorded where the systems file says, for growth only.

## 9. The raw record

One JSON file per run, valid against [`record.schema.json`](record.schema.json),
the same for every system. Every string the system produced is kept
**verbatim** (JSON-escaped, never trimmed, reflowed or decoded beyond the
system's own output encoding; bytes that are not UTF-8 are written as
`�` and noted in `harness_faults`). A value the harness could not
read is `null`, never estimated.

### Run metadata (`run`)

| field | what |
|---|---|
| `run_id` | unique, also the file's stem: `<instance>.<mode>.<UTC timestamp YYYYMMDDTHHMMSSZ>` |
| `spec_tag` | `spec-1.0` |
| `system`, `configuration` | as in `systems/` |
| `problem`, `subproblem`, `instance`, `parameters` | from `stages.json`; `parameters` copied exactly |
| `mode` | behaviour, cost or storage |
| `purpose` | `primary`, `variant` (the verifier's), `qualification`, `example` (made up) |
| `program` | `path` and `sha256` of the program file as run, and the repository commit it was taken from |
| `constants` | `block`, `input` or `none`; the input file's path and SHA-256; the hidden variant's id when the verifier runs one |
| `system_build` | the pinned `commit` (from `/opt/src/COMMITS` in `cp-systems`), the `image` digest, the `binary`, the system's `version_output` verbatim, and whether the build or run is `instrumented` |
| `harness` | the harness's path, its git commit, and whether its files differed from it (`dirty`) |
| `command` | the harness command line as invoked |
| `posing` | `incremental` or `reposed`: the configuration's way of receiving a stage |
| `limits` | `budget_steps`, `step_unit`, `safety_limit_s`, `rerun_limit_s` |
| `started_utc`, `ended_utc`, `complete`, `incomplete_reason` | |
| `confounds`, `environment` | the system harness's listed confounds; environment it set (`PYTHONHASHSEED=0`, for instance) |

### Per stage, per attempt (`stages[].attempts[]`)

| field | what |
|---|---|
| `attempt`, `limit_s` | 1 under 60 s (600 s for P12, P13, P16); 2 for the rerun under 600 s |
| `posed` | `how` (`fresh`, `incremental`, `reposed`), `reason` (`first-stage`, `configuration`, `after-budget`, `after-error`, `after-timeout`, `safety-rerun`), `replayed` (the earlier stages replayed, `[1 … k−1]` when reposed), `replayed_commitments` (P11), `continued_after_budget`, `instance_parameters_passed` |
| `computations[]` | per computation: `id`, `spawned`, `spawn_index`, `side_by_side`; its `queries` (each with `id`, `cap`, `answers` verbatim with `steps_at` and `alternatives_at` where measured, `ended_by`, `collected_on`); its `execution_state` (`states`, `determined`, `basis`, `error_verbatim`); its `steps` (`unit`, `budget`, `budget_exhausted`, `budget_enforced`, incremental `stage`, `restated`, `restart_cost`, `to_first_answer`, `between_answers`, `to_end`, `repeated_work`); its `alternatives` in the systems file's unit (`at_boundary`, `at_budget`, `peak`, `held_as`: all live at once or kept for backtracking, `by_type`, `problem_defined`); its `suspended` work in the system's own terms (`at_boundary`, `peak`, `items` by kind with counts); `problem_operations` by relation case; `candidates_examined` (P12) |
| `observe` | `raw` verbatim, `method`, `taken_on`, `bindings` |
| `print` | verbatim |
| `store` | the systems file's vector, by quantity: `boundary`, `peak` (`exact` or `sampled`, with its interval) |
| `wall_time_s`, `cpu_time_s`, `max_rss_kb` | wall time (for the safety limit, not a metric); CPU and RSS for P13 growth only |
| `stdout`, `stderr` | verbatim, everything the system and program wrote during the attempt |
| `exit` | status and signal, or null where the process continues into the next stage |
| `safety_limit` | `hit`, `action` (`none`, `rerun`, `final-timeout`, `fixed-limit-timeout`), `how_stopped` |
| `effects` | P11: the log entries this attempt appended |
| `manual_actions` | every action by a person, or by code written for one problem, that the fixed harness does not perform (`METRICS.md`, "Intervention"), with who and why |
| `separate_run` | the separate run of stages 1 to k, where answers or observation were taken on one |

At record level: `effects` (P11: the logs' paths and the whole
classification log after the run; null otherwise), `manual_actions`
outside any stage, `harness_faults` (what the harness itself failed to
do), `notes`.

### Rules a record must keep (checked by `validate.py`)

Beyond the schema:

1. The instance exists in `stages.json`, with the same problem,
   sub-problem and parameters, and the problem's limits; a complete run
   has every stage, numbered 1 … K.
2. Each stage's queries are those of `stages.json`, on the computations it
   names, with its caps; spawned computations are those it spawns, in the
   instance's `spawn_order` (or the P16b fallback).
3. No query has more answers than its cap; `ended_by: "cap"` has exactly
   cap answers; `ended_by` budget, timeout or error appears in the
   computation's state.
4. Stage 1 is `fresh`. A reposed stage replays exactly 1 … k−1. An
   incremental stage replays nothing, and is not used in a reposing
   configuration except to continue after budget. After an error the next
   stage is reposed. A `continued_after_budget` stage follows a *budget*.
5. A reposed stage's budget is its restart cost plus the problem's
   budget; any other stage's is the problem's budget.
6. A second attempt exists only after the safety limit stopped the first,
   under the problem's rerun limit; none under a fixed limit. A *timeout*
   state and a safety-limit stop go together.
7. `finished` stands alone; at most one of budget, timeout, error;
   *error* has its text; *budget* matches `budget_exhausted`.
8. No sampled maximum outside a storage record.
9. A separate run, where one is used, replays 1 … k.
10. P11 records have `effects`; others do not. The entries of the
    attempts are exactly the classification log's entries after
    `entries_before_run`; cost and storage runs write only to the
    observation log; replayed commitments are for earlier commit stages.

```
python3 harnesses/validate.py results/<system>/<configuration>/<problem>/raw/*.json
python3 harnesses/validate.py --check-stages            # checks stages.json itself
python3 harnesses/validate.py --stages harnesses/examples/stages-made-up.json harnesses/examples/made-up-*.json
```

The last line runs on the made-up examples: three valid records (an
incremental run with a safety-limit rerun; a reposing run with a commit
and the effects log; two spawned computations in a storage run with a
separate observation run) and one deliberately invalid record, which it
rejects with six errors.

## 10. Where records go

    results/<system>/<configuration>/<problem>/raw/<run_id>.json
    results/<system>/<configuration>/P11/raw/<instance>.effects.jsonl
    results/<system>/<configuration>/P11/raw/<instance>.effects-observation.jsonl

`OUTDIR` is that `raw/` folder. A harness never overwrites or deletes a
record: every run, including reruns, failed runs and runs on hidden
variants (`purpose: "variant"`, written under the verifier's own
`OUTDIR`), is kept. The result files of `PROTOCOL.md`, "Recording a
result" (`results/<system>/<configuration>/<problem>.md`) are written
from these records by the classifiers, and cite them by `run_id`.

## 11. What a program must provide

A program author cannot run anything before the program is fixed (only
the system harness's `check`, which executes nothing). So each system
harness's README says exactly, per configuration, how a program meets
these requirements; the common part is:

1. **Stages as units the harness can pose.** The program handles stage k
   when, and only when, the harness poses it, in the way the
   configuration receives stages (incremental, or by replaying 1 … k).
   Code for stage k does not depend on any later stage.
2. **Replay.** In a reposed run the program carries out every stage
   1 … k in order, replacements and withdrawals included, and accepts a
   replayed commit stage as the information x = v, with v as the harness
   passes it (the verbatim answer of the commit stage).
3. **Instance parameters.** The program takes n, an arrival order, a
   spawn order or the answer mode from the harness, as `stages.json`
   names them, and holds everything else.
4. **Answers through the standard mechanism.** Answers reach the harness
   only through the configuration's standard mechanism for answers, in
   the form the system harness's README fixes (for Python and ALGOL 60,
   printed lines with the delimiters it defines).
5. **State for observe().** Whatever the system does not expose by
   itself (a Python program's named pending structure, its counters of
   problem operations), the program exposes in the form the system
   harness reads. Counters that only count are H (`METRICS.md`).
6. **Constants for the verifier** (`PROTOCOL.md`, "Writing a program",
   rule 6). Every constant of every stage is in **one** place the
   verifier can replace without touching anything else, and the program
   stays correct for other constants. Which place is fixed per system by
   its harness README, not here, with this default:

   | system | where the constants are |
   |---|---|
   | ALGOL 60 | **input**: read with the input procedures as integers in the problem's encoding (`systems/algol-60/README.md`, "Values"), from a constants file the harness passes; recorded as `constants.how = "input"` with its SHA-256 |
   | Absys, SWI-Prolog, Python | **one marked constants block** in the program, between a line containing `CONSTANTS BEGIN` and a line containing `CONSTANTS END`, each inside a comment of the language, holding nothing but the constants, or **input**, as the system harness decides and documents; recorded as `block` or `input` |

   A sub-problem with no constants (P04d, P04f, P08b; `variants/README.md`)
   records `none`. Sizes n and arrival orders are not constants (they are
   not varied) and come from the harness (point 3).
7. **Provenance** (`PROTOCOL.md`, "Writing a program", rules 1, 2, 8): its
   author, whether the author had seen a precursor, and the source of each
   idiom, in a comment the system harness README places.

**H tokens** (`METRICS.md`, class H) are the per-system harness's own
calls as they appear in a program: the calls that pose stages, request
answers and print, the emit stub's binding, and output adapters (rule
13). Each system harness's README lists them, construct by construct,
before any program is written. Code a program adds beyond them is
classed by the rules of `METRICS.md`, not as H.

## 12. What every system harness writes

As its brief says (`sandbox/briefs/harness-system.md`), under
`harnesses/<system>/`: `run` with this command line for every
configuration and every mode the systems file allows, for every problem
P01–P16, spawn and the effects log included; `check CONFIGURATION
PROGRAM`, which executes nothing; a `README.md` with the program contract
of section 11 for its system, a complete minimal example for a made-up
problem, the H tokens, how it stops a system at the safety limit, whether
each configuration can continue after budget, and its confounds;
`S-mechanisms.md`; and `qualification/`, whose every record passes
`validate.py`. Anything it cannot do as this file says goes in its own
`QUESTIONS.md`, with the reading it implemented.
