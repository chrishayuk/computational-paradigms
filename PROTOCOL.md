# Protocol

*Draft 0.2.*

## Phases

1. **Draft.** `SPECIFICATION.md`, `METRICS.md`, this file and `problems/`
   are written. No system's programs are written.
2. **Independent review.** A reviewer who has not written the draft reads
   it for ambiguity, for errors in the valid outcomes, for language bias,
   and for problems missing from the suite. Findings and responses are kept
   in `reviews/`. *(Draft 0.1 has had one review. Draft 0.2 answers it, and
   is awaiting a second.)*
3. **Freeze.** The specification is tagged `spec-1.0`, together with:
   - the pinned version or commit of every system in the first comparison;
   - each systems file's cores, flags and units;
   - the generic harness interface below.

   From then on, these change only by amendment.
4. **Harnesses.** One harness per system implements the interface, and is
   published before any program is run.
5. **Implementation.** Programs are written for each configuration from the
   problem files, one per configuration and problem, fixed before any of
   them is run.
6. **Results.** Each program is run and classified, and the results are
   recorded in `results/`.
7. **Comparison.** Only after results exist for at least two systems on
   every problem.

No system is implemented before the freeze. The benchmark is not changed
afterwards to suit any system, including PLANNER and the systems after it.

## Amendments

An amendment is a numbered, dated change to a frozen file, with its reason.
It applies to every system. Results obtained before it are kept, marked
with the specification version they were obtained under, and rerun under
the new version.

A problem proposed after the freeze does not join the frozen suite. It goes
into a separate, dated supplementary suite, reported apart from the frozen
one, with the date it was proposed and the results that existed then.

## Evidence classification

Every implementation is given one or more of these classes:

| class | meaning |
|---|---|
| **original** | a surviving historical implementation, on the hardware or software it was written for |
| **rehosted** | a surviving historical implementation, running in a modern environment (an emulator, a port of the original source) |
| **reconstructed** | a modern implementation derived from historical documents, where no implementation survives |
| **modern** | a contemporary implementation of the language |
| **extended** | mechanisms supplied for the experiment, beyond the implementation's own |

Two qualifiers may be attached to a class:

- *with external mechanisms*: libraries or run-time features outside the
  configuration's core are used (`METRICS.md`);
- *alternative reading*: a reconstruction run with a decision taken the
  other way, where its sources conflict.

Results are always reported with the class. No result from a modern or
extended configuration is attributed to the historical language. Where a
language was described more fully than it was implemented (PLANNER and
Micro-Planner, for instance), the described language and the implemented
subset are separate systems.

## Configurations

A configuration is one system with a stated set of mechanisms. Results are
kept separate per configuration, so that a capability introduced later is
not attributed to the earlier model. Each systems file lists, per
configuration:

- its core, built-in by built-in;
- its flags;
- the unit of steps, of an alternative and of store, and how each is
  measured;
- what "the same computation" means. That is, whether a stage can be
  received into a computation already running, and how.

A reconstruction is pinned at a commit when the specification is frozen.
Any later change to it, for whatever reason, makes a new configuration,
reported separately, and never replaces the pinned one.

## The harness interface

Every harness provides exactly these operations, and nothing that orders,
chooses or re-poses goals on its own:

- **pose(stage)**: give the system the information of one stage, into the
  same computation if the configuration allows it, or else by reposing
  stages 1 to k together;
- **answers(cap)**: collect the answers the system reports, through its
  standard mechanism for enumerating them, until it is exhausted, the
  budget runs out, or `cap` answers have been collected. The cap is 20;
- **observe()**: record the state the common observations need;
- **print()**.

**Observing must not consume the computation.** In a system where
collecting answers would end or alter the computation that the next stage
extends (exhausting a backtracking search, for instance), the observation
of stage k is taken on a separate run of stages 1 to k. The incremental
run is left as it was.

Concurrency used to run computations (threads, processes) is a mechanism of
the configuration, listed in its systems file. A harness may not run
computations concurrently itself. In P09, all computations run in one
instance of the system, sharing one database, never in separate operating
system processes.

## Writing a program

1. Write it from the problem file. Programs written for this study's
   precursors (the absys experiments E01–E09) exist, and their author may
   have seen them; each program says whether its author had.
2. Use the idioms of the system's period where they are known. Cite the
   source of each idiom: a manual, a paper or a published program.
3. Transcribe the definitions given. Anything else is reformulation, and
   counts as R.
4. Where several idiomatic programs are possible, choose one per
   configuration and problem before any is run, or run and report every
   variant.
5. A program may not be revised after its results are seen, except to fix a
   transcription error: a place where the program departs from the text of
   the problem file. Each fix is recorded as a diff, with the reason. A
   program changed for any other reason is a separate, named variant, and
   is reported as such.
6. Record the author of each program, human or agent.

## Running

- Pin the version of every system, and record its source and commit.
- **Budget.** 10⁶ steps in the system's own unit, per stage and per
  computation. In P09, each separate computation has its own budget and its
  own classification.
- **After budget or error.** If stage k ends in *budget* or *error*, stage
  k+1 is posed by reposing stages 1 to k+1. That reposing counts under
  restart cost.
- **Safety limit.** A limit of 60 seconds per stage protects the harness.
  It is not a measurement. A stage it stops is classified *timeout* and
  rerun on a faster machine, or with the limit raised, with both recorded.
- Run in CI where the system allows it, and compare with recorded output.

## Recording a result

Each result is a file `results/<system>/<configuration>/<problem>.md` that
gives:

- the specification version, the system version or commit, the
  configuration and the evidence class;
- the program, or a link to it at a commit, and whether its author had seen
  a precursor;
- for each stage, the common observations of `SPECIFICATION.md` and the
  problem's own;
- the token counts by class, per classifier, with the disputed tokens;
- the configuration's expressibility for the problem.

## Guarding against bias

- The reasons for choosing a problem, and the history of each system's
  implementation, are disclosed.
- Every review is asked for problems that favour designs other than those
  the suite came from.
- Results are reported for every system on every problem, including
  "not expressible".
- No ranking is computed. A summary may say where a system needed control,
  supporting code or intervention that another did not, and what it held in
  store to avoid them.
- Interpretation, including any connection to later work, is kept out of
  `results/` and in a separate document written after the comparison.
