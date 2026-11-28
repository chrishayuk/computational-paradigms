# Batch 1B (P04–P08): what was done, and where the classifiers differ

Wave 1, batch 1B, on `spec-1.0.1`. Figures only. No ranking is computed,
and interpretation is kept out of `results/` (`PROTOCOL.md`, "Guarding
against bias"). The results are `results/<system>/<configuration>/P0{4..8}.md`,
assembled by `tools/write-results.py --classes classes-1B` from the
records and both classifiers' files.

**Absys P05** came last. Its P05a and P05b runs take up to about an hour
each: stages reach the safety limit (60 s, then 600 s), and each reposed
stage has a restart-cost replay. Its records, labelled reruns,
classification and result files are now included throughout.

## Chronology

| step | commit |
|---|---|
| implementation authors, from `651a55b`; audited | `dcba161`, `b0d267a`, `4e4a12a`, `f0e6d3c`; audit `1c758fd` |
| run driver: named variants in `variants/` folders | `1c758fd` |
| runs, in the pinned images | from 27 November, 22:40 |
| driver: `--configs`, `--skip-logged`, to run the rest in parallel | `b92cd18` |
| Absys measurement build `8a0eefd` (`--peak-every`), qualified; harness `98baa62` | `6aced67`, `98baa62`, `0c7cfc5` |
| labelled measurement reruns (Absys) | `5f7af01`, `c7c7a58` |
| tokens, classifier brief for 1B | `5f7af01`, `fa93843` |
| classifications A (Claude) and B (Codex), result files (Absys P05 pending) | `95f7ade` |
| Absys P05: records, P05b reruns; its classifications from clones at `1f291be`; result files | `923cf09`, `32d0559`; this commit |

No program was changed after any run (owner's decision: "Proceed with
Batch 1B as written, without correcting the primary programs before
execution").

## Runs

| system | runs | records that validate | harness faults (`*.INVALID.json`) |
|---|---|---|---|
| Absys | 297 | 289 | 8 |
| SWI-Prolog | 510 | 494 | 16 |
| Python | 279 | 279 | 0 |
| ALGOL 60 | 217 | 217 | 0 |

Measurement reruns, labelled, beside the originals (`results/absys/RERUN-M2.md`):
18 in batch 1B (P04d, P04f and P05b, cost and storage, in each Absys
configuration) and 6 in batch 1A (P03f). P05b's reruns reach the step
budget in every stage, so its measurements are recovered. P05a was not
rerun: its behaviour runs reach the safety limit too, so the stop is the
computation's, and its measurements stay **unavailable**. P04d and P04f's reruns end where
their behaviour runs do: the process is killed when the container's 4 GB
of memory runs out, before the step budget. So their steps and store at
the budget stay **unavailable**.

## Tokens by class, per classifier

Over every program text of the configuration, each shared text counted in
each configuration that runs it.

| system | configuration | tokens | A: P C R S H | B: P C R S H | agreement |
|---|---|---|---|---|---|
| absys | absys | 1670 | 1556 0 114 0 0 | 1538 0 132 0 0 | 98.9% |
| absys | absys-depth-first | 1670 | 1556 0 114 0 0 | 1538 0 132 0 0 | 98.9% |
| absys | absys-wake-back | 1670 | 1556 0 114 0 0 | 1538 0 132 0 0 | 98.9% |
| swi-prolog | plain | 3939 | 2390 101 104 0 1344 | 1793 151 651 0 1344 | 84.8% |
| swi-prolog | tabling | 4003 | 2390 165 104 0 1344 | 1793 215 651 0 1344 | 85.1% |
| swi-prolog | coroutines | 4381 | 2550 383 104 0 1344 | 1799 443 795 0 1344 | 82.9% |
| swi-prolog | constraints | 3365 | 1955 66 0 0 1344 | 1857 116 48 0 1344 | 97.1% |
| swi-prolog | session | 3365 | 1955 66 0 0 1344 | 1857 116 48 0 1344 | 97.1% |
| python | core | 14952 | 4040 0 6579 0 4333 | 5283 349 3703 1382 4235 | 77.0% |
| python | stdlib-concurrency | 17932 | 4051 3604 5929 0 4348 | 5240 2618 3341 2471 4262 | 74.8% |
| python | extended | 22063 | 5002 804 5467 4123 6667 | 6204 1129 2230 6047 6453 | 77.1% |
| algol-60 | report | 22436 | 5575 54 3357 0 13450 | 5223 345 3313 0 13555 | 94.0% |
| algol-60 | x1 | 20873 | 5365 54 3357 0 12097 | 5019 345 3313 0 12196 | 93.5% |
| algol-60 | x1sim | 20873 | 5365 54 3357 0 12097 | 5019 345 3313 0 12196 | 93.5% |

Per program, with the disputed constructs: each result file, and
`results/<system>/classes-1B/agreement-tokens.txt`.

## Stage outcomes

`results/<system>/classes-1B/agreement-outcomes.txt` (`tools/outcome-agreement.py`;
values compared reading by reading where P08's closed and open readings
are given).

| system | stages | semantic | representation | simplification | identical to posed | execution state |
|---|---|---|---|---|---|---|
| absys | 162 | 162 | 147 | 147 | 138 | 162 |
| swi-prolog | 310 | 273 | 284 | 308 | 308 | 307 |
| python | 147 | 145 | 146 | 147 | 147 | 147 |
| algol-60 | 147 | 144 | 147 | 129 | 135 | 147 |

## Late definition (P08)

What a program does when a procedure is applied before its definition has
arrived (`sandbox/briefs/classifier.md`, section 4).

| system / configuration | A | B |
|---|---|---|
| Absys, all three (and the redefine variant) | code awaited | code awaited |
| SWI-Prolog *session* (primaries) | code awaited | code awaited |
| SWI-Prolog *plain*, *tabling*, *coroutines*, *constraints*, and every `unknown-fail` variant | neither | neither |
| Python *extended* | code awaited (by program-supplied S, 142 tokens) | code awaited (249 tokens) |
| Python *stdlib-concurrency* | permission awaited | code awaited |
| Python *core* | neither (`NameError`) | neither |
| ALGOL 60, all three | permission awaited | permission awaited |

## Classification-sensitive

Conclusions that change if one classifier's classes replace the other's:

| what | A | B |
|---|---|---|
| Python *core* and *stdlib-concurrency*: is the holding code, repeated from problem to problem, supporting code? | no: R (rule 19, written for the program's relations) | yes: S (rule 19, "reusable from one problem to another"); then these programs use S, and belong in an extended configuration |
| Python *stdlib-concurrency* P08: late definition | permission awaited | code awaited |
| SWI-Prolog *plain*, *tabling*, *coroutines* P07: the `nonvar/1` mode tests in the arithmetic evaluators | P | R (651–795 tokens per configuration) |
| Python: evaluators a program carries but does not use | R | P |
| ALGOL 60 P08: simplification of the held application | reduced | closed: inconsistency undetected; open: reducible |
| P06c stage 2 (ALGOL 60), where the program reports "no solution" but `observe()` reads x = 1 | complete | unsound |
| P08 SWI-Prolog *session*, closed reading | complete and unsound by stage | complete |
| Absys P05a–b: the stage applications `gt(x, k)` and `ne(x, k)` | P (the information posed) | R (the reformulated comparison) |
| Absys P05b stage 2: the derivations held at the budget | residual, reducible (every printed derivation, finished or not, read as the report: their union is {2, 3}) | explicit |

## Supporting mechanisms

Python's are accounted, batch by batch and per classifier, in
`results/python/extended/MECHANISMS.md`. In batch 1B, *extended*'s
programs supply negation as failure (P06d–e) and a wait-for-definition
layer (P08), beside batch 1A's unification and resolution. None was
listed at phase 4. SWI-Prolog *session*'s listed wait-for-definition code
(158 tokens) is exercised only by its P08 primaries. No Absys or ALGOL 60
program uses S.

## Diagnostics (not records of the study)

- **ALGOL 60 *x1sim*, P04a:** its behaviour record says the process was
  killed by SIGKILL, with no message, below the safety limit. A diagnostic
  run of the same harness command, in the same image under the same 4 GB
  limit, showed the container's `memory.events` `oom_kill` going from 0 to
  1, and `memory.peak` at 4,177,874,944 bytes. So it ran out of memory.
  P04c and P04d stop with a stack overflow, and P04e and P04f with
  "Unknown descriptor of formal argument", from the reconstructed X1
  run-time.

## Harness and measurement defects

Recorded here, apart from the computational findings. The records stand
as made.

- **Absys measurement build `5450449`:** an exact peak taken by walking the
  whole computation after every step. Fixed by `8a0eefd`, with labelled
  reruns (above).
- **SWI-Prolog, 16 invalid records (step accounting):**
  - *session* P05c and *session* P08a–c `unknown-fail` (12): a stage fails,
    the next is reposed, the replay fails at the same stage, and no restart
    cost can be read. Stages after the failing one are read as *not
    reached*.
  - storage runs of *plain*, *coroutines* and *constraints* P08a
    `unknown-fail` (3): step figures recorded where storage records must
    have none.
  - *constraints* P05a storage (1): a negative `between_answers`.
- **Absys P05a, 8 invalid records** (behaviour and cost in all three
  configurations, storage in absys-depth-first and absys-wake-back):
  invalid for the same restart-cost reason, around a genuine timeout at
  stage 2. Stage 3 is *not reached*: the replays did not get past stage 1.
- **SWI-Prolog, storage runs of P04a–d** in the four non-tabling
  configurations: an unparsed harness event recorded as *error*. The
  classifiers read them as *budget*, as in behaviour.
- **SWI-Prolog *session* P05a storage**, stage 3: no answer, against X = 3 in
  behaviour and cost. A fault of the instrumentation.
- **SWI-Prolog, P04b storage** (three configurations): the answer at 97
  steps against 5 in behaviour.
- **Python, 16 records:** "the program is not committed unchanged". In
  every one, the program's hash in the record equals the committed file.
  The harness's own `git status` failed while four systems ran against one
  working tree.

## Process notes

- **Parallel running.** From `b92cd18`, the rest of the batch ran as one
  job per configuration and problem, seven at a time, with 2 CPUs and
  4 GB each. No limit changed. Interrupted runs had written no record and
  were run from the start.
- **Harness revision during the batch.** The jobs mounted the working tree,
  so Absys runs that started after `98baa62` used that harness, in the old
  image, where it keeps the old path (qualified: 297 of 297). From batch
  1C, each batch runs from a read-only checkout of one commit.
- **The batch log.** `results/<system>/batch-log.tsv` was appended to by
  parallel jobs, and some lines are interleaved. The records, one file per
  run, are the evidence; the log is kept as it was. It holds no line at all for the
  *absys* configuration's P05 runs, whose 9 records exist. From batch 1C,
  each job has a log of its own (`tools/run-job.sh`).
- **Classifier briefs.** The first ten briefs (Python, ALGOL 60) said "batch
  1A" in their opening sentence. Their title, problem files and paths were
  1B's, and the classifiers read them so. Fixed in `fa93843`, before the
  Absys and SWI-Prolog briefs. The classifier B clone was moved from
  `3c7c778` to `b73d59a` while the Python and ALGOL 60 Codex runs were
  reading it. The change added nothing they read.
- **Classifier provenance.** A: Claude agents (Claude Opus 5.5), one per
  system and problem range. B: Codex (codex-cli 0.166.0, `codex exec`).
  Each worked in a clone and wrote outside the repository. Every command
  and read in their 18 transcripts was checked against the brief: none
  executed a program or the system, none read `calibration/`, `reviews/`,
  `variants/`, `transcripts/`, earlier classes or results, the authors'
  notes or the other classifier's output. Several directory listings (of
  A and of B) showed the names of forbidden files or folders, which were
  not opened; each is disclosed in that classifier's notes. The Absys P05 classifier A read the first five lines of
  `results/absys/RERUN-M2.md` by accident, stopped, and disclosed it. Two A agents
  and one B run wrote a scratch file outside their folder, deleted it and
  disclosed it.
