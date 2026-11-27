# The Python harness

*Phase 4, wave 1, against `spec-1.0`. Written by the Python harness author
(`harness-python`, an agent) from the common contract in
[`../README.md`](../README.md), `systems/python/`, `PROTOCOL.md`,
`SPECIFICATION.md` and `METRICS.md`. Where the contract could not be
implemented as written, the reading taken is in
[`QUESTIONS.md`](QUESTIONS.md).*

| file | what it is |
|---|---|
| [`run`](run) | the harness: `run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR` |
| [`runtime.py`](runtime.py) | the part of the harness that runs inside the program's interpreter process (the step meter, the `cp` calls, `observe()`) |
| [`check`](check) | `check CONFIGURATION PROGRAM`: compiles and reads the program's syntax tree, executes nothing |
| [`constants.py`](constants.py) | finds, checks and parses a program's constants block (used by `run` and `check`) |
| [`S-mechanisms.md`](S-mechanisms.md) | the S mechanisms each configuration provides |
| [`QUESTIONS.md`](QUESTIONS.md) | what could not be implemented as written, and the reading taken |
| [`qualification/`](qualification) | evidence that the harness does what this file says: [`qualify.py`](qualification/qualify.py) reruns all of it; [`output.txt`](qualification/output.txt) is its output |

Everything is written in **CPython 3.13.7 with its standard library**, as
the pinned `python:3.13.7` image provides it (`/usr/local/bin/python3`).
Nothing is installed. `run` and `check` are run inside the image, from the
repository root mounted at `/work`:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \
        cp-agent-python:spec-1.0 harnesses/python/run core P01 P01a behaviour PROGRAM results/python/core/P01/raw

## 1. How a run works

`run` is the harness process. It reads `harnesses/stages.json`, checks the
program by reading its bytes, and starts the program in **its own
interpreter process**:

    /usr/local/bin/python3 -B -s -P harnesses/python/runtime.py FD_IN FD_OUT

with the environment cleared to `PATH`, `HOME` and **`PYTHONHASHSEED=0`**,
standard input `/dev/null`, and standard output and standard error going to
files that `run` reads at stage boundaries. `-B` writes no `.pyc` files,
`-s` ignores user site-packages, `-P` keeps the runtime's directory off
`sys.path`. No other interpreter flag is set; the recursion limit is
CPython's default, 1000 (QUESTIONS.md, Q1).

`runtime.py` compiles the program's text, as `run` sends it with the
constants block's lines emptied (it never reads the file), makes a fresh module `__main__` for it
(`__file__` the program's path, `sys.argv = [path]`, the program's directory
first on `sys.path`, as `python3 PROGRAM` would), puts the name **`cp`** in
its globals, switches on the step meter, and `exec`s it in the process's
main thread. `run` and the runtime talk over two pipes (marshal frames). The
runtime never runs program code of its own accord: the program runs from
its first line, and receives a stage only when it calls `cp.stage()`.

For stage k, `run` does, in this order:

1. **pose**: tells the runtime stage k (and, in a reposed run, first replays
   stages 1 … k−1 the same way, one at a time, each waiting for the program
   to finish it);
2. waits for **main's part of the stage to end**: the program calls
   `cp.stage()` again (asking for the next stage), or its module ends
   (normally, by `SystemExit`, or by an uncaught exception), or its budget
   runs out (its thread is paused), or it is quiescent (section 6);
3. **spawn**s each computation the stage spawns (`stages.json`), in the
   instance's `spawn_order`, and waits for each to end its part (section 5);
4. **answers**: the answers each computation reported through `cp.answer()`
   while stage k was posed, up to the query's cap;
5. **observe()**: the runtime reads the objects the program registered
   (section 3) and the mode's measurements;
6. **print()**: what the program wrote to standard output while stage k was
   posed (after any replay), verbatim.

The safety limit covers 1–6 for an incremental stage and the whole run of
1 … k (replay included) for a reposed one (common contract, Q13). After the
last stage `run` tells the program there are no more stages (`cp.stage()`
returns `None`), gives the process 5 s to exit, kills it otherwise
(recorded in the attempt's notes), validates the record with
`harnesses/validate.py`, and exits 0; an invalid record is kept as
`<run_id>.INVALID.json` and `run` exits 3. Usage errors (unknown
configuration, mode or instance, a missing program, a program without a
valid `CP-POSING` line) exit 2 with no record.

Environment variables `run` reads, all optional: `CP_IMAGE_DIGEST` (the
launcher passes the image digest; recorded in `system_build.image`, else
null), `CP_PURPOSE` (`primary`, the default, `variant` or `qualification`),
`CP_VARIANT` (the hidden variant's id), and `CP_STAGES` (a stages file other
than `harnesses/stages.json`, used only by the qualification's made-up
problems and recorded in the record's notes).

## 2. The configurations

From `systems/python/README.md`. All three have every mode (`PINS.md`).

| configuration | what a program may use | spawn() | posing |
|---|---|---|---|
| **core** | the language, its built-in functions and types, and `cp`; no imports. Any other standard-library module it imports is an external mechanism, to be listed | one after another (`side_by_side: false`) | incremental or reposed, as the program declares |
| **stdlib-concurrency** | core, plus `threading`, `queue` and `asyncio` | side by side (`side_by_side: true`) | as declared |
| **extended** | core, plus the S mechanisms listed in [`S-mechanisms.md`](S-mechanisms.md) (none at phase 4) | one after another | as declared |

The configurations differ, in the harness, only in how `spawn()` runs
computations; `check` also rejects `threading`, `queue` and `asyncio`
outside stdlib-concurrency. Whether extended includes stdlib-concurrency's
modules is QUESTIONS.md, Q2.

**Posing.** `systems/python/README.md` ("The same computation") allows both
ways in every configuration: a program that reads each stage as it arrives
is one computation (**incremental**); otherwise stages 1 … k are rerun
(**reposed**). The harness never chooses: the program declares which, by
one comment line (section 3). The same program text works both ways, since
a reposed run gives it stages 1 … k in order through the same `cp.stage()`.

**After budget**, every configuration **can continue**: the computation's
thread is paused at exactly its budget and, at the next stage, released
with a new budget of 10⁶ (10⁸) instructions, in the same process
(`continued_after_budget: true`). It then carries on with what it was doing
and receives stage k+1 when it next calls `cp.stage()`. (In a reposed
program every stage is a new process anyway.) **After an error** or a
**final timeout**, stage k+1 is posed by reposing 1 … k+1 in a new process
(`after-error`, `after-timeout`), in every configuration.

## 3. The contract a program must meet

A program is **one file** of Python 3.13 source in UTF-8. It is run as a
script: from its first line to its last, in the process's main thread.

### 3.1 Required lines

1. **Posing**, exactly one line, anywhere (by convention the first):

        # CP-POSING: incremental

   or `# CP-POSING: reposed`. Without it, `run` refuses the program (exit 2).
2. **Provenance** (`PROTOCOL.md`, "Writing a program", rules 1, 2, 8), a
   comment block after the posing line, beginning `# PROVENANCE`, giving the
   author (person or agent), whether the author had seen a precursor (the
   absys experiments E01–E09), and the source of each idiom used (a manual,
   a paper, a published program).
3. **Constants**, if the sub-problem has any: **one marked constants
   block**, which the harness reads and **the program never executes**.
   It runs from a comment line containing `CONSTANTS BEGIN` to a comment
   line containing `CONSTANTS END`, and is divided by comment lines
   `# stage k` (k a stage number of the instance). Under each `# stage k`
   come the constants that **stage k first uses**, one assignment of a
   literal value (numbers, strings, `True`/`False`/`None`, and tuples,
   lists, dicts and sets of literals) to a plain name per statement:

        # CONSTANTS BEGIN
        # stage 2
        A_VALUE = 3
        # stage 3
        B_VALUE = 4
        # CONSTANTS END

   Nothing else goes inside, and no constant of any stage appears outside
   it. `run` parses the block (`constants.py`) and gives the program its
   text **with the block's lines emptied** (line numbers kept), so none of
   these assignments runs and no name in the block exists in the program.
   Stage k's constants reach the program **only when stage k is posed**, as
   the dict `s.constants` that `cp.stage()` returns with it (`{"A_VALUE":
   3}` at stage 2), and again with stage k whenever stage k is replayed. A
   constant a later stage needs again is kept by the program (it may store
   what it received); it is tagged once, with the first stage that uses it.
   The same name may appear under two stages, with each stage's own value.
   This makes no anticipation (`PROTOCOL.md`, "Writing a program", rule 5)
   structural: before stage k is posed, nothing of stage k's constants is
   anywhere in the program's process (the qualification scans its whole
   memory). The program file is never read by the program's process; a
   program may not read files (`open`, `__file__`, `linecache`, `inspect`,
   ...), which `check` rejects. The verifier replaces the block's lines and
   nothing else, so the program must stay correct for any other values of
   the same shapes. A program with no block is recorded
   `constants.how = "none"` (right only for P04d, P04f and P08b). Sizes n,
   orders and answer modes are not constants: they come from `cp` (below).
   A block that does not parse, an entry before any `# stage k` line, or a
   stage the instance does not have makes `run` refuse the program (exit 2).

### 3.2 The names `cp` gives the program

`cp` is a global the runtime puts into the program's module before its first
line runs. It is never imported. Everything below is a harness call (H).

| call | what it does |
|---|---|
| `cp.stage()` | **Receive the next stage.** Called only from the main thread. Returns a stage object `s`, or `None` when the harness has no more stages for this run (then the program should end). Calling it **ends the program's part of the current stage**: whatever the program has not done by then is not part of the stage. It blocks until the harness poses the next stage. |
| `s.k` | the stage number, 1 … K, as `stages.json` numbers it (the problem file's numbering, except P16d2: QUESTIONS.md of the common part, Q15) |
| `s.replay` | `True` when stage `s.k` is being **replayed** in a reposed run (stages 1 … k−1 before stage k); `False` when it is the stage being posed. Answers given while `s.replay` is true are not collected; a program may test it to print nothing then |
| `s.commitment` | for a replayed **commit stage** (P11c stage 3, P11d stage 2): the verbatim text of the answer that stage gave when it was first posed in this run, which the program must take as the information x = v; otherwise `None` |
| `s.constants` | a dict of the constants the block tags with stage `s.k`, by name; `{}` if none. Given with the stage when it is posed and when it is replayed, never earlier |
| `s.params`, `cp.params` | the instance's parameters, exactly as `stages.json` gives them: `n`, `order` (a list of strings), `answers` and `cap` (P12), `spawn_order` (P09) |
| `cp.answer(value)` | **Report one answer** of the computation that calls it, for the stage being posed. `value` is rendered as `print(value)` would render it (`str()`), and written with a newline to standard output, exactly as `print(value)` would, and sent to the harness. One call is one answer, however many lines it contains. `str()` of a deeply nested value recurses in C and fails with `RecursionError`, as `print` would: render such values with an iterative printer of the program's own (an output adapter, H) and pass the string |
| `cp.emit(m)` | P11 only: append m, rendered by `str()`, to the effects log; returns `None`; never fails, defers or deduplicates (common contract, section 6) |
| `cp.bindings(mapping)` | register the dict (or any mapping) that holds the program's **bindings**: unknown name → value. Read at each `observe()`, by reference: register it once, keep updating it |
| `cp.pending(name, obj)` | register a structure of **alternatives pending** (a stack, a queue, a frontier, a generator, a list of generators), under a name that says what an entry is. Its entries count `len(obj)`; a generator or coroutine counts 1 while suspended, 0 when finished. Any entry makes the computation's state *alternatives pending* |
| `cp.suspended(name, obj)` | register a structure of **waiting work** (relations or computations held until information arrives), counted the same way. Any entry makes the state *suspended* |
| `cp.held(name, obj)` | register anything else `observe()` should read: residual relations the program holds and acts on later, a store of values. Rendered, not counted |
| `cp.problem_alternatives(name, obj)` | register a structure whose entries are the problem's own alternatives (`METRICS.md`: P05's values of x still held, P12's partial sequences, P15a's interleavings); counted into `alternatives.problem_defined[name]` |
| `cp.relations(name=function, ...)` | name the functions that **transcribe the problem's relations**, one function per relation; in cost mode each call of each is counted (`problem_operations[name]`). For P12, a relation registered as `accept` also gives `candidates_examined` |
| `cp.computation(name, function)` | register the function a spawned computation runs (P09, P16b), under its name in `stages.json` (`A`, `B`, `C1` … `C4`). The harness calls `function()`, with no arguments, when it spawns it |

Registrations made by a spawned computation's thread belong to that
computation; all others belong to `main`. Registering a name again
replaces the earlier object.

### 3.3 Stages

The program receives stages in a loop, and handles stage k when, and only
when, `cp.stage()` returns it:

    while (s := cp.stage()) is not None:
        if s.k == 1:
            ...   # the information of stage 1
        elif s.k == 2:
            ...

- **No anticipation.** The program is told nothing of later stages, nor how
  many there are; code for stage k may not depend on them (`PROTOCOL.md`,
  rule 5).
- **Replay.** In a reposed run, `cp.stage()` returns 1, 2, … k−1 with
  `replay` true, then k with `replay` false, in one fresh process. The
  program carries out **every** replayed stage, replacements and
  withdrawals included, and takes a replayed commit stage as x = v from
  `s.commitment`. An incremental program needs nothing extra for this: the
  harness reposes it after an error or a timeout.
- **Where a stage's work happens.** Only between `cp.stage()` returning k
  and the next call of `cp.stage()`. Steps before the first call (defining
  functions, registering) count in stage 1's budget and steps.
- **Answers** are collected for the computation that calls `cp.answer()`, if
  that computation has a query in the stage, up to the cap (1 for an *any
  one* query, 20 otherwise, from `stages.json`). Python has no mechanism for
  asking for more: what the program reports is all there is
  (`ended_by: "no-enumeration"`). Answers beyond the cap are printed but not
  collected (`ended_by: "cap"`, counted in the notes). Printing with
  `print()` is not answering: it appears in `stdout` and `print`, never in
  `answers`.
- **Ending a stage.** For `main`, by calling `cp.stage()`. For a spawned
  computation, by returning from its function. A thread the program starts
  (stdlib-concurrency) belongs to the computation that started it: its
  instructions count there, and its answers are that computation's. The
  harness does not wait for it.

### 3.4 Spawned computations (P09a, P09b, P16b)

After main's part of a spawning stage, the harness spawns each computation
in `stages.json` order (the instance's `spawn_order` for P09a), by calling
the function the program registered with `cp.computation()`, in a thread
the runtime starts in the same interpreter: one database (the program's
module and every object in it), never another process.

- **core, extended**: the first runs to its end, its budget, or quiescence,
  then the next is started (`side_by_side: false`).
- **stdlib-concurrency**: all are started at once and run side by side
  (`side_by_side: true`); `spawn()` returns at once.

Each has its own budget, from its start, and its own execution state,
steps and registrations. A name the program did not register is recorded
as spawned, with an undetermined state and a note. All three configurations
let spawned computations share unknowns (they share every object), so
P16b's `spawn_fallback` is never used.

### 3.5 What observe() reads, and the execution state

At the end of each stage (and, for a computation stopped by its budget, at
the moment it stopped), the runtime reads every registered object of every
computation of the stage and writes `observe.raw` as one line per object:

    main.bindings = {'a': 3}
    main.suspended[waiting relations] = ['s = a + b']
    A.pending[frontier] = [(1, 2), (2, 1)]

Each object is rendered exactly as `repr()` renders it, computed iteratively
for `list`, `tuple`, `dict`, `set` and `frozenset` (so deep nesting does not
fail), and by `repr()` itself for any other object (a `repr()` that fails is
a harness fault, recorded). `observe.bindings` is the bindings mapping split
by key (`A:x` for a spawned computation's), each value so rendered.
**Nothing unregistered is read**, and nothing is ever inferred from the
posed information: a residual the program holds but did not register is not
reported.

The execution state of each computation, as far as the harness can tell:

| state | when |
|---|---|
| `budget` | its thread was paused at exactly its budget |
| `timeout` | the safety limit stopped the process before it ended its part |
| `error` | an uncaught exception ended it (its traceback, as the interpreter prints it, is `error_verbatim`), or the interpreter process died (signal, exit status and stderr) |
| `alternatives pending` | its registered pending structures hold entries |
| `suspended` | its registered waiting structures hold entries, or it was quiescent (then `determined: false`: section 6) |
| `finished` | none of the above |

## 4. What each mode measures

The step meter (budget and count) runs in every mode (common QUESTIONS.md,
Q17); everything else only where shown.

| mode | recorded | how |
|---|---|---|
| all | steps: `stage` (incremental cost), `restated`, `to_end`, `restart_cost`, `to_first_answer`, `between_answers`, `steps_at` per answer; alternatives and suspended at the boundary and at budget, from the registrations | `sys.monitoring` INSTRUCTION events, global, one tool; counted per computation thread; the runtime's own code and everything a thread runs inside an H call excluded |
| cost | `problem_operations` per registered relation, `candidates_examined` (P12) | `sys.monitoring` PY_START local events on each registered function's code object (systems file, method C) |
| storage | `store.quantities`: `traced_bytes` (current at the boundary, exact peak), `traced_bytes_at_window_start`, `allocated_blocks`, `allocated_blocks_at_window_start`; `alternatives_at` per answer; suspended generator frames, coroutines and async generators | `tracemalloc` (1 frame) started before the program runs, peak reset at the start of each budget window; `sys.getallocatedblocks()`; `gc.get_objects()` after `gc.collect()`, process-wide |
| behaviour, cost; P13 only | `cpu_time_s`, `max_rss_kb` | `resource.getrusage(RUSAGE_SELF)` in the program's process at the end of the stage (KiB on Linux), tracemalloc off, one process per stage (P13 has one stage) |

- **Step**: one CPython 3.13.7 bytecode instruction executed in Python code
  (`step_unit` in the record). Work inside built-ins is not counted.
- **Budget**: 10⁶ instructions per stage and computation (10⁸ for P12, P13,
  P16), from the start of the stage's window: the program's start for
  stage 1 or a new process, the posing of stage k otherwise, the release
  for a continued stage. A reposed stage's budget is its restart cost plus
  10⁶ (10⁸). When the next instruction would exceed it, the computation's
  thread waits inside the monitoring callback, so the count is exactly the
  budget and nothing in the program can catch or delay it. A loop inside
  one C call executes no instruction and is stopped only by the safety
  limit.
- **Restart cost**: measured in-run: main's instruction count at the moment
  stage k is first given to the program in a reposed run, after the replay
  (`restart_cost_method: "in-run"`). If the replay itself is stopped (by a
  replayed stage's budget, an error or the safety limit), stage k is never
  posed, and the restart cost is the replay's whole count (QUESTIONS.md, Q4).
- **Repeated work**: `null`; the systems file names only problem operations
  counted by the program, which `problem_operations` reports per stage.
- **Alternatives**: the registered pending structures' entries
  (`by_type` by name), never a peak (none is recorded by the harness);
  `held_as` is `unknown` (the classifiers decide from the program), or
  `none` when nothing is registered.

## 5. Stopping a system at the safety limit

The safety limit (60 s, rerun 600 s; 600 s fixed for P12, P13, P16) is
timed by `run`. When it runs out, `run` sends **SIGKILL** to the program's
interpreter process (`safety_limit.how_stopped`), keeps the answers it had
collected, and records `timeout` for every computation that had not ended
its part. The process is gone, so the rerun of stage k is a reposed run of
1 … k (stage 1: a fresh run) under the raised limit, and the next stage
after a final timeout is reposed (`after-timeout`).

## 6. Quiescence

A Python thread waiting on a lock, an event or a queue executes no
instruction, and would otherwise only end at the safety limit. The runtime's
watcher samples, every 0.1 s, the instruction counts of the computations
that are running their part of the stage; if **all** of them are alive and
none has executed an instruction over five consecutive samples (0.5 s), it
reports them quiescent, with each thread's innermost Python frame. The
harness then takes their part of the stage as ended and records them
`suspended`, `determined: false`, with that frame as the basis: the harness
cannot tell mechanically whether the thread waits for information or is
inside a C call that released the interpreter lock. A blocked computation
that later runs again is not resumed by the harness; it may be by the
program's other computations.

## 7. H tokens

The H class (`METRICS.md`, rule 13; common contract, section 11) for a
Python program, construct by construct:

1. The stage loop's header, `while (s := cp.stage()) is not None:`, or any
   statement whose only role is to call `cp.stage()` and bind or test its
   result.
2. The tests that dispatch on the stage number (`if s.k == 1:`, `elif s.k ==
   2:`, the comparison, its keyword and colon; not the statements inside).
3. Reading `s.replay`, `s.commitment`, `s.constants[...]`, `s.params[...]`, `cp.params[...]`, and
   the tests on `s.replay` whose only effect is to print or answer nothing
   during a replay.
4. Every call of `cp.answer(...)`, `cp.emit(...)`, `cp.bindings(...)`,
   `cp.pending(...)`, `cp.suspended(...)`, `cp.held(...)`,
   `cp.problem_alternatives(...)`, `cp.relations(...)` and
   `cp.computation(...)`, with their arguments when an argument only names
   an object or renders one for printing.
5. **Output adapters** (`METRICS.md`, rule 13): code whose only effect is to
   render, for `cp.answer()` or `print()`, an answer already computed (an
   iterative printer of a nested sequence, a format string).

Not H: what a program does with `s.commitment` beyond taking it as x = v
(classed by the rules), the bodies of stages and of spawned computations,
the definitions registered with `cp.relations` and `cp.computation`, and any
code that decides which result is reported. The `CP-POSING`, `PROVENANCE`,
`CONSTANTS BEGIN`/`END` and `# stage k` lines are comments and are not
tokens; the block's entries are the stages' information, classed by the
rules (not H), though the program never executes them.

## 8. A complete example, for a made-up problem

**X01a** (made up, not in the suite): *stage 1:* s = a + b; *stage 2:*
a = ⟨k⟩; *stage 3:* b = ⟨k⟩; the query at each stage: the values of s.
The program holds the relation until both values have arrived. It is
[`qualification/programs/x01_total.py`](qualification/programs/x01_total.py):

```python
# CP-POSING: incremental
#
# PROVENANCE
#   author: harness-python (an agent), as the README's example; not a study program
#   seen a precursor (absys E01-E09): no
#   idioms: the Python Language Reference (assignment expressions, dict, list)
#
# Made-up problem X01a: s = a + b is stated at stage 1, a arrives at stage 2,
# b at stage 3; the query at each stage is the values of s.

# CONSTANTS BEGIN
# stage 2
A_VALUE = 3
# stage 3
B_VALUE = 4
# CONSTANTS END

known = {}       # the bindings the program holds: unknown name -> value
waiting = []     # relations held until their values arrive

cp.bindings(known)
cp.suspended("waiting relations", waiting)


def plus(x, y):  # the relation s = a + b, evaluated when a and b are known
    return x + y


cp.relations(plus=plus)


def decide():
    for rel in list(waiting):
        if rel == "s = a + b" and "a" in known and "b" in known:
            known["s"] = plus(known["a"], known["b"])
            waiting.remove(rel)


while (s := cp.stage()) is not None:
    if s.k == 1:
        waiting.append("s = a + b")
    elif s.k == 2:
        known["a"] = s.constants["A_VALUE"]
    elif s.k == 3:
        known["b"] = s.constants["B_VALUE"]
    decide()
    if not s.replay and "s" in known:
        cp.answer("s = %d" % known["s"])
```

What the harness records for it (from the qualification, core, behaviour):

| stage | answers | state | observe.raw |
|---|---|---|---|
| 1 | none (`no-enumeration`) | suspended (1 waiting relation) | `main.bindings = {}` / `main.suspended[waiting relations] = ['s = a + b']` |
| 2 | none | suspended | `main.bindings = {'a': 3}` / … `['s = a + b']` |
| 3 | `s = 7` | finished | `main.bindings = {'a': 3, 'b': 4, 's': 7}` / … `[]` |

With `# CP-POSING: reposed` the same text gives the same answers and the
same observations, each stage in a new process replaying the ones before it
([`x01_total_reposed.py`](qualification/programs/x01_total_reposed.py)).
Its constants are delivered with stages 2 and 3; at stage 1 neither value
is in the program's process. Its H constructs are the loop header, the
three `s.k ==` tests, the two `s.constants[...]` reads, the `s.replay` test, and the calls `cp.bindings`, `cp.suspended`,
`cp.relations` and `cp.answer` with the format string.

## 9. check

`harnesses/python/check CONFIGURATION PROGRAM` is the only thing a program
author may run before the program is fixed. In every configuration it:

1. reads the file's bytes and calls `compile(source, path, "exec",
   dont_inherit=True)`, which parses and compiles and executes nothing;
   syntax errors are printed verbatim as the interpreter formats them
   (`traceback.format_exception_only`), and compile-time warnings
   (`SyntaxWarning`) verbatim;
2. reads the syntax tree (`ast.parse`) and reports, as errors: a missing or
   invalid `CP-POSING` line; a malformed constants block (parsed by the same
   `constants.py` as `run`): anything but assignments of literals to names,
   an entry before any `# stage k` line, a name given twice for one stage;
   a block constant's name used outside the block (it does not exist when
   the program runs); a use of `open`, `__file__`, `__loader__`, `__spec__`,
   or an import of `linecache`, `inspect`, `tokenize`, `pathlib`, `io`,
   `runpy` or `importlib` (reading files or source, where every stage's
   constants are); an import of `threading`,
   `queue` or `asyncio` outside stdlib-concurrency; a `cp.` name that is not
   in section 3.2; a program that never calls `cp.stage()`. Other imports
   are listed as external mechanisms.

It never imports, executes or poses anything, writes no file, and prints
nothing the program would compute; the qualification shows that a checked
program whose only effects are writing a file and printing a marker leaves
neither. The three configurations differ only in the import rule. Errors
that only a run reveals (a `NameError`, a wrong stage) cannot be found
without executing, and `check` does not look for them.

## 10. Confounds

Everything this harness does beyond passing stages in, collecting answers
and reading state. Each record copies this list into `run.confounds`.

1. The runtime runs inside the program's interpreter process (the meter and
   the program's objects can only be read there). It imports `marshal`,
   `os`, `sys`, `threading` and `time` (and, through `threading`,
   `_collections`, `_weakrefset`, `itertools`, `types`, `warnings`) before
   the program starts, so a program's own import of these runs no module
   code and counts no instructions.
2. The program's module is `exec`'d under three runtime frames, not run as
   the interpreter's own script: about three fewer frames are available
   before `RecursionError` at the default limit.
3. Two runtime threads (control and watcher) run beside the program in every
   configuration; neither runs program code (except finalizers run by
   `gc.collect()` in storage mode) and neither is counted.
4. The budget counter is the step meter, in every mode, behaviour included
   (common Q17); a computation is stopped at its budget by pausing its
   thread inside the monitoring callback, never by an exception.
5. The instructions of the program's own H call sites (loading `cp`, the
   attribute, the call) are counted as the program's; those executed inside
   the H calls are not, nor those of the traceback module while it formats
   an uncaught exception (instruction events are switched off then if no
   other computation is running; a thread the program started that is still
   running is not counted meanwhile).
6. Spawned computations run in threads the runtime starts; in core and
   extended one after another.
7. The end of a stage is read from the program (its next `cp.stage()`, its
   end, its budget, its error) or from quiescence, which depends on
   wall-clock sampling (section 6).
8. Answers are what the program passes to `cp.answer()`, which prints them;
   answers after the cap are printed but not collected.
9. `observe()` reads only registered objects, rendered by an iterative
   equivalent of `repr()`; the states *alternatives pending* and
   *suspended* come only from registrations.
10. In storage mode tracemalloc traces the runtime's own allocations during
    the stage with the program's, and `gc.collect()` runs at each boundary.
11. Standard output and standard error are files; the runtime flushes them
    at every boundary.
12. P13's CPU time and resident set are the whole interpreter process's,
    runtime threads included.
13. A thread a program starts with `_thread.start_new_thread` directly, not
    through `threading.Thread`, is not attributed to any computation and its
    instructions are not counted.
14. The program is compiled from its text with the constants block's lines
    emptied, and its constants are given to it as `s.constants` with their
    stage; tracebacks show that text, not the file on disk.
