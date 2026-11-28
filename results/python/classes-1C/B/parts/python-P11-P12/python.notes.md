# Independent Python classification, batch 1C, P11–P12

Classifier B: OpenAI Codex. I did not write these programs and did not read
the other classifier's classifications. The source checkout is the one
identified in the brief as `bd43b8d`; I did not inspect Git internals.
Every raw record's recorded program SHA-256 matches the permitted source
file read for this classification. Nothing was written to that checkout.

`python.json` is the classification. `classify.py` constructs it from the
frozen token tables, source constructs and permitted records. `verify.py`
independently checks coverage, log/record completeness, program hashes,
effects logs, valid delivered answers and counterexamples to the observed
budget bindings. Neither script executes or imports any study program,
system, or harness. AST parsing identifies constructs and decodes literal
representations; it does not replace the frozen tokenizer. The scripts and
their verification output are published beside this note.

## Scope and completeness

The manifest contains 16 distinct texts: eight core and eight extended.
The eight stdlib-concurrency programs and their token tables are identical
to the corresponding core files. They use no concurrency module or other
added mechanism, so no token has a configuration-dependent class. Their
classes are consequently given once, under the manifest's core paths.
Their runs and expressibility judgements are still reported separately.

All six P11/P12 job logs reconcile exactly to 252 raw records: 84 behaviour,
84 cost and 84 storage. The behaviour records contain 96 stages, all
reached, with one attempt each. Every stage is fresh or incremental; none
depends on replay reaching a later stage. There are no named program
variants, `.INVALID.json` records, raw harness faults, or `raw-rerun-m2/`
records in this scope. All 192 cost/storage stage comparisons agree with
behaviour on the classified axes, delivered answers, observable bindings
and printed conclusions. Therefore `mode_differences` is empty. Added
storage measurements are observations, not classification differences.

There is no P08 here, so `late_definition` is empty.

## Construct decisions and ambiguities

The rule numbers in the JSON refer to METRICS.md unless another document
is named. Each token index is the supplied frozen index. Significant
INDENT/DEDENT tokens belong to the construct opening/closing that suite;
a DEDENT appearing on the next definition's source line is not silently
assigned to that next definition. Parent headers and nested statements are
separate constructs under rule 10. Separating commas follow rule 20.

**Transcription versus search.** Core `pick`, `choice` and their query
conjunctions are P under rules 2, 3, 6 and 8. In particular, the generator
in core P12 does not become a hand-written general search mechanism merely
because it generates alternatives. Its empty case, positive-n guard,
ordered l/r disjunction, recursive case and construction of the result
are the problem's definition in the required direction. Core P12a tokens
115–168 contain this definition, including its closing layout. The other
P12 files use the same executable AST outside their constants.

`accept(s): return s in facts` is an equivalent closed-world fact test,
P under rules 6, 7 and 9. This built-in membership may conceal work inside
one Python instruction. The case/disjunction enumerations are stated by
the problem and hence P; they are not generators of an unstated domain.
No program imposes an extra finite domain: P11 uses its own three pick
facts, and P12 uses the length bound and alphabet in its definition.

Explicit requests to advance a generator/search, selection of any-one
versus all, and breaks that stop enumeration are C. For example, core
P11a 191–199 requests the first outcome. This is a boundary ambiguity with
rule 13's allowance for stand-ins for fixed harness calls: I treated these
as executable search directives that determine progress and retained
alternatives, while treating the answer printer/collector as H. The P
query inside such a C wrapper is separately classed under rule 10.

**Staged holding.** P11c/d keep a selected provisional value, an encoded
list of added relations and a retained search. Their `holds`, `satisfies`,
`advance` and `add` code is problem-specific holding, R under rule 19,
rather than a reusable propagator, S. The fully known comparisons remain
P. For example, core P11c 140–176 is the encoded-relation dispatch with
its P evaluator calls at 159–166 and 168–175; 206–325 contains the holding
and advancement functions, with the explicit next request at 266–281 C.
The relation's encoding, state tests and retests are not made P merely
because they ultimately produce a valid answer. This split is identical
in all configurations. There is no definition-case omission or movement
of `accept` before `choice` in these programs.

**Commit, emit and H.** P11's explicit instruction that emit and commit
are P takes precedence over the harness README's general inclusion of
`cp.emit` in H. Thus, for example, core P11a 120–126 and core P11c 194–200
are P effects. Deferral would be C, but these programs do not defer effects
to commit. Selecting v and adding x = v is P commitment. Clearing the
unchosen generator/stack is C: after x = v has been added, clearing changes
retained work rather than the committed relation. Decoding a rendered
replay commitment by scanning the facts is R; for example, core P11c
342–368. Reading `s.commitment` itself is H, as fixed by the harness.

The stage receive loop, stage-number dispatch, input accesses and fixed
registrations are H. The nested reads of `s.constants`, `s.params` and
related fields are separated from the P or R constructs that use them,
including the comma preceding an H argument. Constants-block entries
themselves are P. `show`, `report`, output-only sentinels and a mapping
whose sole use is to expose an already computed answer are H under rule
13. The staged `known` mapping is R because subsequent computation uses
it to retain, retest and withdraw outcomes. No output adapter derives a
solution from the original relation in place of the computation.

**General mechanisms in extended.** `unify` is S, not P encoding code:
it is general over terms, aliases variables and undoes failed bindings.
`children` and `done` form a reusable interpreter of relation goal lists,
also S. P12's `either` adds generic disjunction over goal lists and is
counted as part of that interpreter, S. Its invocation with the two stated
l/r cases remains P inside `choice`. The boundary between such a generic
connective and a P rendition of disjunction is potentially disputable;
the implementation here accepts arbitrary goal lists and supplies the
general mechanism, rather than being confined to choice's two atoms.

Calls that implement a particular relation's head equality, and sequence
construction/conversion, remain P under rule 15. The implementation of
general unification remains S. Selecting/importing the mechanisms and
creating their binder, trail and stack are C configuration constructs,
not another copy of their S implementations. The unused `NIL = ()` in
each extended P11 file is a five-token remnant of the generic term-runtime
prelude, S with the unification mechanism; it is not P11 vocabulary.
In P12, NIL actually expresses the empty-sequence case and is P. The
frozen rules do not specifically discuss dead declarations; this is my
explicit treatment of this small ambiguity.

**Expressibility with optional S.** My judgement concerns what the stated
configuration can express, not whether its chosen program uses the fewest
mechanisms. All configurations include core. The core transcriptions
demonstrate expressibility for P11a/b and P12a–d. The core staged holding
programs demonstrate expressibility with reformulation for P11c/d. The
chosen extended programs add unification and resolution, fully charged
as S, without making that S native. I have not labelled the configuration
"not expressible" solely because its author chose optional S where the
permitted core program already establishes a transcription or an R
implementation. The specification's phrase "only ... supporting code"
would support a different judgement if it were intended as a judgement
of the selected text alone, rather than of the configuration. Both the
S dependency of the selected extended text and my expressibility reading
are explicit in the JSON. Hidden variants were not read; no claim of
passing hidden tests is made.

## Outcomes that required judgement

### P11: answer semantics, commitment and effects

P11 requests any one outcome at every stage, including the provisional
stages. Reporting x = 1 while {1,2,3} is admitted, or x = 2 while {2,3}
is admitted, is therefore complete for that query, rather than partial.
Effects are judged separately at the end of the problem.

| Subproblem | Reported outcomes by stage, every configuration | Final L | Effects |
|---|---|---|---|
| P11a | 2 | [2] | exact |
| P11b | 2 | [1,2] | extra |
| P11c | 1; 2; commit 2 | [1,2] | extra |
| P11d | 1; commit 1; explicitly no solution | [1] | exact |

Each emit occurs before commitment: in the one-stage cases emit precedes
the reporting that commits; in c/d it precedes the explicit commit stage.
Exact effects need not have occurred at commitment. P11c replaces the
reported provisional x = 1 by x = 2 but cannot withdraw the emitted 1.
P11d removes the binding after x != 1 and prints no solution; that is a
complete explicit empty report. Its previously committed effect 1 remains
exact under P11d's express exception. There are no reposing duplicates.
The raw classification JSONL logs agree exactly with the records' final
log snapshots. Cost/storage effect logs are observation logs and are not
added to the classification L.

### P12: observable bindings at budget

Core and stdlib-concurrency finish every all query, and give a valid
first answer for every any-one query. Extended does the same at n = 8 and
12; at n = 16 it exhausts 100,000,000 instructions in a.all, b.all, c.all,
c.any and d.all. These are budget stops, not timeouts. The later SIGKILL
mentioned in notes is teardown of the still-paused process, not a new
error or timeout for the already observed stage.

The difficult decision is SPECIFICATION.md Outcomes 1: a binding read by
observe() is reported even at budget, whether or not the standard answer
mechanism would deliver it. Extended registers the working Var s, not
just a dictionary of certified answers. At those five budget boundaries
it exposes an invalid tentative binding. I therefore class each stage
**unsound**, not merely partial or none reported. This is not an inference
that the search would accept that candidate if allowed to continue.

Concrete counterexamples are below. Strings abbreviate atom sequences;
the JSON preserves the cons representations verbatim.

| Extended n = 16 instance | Answers delivered before budget | Also observable at budget | Delivered-answers-only reading, for comparison |
|---|---|---|---|
| P12a.all | l^16 | lrllrllrrrrlrrlr | partial: r still missing |
| P12b.all | r | rlrlrrlrllrllll | complete answer set; search unfinished |
| P12c.all | none | lrlrllllllrlrrr ++ t | none reported |
| P12c.any | none | lrlrllllllrlrrr ++ t | none reported |
| P12d.all | l^16 | lrlrllllllrlrrlr | complete answer set; search unfinished |

The fully bound candidates are outside their closed-world accept sets.
For c, t is an unbound Var: setting it to the empty sequence already gives
an invalid l-prefixed sequence, and no completion of that prefix equals
the sole valid r^16. `verify.py` establishes these witnesses without
running the program. That visible binding is a non-equivalent solved
form, so c's two entries have `residual_equivalence.equivalent = false`.
The other three budget reports are explicit and unsound because they
include the invalid observed value as well as the delivered valid answer.

I did not reinterpret opaque pending-generator addresses as a printed
residual of choice and accept. They are unfinished search, with no
relation conditions exposed by observe(). The observed c term itself has
a free tail and no relation left in that represented term, hence solved
form. No reported residual occurs in this scope, so simplification,
identical-to-posed and residual-size fields are null. The restored free
Var s after successful exhaustive search is not a binding to a value or
prefix: the more explicit valid answer collection determines that stage's
representation, as Outcomes 2 directs. That is different from the bound
invalid candidates exposed at budget.

The raw harness gives budget priority over other execution states. I
retain budget for these actively interrupted searches and record their
remaining choice points as observations, rather than adding "alternatives
pending" as though the computation had stopped after answering. The
boundary counts are respectively 51, 48, 47, 47 and 51. No stage holds work
suspended on unavailable information. Suspended generator frames counted
in storage mode represent lazy search alternatives, not such waiting
relations.

P12's delivered answer order is depth first in all configurations. The
JSON records candidate positions derived from the cases separately from
measured total candidates: l^n is candidate n+1, r is 2^n+1, and r^n is
2^(n+1)-1. Program-defined partial-sequence counts and alternative peaks
are unavailable; no registered structure measures them. They are not 0.
Storage provides traced-allocation peaks, with the harness-allocation
confound stated in the records, not peaks of retained alternatives.
All cost/storage records are linked from their corresponding behaviour
stage, with measurements kept separate from classification differences.

## Supporting mechanisms and counting

Core and stdlib-concurrency use no S or imported external mechanism in
this scope. Each extended program uses the phase-4 backtracking search
(176 tokens) and the Var/deref/binding parts of the suspension queue
(full module 537 tokens), plus its own unification and resolution. No
program uses the finite-domain propagator, and none calls Queue.wait/run
to await information. The supplied modules' complete sizes are the
documented frozen phase-4 sizes; no token TSV for those modules was
supplied, and I did not re-tokenize them. Their call sites, setup and
program-local S are classed in the program TSVs as described above.

| Local implementation | Extended P11a/b | Extended P11c/d | Extended P12a |
|---|---|---|---|
| Unification body | 69–240 | 107–278 | 165–336 |
| Unused NIL prelude, with unification | 50–54 | 50–54 | not applicable: NIL is P |
| Resolution children | 241–285 | 279–323 | 337–381 |
| Resolution done | 286–298 | 324–336 | 382–394 |
| Resolution either | not used | not used | 421–441 |

These are inclusive frozen ranges. P12b–d have different-sized constants
blocks, so their exact shifted ranges are in `s_mechanisms`, not copied
from P12a. There are 172 tokens in the unification function, 45 in
children, 13 in done and 21 in either. The unused P11 prelude adds 5.
The s_mechanisms rows are per-program references, not a direction to add
the same module or function repeatedly. The once-per-extended-configuration
inventory used by this batch is 176 + 537 + 172 + 45 + 13 + 21 + 5 =
**969 S tokens**. Raw token-span totals necessarily count repeated copies
in the different program texts; that figure is separately reported below.

## Access record

No file outside the brief's permitted list was read. In particular no
author README/audit, calibration, review, hidden variant, transcript,
earlier classification/result report, other system folder, private home
directory or web source was consulted. File-name inventories were confined
to the permitted program/token/raw/log trees and the output directory.
An initial search for AGENTS.md in the output directory returned no file.
My own scripts, JSON and verification artifacts were read in that allowed
output directory. No prohibited file was encountered accidentally.

## Totals

Exactly **10,096 frozen tokens** in **16 distinct texts**, covered once
each by **1,140 construct spans**: **P 3,540; C 850; R 732; S 1,944;
H 3,030**. These are manifest-text totals, including repeated local S
implementations; the once-per-configuration S inventory is 969 as above.

Across **96 behaviour stages**: **91 complete, 5 unsound**; **94 explicit,
2 solved form**, no residuals; **41 finished, 50 alternatives pending,
5 budget**. All stages were reached; none suspended, errored or timed out.
P11 has **6 exact and 6 extra** final effect classifications, none missing.
All **192 measurement-stage comparisons** agree; no mode differences.
