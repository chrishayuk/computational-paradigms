# Independent classifier B: ALGOL 60, P04–P06

The artifact is `algol-60.json`. Its token keys follow the first paths in
`results/algol-60/tokens/TEXTS-1B-P04-P06.tsv`; a shared text is not counted
again. I verified every alias against its supplied frozen token sequence.
No configuration requires a different class for a shared text. The scope is
the P04–P06 manifest and the matching batch-log entries; the brief's isolated
reference to batch 1A does not change that explicit scope. There is no P08
program here, so `late_definition` is empty.

I did not execute an ALGOL program, compiler, interpreter, simulator, harness,
or measurement build. All checking scripts operate on permitted files and
on my own artifacts. I did not inspect another classifier's work.

## Token decisions and difficult constructs

**Relation evaluators versus holding machinery.** Rule 19 is decisive for
P05 and P06a–c. Arrived-relation flags, knownness tests, retained candidate
flags, the problem-specific propagation pass, and their declarations are R.
A fully known relation test and its accept/reject or contradiction verdict
are P, even inside an R evaluator. For example, in
`report/P06a.alg`, tokens 49–51 test knownness (R), 53–60 test the stated
negated equality (P), 66–68 record its contradiction (P), and 106–108 compute
x from the equality (P). The adjacent updates of knownness, changed-work and
held-relation flags remain R. `report/P05a.alg` similarly separates its
`test` procedure's flags/iteration from the inner comparisons on known xv
values. The program's local variable `inconsistent` denotes a semantic
verdict, rather than a scheduling instruction.

**P04 continuations and encoded unknowns.** In `report/P04a.alg`, the `equals`
definition at tokens 60–114 is split among the equality, the extra knownness
and continuation arguments, knownness dispatch, and restoration. The `found`
parameter is an added success continuation (R), including when its actual
argument happens to be an H printer. The printer's *definition* is H, but
that does not make the extra procedural argument part of the fixed harness.
The loop case and query branch order are P. I did not classify ordinary
recursion as C merely because it diverges.

In `report/P04c.alg` and `report/P04e.alg`, the equation evaluator at
295–411 and the alist definitions beginning at 412 contain the same split.
Construction, decomposition and equality of encoded sequences are P under
rule 15; knownness arguments and dispatch are R. Added `second`, `body`, and
`head` continuation declarations are R at their shells; the problem's
relation applications inside them are classed independently by rule 10.
`same` is equality of two already encoded finite sequences, not a general
unifier. `conseq` is the one equation needed by alist, not a general solver.

Restoring a temporary knownness flag immediately after `found` is C: it
undoes the temporary binding for the next branch. Releasing the just-made
cell with `top := top - 1` is C under rule 16. Initializing a knownness flag
before a query or recursive call is R instead. This distinction is
operationally meaningful but not stated explicitly for bindings in rule 16;
rule 2 supports C for restoration that also changes subsequent choices.

**No S mechanism.** These programs contain no mechanism general over
relations: no reusable scheduler, generic propagation store, unifier or
search interpreter. The repeated procedural pattern across P04 files is
problem-specific continuation plumbing, counted as R; repetition alone does
not meet rule 19's generality criterion. The general-looking `cons`,
`readseq`, and `same` procedures are operations on the systems-file encoding,
so rule 15 makes them P. The phase-4 list supplies no S mechanisms either.
The JSON includes a `mechanism: "none"`, zero-token entry for each program;
these are absence attestations, not counted mechanisms. This zero is known
absence of S, not an unavailable measurement.

**Facts versus invented enumeration.** The P05 loops read the given pick
facts. P06e's loops range over the supplied student, maths and takes facts.
These are P under rule 6, not generators over a domain invented by the
program. All p and k values are known before `takes(p,k)` is negated.
`mem` and `setdiff` in P06d follow the given cases in the query direction
(rules 2, 3 and 15); returning d through a function result does not make an
inverse relation or changed algorithm. There is no built-in substituting
for one of these defined relations.

**H and nested constructs.** Fixed instance/message reads and stage dispatch
are H; reads of the stage's constants and encoded facts are P. A declaration
is split when identifiers have different roles. In particular P06e's top-level
`i` indexes fact-input arrays as well as the instance-code loop, so its
declaration is P rather than harness-only H. Operation counters and counters
that only count reported values/conditions are H. Output-only procedures,
and the inline adapters that print an already computed binding, candidate
array or condition, are H under rule 13. Their tests choose formatting of
held state; they do not solve another computation to replace it. Thus the
large H total includes genuine output adapters rather than just I/O calls.
The report configuration's IFIP I/O procedures are external mechanisms as
listed in the systems file; the X1 versions use their X1 I/O procedures.

Rules 10 and 20 are applied to nested constructs and leading separators.
Block delimiters follow their introducing construct, not the first nested
counter or output statement. A semicolon between constructs and a comma
between arguments follow the construct after them. A declaration/call shell
can therefore be separated from its R argument spans. Several source-line
spans in the JSON are deliberately small at these boundaries. All indices
come from the frozen TSVs; no source was re-tokenized.

## Outcome decisions and residual proofs

**P04.** In report and x1, a/c/d produce no report before the step limit;
this is `none reported`, not an assertion of no solutions. P04b reports the
only valid value, x = 1, and is semantically complete despite then reaching
the budget. P04e reports true and finishes. P04f's collected answers are
exactly the a-sequences of lengths 0 through 19, so they are a nonempty
proper subset of the infinite valid outcome: partial / explicit / budget.
The full behaviour stdout contains 301 complete answer tags in report and
289 in x1, but the harness collects the first 20. Neither larger finite
prefix is a finite representation of the infinite set.

The right-recursive P04f program reaches successive lengths when its
callbacks work. The fixed cell array and finite machine store prevent a
literal assertion that *this executable*, given merely more steps, reaches
every finite length. Its 20000-cell capacity is a resource bound rather
than a test imposing a new mathematical domain for x or s. The left-recursive
P04c/d programs do not reach their first solution. There is no fairness
mechanism that rescues the finite branch.

All six x1sim P04 records end in error. P04b still reports its complete
answer x = 1; P04f reports only the empty sequence, hence partial. P04c/d
have `Error: Stack overflow`; P04e/f have the recorded unknown-formal-argument
descriptor errors. P04a/b instead end with SIGKILL and no error text. Their
records explicitly say `safety_limit.hit = false`, have only one attempt,
and classify error. The duration near 60 seconds is insufficient evidence
to substitute timeout or invent a missing safety rerun. The cause of those
SIGKILLs is unresolved by the permitted records.

**P05.** All three configurations report the exact surviving explicit values
for a: {1,2,3}, {2,3}, {3}; b stage 2: {2,3}; and c: {1,2,3}, then no
solution at both later stages. Their xv/xa arrays retain surviving values
all at once. Those values have already been printed: retaining them for a
future constraint does not mean an answers request would resume pending
search. I therefore retain `finished`, while reporting the actual
problem-defined alternative counts separately. The generic alternative
counter's null/`held_as: none` does not erase the textual all-live array.
Rejected values are withdrawn by their absence from the next reported set
and their cleared xa flags, without a separate retraction event. In P05c,
stage 3 is reached and does not revive a value from the already empty set.

P05b stage 1 is complete / residual / reduced / suspended. Its held r1 flag
and c1 = 1 are state tested at the next stage: the condition is exactly
x > 1. Primitive comparison semantics already restricts x to integers, so
this residual neither loses noninteger solutions nor imposes a finite
integer domain. Input and residual each have one primitive relation and
one unknown occurrence. The condition is identical to the posed information;
removing it would admit invalid x values. The 1000-slot pick array is storage
for supplied facts, not an enumeration of an unstated bounded domain for x.

**P06a/c stage 1.** Both hold exactly `not (x = 1)`, with xk false. This is
complete / residual / reduced / suspended, identical to the posed information,
with size 1 primitive relation / 1 unknown occurrence beside input 1 / 1.
The proof is symbolic identity over the specification's full Values domain,
not a finite sampling of integers. The integer slot xv has no selected value
while xk is false and supplies no domain guard to that condition. A typed
slot by itself is not an asserted constraint that an unknown is an integer;
otherwise this would have to be partial. The condition is actually evaluated
when the next stage arrives, satisfying the requirement for a held residual.
Negation is not decided prematurely. P06a then reports x = 2, matching P06b's
later result. P06b has x = 2 at both stages.

**P06c stage 2: an ambiguity in the specification that affects the class.**
The program detects inconsistency, prints `no solution`, suppresses its
`[answer]` block, clears the relation and ends. It also prints an unqualified
`[bind x]1[/bind]` (with dialect-specific whitespace). The specification says
that a held binding readable by `observe()` is reported, whether the answer
mechanism delivers it or not. Applying that sentence literally, the combined
report includes x = 1 although the valid outcome is empty: I class it
**unsound / explicit / finished** in all three configurations. I preserve the
correct no-solution message and the conflicting binding verbatim. This is
not a claim that its internal test missed the contradiction.

If an inconsistency flag were specified to invalidate every binding in the
same diagnostic state, the report would instead denote the empty set and
would be complete. The binding-as-reported rule contains no such exception
for P06c. This is the most consequential ambiguity in this batch. A future
amendment should say explicitly whether a binding within a failed context
is a query outcome. I did not silently choose that exception. The same
interpretation is applied to both measurement modes.

**P06d/e.** The observed difference is exactly (1,3). Nonmajor(brown) is true,
nonmajor(smith) reports no solution, and the unknown-p query returns brown.
These are complete / explicit / finished in every configuration. The fact
arrays and evaluation order establish that p and k are known before each
negation, rather than relying solely on the printed assertion about them.

No solved form or cyclic representation occurs. The nine residuals are all
reduced; none has a hidden inconsistency. In a stage with no report,
representation and residual-only fields are null. Residual equivalence is
null for explicit results because that particular check does not apply;
their finite answer sets are checked independently against the problem-file
sets by `build_results.py`.

## Expressibility

Expressibility is necessity of reformulation, not simply the presence of
some R tokens in this particular program. I judge P04a/b expressible by the
one recursive loop case and the assignment/reporting branch in presentation
order; loop never examines a value of x. P04e's known-sequence direction is
a direct case-by-case Boolean procedure. Their published knownness and
continuation plumbing is optional and is nevertheless counted as R.

P04c/d/f require the unknown-sequence direction within their given query or
recursive case, so the explicit continuations/unknown representation are
necessary reformulation. P05a/b/c and P06a/c use problem-specific retained
alternatives or undecided-relation state, also reformulation. P06b can assign
the value and then test its negation directly, so its reuse of the holding
loop does not make that order inexpressible without reformulation. P06d and
all P06e directions transcribe their cases directly. These judgments are
the same for all three configurations. The x1sim runtime failures are
separate execution evidence; they do not by themselves show that no
mode-faithful program can be written. No subproblem is judged to require a
general supporting mechanism or a meaning-changing reformulation.

## Harness, measurements and reproducibility

All 48 behaviour runs in the batch log have exactly one matching raw record;
every one of their 72 stages is reached. None of these records is named
`*.INVALID.json`, and none has a harness-fault entry. There is no stage here
whose replay stopped before reaching it. The specific fault/not-reached
rules therefore do not require additional entries in this subset.

I compared all 64 cost/storage records against behaviour, 96 stage
comparisons in total. Collected answers, observed state and all requested
classification axes agree. `mode_differences` is empty. Missing measurements
remain null/unavailable, including live store at unobservable boundaries;
no null was converted to zero. Recorded step/store differences between modes
are measurements, not differing semantic or execution classifications.
`raw-rerun-m2/` contains no records for this scope, and the allowed
`results/algol-60/rerun-m2-log.tsv` path is absent in this clone. Thus there
are no labelled measurement reruns to compare or replace. x1sim has behaviour
only, as its systems file specifies.

Input exhaustion after `[end]` in the interpreter configurations is the
fixed harness's process termination convention, not an error of the
completed stage. Re-created prefixes in report/x1 are retained in the
observation notes; their automatic re-creation is not counted as a manual
action. No record reports a manual intervention.

`classify.py` contains the construct annotations. `build_results.py` writes
the JSON and verifies text aliases, finite answers, residual identity proofs,
all batch-log entries, and both measurement modes. `validate_output.py`
independently reopens the saved JSON, checks exact contiguous token coverage
against every frozen first-path TSV, and matches its outcome keys and
verbatim answers to all behaviour records. `verification.json` holds totals;
`mode-comparisons.json` lists the 96 successful measurement comparisons.
The line correspondence used for dialect annotations is between the supplied
frozen token streams; it is not a tokenizer.

## Access disclosure

No excluded file's contents were read. One initial `ls` of the permitted
clone's root exposed **directory-entry names**, including excluded file names
`FREEZE-MANIFEST.md`, `LICENSE`, and `PINS.md`, and excluded directories
`calibration`, `reviews`, `sandbox`, `sources`, `tools`, `transcripts`, and
`variants`. I stopped that enumeration and did not open or descend into
those entries. This is recorded as accidental exposure of names, not as a
read of their contents. All subsequent repository reads were confined to
the brief's allowlist. No author's notes, other systems' files, earlier
classes/results, private directories, skill files, or web resources were
read. Own scripts and artifacts were written only in the designated output
directory. The unsuccessful attempt to read the allowed rerun-m2 log is
noted above.

## Totals

Counts below count each distinct text once, including shared texts only at their first path.

| Class | Tokens |
|---|---:|
| P | 5,049 |
| C | 160 |
| R | 2,136 |
| S | 0 |
| H | 9,138 |
| **Total** | **16,483** |

| Configuration | Complete | Partial | Unsound | None reported |
|---|---:|---:|---:|---:|
| report | 19 | 1 | 1 | 3 |
| x1 | 19 | 1 | 1 | 3 |
| x1sim | 18 | 1 | 1 | 4 |

28 texts cover 48 program paths; all 16,483 token indices are covered exactly once. The 72 behaviour stages comprise **56 complete, 3 partial, 3 unsound and 10 none reported**. Execution states are **47 finished, 9 suspended, 10 budget and 6 error**. There are **9 reduced residuals**, **0 mode differences**, and **0 S tokens**. Expressibility is **24 expressible and 24 expressible with reformulation**.
