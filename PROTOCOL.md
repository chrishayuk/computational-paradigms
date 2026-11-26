# Protocol

*Draft 0.1.*

## Phases

1. **Draft.** `SPECIFICATION.md`, `METRICS.md`, this file and `problems/`
   are written. No system's programs are written. *(We are here.)*
2. **Independent review.** A reviewer who has not written the draft reads
   it for ambiguity, for errors in the valid outcomes, for language bias,
   and for problems missing from the suite. Findings and responses are kept
   in `reviews/`.
3. **Freeze.** The specification is tagged `spec-1.0`. From then on, the
   problems and the classification rules change only by amendment (below).
4. **Implementation.** Programs are written for each system and
   configuration, from the problem files alone.
5. **Results.** Each program is run and classified, and the results are
   recorded in `results/`.
6. **Comparison.** Only after results exist for at least two systems on
   every problem.

No system is implemented before the freeze. The benchmark is not changed
afterwards to suit any system, including PLANNER and the systems after it.

## Amendments

An amendment is a numbered, dated change to a frozen file, with its reason.
It applies to every system. Results obtained before it are kept, marked
with the specification version they were obtained under, and rerun under
the new version. A problem may be added by amendment, never removed.

## Evidence classification

Every implementation is given one or more of these classes:

| class | meaning |
|---|---|
| **original** | a surviving historical implementation, on the hardware or software it was written for |
| **rehosted** | a surviving historical implementation, running in a modern environment (an emulator, a port of the original source) |
| **reconstructed** | a modern implementation derived from historical documents, where no implementation survives |
| **modern** | a contemporary implementation of the language |
| **extended** | mechanisms supplied for the experiment, beyond the implementation's own |

Results are always reported with the class. No result from a modern or
extended configuration is attributed to the historical language. Where a
language was described more fully than it was implemented (PLANNER and
Micro-Planner, for instance), the described language and the implemented
subset are separate systems.

## Configurations

A configuration is one system with a stated set of mechanisms. Results are
kept separate per configuration, so that a capability introduced later is
not attributed to the earlier model. The configurations of the first two
systems are in `systems/absys/README.md` and `systems/swi-prolog/README.md`.

## Writing a program

1. Write it from the problem file alone.
2. Use the idioms of the system's period where they are known. Cite the
   source of each idiom: a manual, a paper or a published program.
3. Transcribe the definitions given. Anything else is reformulation, and
   counts as R.
4. A program may not be revised after its results are seen, except to fix
   a transcription error, which is recorded. A program tuned after the fact
   is a separate, named variant, and is reported as such.
5. Record the author of each program, human or agent.

## Running

- Pin the version of every system, and record its source and commit.
- Set a step budget of 10⁶ steps in the system's own unit, per stage. A
  safety limit of 60 seconds per stage protects the harness; it is not a
  measurement.
- Pose the stages in order, into the same computation where the
  configuration allows it. Otherwise, restate them, and count the
  interventions.
- Run in CI where the system allows it, and compare with recorded output.

## Recording a result

Each result is a file `results/<system>/<configuration>/<problem>.md` that
gives:

- the specification version, the system version, the configuration and the
  evidence class;
- the program, or a link to it at a commit;
- for each stage, the common observations of `SPECIFICATION.md` and the
  problem's own;
- the token counts by class, with both classifiers' counts and their
  disagreements;
- anything the program could not express.

## Guarding against bias

- The reasons for choosing a problem are disclosed (`SPECIFICATION.md`).
- The reviewer is asked to propose problems that favour other designs.
- Results are reported for every system on every problem, including
  "not expressible".
- No ranking is computed. A summary may say where a system needed control,
  supporting code or intervention that another did not, and what it held in
  memory to avoid them.
- Interpretation, including any connection to later work, is kept out of
  `results/` and in a separate document written after the comparison.
