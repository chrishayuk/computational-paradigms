# Protocol

*Draft 0.7.*

## Phases

1. **Draft.** `SPECIFICATION.md`, `METRICS.md`, this file and `problems/`
   are written. No program for the study is written, apart from the
   calibration programs (`METRICS.md`, Calibration), which are development
   examples and never results.
   Measurement may be qualified at this phase: establishing what each
   system can report, and adding instrumentation that changes no result,
   under the conditions in "Instrumentation" below.
2. **Independent review.** A reviewer who has not written the draft reads
   it for ambiguity, for errors in the valid outcomes, for language bias,
   and for problems missing from the suite. Findings and responses are kept
   in `reviews/`. *(Draft 0.1 had one review, answered in draft 0.2. Draft
   0.3 had a second, by a fresh reviewer, answered in draft 0.4. Draft 0.5
   had a third, answered in draft 0.6. Draft 0.7 is the freeze candidate.)*
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

## Roles

| role | does | has access to |
|---|---|---|
| **specification author** | writes the problems and the protocol | the public repository |
| **variant custodian** | writes the hidden variants and their valid outcomes | the specification, and the private variants |
| **implementation author** | writes the programs | the public repository only |
| **harness author** | writes each system's harness (phase 4) | the public repository |
| **classifier A** | classes the programs' constructs, and the outcomes of every run on all axes, checking residual equivalence | the specification, the metrics, the programs, their outputs and the valid outcomes |
| **classifier B** | does both independently | the same, without A's classes |
| **verifier** | runs the programs on the hidden variants | the programs, the variants and their outcomes |

Each role is a separate agent or person, with its own context, and its
provenance is recorded. The two classifiers are of different origin (for
instance Claude and Codex), and neither wrote the program it classes.
Their disagreements, on tokens and on outcomes, are recorded, and a
disputed outcome is reported under both classes.

**Hidden variants** are made inaccessible, not merely placed where an
implementation author is told not to look. The custodian writes them
before the freeze and encrypts them with a key the project's owner holds
but does not use. The plaintext begins with a random nonce of at least 128
bits, so that a small space of constants cannot be recovered from its
hash. Only the ciphertext and the SHA-256 hash of the plaintext are
committed. The key is given to the verifier only after every primary
program and its results are committed. The verifier publishes the
plaintext, and anyone can check it against the hash. Each later wave of
systems (PLANNER onwards) has its own sealed set, made before that wave's
programs are written, since revealing a set publishes it.

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

## Instrumentation

A measurement added to a system must not change what it computes. For a
reconstruction:

- the unmodified commit is kept as the baseline;
- instrumentation is made on a separate branch, and recorded as its own
  commit;
- it may not change scheduling, search, equality, suspension or any other
  rule of the machine;
- the instrumented build, with measurement on and off, must give output
  identical to the baseline's, byte for byte, on every example and in every
  output mode, including full traces. The check and its result are
  recorded.

## The harness interface

Every harness provides exactly these operations, and nothing that orders,
chooses or re-poses goals on its own:

- **pose(stage)**: give the system the information of one stage, into the
  same computation if the configuration allows it, or else by reposing.
  A reposed run replays **every** stage 1 to k in order, replacements and
  withdrawals included, and the program must carry them out. The harness
  never works out the net information itself;
- **spawn(computation)**: start a separate computation in the same
  instance (P09), returning at once where the configuration can run
  computations side by side. In a configuration that cannot, the first
  runs to its end or its budget, and then the next;
- **answers(cap)**: collect the answers the system reports, through its
  standard mechanism for enumerating them, until it is exhausted, the
  budget runs out, or `cap` answers have been collected. `cap` is 1 for an
  *any one* query and 20 otherwise, as each problem states. The execution
  state is classified after the call;
- **observe()**: record the state the common observations need, including
  bindings the system holds (`SPECIFICATION.md`, "reported");
- **print()**.

Each system's systems file says what its standard mechanism for answers
is. For Python and ALGOL 60, it is the values the program prints.

**Observing must not consume the computation.** In a system where
collecting answers would end or alter the computation that the next stage
extends (exhausting a backtracking search, for instance), the observation
of stage k is taken on a separate run of stages 1 to k. The incremental
run is left as it was.

**Commitments are preserved when a run is reposed.** When a commit stage
has selected an outcome v (P11), a reposed run replays it as the
information x = v. It does not ask the system to select again, which could
commit to a different outcome.

**External effects** (P11) are written to one log per problem, never reset,
across every run the harness makes for classification, reposed runs
included. Separate observation runs write to a separate log, which is not
judged. Entries that are duplicated only because a run was reposed are
counted separately, as the cost of reposing an irreversible effect.

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
   variant. In either case, one is designated the **primary** variant
   before any is run, and stands for the configuration.
5. **No anticipation.** The code that handles stage k may not depend on the
   content of any later stage.
6. **Genericity.** A program must stay correct when the constants in a
   problem's stages are changed. It keeps them in one marked place, or reads
   them as input, so that the verifier can substitute them. Each problem
   has hidden variants with other constants, held by someone who does not
   write programs. Every program is run on them after its results are
   recorded. The custodian works out each variant's valid outcomes
   independently, stage by stage, as the problem files give them for the
   original constants. A variant's outcomes need not have the same classes
   as the original's: other constants can make a finite outcome infinite,
   or a consistent stage inconsistent. A program's run on a variant is
   classified against **that variant's** valid outcomes, on the semantic and
   effects axes, exactly as a primary run is. A program **fails** a variant
   where that classification differs from its classification on the
   original constants, each against its own valid outcomes: a program
   complete on the original and unsound on the variant fails it. It is
   recorded as such, since it encodes a conclusion rather than computing
   it. The custodian records, for each variant, which of the original's
   outcome classes it was built to keep, if any.
7. A program may not be revised after its results are seen, except to fix a
   transcription error: a place where the program departs from the text of
   the problem file. Each fix is recorded as a diff, with the reason. A
   program changed for any other reason is a separate, named variant, and
   is reported as such.
8. Record the author of each program, human or agent.

## Running

- Pin the version of every system, and record its source and commit.
- **Budget.** 10⁶ steps in the system's own unit, per stage and per
  computation. In P09, each separate computation has its own budget and its
  own classification. A reposed run of stages 1 to k has a budget of its
  measured restart cost plus 10⁶.
- **The budget is relative to each system.** 10⁶ Absys steps, SWI-Prolog
  inferences and Python instructions are different amounts of work. So
  *budget* is a classification within a system, and is not compared
  across systems. Each system records, as a calibration figure, its steps
  for P13b at n = 10³, or, where P13b is not expressible, for P03e.
- **After budget.** If stage k ends in *budget* and the configuration can
  keep its computation and continue it, stage k+1 is posed into that same
  computation, with a new budget. Whether it can is recorded, since
  continuing past an exhausted budget is itself a capability. Stages 1 to
  k+1 are reposed only when the configuration cannot continue, and the
  reposing counts under restart cost.
- **After error.** Stage k+1 is posed by reposing stages 1 to k+1, counted
  under restart cost.
- **Safety limit.** A limit of 60 seconds per stage protects the harness.
  It is not a measurement. A stage it stops is rerun once, with the limit
  raised tenfold. If the rerun also stops, *timeout* is final for that
  stage. Both runs are recorded. Answers reported before the limit stopped
  the run are kept and classified on the semantic axis; only the execution
  state is *timeout*.

## Modes of running

Each program is run in up to three modes:

| mode | what it establishes | instrumentation |
|---|---|---|
| **behaviour** | the outcomes, the three axes and effects | none beyond the harness |
| **cost** | steps, answer latency, problem-defined operation counts | step counting only |
| **storage** | store, retained alternatives, suspended state | the systems file's storage measurement |

- The semantic result and execution state are taken from the behaviour run.
- Where two modes can be compared, their semantic results must agree, and
  any disagreement is reported as a fault of the instrumentation.
- A sampled measurement is never taken from the run that gives the step
  count or the classification, because sampling adds steps of its own.
- A run that hits the safety limit only because it is instrumented (in
  cost or storage mode, when the behaviour run finished) is not evidence
  that the model cannot complete the problem. It is recorded as a limit of
  the measurement.
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
- the configuration's expressibility for the problem;
- the supporting code (S) used, by mechanism. An *extended* result is named
  by its mechanism. Every configuration's S mechanisms are listed, with
  their size, at phase 4, before any program is run;
- whether the program passed its hidden variants.

## Guarding against bias

- The reasons for choosing a problem, and the history of each system's
  implementation, are disclosed.
- Every review is asked for problems that favour designs other than those
  the suite came from.
- Results are reported for every system on every problem, including
  "not expressible".
- Both classifiers' token classes are kept and reported for every result,
  throughout the study, never only an adjudicated set. A comparative
  conclusion that would change if one classifier's classes were used in
  place of the other's is reported as **classification-sensitive**, with
  both figures.
- No ranking is computed. A summary may say where a system needed control,
  supporting code or intervention that another did not, and what it held in
  store to avoid them.
- Interpretation, including any connection to later work, is kept out of
  `results/` and in a separate document written after the comparison.
