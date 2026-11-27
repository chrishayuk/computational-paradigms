# Held-out calibration: P02

**Development examples, not results.** A check of the classification
rules on a problem they were not amended on, before the freeze. No figure
here is a result of the study.

P02 was chosen because it is staged: an imperative program has to hold
relations whose values have not arrived and take them up again later.
Rounds 1 and 2 (`calibration/README.md`) used P03 and P13, which have no
such code. Review 3 named this as the case where classifiers were most
likely to disagree, and rule 19 was written for it without being tested.

## What was done

| role | who | what |
|---|---|---|
| implementation author | a fresh Claude agent, reading only the public specification (draft 0.6), `problems/02`, the two systems files and the ALGOL 60 interpreter's own documentation | wrote P02 (a, b in all six orders, c) in Python *core* and ALGOL 60 *report*, and ran them ([`programs/`](programs), with its notes in `programs/README.md`) |
| tokenizer | `calibration/tools/tokens.py` | cut both programs into numbered tokens ([`tokens/`](tokens)) |
| classifier A | a fresh Claude agent | classed every token and every stage outcome ([`classes/A.json`](classes/A.json), notes in `classes/A.notes.md`) |
| classifier B | Codex (codex-cli 0.166.0) | did both independently ([`classes/B.json`](classes/B.json), notes in `classes/B.notes.md`) |

Neither classifier had taken part in round 1 or 2, and the brief
([`classifier-brief.md`](classifier-brief.md)) forbade reading the earlier
rounds' classes, their write-up, the author's notes and the reviews. Each
wrote outside the repository, where the other could not read. Codex's log
shows no read of a forbidden file. The comparison is
`calibration/tools/agreement.py`, and its full output is
[`agreement.txt`](agreement.txt).

Both programs gave the valid outcome at every stage of every run. Neither
was changed after it ran.

## Agreement

**Outcomes.** 22 stage outcomes per program, 44 in all. The classifiers
agreed on all 44 on the semantic axis (every one complete) and on all 44
on the representation axis. They agreed that every residual was
*reduced*. Classifier A also set the flag *identical to the posed
information* on the stages where only R1 or only R2 was held; classifier
B did not record that flag. The brief asked for "the simplification flag"
without naming this second flag, so the difference is the brief's, not
the rules'.

**Tokens.** 3,446 tokens in 2 programs.

| system | tokens | agreed | rate |
|---|---|---|---|
| Python | 1,573 | 1,385 | 88.0% |
| ALGOL 60 | 1,873 | 1,680 | 89.7% |
| both | 3,446 | 3,065 | 88.9% |

Against 99.9% in round 2 on the programs the rules were amended on. The
disagreements, as (A, B):

| A → B | Python | ALGOL 60 | where |
|---|---|---|---|
| R → P | 105 | 94 | branches of the relation evaluators that no run reached (R1 with v known first, R2 with w known), and the arithmetic in them |
| P → R | 69 | 44 | the tests of which places are known, inside the evaluators |
| H → R | 8 | 37 | the report's test of what is still held, which decides whether to derive the ten triples |
| R → C | 4 | 16 | resets between runs, and the loops over divisors' signs |
| other | 2 | 2 | |

## What the disagreements show

**One boundary, read two ways.** Almost all of it (312 of 381 tokens) is
inside the functions that evaluate R1, R2 and R3, where rule 3 (a
direction the queries do not use is R) meets rule 19 (code that holds
relations is R):

- A classed each direction by whether a run used it, so a branch that no
  order reached was R, and the tests of which places are known were part
  of the transcribed relation (P).
- B classed every direction as the relation itself (P), since the problem
  states it without a direction, and the tests of which places are known
  as the holding (R).

Both classifiers named exactly this boundary as the hardest, and both said
the rules did not settle it. B's reading is the defensible one. A class
that depends on which branches a run reaches cannot be fixed before any
program is run, and a hidden variant can reach a branch the original
constants do not.

**The paradigm question.** These disagreements are all in imperative
code, as in round 1, and for the same reason: the code is there because
the language lacks the mechanism, and the rules had said too little about
it. They move tokens between P and R, which is the ratio the study
reports, so the boundary matters and is not cosmetic.

## Clarifications made after the check

Made in `METRICS.md` and `SPECIFICATION.md`, marked "clarified after the
held-out check". **The check was not rerun under them,** so they are
untested, and the held-out figures above stand as the result of the check.

1. **Rule 19, evaluators.** Inside code that holds undecided relations,
   computing any place of a relation from the others, and testing a fully
   known relation, is P in every direction. The tests of which places are
   known, and the verdict to wait, are R. Which branches a run reaches
   never decides a class. This settles the first two rows, in B's
   direction.
2. **Rule 13, choosing what to report.** Code that decides which
   computation's result is reported is not an output adapter. This settles
   the third row, in B's direction. The rule's existing words ("code that
   computes anything the report depends on") already implied it.
3. **Two forms of report** (`SPECIFICATION.md`, "reported"). Where a
   program reports both the relations it holds and solutions derived from
   them, the representation is classified on the more explicit valid form,
   and the other is an observation. Both classifiers had done this, and
   both asked for it to be written down.

The R → C rows (resets, sign loops) are covered by rules 6 and 16 as they
stand; the classifiers applied them to different spans.

## What this does and does not show

The rules give the same outcome classes to two independent classifiers on
code they were not fitted to. They do not yet give the same token classes
there: 88.9%, with the gap concentrated in one boundary that both
classifiers identified. That boundary is now written down, but no
classifier has applied the written version. The first results of phase 6,
classified by both classifiers under the frozen rules, will show whether
it holds. Their agreement is reported with every result, and disputed
tokens are reported under both classes (`PROTOCOL.md`, Roles).
