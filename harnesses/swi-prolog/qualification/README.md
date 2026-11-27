# Qualification of the SWI-Prolog harness

Evidence that the harness does what `../README.md` says and does not change
what the system computes. **Only made-up programs are run**, against a
made-up stages file; no problem P01–P16 and none of their constants is
used.

| file | what it is |
|---|---|
| `stages-made-up.json` | twelve invented problems X01–X12 (a `cp-stages/1` file; `validate.py --check-stages` accepts it): stages, caps, a commit with effects, spawned computations, a small budget, short safety limits with and without a rerun, sizes and orders, answer modes, a replacing stage, a spawn fallback |
| `programs/` | the made-up programs, and the systems file's probes (`systems/swi-prolog/probes/`) recast as one-stage programs (`probe-*.pl`), and `noexec.pl` for `check` |
| `direct.pl` | the system run **without the harness**, measured as the systems file qualifies its units |
| `run.py` | runs everything below inside the image and checks it; exit 0 if every check passed |
| `rerun.sh` | starts `run.py` in the pinned image from the host and writes `output.txt` |
| `output.txt` | the output of the last full run |
| `records/` | every record that run wrote (`records/<configuration>/<problem>/raw/`), kept, with the effects logs of X02 |

Rerun from the repository root: `harnesses/swi-prolog/qualification/rerun.sh`.
Records are never deleted: a rerun adds its own, and the X02 effects
logs grow (each record gives `entries_before_run`).

## What is checked

**(a) The system run directly, against the harness.** For made-up programs
in plain, coroutines, constraints and tabling, and for every stage:

- the answers the harness records are, byte for byte, what SWI-Prolog's
  own interactive toplevel prints for the same query (`stage(1,V), …,
  query(k,V).` piped to `swipl` with `;` for each further answer), with
  `answer_write_options` `max_depth(0)` in both;
- the steps to the first answer equal the `statistics(inferences)`
  difference minus one around the posed goals, and (in *plain*) the
  smallest limit under which `call_with_inference_limit/3` lets them reach
  it is that plus one (the call of the clause holding them; outside
  *plain* the two measures differ, `../QUESTIONS.md`, S16, and the limit
  is printed as information); the steps at every
  answer equal the same limit found per answer; the steps to exhaustion
  equal the `statistics/2` difference around `(goals, fail ; true)`;
- the retained choicepoints at each answer (storage) equal the probe's own
  `cp_since/2` (`probes/cpcount.pl`) from a mark at the query's start;
- attributed variables and residual goals (`term_attvars/2`,
  `copy_term/3`), and tables and table answers, equal the direct reading;
- behaviour, cost and storage runs record the same answers and the same
  steps.

**The systems file's probes**, run through the harness, against
`probes/expected-macos-arm64.txt` (whose platform-independent lines the
Linux image reproduces, `measurement.md`): `work/0` and `w2/0` take the
probe's warm inference counts, and the budget-relevant count is the
probe's `minlimit`; `gen(4, _)`'s choicepoints at the first 20 answers are
the probe's, less the 2 of its `findall/3`, and the probe's histogram is
the expected one; the freeze and clpfd cases have the expected attributed
variables and residual goals; `path(1, _)` has the expected tables,
answers and `table_space_used`.

**(b) Incremental and reposed posing.** The same programs in *session*
and in a reposed configuration give the same answers at every stage, and
the same restated steps (the session's from its separate runs).

**(c) Budget, safety limit, error.** Under a made-up budget of 5000, a
stage of exactly 5000 steps finishes and one of 5001 is *budget*, stopped
at 5001, with the bindings read at the stop; the next stage is reposed
`after-budget` with an in-run restart cost; a stage that loops without
entering harness code stops within the 8-inference slack; a stage past a
1 s safety limit is stopped, rerun at 3 s, *timeout* both times, and the
next stage reposed `after-timeout`, its replay's restart cost read when
it stopped; a fixed limit gives one attempt; an undefined procedure and a
syntax error are *error*, and the next stage is reposed `after-error`;
`h_wait/0` outside *session* is an error; in *session* a stage that waits
is *suspended* and the next stage is received into it.

**H calls** cost the program nothing: a program with `h_count/1`,
`h_candidate/0` and `h_held/2` has the same steps as without them, in
every mode.

**Effects**: the classification log grows by exactly the entries the
attempts list; cost runs write only to the observation log; replayed
commitments are recorded.

**(d)** Every record written passes `harnesses/validate.py` (with the
made-up stages file).

**check executes nothing**: `noexec.pl`, whose every directive and goal
would print a marker and write a file, leaves neither under `check`, and
leaves both when the harness runs it. `check` is run on every program
here.

**No anticipation**: `xlate.pl`'s stage-3 constant is a word that occurs
nowhere else; at every stage the program looks for it among all the
atoms the process holds and in every string the harness holds. In plain
(each stage's process) and in session (the incremental computation and its
separate runs) stages 1 and 2 find nothing, and stage 3 finds it.

**Usage errors** (unknown configuration, instance or mode; an instance of
another problem) exit 2 and write no record.
