# Independent classifier B: ALGOL 60, batch 1C, P09/P10

I did not write these programs and did not consult another classifier's work.
The source clone was read only. Only this output directory was written. No
ALGOL program, interpreter, compiler, harness, qualification, or system was run.
The Python checking script reads the frozen token tables and the permitted
evidence; it never re-tokenizes a program.

## Evidence and coverage

The first paths in `TEXTS-1C-P09-P10.tsv` identify 18 distinct texts.
The script checks that every alias has identical program bytes and identical
frozen token rows. The report AB/BA texts share one classification. The X1
texts also cover x1sim, and its AB/BA aliases. No class changes with the
configuration: X1 output/input calls are its own procedures; the report
IFIP procedures are external mechanisms, but their token classes still
follow their role (constant input P, harness words and output adapters H).

There are 30 behaviour records and 40 measurement records: 20 cost and
20 storage. The six permitted batch-1C job logs reconcile exactly with
those 70 record jobs. The older batch log and measurement-rerun log contain
no P09/P10 jobs, and the permitted P09/P10 measurement-rerun directories
contain no records. There are no INVALID records, harness_faults entries,
named variants, or P08 programs in this assignment. `late_definition` is
therefore empty. Every program has an explicit zero-S entry.

The JSON uses the logged instance `P09d` plus a `reading` field for its
two judgements, rather than inventing two runs. Spawned computations have
separate entries. Both safety attempts are preserved with `attempt` and
`final_attempt`; use the latter for final outcomes. There are 76 entries
including retries and both readings, or 72 final entries. An unreached
computation has `reached:false`, null outcome axes, no execution state of
its own, and the stopping explanation. It is not counted as its own error.
Observe blocks are attempt-wide; a B binding in P09a.BA is not an A answer.

## Difficult token decisions

* Sequence cell construction, decomposition, input assembly and its storage
  are P (systems Values; rules 3 and 15). Forward conc/rev/gen and sum3
  follow the given cases. The recursive call before the constructor in
  genu is P; it is not an added fairness directive or an omitted base case:
  the problem itself gives no base case. The initial top=0 in a newly
  allocated local encoding is P, not a store-reuse reset (16).
* The unused knownness and continuation arguments of loop are still extra
  arguments (R, 3/5), although they do not explain its nontermination.
  This incidental R does not make the recursive relation itself
  inexpressible. Argument punctuation follows the following argument (20).
* P09b's scalar `equals` wrapper is the hardest boundary. I class the
  extra knownness/continuation wrapper R; binding a place and comparing
  fully known equality are P; invoking the selected continuation is C;
  restoring its temporary knownness is C. It implements this problem's
  scalar equality/conjunction, not a general structured-value unifier,
  relation store, or search engine. I therefore find no S mechanism.
  I record the supplied equality implementation as expressible with
  reformulation; a more direct native assignment/test transcription would
  make a defensible expressibility disagreement here.
* P09e has hard-coded evaluators for two equations. All arithmetic
  evaluations and the fully known tests are P in BOTH directions (19),
  even though this run reaches none of them. Known-place dispatch and
  relation retention are R. Convergence flags and the repeated-pass loop
  are C. `propagate` is R/C rather than S: it cannot accept an arbitrary
  relation or evaluator. Its procedure name does not decide its class.
* P10b's active standing relation, knownness and re-evaluation call are R;
  the multiplication is P. Its recomputation counter is H. P10a/P10c
  availability flags are H because only output reads them: no evaluator
  waits on them. This differs from P10b's bk flag, which gates computation.
* P10d's fact input and traversal of facts are P (6), not a generator of
  unstated integers. Live-value and comparison-activity storage is R (19).
  Testing the fully known comparison is P. Disabling its activity is R,
  and the withdrawal-display flag is H. Traversal purely for output, case
  numbering and operation counters is H (13 and harness 2.7).
* Pure printers, including branches and decimal-digit arithmetic wholly
  inside num/digits/printseq, are H (13). Tests that suppress an inconsistent
  computed outcome are separately C under rule 2. Semicolon separators
  follow the next construct (20), including at changes of class. Introducers
  and nested statements follow rule 10 rather than inheriting a surrounding
  relation-holder's class without examination.

The phase-4 S list supplies no mechanisms in any configuration. I found no
program-supplied mechanism general over relations. The R/C mechanisms are
still charged in full; they are not credited as native suspension,
propagation, retraction of logical facts, or concurrency.

## Outcomes and equivalence

* P09a: in report/x1, A reaches budget. In AB, B never starts; in BA,
  B explicitly reports (3,2,1) before A starts. B does not progress while
  A runs. The X1 simulator has no enforced step budget. Its first attempts
  time out at 60 seconds. The 600-second retries actually end after about
  69 seconds with SIGKILL, no error text and `safety_limit.hit:false`.
  I preserve the recorded error, not a conjectured second timeout, and
  cannot determine the kill's cause from these records. Both retries
  retain the same order-sensitive B result.
* P09b: A explicitly observes no solution, so this is complete/explicit
  for the empty set, not none reported. B independently reports y=3.
  Logical failure is isolated; a process-ending stop in P09a is not.
* P09c: the observation states that gen finished before sum3 began.
  Induction on gen's cases gives (1,2,3,4,5); the sole sum3 case gives 6.
  The explicit outcome is exact, with no producer/consumer overlap.
* P09d: no s or total is observed in any configuration. Report/x1 exhaust
  budget; x1sim reports `Error: Wrong result type in TIRD\n`.
  Under the finite reading genu has no finite instances, but the run does
  not report successful exhaustion or no solution: none reported. Under
  the stream reading no total=6 is exposed either: also none reported.
  No finite-domain partial-result inference is warranted: no cell is
  constructed before the recursive call returns, and no answer is given.
* P09e: a genuine problem-specific pair of executable held equations is
  read by observe, not just a literal echo. Its residual is exactly the
  posed information, complete and reducible, with two primitive relations
  and four occurrences of unknowns. Algebraically y=x-1 iff x=y+1 over
  the integer domain. Thus its solutions are exactly (t+1,t), and one
  equation can be removed, reducing the size to one relation/two
  occurrences. No finite interval or enumeration is used. The suspended
  count is two held equations; each was examined once. ALGOL's process
  ending does not turn the reported waiting relation state into a solved
  form or a native suspension facility.
* P10a: b=10,15,7. P10b first holds d=2*b, then reports (b,d)=(10,20),
  (15,30),(7,14). The first stage is complete/reduced/residual, identical
  to the posed one primitive relation with two unknown occurrences.
  Arithmetic expressions are not solved-form term constructors under
  the specification. Later stages have explicit valid values and keep
  the standing relation as an observation. Exactly one dependent value
  is recomputed per replacement; cumulative counts are 0,1,2,3.
* P10c: b=10 with d unassigned, then (10,20),(15,20),(7,20). d is a
  named quantity with no value at stage 1, not a free logical variable
  or an unsolved multiplication. Assignments preserve its snapshot.
* P10d: all 1,2,3 are held, then 2,3, then 1,2,3. The facts remain
  stored when their live flags change; withdrawing the comparison does
  not require re-input of pick. The comparison withdrawal is printed.
  The new answer set omits x=1 at stage 2; there is no separate explicit
  cancellation event for that prior answer. Retained live data after
  printing every answer is not `alternatives pending`: asking for more
  answers does not resume an unfinished enumeration. The explicit set
  is the problem's stated finite set, not an imposed finite domain.

All P10 replacements overwrite ordinary variables; no older value can be
retrieved from a version history. The records contain no manual actions.
The report/x1 harness recreates prefixes for budgets and validates identical
prefix output; x1sim receives the stages in one live process. I preserve
those confounds rather than attributing recreation to the program.

For every cost/storage run the checker compares actual answer strings,
observe blocks, execution classifications and semantic/representation axes
with behaviour, as well as independently computing expected reported values
from the permitted constants. All agree. `mode_differences` is empty.
Null measurements remain unavailable. No unmeasured suspended/alternative
count is silently changed to zero; exact held-relation counts are used only
where printed. After a stop, missing bindings are not inferred from source.

## Ambiguities and limits of these judgements

Rules 1/2, 3 and 19 leave a narrow boundary between imperative continuation
scaffolding and a transcription of equality/conjunction. My split above is
explicit, so another classifier can disagree without losing the P evaluator
inside R code. The special H treatment of output adapters also makes their
fairly large decimal-printer bodies H; I apply that frozen rule consistently.

The definition of a residual says the program holds and acts on its state
"at a later stage". Read literally as requiring an actually occurring later
stage, it would reject the specification's own single-stage residual examples
as well as P09e. I read it as requiring genuine held/evaluable state, rather
than a printed copy of the question. P09e has knownness bits, relation flags,
evaluators, a propagation pass and observe access to those same flags and
constants. Its one-stage execution is reported as such; no later resumption
is claimed. P10b also demonstrates actual evaluation at subsequent stages.

Expressibility is kept separate from producing an answer within a limit.
In particular, eager recursion can transcribe a finite least relation even
when it gives no answer. My P09d2 `not expressible` judgement is relative to
the provided eager finite-sequence transcription: it does not express the
greatest-relation stream or expose its total. This is the most contestable
expressibility judgement. A problem-specific prefix/stream representation
could instead be proposed as reformulation; no such program or R tokens
are present here. I do not infer a theorem that ALGOL cannot implement it.
No inaccessible hidden variants were consulted, so expressibility claims
about generic constants are based on the supplied algorithms and input
contract, not on any claimed hidden-variant pass.

I identify no frozen rule that should be silently replaced or changed. The
points above are readings that should remain visible in a disagreement.

## Files read and access discipline

No file outside the user's permitted list was read, accidentally or
otherwise. In particular, no calibration, reviews, variants, transcripts,
earlier classifications, result summaries, author README/audits, other
system folders, private directories, skills, or web sources were opened.
Permitted README/specification text contains links naming some excluded
locations; none was followed.

Evidence read: README.md, SPECIFICATION.md, METRICS.md, PROTOCOL.md,
AMENDMENTS.md; the six permitted problems files; systems/algol-60/README.md;
harnesses/README.md, stages.json and record.schema.json; the ALGOL harness
README, S-mechanisms and QUESTIONS; the P09/P10 program and constants files
in report/x1/x1sim; their frozen token tables and TEXTS manifest; all 70
permitted P09/P10 raw records; the six corresponding batch-1C log files,
and the two permitted older/measurement-rerun logs filtered to these
problems. Listing the permitted systems/harness subtree revealed filenames
only; no qualification programs or records were executed. Files created
and subsequently read here are classify.py, algol-60.json and these notes.

## Totals

| Frozen text (first path) | P | C | R | S | H | Total |
|---|---:|---:|---:|---:|---:|---:|
| report/P09a.AB.alg | 334 | 0 | 22 | 0 | 617 | 973 |
| report/P09b.alg | 48 | 7 | 76 | 0 | 234 | 365 |
| report/P09c.alg | 253 | 0 | 0 | 0 | 515 | 768 |
| report/P09d.alg | 218 | 0 | 0 | 0 | 178 | 396 |
| report/P09e.alg | 62 | 41 | 138 | 0 | 595 | 836 |
| report/P10a.alg | 36 | 0 | 0 | 0 | 196 | 232 |
| report/P10b.alg | 51 | 0 | 42 | 0 | 399 | 492 |
| report/P10c.alg | 52 | 0 | 0 | 0 | 271 | 323 |
| report/P10d.alg | 78 | 0 | 57 | 0 | 640 | 775 |
| x1/P09a.AB.a60 | 328 | 0 | 22 | 0 | 560 | 910 |
| x1/P09b.a60 | 39 | 7 | 76 | 0 | 219 | 341 |
| x1/P09c.a60 | 250 | 0 | 0 | 0 | 470 | 720 |
| x1/P09d.a60 | 215 | 0 | 0 | 0 | 161 | 376 |
| x1/P09e.a60 | 56 | 41 | 138 | 0 | 533 | 768 |
| x1/P10a.a60 | 27 | 0 | 0 | 0 | 177 | 204 |
| x1/P10b.a60 | 39 | 0 | 42 | 0 | 341 | 422 |
| x1/P10c.a60 | 40 | 0 | 0 | 0 | 242 | 282 |
| x1/P10d.a60 | 69 | 0 | 57 | 0 | 562 | 688 |

Unique-text tokens: P=2195, C=96, R=670, S=0, H=6910; total=9871. Every index is covered exactly once.

Final outcomes (72 entries, separate computations and both P09d readings): 57 complete, 12 none reported, 3 not reached; 51 finished, 8 budget, 6 suspended, 4 error, plus the 3 unreached computations. Six residuals are equivalent: three reducible P09e residuals and three reduced P10b stage-1 residuals. The four additional first-attempt entries preserve two timeouts, one complete B outcome and one unreached B. There are no mode differences, no S tokens, and no manual actions.
