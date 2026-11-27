# Questions: the SWI-Prolog harness

*Where the common contract (`harnesses/README.md`, `harnesses/QUESTIONS.md`)
or the specification could not be implemented as written for SWI-Prolog,
or left a choice, and the reading implemented. No file outside
`harnesses/swi-prolog/` was changed. The common part's readings Q1–Q19
are implemented as written.*

## S1. The budget cannot be enforced with `call_with_inference_limit/3`

The systems file names `call_with_inference_limit/3` as the budget
mechanism. That predicate restarts its limit for each solution (on
backtracking into it, the limit is set again, in full), and it counts
whatever the harness does between answers against nothing; a stage that
collects several answers, or whose budget must be the restart cost plus
10⁶ from the start of a reposed run, cannot be bounded by it.

**Implemented:** the same limit, set absolutely with the predicates
`call_with_inference_limit/3` is built from (`'$inference_limit'/2` and
`'$inference_limit_false'/1`), raising the same `inference_limit_exceeded`.
Harness code inside the computation lifts it and puts it back, moved on
by what it spent, so that only the program's inferences count. Since
entering harness code costs a few inferences before the limit can be
lifted, the limit stands 8 inferences beyond the budget while program
code runs, and every harness entry checks the budget exactly, raising the
exception itself when the program's steps exceed it. So the *budget*
classification is exact at every harness entry (each answer, each stage
mark, each H call, the end of the stage); between harness entries the
system stops a stage at most 8 inferences after its budget, and the steps
recorded at that stop say so. Listed as a confound.

## S2. A replay that does not reach stage k

The in-run restart cost is "the step count at the moment stage k is first
posed". If the replay of stages 1 … k−1 runs out of a replayed stage's
budget, or is stopped by the safety limit, stage k is never posed.

**Implemented:** the restart cost is every step the replay took, read when
it stopped (in the exception hook, or by the SIGUSR1 handler), with
`restart_cost_method: in-run` and a `restart_cost_source` that says so;
the stage's budget is that plus 10⁶, and the stage is *budget* or
*timeout*. If the process ends at the safety limit without answering
SIGUSR1 (a loop inside a foreign predicate, which never reaches a point
where signals are handled), no count can be read; the restart cost is
then null, the record does not validate, and `run` keeps it as
`.INVALID.json` and exits 3, rather than estimate it.

## S3. A session computation that has failed cannot receive the next stage

In *session*, if the computation fails (a stage's goal and every earlier
alternative fail), the engine has finished: there is no computation to
post stage k+1 into, and none of the reasons of the record (`after-budget`,
`after-error`, `after-timeout`) applies.

**Implemented:** stage k+1 starts a new computation, with stages 1 … k
posted again (`posed.how = reposed`, `reason = configuration`), and the
stages after it are posted into that one. In a reposed configuration a
failed stage is followed the same way by every later stage.

## S4. Which session answers are taken on a separate run

The common contract: where collecting answers would consume the
computation the next stage extends, answers are taken on a separate run
of stages 1 … k.

**Implemented:** in *session*, at every stage except the instance's last,
`answers()` is taken on a separate run (a fresh process and engine:
stages 1 … k−1 posted as replay, then k with its query), and `observe()`
and `print()` read the incremental computation's held state without
consuming it (`taken_on: this-run`). At the instance's last stage nothing
extends the computation, so its answers are collected in it. A spawned
computation (P09) is likewise collected in place. The separate run's
`steps_restated` is beside the incremental stage's own steps; the
latencies (`to_first_answer`, `between_answers`, `to_end`) are the
separate run's, counted from the posing of stage k in it. `query(K, Vars)`
is called only where answers are collected, so in the incremental
computation it runs at the last stage only.

## S5. Spawned computations, and P16b

No SWI-Prolog configuration runs computations side by side by itself:
threads are in no configuration, and engines (in *session*) run only when
asked, so running them side by side would be the harness interleaving
them, which it may not do. Nor can separate computations share unknowns:
a separate query, an engine and a thread each copy their goal.

**Implemented:** a spawned computation is a separate query in the same
process, sharing its database, run to its end or budget before the next
(`side_by_side: false`), in every configuration. P16b is always posed by
its fallback, the four contributions as one conjunction in `main`.

## S6. After budget, no configuration can continue

The budget's exception unwinds the stage's goal, so the computation that
ran out cannot be resumed with a new budget in any configuration, *session*
included (the engine survives, but the stage's work is undone).

**Implemented:** stage k+1 after *budget* is reposed (`after-budget`) in
every configuration; `continued_after_budget` is never true.

## S7. What observe() reads when the answers are exhausted

When the last request for an answer fails, backtracking has left the
posed goal: no binding, choicepoint or attributed variable of it is held.

**Implemented:** `observe.raw` is empty and `method` says why; the answers
themselves are recorded verbatim. Where the query is still at an answer
(cap, or a last answer without choicepoints), at the budget, at an error
and at the safety limit, observe() reads the state held there.

## S8. H calls and the step count

`METRICS.md` classes the harness's calls as H tokens, and the steps are the
system's inferences.

**Implemented:** the inferences of H calls, their call ports included, are
excluded from the steps and from the budget, so that a program's steps
do not depend on whether it counts its problem operations, emits effects
or reads its parameters. A program's S code is not excluded.

## S9. Rendering answers

The toplevel elides answers deeper than `max_depth(10)`, which would lose
answers the classifiers need (long sequences, P13, P16).

**Implemented:** the toplevel's own rendering code with
`answer_write_options` `max_depth(0)`; otherwise as the toplevel prints.
A deterministic last answer ends `.` (the `query(yes(…))` message), a
nondeterministic one with a space (`query(more(…))`), exactly as the
toplevel prints them. A commit stage's value v is that text, verbatim,
trailing space or `.` included.

## S10. Where latency is counted from in a reposed stage

**Implemented:** `to_first_answer`, `steps_at`, `between_answers` and
`to_end` count from the posing of stage k, after the replay (so that
they are comparable with an incremental stage's); `restated` and
`restart_cost` give the run's totals.

## S11. The session configuration's supporting code

The systems file defines *session* as including "supporting code that
makes an application wait for an undefined procedure", counted as S, and
the S mechanisms must be listed with their size before any program is
run.

**Implemented:** that code is `S/session-wait.pl` (listed in
`S-mechanisms.md`), loaded by the harness in every *session* run before
the program. Its one call to the harness, `h_wait/0`, is H; the rest is S.
A *session* program may also wait explicitly with `h_wait/0`.

## S12. Messages that name the harness

SWI-Prolog's error messages include the predicate that called the failing
goal; where that is the clause the harness compiles for the query (last
call optimisation removes the program's frame), the message names
`'$cp_query'/1` (or, in *session*, `cp_harness:engine_step/4`), and under
`-g` the system prefixes `[Thread main]`.

**Implemented:** the message is recorded verbatim, as the system words
it.

## S13. `system_build`

The `swipl:11.0.1` image has no `/opt/src/COMMITS`, and a harness inside
the container cannot read the image's digest. **Implemented:** the build
is recorded as the pinned image's digest, `system_build.image`: the value
of `HARNESS_IMAGE_DIGEST` if the launcher sets it (else
`CP_IMAGE_DIGEST`), and otherwise the `swipl:11.0.1` index digest that
`PINS.md` pins,
`sha256:b51af487f3306fe240eae8c13159c85b5526509952e1b949cc22f48a1f82a742`.
`system_build.commit` stays null (there is no system commit for an image
pinned by digest), and `version_output` is `swipl --version`, verbatim.

## S14. The effects logs' folder

**Implemented:** the logs are written in `OUTDIR`, which for P11 is the
folder the common contract names (`results/swi-prolog/<configuration>/P11/raw/`);
the verifier's runs, under its own `OUTDIR`, have their own logs.

## S15. A separate run stopped by the safety limit

**Implemented:** the separate run of a *session* stage has the attempt's
limit; if it is stopped, the attempt is recorded as stopped by the
safety limit, and the stage is rerun as attempt 2 (a reposed run of
stages 1 … k under the raised limit), from which the incremental
computation continues.

## S16. The systems file's two step measurements do not always agree

The systems file says that the `statistics(inferences)` difference minus
one "is exactly the smallest limit `call_with_inference_limit/3` lets a
goal finish under". The qualification confirms it for some plain
programs (the probes, and made-up stages of facts and member/2), but finds
that it does not hold where coroutine wake-ups (freeze, dif, clpfd) or
tabling run, or memberchk/2 is called: there the smallest limit is smaller
(for a made-up clpfd stage, 100 against 111; for a tabled one, 4 against
63; for a stage that calls memberchk/2, a few inferences), presumably
because some of the work is not inside the limited call.

**Implemented:** the harness's steps are the `statistics/2` count, and its
budget is checked against that count at every harness entry (section 9),
so a stage's steps and its budget agree with each other and with the
`statistics/2` measurement in every configuration. The qualification
reports the `call_with_inference_limit/3` figure beside it, as
information. It also finds that the first call of a library predicate in
a process (memberchk/2 here) can cost an inference more than later calls,
so each `statistics/2` reference figure is taken first in a fresh
process, as the harness's are. The systems file's claim of agreement may
need an amendment.

## S17. No storage sampler in tabling

The heartbeat sampler's inferences are excluded from the steps like other
harness code; the qualification found that under tabling (SLG resolution,
which suspends and resumes goals with delimited continuations) this
exclusion is not exact (a made-up tabled stage gained 618 steps in its
storage run).

**Implemented:** in *tabling* the storage run takes no sampled maxima
(their `peak` is null); the store at the boundary, which tables only
grow, is still read. The other configurations sample as described.

## S18. No anticipation of constants (rule 5), made structural

A constants block loaded with the program would put every later stage's
constants into the system, as clauses, from stage 1 on, so that rule 5
would rest on the program's discipline alone.

**Implemented** (as for the other three systems): each entry of the block
is tagged by a `% stage K` comment line with the stage that first uses
it; the driver splits the block and loads the program with the block's
lines blanked; stage k's entries reach the process only when stage k is
posed, and the program only as the last argument of `stage(k, Vars,
Constants)`, the entries of stages 1 … k (again on every replay). The
program contract changes accordingly: `stage/3` and `spawned/4` replace
`stage/2` and `spawned/3`. The verifier still substitutes only the block.

One reading: in a reposed configuration a whole process poses stage k,
its replay of stages 1 … k−1 included, so stage k's entries are in that
process from its start (as text in the control file, read as terms when
the stage's goal is built). The replayed stages' code is called with only
the entries of their own stages 1 … j, so it cannot use them. In
*session*, stage k's entries arrive with the command that posts stage k.

The harness loads a stripped copy of the file (of the same name, in its
work directory), so that the system never opens the original; error
messages therefore name that copy's path, with the original's line
numbers.
