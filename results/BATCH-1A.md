# Batch 1A (P01–P03): what was done, and where the classifiers differ

Wave 1, batch 1A, on `spec-1.0.1`. Figures only; no ranking is computed,
and interpretation is kept out of `results/` (`PROTOCOL.md`, "Guarding
against bias"). The results themselves are the 42 files
`results/<system>/<configuration>/P0{1,2,3}.md`, assembled by
`tools/write-results.py` from the records and both classifiers' files.

## Chronology

| step | commit |
|---|---|
| harnesses qualified and published | `1fd1dfc` |
| `spec-1.0.1` (amendments 1–3) | `c4367b3` |
| programs, written independently and checked by syntax only, then audited | `aa7859e` … `be282ca`, audit `0102bfa` |
| run driver published before any run | `eaad40e` |
| 695 runs (behaviour, cost, storage; x1sim behaviour only); every run exited 0 and every record validates | `bfe78c6` |
| tokens (frozen tokenizer, one recorded mapping for x1/x1sim underlining) and the classifier brief | `628a324` |
| classifications A (Claude) and B (Codex), with agreement | `716268f` |

No program was changed after any run. The hidden variants (wave-1b) are
not opened: the verifier runs them after all of wave 1 is committed.

## Tokens by class, per classifier

Over every program text of the configuration (P02b's six orders
included), each shared text counted in each configuration that runs it.

| system | configuration | tokens | A: P C R S H | B: P C R S H | agreement |
|---|---|---|---|---|---|
| absys | absys | 606 | 606 0 0 0 0 | 606 0 0 0 0 | 100.0% |
| absys | absys-depth-first | 606 | 606 0 0 0 0 | 606 0 0 0 0 | 100.0% |
| absys | absys-wake-back | 606 | 606 0 0 0 0 | 606 0 0 0 0 | 100.0% |
| swi-prolog | plain | 3862 | 2887 80 208 0 687 | 2887 288 0 0 687 | 94.6% |
| swi-prolog | tabling | 3924 | 2887 142 208 0 687 | 2887 350 0 0 687 | 94.7% |
| swi-prolog | coroutines | 4710 | 3191 624 208 0 687 | 3175 848 0 0 687 | 95.2% |
| swi-prolog | constraints | 2526 | 1831 8 0 0 687 | 1831 8 0 0 687 | 100.0% |
| swi-prolog | session | 2526 | 1831 8 0 0 687 | 1831 8 0 0 687 | 100.0% |
| python | core | 5124 | 1307 0 1935 0 1882 | 1111 34 2168 0 1811 | 93.6% |
| python | stdlib-concurrency | 6212 | 1323 1321 1686 0 1882 | 1127 1054 2220 0 1811 | 90.1% |
| python | extended | 8269 | 2585 259 804 1668 2953 | 2074 498 1040 1917 2740 | 79.0% |
| algol-60 | report | 16070 | 3663 0 2694 0 9713 | 3642 0 2567 0 9861 | 96.4% |
| algol-60 | x1 | 14564 | 3402 0 2679 0 8483 | 3435 0 2552 0 8577 | 96.4% |
| algol-60 | x1sim | 14564 | 3402 0 2679 0 8483 | 3435 0 2552 0 8577 | 96.4% |

Per program, with the disputed constructs: each result file, and
`results/<system>/classes/agreement-tokens.txt`.

## Stage outcomes

`results/<system>/classes/agreement-outcomes.txt` (`tools/outcome-agreement.py`).

| system | stages | agree on every axis | disputed |
|---|---|---|---|
| absys | 102 | 102 | none |
| swi-prolog | 175 | 171 | P03f in plain, coroutines, constraints, session: A *complete* with *budget*, B *unsound* |
| python | 102 | 101 | extended P03f: A *complete*, B *unsound* (both *budget*) |
| algol-60 | 102 | 93 | simplification of P01a stages 1–2 and P01c's rational reading, in all three configurations: A *reduced*, B *reducible* |

Both P03f disputes turn on one rule: `SPECIFICATION.md` counts a binding
`observe()` reads at the budget as reported. A followed P03's own note
(complete with budget); B applied the rule literally (the tentative
binding is an invalid reported outcome). Both are reported.

## Classification-sensitive

Conclusions that change if one classifier's classes replace the other's
(`PROTOCOL.md`, "Guarding against bias"):

| what | A | B |
|---|---|---|
| SWI-Prolog *plain* and *tabling*, P02a–c: expressibility | not expressible (R3R1R2: with reformulation) | expressible |
| SWI-Prolog *coroutines*, P02a–c: expressibility | expressible with reformulation | expressible |
| SWI-Prolog P02, R tokens in plain, tabling, coroutines | 208 each (the `nonvar/1` mode tests, rule 19 by analogy) | 0 (the same tokens as C) |
| Python *extended*, P01b, P01c, P03b, c, d, f: expressibility | expressible | expressible with reformulation |
| Python *extended*, S tokens | 1,668 | 1,917 |
| semantic result of P03f at the budget (SWI-Prolog four configurations, Python extended) | complete | unsound |
| simplification of a held x = y (ALGOL 60 P01a) | reduced | reducible |

Expressibility agrees everywhere else: Absys, every sub-problem
expressible in all three configurations; ALGOL 60, P03a and P03e
expressible and the rest expressible with reformulation, in all three;
Python core and stdlib-concurrency as ALGOL 60; SWI-Prolog constraints and
session, all expressible.

## Harness observations raised by the classifiers

Recorded here, not corrected: the records stand as made.

- **SWI-Prolog, P03f storage runs** (plain, coroutines, constraints,
  session): the record says *error*; the harness could not parse its own
  budget event (the run reached the budget at 1,000,009 inferences). The
  answer matches the behaviour run.
- **SWI-Prolog, plain P02b.R3R1R2 stage 2:** 99 steps in the storage run
  against 7 in behaviour, where the harness says the two agree.
- **SWI-Prolog, restart_cost_source** says "stopped by budget" where the
  replay stopped on an error.
- **SWI-Prolog cost records** leave the step field `stage` empty and give
  the stage's own count as `to_end`; the result files show both columns.
- **Absys P03f, cost and storage** (all three configurations): both
  instrumented attempts (60 s, 600 s) hit the safety limit, so steps,
  store and repeated work are unavailable. The behaviour runs completed.
- **Every record** carries `spec_tag: spec-1.0`; the specification in force
  is `spec-1.0.1`, whose amendments change no harness behaviour.

## Classifier provenance

A: four Claude agents (Claude Opus 5.5), one per system. B: Codex
(codex-cli 0.166.0, `codex exec`), one per system. Each worked in its own
clone at `628a324` and wrote outside the repository. Every command and
read in their transcripts was checked against the brief: none read
`calibration/`, `reviews/`, `variants/`, the private store, the authors'
notes or the other classifier's output, and none ran a program or the
system. A's agents disclosed that the harness put the owner's memory
index into their context, unopened.
