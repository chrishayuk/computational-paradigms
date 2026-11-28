# Classifier A (Claude agent): swi-prolog, batch 1B, P04, notes

Output: `swi-prolog.json` beside this file. Scripts I wrote and used, all here:
`summarise.py` / `table.py` (read the records), `check_answers.py` (checks every
reported answer against the valid outcomes of `problems/04-unbounded-alternative.md`),
`build.py` (token spans, with a coverage check; `spans-check.txt` prints each
span's tokens), `outcomes.py` (writes the JSON from the spans and the records).

## Texts

Twelve distinct texts (`TEXTS-1B-P04.tsv`). `constraints/P04a.pl` … `P04f.pl` are
also the texts of plain, coroutines and session (I checked byte equality with
`cmp`). I did not class any of them separately for session. Session loads
`S/session-wait.pl`, but that code is not in the program text, and it never
fires in P04 because every procedure called is defined. So no token's class
changes.

## Constructs that were hard to class

1. **`memberchk(alternative_value(K), Cs)` / `memberchk(alist_argument(S), Cs)`.**
   This goal reads the stage's constant out of the list the harness passes.
   I classed it **P** under rule 1: without it, K (or S) is unbound and the
   query's solutions change. The harness contract requires this access
   pattern, so the goal could be argued to be H, a stand-in for a harness
   call. But rule 13's H exemption covers output adapters only, and harness
   README 12 says stage bodies are classed by METRICS. memberchk/2 is listed
   as an external mechanism (library(lists), outside plain's core). In each
   of P04a, b, c and e this is 9 tokens. A classifier who reads it as H
   would move 36 P tokens to H in each configuration.
2. **The CONSTANTS block entry** (`alternative_value(1).`, `alist_argument([a, a]).`).
   The tokenizer counted it. I classed it **P**, as the stage's information.
   Its markers are comments.
3. **The `.` ending a `stage/3` clause.** The head is H, including `:-`
   (harness README 12), and the body is P. The README does not say where the
   terminator goes. I gave it **H**, with the clause frame. Rule 20 cannot
   decide it, because the terminator is not a separator. The `.` ending a
   definition clause stays with that clause (P). One token per text.
4. **`:- table loop/1.` / `:- table alist/1.`** These are **C**: METRICS lists
   tabling declarations, and removing one changes termination, not the
   least-relation solutions (rule 1). In tabling they change P04a from
   budget to complete/finished, and P04f from a fair enumeration to a
   timeout. The class is clear-cut, but the effect is large.
5. The program has no reformulation. Cases, conjuncts and disjuncts are all
   in presentation order, so there are 0 R tokens and no moves or omissions.

## Outcomes that were hard to class

1. **P04f (untabled), 20 answers at the cap.** I classed this as *partial*
   (a nonempty proper subset of an infinite set) with *alternatives pending*.
   I also record that the enumeration is fair: every solution would be
   reached, the length-n sequence being answer n+1. The problem file says
   to compare this property, not the count. An equally defensible reading is
   that a cap-limited enumeration of an infinite set is "complete up to the
   cap". The spec's wording points to *partial*.
2. **P04b (untabled), X = 1 then budget.** I classed this as *complete*,
   because answers reported before the budget are classified, and
   *budget*, because the harness asked for a second answer and loop(X) ran
   to the budget.
3. **Tabling P04c, P04d and P04f: timeout, not budget.** The final attempt
   (600 s) reached only 962186, 891860 and 652229 inferences, all under the
   10^6 budget. SLG table work is largely not counted as inferences. The
   one rerun was done, so *timeout* is final (PROTOCOL, safety limit). This
   matters for comparison: under the same budget, the untabled runs stop on
   *budget* in under 1 s.
4. **Storage runs with harness faults (16 records).** These are the storage
   runs of P04a to P04d in plain, coroutines, constraints and session. None
   is named `*.INVALID.json`, and there are no INVALID records anywhere in
   P04. Yet each has a `harness_faults` entry: an unreadable, interleaved
   event, after which there is no end event. The record's state is `error`
   with `determined: false`, "not the system's error". In the reposed
   configurations the exit status is 3; in session it is 0. The fragment of
   the event that survives shows the budget exception in each case, so I
   class these stages *budget*, as in behaviour, and set
   `harness_fault: true` in `mode_differences`. The strict reading would be
   *error*. I list both, with the recorded state and the state as I class
   it. The semantic result agrees with behaviour in every case.
5. **Steps discrepancy.** In plain, coroutines and constraints, the
   P04b storage run reports X = 1 at `steps_at` 97, against 5 in behaviour
   and cost (session's storage run gives 5). The harness says storage steps
   equal behaviour steps (README 6). I report this as an instrumentation
   discrepancy. It does not affect any class.
6. Cost runs agree with behaviour in every classification. Tabling's
   timeout step counts differ from run to run, as expected of a
   wall-clock limit. Tabling's storage runs also agree with behaviour.
   There are no `raw-rerun-m2/` directories and no `rerun-m2-log.tsv` for
   P04.
7. Alternatives in behaviour mode are null, and I read them as
   *unavailable*, not 0 (AMENDMENTS 3.1). Where a storage run measured them,
   I quote it: P04f has 1 clause choicepoint at every answer.

## Rules I think ambiguous

- Harness README 12 does not say how to class the terminator of a harness
  contract clause, or a stage body's goal that only reads the passed
  constants (items 1 and 3 above). These two choices account for all the
  room two classifiers have to disagree on these texts.
- The brief says to set `harness_fault` only on `*.INVALID.json` records.
  Records that carry `harness_faults` but were kept under the normal name
  (here, with exit 3) are not covered. I treated them the same way.
- The batch log has no line for `tabling P04f storage`. The record
  exists, `P04f.storage.20261128T003131Z.json`. The log's last P04 line is
  tabling P04f cost. This does not matter for the behaviour runs, which are
  all logged and all have records.

## Files read outside the list

None. Every file I read was in the brief's list (the specification files,
`problems/04`, `systems/swi-prolog/README.md`, the harness README, the
S-mechanisms file and `S/session-wait.pl`, a grep of the harness
`QUESTIONS.md` for S17 and S18, `harnesses/stages.json`, the P04 programs, the P04
records, `batch-log.tsv` and the token files). Two listings went slightly
wider: `ls programs/swi-prolog/*/`, which shows other problems' file names,
and the top-level `ls`. I did not open the author's `programs/swi-prolog/README.md`.
The tabling programs' comments cite that README, and I did not follow the
citation.

## Summary

**Tokens** (788 over the 12 distinct texts; no S, no R):

| | P | C | R | S | H | total |
|---|---|---|---|---|---|---|
| plain, coroutines, constraints, session (same 6 texts) | 212 | 0 | 0 | 0 | 164 | 376 each |
| tabling | 212 | 36 | 0 | 0 | 164 | 412 |

The 36 C tokens are six table/1 directives of 6 tokens each.

**Outcomes** (30 behaviour stages, one per configuration and instance;
harness_fault false for all of them):

| instance | plain / coroutines / constraints / session | tabling |
|---|---|---|
| P04a | none reported, budget | complete, explicit, finished |
| P04b | complete, explicit, budget (X = 1 at 5 steps) | complete, explicit, finished |
| P04c | none reported, budget (left recursion) | none reported, timeout (final) |
| P04d | none reported, budget; no solution ever reached | none reported, timeout (final) |
| P04e | complete, explicit, finished | complete, explicit, finished |
| P04f | partial, explicit, alternatives pending; 20 answers by length, fair | none reported, timeout (final) |

No residual or solved form is reported anywhere, and nothing is suspended
(session-wait never fires). There are 16 mode differences, all
storage-mode harness faults on budget stages, which I class as budget.
Every subproblem is *expressible* in every configuration. There are no
late-definition entries, since P08 is not in this batch. The only S
mechanism is session's listed wait-for-definition hook: loaded, never
exercised, with 0 program tokens.
