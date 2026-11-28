# Batch 1C (P09–P12): what was done, and where the classifiers differ

Wave 1, batch 1C, on `spec-1.0.1`. Figures only. No ranking is computed,
and interpretation is kept out of `results/` (`PROTOCOL.md`, "Guarding
against bias"). The results are `results/<system>/<configuration>/P{09..12}.md`,
assembled by `tools/write-results.py --classes classes-1C` from the
records and both classifiers' files.

**Absys P12 is pending.** Its runs in *absys-depth-first* are complete;
in *absys* and *absys-wake-back* they are running (each n = 16 run reaches
the safety limit at 60 s and again at 600 s). Its records, classification
and result files will be added to this file when they are done. Every
other figure below is for P09–P11 in Absys, and P09–P12 in the other
three systems.

## Chronology

| step | commit |
|---|---|
| implementation authors, from `1f291be`; audited (`programs/AUDIT-1C.md`) | `aa04900`, `ed33aef`, `50115c5`, `899e49b`; audit `0f7de92` |
| tokens of every P09–P12 program | `4339969` |
| runs, from a read-only checkout at `0f7de92`, one log per job (`tools/run-job.sh`) | from 28 November, 05:02 UTC; records `43bec0a` |
| run driver: a program may be named for a dot-prefix of the instance id | `697063a` |
| Absys P12, from a second read-only checkout at `eefc839` | running |
| classifier text lists per problem range; classifications A (Claude) and B (Codex) from clones at `bd43b8d` | `bd43b8d`; this commit |

No program was changed after any run.

## Runs

| system | runs | records that validate | harness faults (`*.INVALID.json`) |
|---|---|---|---|
| Absys (P09–P11) | 171 | 162 | 9 |
| SWI-Prolog | 570 | 570 | 0 |
| Python | 342 | 342 | 0 |
| ALGOL 60 | 266 | 266 | 0 |

No measurement rerun was needed: no cost or storage run reached the
safety limit where its behaviour run did not. Eight Absys P09 cost records
are over 50 MB (72 to 128 MB; 0.2 to 18 MB compressed) and are committed
as `.json.gz`.

**Absys P12, first attempt.** The first run of the three Absys P12 jobs
found no program for any instance (72 lines `no program` in
`results/absys/logs/1C-absys-*-P12.tsv`, kept). The author wrote one file
per sub-problem and n (`P12a.n8.ab1`) to serve both answer modes
(`P12a.n8.all`, `P12a.n8.any`); the driver looked only for the whole
instance id or the sub-problem id. `697063a` adds the dot-prefix; checked
against every instance of batch 1C, it changes only these 72 Absys runs.
They are run from a second read-only checkout, with logs
`results/absys/logs/1C-p12-*.tsv`.

## Tokens by class, per classifier

Over every distinct program text of the configuration, each shared text
counted once in each configuration that runs it.

| system | configuration | tokens | A: P C R S H | B: P C R S H | agreement |
|---|---|---|---|---|---|
| absys (P09–P11) | absys | 1143 | 864 2 277 0 0 | 826 2 295 0 20 | 96.7% |
| absys (P09–P11) | absys-depth-first | 1143 | 864 2 277 0 0 | 826 2 295 0 20 | 96.7% |
| absys (P09–P11) | absys-wake-back | 1143 | 864 2 277 0 0 | 826 2 295 0 20 | 96.7% |
| swi-prolog | plain | 2709 | 1819 44 122 0 724 | 1708 95 182 0 724 | 94.3% |
| swi-prolog | tabling | 2767 | 1819 102 122 0 724 | 1708 153 182 0 724 | 94.4% |
| swi-prolog | coroutines | 2864 | 1817 163 160 0 724 | 1712 202 226 0 724 | 94.2% |
| swi-prolog | constraints | 2675 | 1855 60 36 0 724 | 1689 144 118 0 724 | 92.9% |
| swi-prolog | session | 2675 | 1855 60 36 0 724 | 1689 144 118 0 724 | 92.9% |
| python | core | 6271 | 2701 30 739 165 2636 | 2388 254 1049 0 2580 | 86.3% |
| python | stdlib-concurrency | 8409 | 3151 84 890 1458 2826 | 2801 900 1326 662 2720 | 80.6% |
| python | extended | 11539 | 3749 281 1084 2786 3639 | 3442 989 1128 2543 3437 | 89.8% |
| algol-60 | report | 8923 | 2041 78 537 0 6267 | 1778 186 600 53 6306 | 95.9% |
| algol-60 | x1 | 8158 | 1927 77 537 0 5617 | 1664 185 600 53 5656 | 95.5% |
| algol-60 | x1sim | 8158 | 1927 77 537 0 5617 | 1664 185 600 53 5656 | 95.5% |

Per program, with the disputed constructs: each result file, and
`results/<system>/classes-1C/agreement-tokens.txt`.

## Stage outcomes

`results/<system>/classes-1C/agreement-outcomes.txt` (`tools/outcome-agreement.py`).
Some differences are of labels only: A names P09d's readings *P09d1* and
*P09d2*, B *finite* and *stream*, with the same values. They are counted
in the tool's figures below and listed beside them.

| system | stages | semantic | representation | simplification | identical to posed | execution state | of which labels only |
|---|---|---|---|---|---|---|---|
| absys (P09–P11) | 99 | 83 | 54 | 88 | 85 | 99 | semantic 3 |
| swi-prolog | 260 | 255 | 255 | 257 | 260 | 260 | semantic 5, simplification 3 |
| python | 156 | 156 | 154 | 156 | 156 | 156 | — |
| algol-60 | 156 | 150 | 156 | 156 | 156 | 139 | semantic 3 |

The remaining three ALGOL 60 semantic differences are of form: P09a.AB's
computation B, which A gives as *not reached* and B as `reached: false`
with no semantic class.

Outcomes on which **both** classifiers agree, and which are not
*complete*:

- **SWI-Prolog *session* P11d, stage 3: unsound.** The commit stage's
  answer x = 1 was taken by the harness from a separate run; at stage 3
  the program backtracked through the commit and answered x = 2.
- **Python *extended* P12a, P12b, P12d (n = 16, all) and P12c (n = 16,
  all and any-one): unsound.** Each reached the step budget (10⁸) while
  the bindings, readable at the budget, held a candidate under test.
  Classifier A gives beside each the class on the answers alone (P12a
  partial, P12b and P12d complete, P12c none reported).
- **Absys P09b (primary), computation B, every configuration: unsound.**
  The two computations are conjoined in one session; A's failure removes
  the only derivation, and y = 3 is reported as having no solution.
- **Absys P10d, every configuration:** stage 2 none reported (final
  timeout at 600 s); stage 3 *not reached* (harness fault, below).
- **ALGOL 60 *x1sim* P12, every instance: none reported, error**
  (`Unknown descriptor of formal procedure: 40600011`, no output). The
  same text runs in *x1*.
- **ALGOL 60 P09a.AB, computation B: not reached**, in every
  configuration: A ends the one process. In P09a.BA, B is complete.

## Effects (P11)

| system | P11a | P11b | P11c | P11d |
|---|---|---|---|---|
| Absys (named variants for P11a–b) | extra | extra | extra | extra |
| SWI-Prolog | exact | extra | extra | extra |
| Python | exact | extra | extra | exact |
| ALGOL 60 | exact | extra | extra | extra (⟨1, 2, 3⟩) |

Both classifiers, every configuration of the system.

## Expressibility: where the classifiers differ

Compared per configuration and sub-problem (P09d by reading).

| system | configurations | sub-problem | A | B |
|---|---|---|---|---|
| Absys | all three | P09a, P09b | with reformulation (the computations are conjoined; the named `or` variants keep each computation's outcomes) | not expressible (separate computations cannot be transcribed; the `or` variants share one report between the two queries) |
| Absys | all three | P10d | with reformulation (withdrawal by restating, of a fresh unknown) | not expressible (discarded derivations cannot be revived; not generic) |
| Absys | all three | P11c, P11d | expressible (the commit stage is one omission, judged by the problem's rule for a system that cannot select) | not expressible (commitment cannot be transcribed) |
| SWI-Prolog | plain, tabling | P09e, P10b | not expressible (the program errs on the problem's own input) | with reformulation (the definitions keep the relation; the error is of execution) |
| SWI-Prolog | all five | P11c, P11d | expressible | with reformulation |
| SWI-Prolog | all five | P10c | with reformulation | expressible |
| SWI-Prolog | constraints, session | P10b | with reformulation | expressible |
| Python | all three | P09d2 | with reformulation (a lazy encoding would keep the meaning; not written) | not expressible (no stream representation in the program) |
| Python | extended, stdlib-concurrency | P09c, P09d1 | with reformulation | expressible |
| ALGOL 60 | all three | P09b | expressible | with reformulation |
| ALGOL 60 | all three | P09d2 | with reformulation | not expressible |
| ALGOL 60 | all three | P12a–d | with reformulation (`choice` transcribed by its cases, P; the extra parameter R) | not expressible in the configuration: the program supplies a continuation-based depth-first search (S, 53 tokens), not listed at phase 4 |

## Classification-sensitive

Conclusions that change if one classifier's classes replace the other's:

| what | A | B |
|---|---|---|
| ALGOL 60 P12: is `choice` with its continuation a hand-written search? | no: P, with 13 R tokens | yes: S, 53 tokens per configuration; then P12 in ALGOL 60 uses program-supplied S, and belongs in an extended configuration |
| Python *core* P09e and *stdlib-concurrency* P09c–e, P10b, P10d: is the holding or thread code S? | yes: S (rule 19, reusable), 165 tokens in core P09e, 195–349 per stdlib text; these programs belong in an extended configuration | core P09e: R; stdlib P09c–d: S (331), the rest R |
| Absys P11: `tout("emit", x)` | P (problem file P11, Rules) | H (harness README), 20 tokens |
| Absys P09a, P09b named `or` variants | complete, and none reported for the computation never answered | complete, and unsound (the shared report gives B's solution to A's query) |
| Absys P09c (absys, absys-wake-back): one derivation holds the answer, 15 others still running | residual, reducible | explicit |
| Absys P10a, P10c | explicit | solved form |
| Absys P10b stages 2–4 | explicit | residual, reducible |
| ALGOL 60 P11c–d, stages holding pick's untried facts | alternatives pending | finished |
| SWI-Prolog P09d1 in coroutines, constraints, session | complete / residual / inconsistency undetected (the held producer has no finite solution) | the same |

For the last row both agree; A notes that read without the held goal it
would be unsound.

Two of the documents classifiers are told to follow disagree on emit: the
problem file of P11 says emit is a problem token, the harness READMEs list
every emit call as H. Seven of the eight classifier runs over P11 followed
the problem file. The specification is not changed for this batch.

## Supporting mechanisms

Python's are accounted in `results/python/extended/MECHANISMS.md`, batch
1C section. *extended*'s programs supply unification (172–188 tokens) and
resolution (58–79) again, and relation adapters for the queue (92–179);
both classifiers agree on these. ALGOL 60 P12 by B's reading: above. No
Absys or SWI-Prolog program uses S; SWI-Prolog *session*'s listed
wait-for-definition code is loaded and not exercised.

## Diagnostics and timings (not records of the study)

- **The safety limit is wall-clock, under parallel load.** Seven jobs ran at
  once, 2 CPUs each. Absys P09d's behaviour runs reached 60 s and ended on
  their rerun at 117–127 s; their cost and storage runs, later, ended on
  the first attempt at 40–47 s. ALGOL 60 *x1sim* P09a's behaviour runs
  ended on their reruns at 69 s. No outcome changed: each stage ended
  within its rerun.
- **ALGOL 60 *x1sim* P09a (A then B), computation A:** on its rerun the
  process was killed (SIGKILL) at about 69 s with no message, below the
  600 s limit. Out of memory was confirmed for batch 1B's *x1sim* P04a by
  the container's diagnostics; it was not checked for this run.
- **ALGOL 60 *x1sim*:** P09d stops with "Wrong result type in TIRD", P12
  with "Unknown descriptor of formal procedure", from the reconstructed X1
  run-time; the same texts run in *x1*.

## Harness and measurement defects

Recorded here, apart from the computational findings. The records stand
as made.

- **Absys P10d, 9 invalid records** (behaviour, cost and storage in all
  three configurations): stage 2 reaches the safety limit at 60 s and
  600 s; stage 3 is reposed, and the separate run of stages 1–2 for its
  restart cost is stopped at 600 s, so no restart cost can be read. The
  same fault as batch 1B's Absys P05a. Stage 3 is *not reached*.
- **SWI-Prolog, 6 storage runs** (P09a.BA in plain, coroutines, constraints
  and session; P09a.AB in session; P09d in plain): an unparsed budget event
  recorded as an error, with steps unavailable; in session P09a.AB, B's
  answer is missing too. The same fault as batch 1B's P04 storage runs.
  8 mode differences in both classifiers' files.
- **SWI-Prolog storage step counts** differ from behaviour by up to about
  5% in P12 outside tabling (classifier A), where the harness README says
  they are equal. Cost runs are the figures of record.
- **Python *stdlib-concurrency* P09a.AB:** computation B's steps are 0 in
  the behaviour and cost runs, against 219 in the storage run and in the
  B-then-A order (classifier A). Read as unavailable.
- **SWI-Prolog *session* P11d:** the harness selects the commit stage's
  answer from a separate run, and the program contract has the program
  read it back; the engine itself does not commit, and stage 3 backtracks
  through the commit. The outcome stands as classified (unsound); whether
  the selection meets the harness contract for P11 is an open question,
  not adjudicated here.

## Process notes

- **Read-only checkout.** Every run of this batch mounted a clone of one
  commit read-only, with only `results/` writable (`tools/run-job.sh`).
  Each job wrote its own log, `results/<system>/logs/1C-<configuration>-<problem>.tsv`.
- **Classifier provenance.** A: Claude agents (Claude Opus 5.5), one per
  system and problem range. B: Codex (codex-cli 0.166.0, `codex exec`).
  Each worked in a clone at `bd43b8d` and wrote outside the repository.
  Every command and read in their 14 transcripts was checked against the
  brief: none executed a program or the system, none read `calibration/`,
  `reviews/`, `variants/`, `transcripts/`, earlier classes or results, the
  authors' notes or the other classifier's output. All seven A agents read
  their own long outputs where the tool saved them under
  `~/.claude/.../tool-results/` (each checked against the agent's own
  calls: copies of allowed files); five disclosed it, two (ALGOL 60
  P11–P12, Python P09–P10) did not. One B run (Absys)
  listed file names with `rg --files` that included forbidden paths, and
  opened none; disclosed. Several directory listings showed names of
  earlier classes folders, which were not opened.
- **Codex launch.** The first launch of the seven B runs failed before any
  started (`xargs: command line cannot be assembled`); they were started
  again, unchanged, from a script.
