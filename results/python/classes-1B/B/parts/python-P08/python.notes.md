# Python P08 — independent classifier B

I classified the nine texts in `results/python/tokens/TEXTS-1B-P08.tsv`,
using their supplied token indices, and all nine P08 behaviour records in
the batch log. There are 39 behaviour stages. Each has a separate entry
for the **open** and **closed** reading, identified by the additional
`reading` field, giving 78 outcome entries. The manifest has no shared-text
aliases or named P08 variants. I treated the explicit P08/1B manifest and
paths as controlling over the brief's incidental reference to batch 1A.

`classify.py` is my reproducible classification and coverage checker.
It parses source only to locate constructs; it never imports or executes
a study program, a harness, or an S implementation, and never regenerates
lexical tokens. `checks.json` records its counts and all 18 mode comparisons.
The repository was read only. All files created are in this output directory.

## Difficult token judgments

**General supporting mechanisms in nominal core and stdlib-concurrency.**
I classified the name-based relation store and dispatcher as **S**, not
R. `decide` accepts any arity of places and invokes an evaluator through
`EVALUATOR[name]`; it handles its evaluator's result protocol (wait,
failure, replacement relations, or bindings) without knowing which relation
is being decided. A new relation requires a table entry and evaluator,
not a change to the dispatcher. Likewise `hold`, `pose`, `told`, `settle`
and `arrived` implement a reusable evaluator/thread/definition protocol.
This meets rules 12 and 19's test of being general over relations and
reusable across problems. It is not made problem-specific merely by the
finite table of relations configured here.

For example, core/P08a has the generic store declarations at tokens
98–112, the evaluator table at 457–472, and generic lookup/dispatch at
473–654 (closing layout is assigned to the construct it closes).
The token spans provide the exact divisions, including nested adapters.
These runs retain their recorded configuration names in the JSON, but
their supplied general mechanisms must be credited as extensions, rather
than attributed to core. The stdlib programs additionally use the external
mechanism `threading` (`Condition`, `Thread`, locking, `wait_for`,
`notify_all`); threading itself is not experiment-written S. Their
additional relation/definition machinery is S.

This distinction is genuinely consequential and potentially disputed.
Rule 19 does not specify how much abstraction constitutes “general over
relations.” A reading that treats the fixed EVALUATOR table as making the
whole store problem-specific would assign much of my S to R, and change
the expressibility judgment. I chose the protocol's actual generality,
not the author's configuration label or its comments. Under rule 19 the
proper effective configuration for these mechanisms is extended; a
threaded version also requires its declared external threading mechanism.

**Evaluator versus holding.** Known-place tests and `return None` wait
verdicts in `equal`, `prefix`, and `reverse` are R under rule 19.
The actual equality/sequence checks, calculations, and substitutions are
P in all evaluator directions. The extra test that rev's definition has
arrived is C, beyond the case's own head (rules 1, 2 and 10).
Generic dispatcher implementation is S as a mechanism definition;
top-level calls requesting a pass, settling threads, scheduling an
application or signalling definition arrival are C. Arguments giving
the actual posed relations are P. Fixed constant reads inside them are
H. Their preceding comma follows that argument under rule 20.

**Transcription and encoding.** The forward `conc` and `rev` functions
use the problem's cases, with recursive rev evaluated before conc, and
are P under rules 2 and 3. They are not R merely because Python uses
functions. The extended case functions likewise transcribe those cases.
Fresh case variables and tuple/cons construction are P encoding operations
(rule 15); `cons` and `onto` only encode the supplied sequence terms.
Their use of `reversed` to construct a cons encoding does not replace the
problem's rev definition. Generic unification, goal-list resolution and
late-definition application dispatch are S (rules 12, 15 and 19).
There is no finite imposed domain, accumulator, case move or omitted
conjunct in these definition transcriptions. Tuple slicing/concatenation,
zip and the encoding operations execute built-in work not represented by
Python bytecode counts; they do not replace the defined rev/conc calls.

**Adapters and layout.** `show`, `report`, and `__repr__` only render
already-held state, so are H under rule 13, even when nested in an S
class. They do not derive another solution when one method fails.
Docstrings contribute no lexical token, but the frozen INDENT next to a
docstring still counts. INDENT/DEDENT are assigned to the construct they
open/close, including dedents before a differently classed statement and
at EOF. The checker uses the frozen layout tokens for this pairing.

**Mechanism accounting.** `s_mechanisms.tokens` counts the exact frozen
program S spans listed in that entry. For imported phase-4 mechanisms,
`implementation_tokens` separately records the frozen declared footprint:
176 for search and 537 for the suspension queue. No propagator is used.
Each implementation is charged once per configuration, not once for
each row listing a program that uses it. The imports account for 9 and
11 frozen S tokens per program text. Program-supplied S includes term
unification, goal-list resolution and the late-definition application
store; the last was not in the phase-4 mechanism list.

For a once-per-configuration P08 footprint, choose the P08a versions of
the common implementations: core's generic store 242; stdlib's named-place
component 51 plus threaded scheduler/store 397; extended's term unification
183, resolution 63, and application store 249. The c programs configure
smaller evaluator tables, reflected in their exact span counts. Repeated
copies/references in different full program texts are all classified, but
must not be summed as separate supporting mechanisms. Imported search and
suspension implementation add 713 once to extended, in addition to their
program integration tokens. The totals below are explicitly totals over
the nine token texts, before this separate mechanism accounting.

## Difficult outcome judgments and equivalence

**Core errors and unposed stages.** Each program raises
`NameError: name 'rev' is not defined` at stage 2. P08a stages 3–6,
P08b stage 3, and P08c stages 3–4 are *not reached*, not errors of their
own. The record explicitly says replay stops at stage 2. I did not treat
the misleading copied execution/error fields, waiting counts, or
`to_end: 0` as observations/measurements of those later stages. Their JSON
entries preserve the earlier failure as evidence, label it as such, and
replace the unavailable stage-end cost with null. Reposing is automatic,
not manual intervention.

At core/P08a and P08b stage 2, `observe()` can still read
`a=<x,y,z>`. Under SPECIFICATION's reported-binding rule this is a report,
despite no printed answer. It gives the open-reading solved solution set
with b free, but is unsound under the closed reading's empty set. The
rev list entry is dead state after an exception, not an application that
can resume on information arrival: later replay dies again. I therefore
do not count it as a live residual, using Outcomes 2's requirement that a
reported residual be held and acted on later. In P08c stage 2 there is
neither an observed binding nor a live residual: *none reported* under
both readings. An error is not a no-solutions assertion.

Whether the residual condition in Outcomes 2 should count dead registered
work after an error is ambiguous. Counting it would change these core
stage-2 representations and semantic judgments. I have made my exclusion
explicit, rather than hiding it behind the record's suspended count of 1.
The actual execution state is error, not suspended.

**Pending applications under the two readings.** Extended and stdlib
hold a live rev application while its definition is absent. Under open
semantics it is exactly the permitted pending residual. Under closed
semantics that same retained rev condition denotes the empty relation:
I class it complete / residual / *inconsistency undetected*. Waiting is
not itself an explicit report that there are no solutions. This applies
the specification's separation of semantic equivalence and simplification.

There is an interpretive ambiguity here: one could instead read a pending
application as only a scheduling object, with the report denoting just the
displayed equations even under the closed reading. That would make the
closed-reading pending reports unsound. I treat it as a residual condition
because it is registered, retained, and acted on when code arrives; that
is exactly why the open-reading result is residual rather than solved
form. The per-reading reasoning is repeated in the JSON entries.

Residual sizes count primitive query relations left undecided, and their
unknown occurrences after substituting solved bindings, beside the
cumulative posed query relations and occurrences. Definition clauses are
vocabulary, not additional query constraints. Sequence literals are
terms, not extra primitive relations. For a/b stage 2 the input is two
relations/six unknown occurrences; the remaining application is one
relation/four occurrences after substituting a. At stage 3, stdlib also
holds x=y (two relations/six occurrences versus input three/eight);
extended aliases x=y (one/four versus three/eight). The literal a binding
is recorded separately. `identical_to_posed` compares the represented
logical information including those bindings, ignoring storage encoding:
it is true for the unreduced pending information and false after aliasing
or resolving rev. The specification does not completely fix this
binding-versus-constraint convention for representation sizes or the flag;
the convention is explicit in every size object.

**Aliasing versus merely holding equality.** In stdlib a/b stage 3,
x=y is still a suspended equality, so the residual is reducible under
the open reading. At P08a stages 4 and 5, rev has produced
`b=<z,y,x>` but x=y (and then y=z) remain held. Together with those
bindings they are exactly the valid outcomes, not unsound merely because
the printer omits the held equations. Aliasing would eliminate the
remaining relations, hence reducible. Their residual/input sizes are
one relation/two occurrences versus three/eight at stage 4, and two/four
versus four/ten at stage 5.

**Extended's repeated printed `h`.** At P08a stage 4 the output prints
`a=<h,h,h>, b=<h,h,h>, x=h, y=h, z=h`. This is an output-name collision,
not an established identification of z with x=y. Each invocation of
rev_2/conc_2 allocates fresh Var objects. `unify` dereferences and binds
by object identity; it never identifies variables because their `.name`
strings match. By induction on the given cases, rev returns the reversed
list of the same variable objects and conc preserves those objects.
The held form is therefore
`x=y=u, z=v, a=<u,u,v>, b=<v,u,u>`, with independent u and v.
It is complete / solved form. This uses the valid held binding form
allowed by Outcomes 2; the ambiguous verbatim printed form is retained
and flagged. At stage 5 y=z identifies u and v; stage 6 binds them to 42
and c to <42,42>, giving the unique valid explicit result.

This proof uses the source and the registered bindings, not an execution
of the program and not an assumption that equal repr strings imply aliasing.
The 11 search iterator/mark entries at stages 4–6 are registered mechanism
choice points, held for depth-first continuation. They are not 11 valid
problem outcomes. The program never requests another answer; execution
is alternatives pending, as recorded.

**Lost c in stdlib/P08a stage 6.** All waiting work is gone, and a, b,
x, y and z have their required values, but c is neither bound nor
constrained. `place(c)` returns None before `prefix` is called. `prefix`
returns a replacement equality with that None value in place of the
original Unknown c, and `hold` cannot write a binding for it. Thus c is
free in the reported solved form. For example c=<> satisfies the reported
state but violates b=<42>++c. This is **unsound**, not partial or merely
an omitted printed binding: `observe()` also lacks c and any residual.
Relevant stdlib/P08a ranges include prefix's replacement generation
346–383, place 514–540, and hold's replacement/binding handling 681–773;
the exact construct splits are in the JSON.

**Partial definitions.** In extended and stdlib/P08c, stage 2 holds one
application distinguishable from failure. Stage 3 installs the actual
empty-sequence fact, wakes the application, fails on <1,2>, empties the
waiting structure and records/prints no solution. This is complete
explicit empty under closed semantics and unsound under open semantics.
Stage 4 installs the recursive case but does not restore/repose the
failed application; no solution remains reported under both readings,
which is unsound. The valid stage-3 closed conclusion should be withdrawn
at stage 4; no withdrawal is observed. These conclusions are based on
the failed structure and verbatim print, not solely on the empty
`queries.answers` array.

**Vacuous P08c stage 1.** The stage introduces only conc's definition,
with no query unknown introduced. Its empty observed substitution is
complete / solved form; silence here is not an assertion that there
are no solutions. This differs from the stage-2 error that reports no
binding or live condition.

## Definition arrival and expressibility

Core is **neither**: it calls the undefined name and errors.
Extended and stdlib are **code awaited**. The relational case functions
or forward definitions are installed by def statements only at the
specified information stages. Early extended rev/conc wrappers contain
no relation cases. The empty case table or defined flag witnesses the
absence/arrival of that code; it does not merely license a complete,
already-installed definition to run. The JSON gives the token ranges of
these constructs for each text. Although the complete source/bytecode
necessarily bundles later stage branches, this judgment is about when
the relation definition becomes installed and callable under the staged
program's ordinary execution, not introspection of unexecuted branches.
P08b keeps waiting when no code arrives. P08c demonstrates the limitation
that arrival of one part consumes the wait, even though more code can arrive.

I judge the full symbolic staged task **not expressible** in the nominal
core and stdlib configurations without their extra S mechanisms. The
forward relation functions individually are P transcriptions, but the
staged problem also requires unknowns and relation retention. In extended,
the admitted and explicitly named supplied mechanisms support the direct
definition-by-cases transcription: **expressible**, with all S credited.
This is a capability judgment about the configuration and definitions,
not a claim that every run computes correctly. Premature failure on partial
definitions and the lost tail remain outcome defects. This judgment is
sensitive to the rule-19 generality boundary described above. Directions
used are recorded with each subproblem; rev is only applied from a given
sequence structure to its output, with forward conc in its body.

## Modes, measurements and access

All 18 original cost/storage records were compared with their matching
behaviour record, including verbatim answers, printed failure reports,
observed bindings and pending/waiting structures, execution/error state,
and never-posed notes. Only address strings for iterator/generator objects
were normalized. No stage classification differs, so `mode_differences`
is empty. There are no P08 raw-rerun-m2 records in the permitted paths;
`results/python/rerun-m2-log.tsv` is absent in this clone. No INVALID P08
record or P08 `harness_faults` entry was found. Empty or null measurements,
unmeasured peaks, repeated work and unavailable problem-operation counts
are not imputed as zero. Actual zero pending/waiting counts are observations,
not missing measurements. No manual actions are recorded in any P08 run.

No forbidden or out-of-list file was read. Specifically, I did not read
author notes, another classifier's classes, earlier result summaries,
variants, calibration, reviews, transcripts, other systems, or any web
source. Permitted directory/path inventories did not open their linked
targets. Files read are within the allowed specification/problem files,
systems/python documentation, Python harness contract/mechanisms,
P08 program sources, frozen tokens/manifest, batch log and P08 raw records,
plus my own output/checking files. Failed attempts to locate the permitted
rerun log or records under P08a-style directories opened no file.

## Totals

All **10,545 frozen tokens** in all nine texts are covered exactly once.

| Text | P | C | R | S | H | Total |
|---|---:|---:|---:|---:|---:|---:|
| core/P08a.py | 448 | 4 | 86 | 242 | 319 | 1,099 |
| core/P08b.py | 325 | 4 | 86 | 242 | 269 | 926 |
| core/P08c.py | 345 | 4 | 55 | 238 | 321 | 963 |
| extended/P08a.py | 480 | 42 | 0 | 515 | 427 | 1,464 |
| extended/P08b.py | 148 | 18 | 0 | 515 | 387 | 1,068 |
| extended/P08c.py | 382 | 54 | 0 | 515 | 399 | 1,350 |
| stdlib-concurrency/P08a.py | 418 | 46 | 84 | 448 | 328 | 1,324 |
| stdlib-concurrency/P08b.py | 307 | 33 | 84 | 448 | 278 | 1,150 |
| stdlib-concurrency/P08c.py | 339 | 35 | 53 | 444 | 330 | 1,201 |
| **All texts** | **3,192** | **240** | **448** | **3,607** | **3,058** | **10,545** |

Across the 78 reading-specific entries: **52 complete, 10 unsound,
16 none reported**. Fourteen entries describe seven not-reached stages;
the other two none-reported entries are core/P08c stage 2 under both
readings. At the 39 actual stage positions: 14 finished, 12 suspended,
3 alternatives pending, 3 error, 7 not reached. No budget or timeout.
All 18 measurement comparisons agree in classification. Core errors on
undefined code; extended P08a reaches the valid final result; stdlib P08a
loses c; both waiting configurations retain P08c's premature failure.
