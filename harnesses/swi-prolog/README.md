# The SWI-Prolog harness

*Phase 4, wave 1, against `spec-1.0` and the common contract in
[`../README.md`](../README.md). Written by the SWI-Prolog harness author,
who wrote no problem program and used no problem's constants. Where the
common contract or the specification could not be implemented as written,
the reading taken is in [`QUESTIONS.md`](QUESTIONS.md).*

| file | what it is |
|---|---|
| `run` | the harness: `run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR` (the common command line). Python 3 (the image's Debian `python3` 3.13.5), the driver only |
| `lib/harness.pl` | the harness's Prolog side, loaded into every `swipl` process before the program: posing, answers, observe(), print(), the budget, the H predicates |
| `check` , `lib/check.pl` | `check CONFIGURATION PROGRAM`: a syntax and static check that executes nothing (section 14) |
| `S/session-wait.pl` | the *session* configuration's supporting code (S), listed in [`S-mechanisms.md`](S-mechanisms.md) |
| `qualification/` | the evidence that the harness does what this file says ([`qualification/README.md`](qualification/README.md)) |

Everything runs inside the pinned image, never on the host:

    container run --rm --platform linux/amd64 --volume REPO:/work --workdir /work \
        cp-agent-swi-prolog:spec-1.0 harnesses/swi-prolog/run plain P01 P01a behaviour PROGRAM OUTDIR

The image is the pinned `swipl:11.0.1` (`PINS.md`); `run` uses only
`/usr/bin/swipl` (SWI-Prolog 11.0.1 for x86_64-linux), `python3`, and
`git` (to record the harness commit). It installs nothing. Environment
variables it reads, all optional: `HARNESS_IMAGE_DIGEST` (the image
digest, from the launcher; else `CP_IMAGE_DIGEST`; else the pinned
`swipl:11.0.1` index digest of `PINS.md`,
`sha256:b51af487f3306fe240eae8c13159c85b5526509952e1b949cc22f48a1f82a742`,
which is what `system_build.image` then records), `CP_PURPOSE` (`primary`,
the default, `variant` or `qualification`), `CP_VARIANT` (the hidden
variant's id, for the verifier), and, for the qualification only,
`CP_SWI_STAGES` (a made-up stages file instead of `harnesses/stages.json`;
recorded in the record's `notes`). Exit status as the common contract
says: 0 a valid record was written, 2 usage error (no record), 3 the
harness failed (the record is kept as `<run_id>.INVALID.json`).

## 1. Configurations, posing and modes

From `systems/swi-prolog/README.md`:

| configuration | adds to plain | posing (`run.posing`) | a new computation is |
|---|---|---|---|
| `plain` | nothing | reposed | a fresh `swipl` process per stage attempt |
| `tabling` | `:- table` | reposed | the same |
| `coroutines` | `when/2`, `freeze/2`, `dif/2` | reposed | the same |
| `constraints` | coroutines, `library(clpfd)`, `library(clpq)` | reposed | the same |
| `session` | constraints, engines, and S code that waits for an undefined procedure | incremental | one engine in one `swipl` process holds the computation; each stage is posted into it |

Every configuration has all three modes (`behaviour`, `cost`, `storage`;
the systems file restricts none). A fresh process per stage gives every
reposed run the same load sequence, autoload state and empty database
(`measurement.md`, "Fixed run conditions"), and makes the reposed run a
new computation: anything a program asserted is gone.

`swipl` is always started as `swipl -f none --no-tty -q -g
cp_harness:h_main(CTL) -t halt(4) harnesses/swi-prolog/lib/harness.pl`:
no init file, not in debug mode, `optimise` false (the default), `gc`
true, the default 1 GB stack limit, `occurs_check` false and `unknown`
error (SWI's and ISO's defaults; a program that is the systems file's
recorded variant sets them itself by a directive, which the record shows
in the `loaded` flags). Standard input is `/dev/null`.

## 2. The program contract

A program for SWI-Prolog is **one Prolog source file**, loaded into module
`user` with `load_files/2` (so: no `:- module` declaration), **without its
CONSTANTS block**: the driver blanks the block's lines (so line numbers
stay the same) and loads that copy; the block never reaches the system as
program text (§ 2.5). It may load
libraries with `:- use_module(library(...))` directives, and must for
operators such as clpfd's. After loading, the harness calls
`autoload_all/0` (and restores the `autoload` flag it switches off), so
that no library is autoloaded while a stage is measured. Directives run
when the file is loaded, before any stage; they must not pose stages or
print answers. A program must not read standard input, define a module,
or define any of the H predicates below or `'$cp_query'/1`.

### 2.1 What the program defines

| predicate | meaning | class |
|---|---|---|
| `unknowns(Computation, Names)` | for each computation (`main`, or a spawned computation's id as `stages.json` names it, e.g. `'A'`), the names of its unknowns, a list of atoms that are Prolog variable names (`['X', 'Y']`). Use the sub-problem's unknowns from `stages.json`, capitalised, or names that hold several of them (`'Xs'`). The harness makes one fresh variable per name, and the answers are rendered with these names. | H |
| `stage(K, Vars, Constants)` | the information of stage K, as a goal over `Vars`, the list of `main`'s unknowns in the order of `Names`. `Constants` is the list of the CONSTANTS block's entries for stages 1 … K, in the block's order (§ 2.5): the only way a constant reaches the program. One clause (or several) per stage number. Stage K's code may not depend on any later stage (rule 5), and cannot see a later stage's constants. | head H; body P/C/R/S by `METRICS.md` |
| `query(K, Vars)` | the query posed after stage K, over the same `Vars`: usually `query(_, _).` (the stages' goals bind the unknowns themselves); for a problem whose stages replace or withdraw named quantities held in the database (`assertz/1`, `retract/1`), the goal that reads them (`query(_, [V]) :- v(V).`). Must be defined. | head H; body classed |
| `spawned(K, Computation, Vars, Constants)` | only where stage K spawns computations (P09a, P09b): the goal of that computation, over its own unknowns, with stage K's constants as for `stage/3` | head H; body classed |

The harness numbers stages 1 … K as `stages.json` does (P16d2's two stages
are 1 and 2). It never passes a constant: the program holds every stage's
information.

### 2.2 How a stage is posed

**plain, tabling, coroutines, constraints (reposed).** For stage k the
harness starts a fresh process, loads the program, and compiles one clause

    '$cp_query'(Bindings) :- h_m(1), stage(1, Vars, C1), h_m(2), stage(2, Vars, C2), …, h_m(k), stage(k, Vars, Ck), query(k, Vars).

where Cj is the list of the block's entries for stages 1 … j.

and runs it as a query. Stages 1 … k−1 are thereby replayed **in order,
every one of them**, replacements and withdrawals included: the program
carries them out (`PROTOCOL.md`, pose). `h_m(J)` is the harness's stage
mark: on the first entry into stage J's part it records the step count
(for stage k: the in-run restart cost) and gives stage J its budget (§ 9);
on every entry it records which stage's code is running (for `emit/1`).
Its inferences are excluded from the steps.

**session (incremental).** One process; the harness creates one engine
whose goal is the harness's loop, and for each stage posts the message
`stage(J, …)` with `engine_post/3`. Inside the engine the posted stages
form one growing conjunction, `stage(1, Vars, C1), …, stage(L, Vars, CL)`, L
the latest stage posted: the engine marks and calls `stage(J, Vars, CJ)`, and when
the computation reaches the end of stage L it yields to the harness and
waits for the next message. If the computation later backtracks into an
earlier stage and comes forward again, the stages after it that were
already posted are called again from the harness's record, without a new
message, as in any conjunction. `query(K, Vars)` is called only where the
answers are collected (§ 3). A stage after a stage that ended in budget,
error or timeout, or after the engine's computation failed (no solution
left, so nothing can receive the next stage; `QUESTIONS.md`, S3), starts a
new engine in a new process, into which stages 1 … k−1 are posted again
(`posed.how = reposed`, replayed), and then k, k+1, … incrementally.

In *session* the configuration's supporting code (`S/session-wait.pl`)
is loaded before the program: a call of a procedure that has no
definition waits, in the engine, until a later stage defines it (as
`h_wait/0` does), instead of raising the existence error.

**Spawned computations** (P09a, P09b): `spawned(1, C, Vars, C1)` for each
computation C in the instance's `spawn_order`, each as a separate query in
the same process (sharing its database), with its own budget, run to its
end or its budget before the next (`side_by_side: false`), in every
configuration. **P16b**: no SWI-Prolog configuration lets separate
computations share unknowns (a separate query, or an engine, copies its
goal), so P16b's stage 1 is always posed as one conjunction in `main`
(`spawn_fallback`): the program's `stage(1, Vars, C1)` is the conjunction of
the four contributions.

### 2.3 The H predicates a program may call

All are exported by the harness into `user`. Their inferences, call
port included, are excluded from the steps and the budget (§ 9), so a
program's steps are the same with and without them (qualification, "H
calls").

| call | what it does |
|---|---|
| `h_param(Name, Value)` | the instance's parameters, as `stages.json` gives them: `n`, `order` (a list of atoms, e.g. `['R2','R1','R3']`, `['312']`… as written there), `answers` (`all`, `'any-one'`), `cap`, `spawn_order`. Fails for a name the instance does not have |
| `h_commitment(V)` | in the code of a commit stage (P11c stage 3, P11d stage 2): succeeds, with V the string the commit stage first reported (the verbatim answer, e.g. `"X = 1 "`), when that stage is being replayed in a reposed run with a selected value; fails otherwise (when the stage is first posed, or nothing was selected). The program turns V into its information x = v itself (for instance `term_string(T, V, [variable_names(Bs)])`) |
| `emit(M)` | P11's effects stub: appends one entry to the effects log, M rendered with `answer_write_options` (`~W`), and returns. It does nothing else, never fails |
| `h_count(Name)` | one application of a case of a relation the problem defines, counted under `Name` (`'conc/1'`): `problem_operations` |
| `h_candidate` | P12: one sequence for which accept(s) is evaluated: `candidates_examined` |
| `h_held(Name, Count)` | problem-defined alternatives held now (P05's values of x, P12's partial sequences, P15a's interleavings); the last value at the stage's end is recorded in `alternatives.problem_defined` |
| `h_wait` | session only: the computation waits here for the next stage. The harness records the stage as ended with the computation waiting (*suspended*); when it posts the next stage, `h_wait` receives it into this computation (marks it and calls its `stage/3`) and returns. Outside session it raises a permission error |

### 2.4 Answers

Answers are the solutions of the posed query, collected by backtracking,
the system's standard mechanism: the harness asks for the next solution
only while the previous one left choicepoints and fewer than `cap`
answers have been collected, exactly as the toplevel offers `;` only for a
nondeterministic answer. Each answer is recorded **as the toplevel renders
it**: the harness calls the toplevel's own `'$toplevel':translate_bindings/4`
and `name_vars/3` and formats the `query(yes(…))` message (an answer
without choicepoints, ending `.`) or the `query(more(…))` message (one
with), with the toplevel's `answer_write_options` except `max_depth(0)`
for `max_depth(10)`, so that nothing is elided. Residual goals (freeze,
dif, clpfd, …) appear as the toplevel shows them; cyclic terms in the
toplevel's `% where` form. The rendering happens under `\+ \+`, so it binds
nothing. For a made-up stage the qualification checks the texts against
the real toplevel's output byte for byte.

A program reports answers only through its unknowns: anything it prints
is recorded in the stage's `stdout`, verbatim, but is not an answer.

`ended_by`: `exhausted` when the last request failed, or the last answer
had no choicepoint; `cap`; `budget`; `error`; `timeout`. In session, at a
stage that is not the instance's last, answers are collected on a
**separate run** of stages 1 … k (a fresh process and engine, stages 1 …
k−1 posted as replay, then k with its query; `collected_on:
separate-run`), because backtracking for further answers would consume
the incremental computation that the next stage extends (common contract,
section 4). At the instance's last stage nothing extends the computation,
and its answers are collected in it. A separate run's effects go to the
observation log.

### 2.5 Constants

Every constant of every stage is in **one marked block** of the file,
between a comment line containing `CONSTANTS BEGIN` and a comment line
containing `CONSTANTS END`. Inside it each entry is a Prolog fact, and
each entry is **tagged with the stage that first uses it**: a comment line
`% stage K` starts the entries of stage K, the stages in increasing order,
and nothing but comments and blank lines comes before the first. A stage
that adds no constant has no section. For example:

    % CONSTANTS BEGIN
    % stage 1
    colour(red).
    colour(green).
    % stage 3
    first_colour(green).
    % CONSTANTS END

The verifier replaces the block and nothing else; the program must stay
correct for other constants (rule 6).

**No anticipation, made structural** (rule 5). The block is never loaded
as program text: the driver reads the file, splits the block by its
`% stage K` lines, and loads the program with the block's lines blanked.
A stage's entries reach the system only when that stage is posed: in a
reposed configuration, the process that poses stage k is given the
entries of stages 1 … k and no others (stage 1's process holds nothing of
stage 2's, as text or as terms); in *session*, stage k's entries are sent
with the command that posts stage k, and only then read. They reach the
program only as the last argument of `stage(J, Vars, Constants)` (and of
`spawned/4`): the list of the entries of stages 1 … J, read as terms when
stage J's goal is built or posted, and again on every replay. A program
that needs them as clauses asserts them itself in the stage that brings
them (`forall(member(E, Cs), assertz(E))`, with a `dynamic` declaration);
that is the program's code. The qualification checks that at stages 1
and 2 nothing of stage 3's constant is among the process's atoms or
strings, and that at stage 3 it is (`programs/xlate.pl`).

`run` records `constants.how = block` when it finds one such block, and
`none` when it finds none (a sub-problem without constants: P04d, P04f,
P08b). A malformed block (two pairs, entries before any `% stage K`,
stages not increasing) is a usage error (exit 2), and `check` reports it.
Sizes and orders are not constants: they come from `h_param/2`.

### 2.6 Provenance

At the top of the file, a comment block

    % PROVENANCE
    %   author: <the program's author, human or agent>
    %   precursor seen: <yes / no: whether the author had seen the absys E01-E09 programs>
    %   idioms: <the source of each idiom: manual section, paper, published program>
    % END PROVENANCE

`check` reports whether it is present.

### 2.7 A complete minimal example

A made-up problem X01, not one of P01–P16 (`qualification/stages-made-up.json`):
two unknowns a and b, the stripes of a flag; stage 1, a is a colour;
stage 2, b is a colour other than a's; stage 3, a is the given first
colour. All answers (cap 20).

```prolog
% Made-up problem X01 (not one of P01-P16): the two stripes of a flag.
% Stage 1: stripe a is a colour. Stage 2: stripe b is a colour other than
% a's. Stage 3: a is the given first colour.
%
% PROVENANCE
%   author: harness-swi-prolog (the harness author), for the qualification
%   precursor seen: none (a made-up problem)
%   idioms: conjunctive queries, ISO Prolog; member/2 and memberchk/2 of
%   library(lists) over the stage's constants
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
colour(red).
colour(green).
colour(blue).
% stage 3
first_colour(green).
% CONSTANTS END

unknowns(main, ['A', 'B']).

stage(1, [A, _], Cs) :- member(colour(A), Cs).
stage(2, [A, B], Cs) :- member(colour(B), Cs), B \== A.
stage(3, [A, _], Cs) :- memberchk(first_colour(A), Cs).

query(_, _).
```

Stage 1 receives `[colour(red), colour(green), colour(blue)]`, stage 2 the
same, stage 3 that and `first_colour(green)`; the processes that pose
stages 1 and 2 never see `first_colour(green)`. In *plain*, stage 3 is
posed as `stage(1, V, C1), stage(2, V, C2), stage(3, V, C3), query(3, V)`
in a fresh process; its answers are recorded as `"A = green,\nB = red "`
and `"A = green,\nB = blue "`, `ended_by: exhausted`, state *finished*.
The same file runs in every configuration; in *session* stages 1 and 2
take their answers from separate runs and stage 3 from the engine itself.
[`qualification/programs/`](qualification/programs) holds the other
made-up programs, among them `x02-commit.pl` (emit/1 and h_commitment/1),
`x03-spawn.pl` (spawned/4), `x09-count.pl` (h_param/2, h_count/1,
h_held/2), `x11-replace.pl` (a replacing stage, with query/2) and
`x08-wait.pl` (h_wait/0).

## 3. observe() and print()

**observe()** reads, at the end of the stage, the state the computation
holds, verbatim (`observe.raw`):

- where the computation is still at an answer (the last answer had
  choicepoints and the cap stopped collection, or it had none): the
  toplevel's rendering of the bindings and residual goals held there;
- in session, at a stage whose answers come from a separate run: the
  incremental computation's own state at the end of the stage, read in the
  engine without consuming it (`taken_on: this-run`);
- at the moment the budget runs out, or an error reaches the harness,
  before the stacks unwind: the same rendering, read in
  `prolog:prolog_exception_hook/5` (the exception is not changed, and the
  program's own `catch/3` of it is respected: only an exception that
  reaches the harness is reported);
- at the safety limit: the same, read by the harness's SIGUSR1 handler (§ 10);
- where the last request failed (exhausted): nothing is held, `raw` is
  empty, and `method` says so.

`observe.bindings` splits the rendering by unknown (the toplevel's
`binding(Names, Value, _)` groups); an unknown that only has residual
goals has no entry. Beside it the harness reads `term_attvars/2` of the
unknowns and the number of `copy_term/3` residual goals (`suspended`), and
in storage mode the retained choicepoints and the store (§ 8).

**print()** is the toplevel's transcript of the answers: each answer's
text, `;\n` between answers when another was requested, and `false.` when
the last request failed. For a session stage whose answers come from a
separate run, it is the rendering of what the incremental computation
holds.

## 4. Execution state

Per computation, after `answers()` (on the separate run, where answers
were taken there; `QUESTIONS.md`, Q14 of the common part), with `basis`:

| state | when |
|---|---|
| `budget` | `inference_limit_exceeded` reached the harness (§ 9) |
| `error` | another exception reached the harness's `catch/3`; `error_verbatim` is SWI-Prolog's message for it, then `% term:` and the term |
| `timeout` | the safety limit stopped the attempt |
| `alternatives pending` | collection stopped at the cap with choicepoints newer than the query's mark (a request for more would resume it) |
| `suspended` | at the last answer, attributed variables are reachable from the unknowns (`term_attvars/2`: freeze, when, dif, clpfd, clpq goals held); or, in session, the computation waits in `h_wait/0` |
| `finished` | none of these: the goal exited without choicepoints and holds no attributed variable, or the last request failed |

The incremental computation's own state, where answers came from a
separate run, is in the attempt's `notes`.

## 5. Steps (the H class's cost)

The step is one inference (`statistics(inferences)`), as the systems file
qualifies it. **A program's steps are the inferences of its own goals**:
from the call of `stage(1, Vars)` to the end of the stage, every call and
redo port of the program's code (the program's S code included), and
none of the harness's: the stage marks, the answer points, observe(), the
H predicates (their call ports included), the storage sampler, the
exception hook. Each piece of harness code that runs inside the
computation runs *paused*: it reads the counter when it starts and when
it ends and adds what it spent, plus the few inferences around those two
readings, to an exclusion counter. The qualification shows that this is
exact: for made-up programs the steps the harness reports at the first
answer, at every answer and at the end equal the systems file's
measurement, the `statistics/2` difference minus one around the posed
goals (and, in *plain*, its other one, the smallest limit under which
`call_with_inference_limit/3` lets them reach that point; outside *plain*
the two differ, `QUESTIONS.md`, S16); behaviour, cost and storage runs report the
same steps; and a program with `h_count/1` calls has the same steps as
without them.

Figures (`steps`): `restated`, the steps from the start of the run to the
end of the stage (for a reposed stage, the replay included); `restart_cost`,
for a reposed stage, the steps when stage k was first entered, after the
replay (`restart_cost_method: in-run`); `to_first_answer`, `steps_at`,
`between_answers` and `to_end` are counted **from the posing of stage k**
(after the replay; for an incremental stage, from the end of stage k−1);
`stage`, for an incremental stage, the steps from the end of stage k−1 to
the end of stage k. `repeated_work` is null: the systems file measures it
only by the program's problem-operation counters (`h_count/1`). Steps are
recorded in every mode; the figures of record are the cost run's.

## 6. Modes

| mode | instrumentation |
|---|---|
| behaviour | the budget counter and the stage marks only |
| cost | the same: step counting is the budget counter itself (`steps_at` at every answer) |
| storage | in addition: retained choicepoints at each answer, at the boundary and at the budget; the store vector at the boundary after `garbage_collect/0`; except in *tabling* (`QUESTIONS.md`, S17), a heartbeat sampler (`heartbeat` flag every 1008 inferences) keeping sampled maxima of choicepoints and global/local/trail use in `flag/3` |

All storage-mode readings are paused, so storage steps equal behaviour
steps, but they move garbage collection, memory layout and where the
heartbeat falls, so the store is taken only from storage records and the
step count never from them. P13 records `cpu_time_s` and `max_rss_kb`
(the process's, from `wait4`) in behaviour and cost runs, where there is
one stage per process; null otherwise.

## 7. Alternatives and suspended work

`alternatives` is in the systems file's unit, **retained choicepoints**:
choicepoint frames newer than the mark taken where the computation's query
starts (so the harness's own frames are excluded), counted by walking
`prolog_choice_attribute/3`, by type, exactly as the systems file's probe
`cpcount.pl` does, at each answer before the next is requested
(`alternatives_at`), at the boundary, inside the exception hook when the
budget runs out (`at_budget`), and as a sampled maximum (`peak.kind:
sampled`, storage only). `held_as: backtracking`. After an exhausted query
none are held (`at_boundary: 0`). Problem-defined alternatives come from
`h_held/2`. `suspended`: attributed variables reachable from the unknowns
and residual goals, at the boundary, in every mode; in session an engine
waiting in `h_wait/0` is one item.

## 8. Store

Storage mode, at the stage boundary (where the computation still holds
its last answer, or after the query failed), after `garbage_collect/0`:
`global_live_bytes` (`statistics(globalused)`), `local_bytes`,
`trail_bytes`; *tabling*: `table_space_used_bytes`, `tables` and
`table_answers` (`current_table/2`, `trie_property/2`); *coroutines*,
*constraints*, *session*: `attributed_variables`, `residual_goals`. Each
with a sampled maximum where the sampler covers it (garbage included for
global; never called a peak), and the same quantities read before the
computation started (`*_at_computation_start`, the harness's baseline).
In session the store is the engine's own stacks.

## 9. Budget

10⁶ inferences per stage and computation (10⁸ for P12, P13, P16), from
`stages.json`; a reposed stage has its measured in-run restart cost plus
that. The budget is the system's inference limit, set absolutely with the
predicates `call_with_inference_limit/3` is built from
(`'$inference_limit'/2`, `'$inference_limit_false'/1`): that predicate
itself restarts its limit for every solution, so it cannot bound a stage
that collects several answers. Every stage mark's first entry gives its
stage the budget from there; every paused piece of harness code lifts
the limit on entry and puts it back, moved on by what it spent, on exit.
While program code runs the limit stands 8 inferences (the most any
harness entry spends before lifting it) beyond the program's budget, and
**every harness entry checks the budget exactly**: if the program's steps
exceed it, it raises `inference_limit_exceeded` itself. So a stage is
*budget* exactly when its program steps exceed its budget (the
qualification: 5000 steps finish under a budget of 5000, 5001 do not),
and between harness entries the system's limit stops it at most 8
inferences late (recorded in `restated`). A program's own `catch/3` with
a variable catcher can intercept the exception, as with
`call_with_inference_limit/3`.

During a replay each replayed stage has the budget it had when first
posed. If the replay runs out of budget, or is stopped by the safety
limit, before stage k is posed, the restart cost is every step of the
replay, read when it stopped (`restart_cost_source` says so).

**After budget: no configuration can continue.** The limit aborts the
stage's goal (the exception unwinds it), so the exhausted computation
cannot be resumed; stage k+1 is posed by reposing stages 1 … k+1
(`reason: after-budget`). After error and after timeout, likewise.

## 10. Safety limit

60 s per stage attempt (600 s for P12, P13, P16, fixed), from the
problem's limits; one rerun at 600 s where allowed. For a reposed stage it
covers the whole process (load, replay, stage); for an incremental stage,
from posting the stage to its end. The driver stops the system by sending
**SIGUSR1**: at the next point where the virtual machine handles signals,
the harness's handler reads the step count and the state held (the
observation recorded at the timeout), reports them, and ends the process
with SIGKILL; if the process has not ended 3 s later the driver sends
SIGKILL (`safety_limit.how_stopped` says which). The stopped computation
is gone, so the rerun is a reposed run of stages 1 … k (attempt 2,
`safety-rerun`), and after a final timeout stage k+1 is reposed
(`after-timeout`).

## 11. Effects (P11)

`emit(M)` writes the entry, flushed at once, to a spool file of the
process, with the stage being posed, the attempt, and `during_replay_of`
(the stage whose code is running, when it is earlier than the stage being
posed in a reposed run; null otherwise). When the attempt (or, in
session, the stage) ends, the driver appends the spool's entries, in
order, to the log, with `seq` and `run_id`: the classification log
`OUTDIR/<instance>.effects.jsonl` for behaviour runs, the observation log
`OUTDIR/<instance>.effects-observation.jsonl` for cost and storage runs
and separate runs. With `OUTDIR` as the common contract gives it
(`results/swi-prolog/<configuration>/P11/raw/`), these are the paths it
names. Logs are never reset. A commit stage's first answer, verbatim, is
kept and passed back, by `h_commitment/1`, whenever that stage is
replayed.

## 12. H tokens

A program's H constructs, class H in `METRICS.md`:

- the heads of `unknowns/2`, `stage/3`, `query/2` and `spawned/4` clauses
  (the functor, the stage number or `_`, the computation id, the argument
  that receives the unknowns and the one that receives the constants:
  `stage(1, [A, _], Cs) :-` is H, with its `:-`), and the whole of each
  `unknowns/2` fact; the CONSTANTS block's markers and `% stage K` lines
  are comments;
- every call of `h_param/2`, `h_commitment/1`, `emit/1`, `h_count/1`,
  `h_candidate/0`, `h_held/2` and `h_wait/0`, with its arguments;
- output adapters (rule 13), if a program has any.

A clause body of `stage/3` or `query/2`, and everything else, is classed
by `METRICS.md`'s rules. `S/session-wait.pl` is S (`S-mechanisms.md`).

## 13. Confounds

Everything the harness does beyond passing stages in, collecting answers
and reading state (also copied into every record's `run.confounds`):

1. Stages are posed by calling the program's `stage/3` (with the constants
   of the stages posed so far) for stages 1..k and
   then `query/2` for k, as one conjunction compiled into one clause (the
   reposed configurations), or by posting each stage into one engine,
   whose loop is the harness's (session). A stage mark precedes each
   `stage/3` call; its inferences are excluded. The CONSTANTS block is
   blanked out of the text that is loaded, and its entries are passed in
   as `stage/3`'s last argument (§ 2.5).
2. Harness code inside the measured computation is excluded from the steps
   and the budget by moving the inference limit on by what it spent
   (SWI-Prolog internals `'$inference_limit'/2` and
   `'$inference_limit_false'/1`), and the budget is enforced with them, not
   with `call_with_inference_limit/3`, which restarts its limit per
   solution. Between harness entries the system's limit stands 8
   inferences beyond the budget.
3. Answers are rendered with the toplevel's own code, with
   `answer_write_options` `max_depth(0)` instead of `max_depth(10)`.
4. `autoload_all/0` after loading the program (the `autoload` flag is
   restored).
5. `prolog:prolog_exception_hook/5` reads the state when any exception is
   raised in the computation, before unwinding, and reports it if the
   exception reaches the harness. It does not change the exception.
6. observe() reads `term_attvars/2`, `copy_term/3` and the toplevel
   rendering at the end of the stage (and, storage, choicepoints and the
   store after `garbage_collect/0`).
7. Storage mode: a heartbeat sampler (`heartbeat` flag every 1008
   inferences), with `flag/3` maxima; excluded from steps, but it moves GC
   and layout.
8. One fresh `swipl` process per reposed stage attempt; one per session
   computation, and one per separate run.
9. Session: answers of a non-final stage on a separate run of 1..k.
10. Spawned computations as successive separate queries in one process.
11. The effects stub's entries go to a spool file and are appended to the
    log by the driver when the attempt ends.
12. Session only: the S code of `S/session-wait.pl` (an
    `user:exception/3` hook) is loaded before the program. It is part of the
    configuration as the systems file defines it, and is counted as S.
13. The safety limit is enforced by a SIGUSR1 handler of the harness,
    which reads the state and kills the process.

## 14. check

    harnesses/swi-prolog/check CONFIGURATION PROGRAM

The same for every configuration, with configuration-specific warnings.
It **executes nothing of the program**: it reads the program's terms with
`read_term/3`, the reader the compiler uses, into a scratch module, and

- reports syntax errors verbatim as SWI-Prolog's message system words
  them (`print_message/2`), and continues after each;
- never compiles or asserts a clause, never executes a directive, never
  calls a goal of the program, never poses a stage. Three kinds of
  directive are interpreted for their effect on reading only: `op/3`
  (applied to the scratch module), and `use_module/1,2`, `ensure_loaded/1`
  and `autoload/1,2` of `library(...)` (the library is loaded into the
  scratch module, so that its operators, such as clpfd's `#=`, and its
  exports are known: that runs the library's code, never the program's).
  `dynamic/1` and `table/1` are noted. Every other directive is listed as
  not executed;
- then checks statically: singleton variables (as the compiler would warn);
  calls to procedures that nothing defines (the program's clauses and
  dynamic declarations, built-ins, the loaded libraries, the autoload
  index, the H predicates), through the control constructs and the
  meta-calls whose argument is a goal; the contract (`unknowns/2`,
  `stage/3`, `query/2`, `spawned/4`); the `CONSTANTS` block's form (one
  pair of markers, `% stage K` sections in increasing order before any
  entry, facts only), whose entries are checked as entries and not counted
  as the program's clauses; the `PROVENANCE` comment; and mechanisms the
  configuration does not have (`:- table` outside *tabling*; `freeze/2`,
  `when/2`, `dif/2` outside *coroutines*, *constraints*, *session*;
  clpfd/clpq outside *constraints*, *session*; engines and `h_wait/0`
  outside *session*), as warnings.

Exit status 0 when there is no error, 1 when there are errors (syntax
errors; neither `stage/3` nor `spawned/4`; `stage/3` without `query/2`;
a `stage/2` or `spawned/3`; a malformed CONSTANTS block), 2 usage. The qualification shows that a
program whose every directive and goal would print a marker and write a
file leaves no trace under `check`, and leaves both under `run`.

## 15. Qualification

[`qualification/`](qualification): made-up programs, a made-up stages file,
`run.py` (inside the image) and `rerun.sh` (from the host), its
`output.txt`, and every record it wrote, under `records/`.
