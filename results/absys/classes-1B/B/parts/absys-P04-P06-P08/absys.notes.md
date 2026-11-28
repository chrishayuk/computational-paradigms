# Independent classifier B: Absys, batch 1B, P04/P06/P07/P08

Classifier provenance: Codex (OpenAI). These are my own classifications from the permitted specification, programs,
frozen token tables and raw records. I did not write or execute the programs,
run Absys, consult the web, or inspect another classifier's work. All writes
were made inside this output directory. The source repository was only read.

`absys.json` contains 90 behaviour runs, 138 actual behaviour stages and 189
outcome entries: each P08 stage has separate `reading: "open"` and
`reading: "closed"` entries. The other stages have one entry. The program
field preserves the `variants/` component. Record paths are relative to the
source repository. The 30 token keys are the first paths from
`TEXTS-1B-P04-P06-P08.tsv`; their classifications also apply to both listed
copies. I checked that every copy's program bytes and frozen token table are
identical. No configuration needs different token classes.

## Token decisions that needed judgement

* **Native scheduling is not program control code.** The recursive `loop`
  case, both `alist` definitions, their presentation orders, and their
  queries are P. They are the specified relations even when they run forever.
  None of these texts has a `key`, delay, generator or scheduling declaration.
  A configuration's search flag is not a token in these programs.
* **Constants blocks are P.** Although the harness substitutes this table
  rather than executing it, each entry supplies a problem constant. The
  frozen tokenizer includes the entries, and the harness README, section
  3.12, says the constants are classed by their role rather than being H.
  Markers and author comments have no frozen tokens.
* **P07a orders are P.** All six are requested instances in P07. They are not
  unrequested moves under rule 4. The same argument applies to the two
  specified `alist` presentations. Arithmetic decompositions and native
  backward arithmetic are P; the problem states integer relations.
* **P08c's extra name is R, not S or a permission gate.** In
  `absys/P08c.ab1`, 77–83 are the extra `or revmore(p,r)` case, 86–92
  introduce the additional lambda, and 116 closes that lambda: 15 R tokens.
  Its recursive head and body, 93–115, are the original case and remain P
  under rule 10. The existing `rev` header and its closing punctuation belong
  to the problem's definition, not to the added call. The extra definition is
  specific factoring of this relation, not a reusable wait-for-definition
  mechanism. Native application of an unbound procedure name supplies the
  waiting; no S implementation or permission test is hidden in the program.
* **The literal P08c variant remains P.** Its stage 3 and stage 4 equations
  contain exactly the individually arriving cases. Neither case is omitted
  from the program; I therefore did not invoke rule 4 on their headers.
  Absys's equation-on-a-procedure interpretation fails to implement additive
  case arrival, and the outcomes record that failure. This is a difficult
  boundary between an unsuccessful transcription and reformulation: labelling
  those headers R because equating two lambdas is not additive would also be
  a plausible reading of the broad definition of R. I used the explicit
  requested stage text as the boundary. The primary needs R to preserve the
  application through partial definition arrival.
* **The set-form variant is P under P06d's express permission and rule 7.**
  Its `set` binder, 61–64, has that explicit rule. All the other membership,
  negation, result and query constructs retain their own P roles. The actual
  report `<1,3>` is correct for this instance. A set of distinct selected
  values is not generally an ordered sequence difference preserving repeated
  occurrences: for example, filtering `<1,1>` against `<2>` should preserve
  two copies of 1. This exposes an ambiguity in “may state the same
  definition” and rule 7's example; I have not treated the permission as a
  proof of general sequence semantics or inspected hidden variants. The
  primary recursive definition does preserve occurrences, and determines
  expressibility for P06d.

The frozen rules do not unambiguously distinguish a text that states the
requested cases in the system's own notation but computes the wrong thing
from a meaning-changing reformulation. I applied the specific permissions
and stage descriptions above, kept execution correctness separate, and have
not silently introduced a new classification rule.

## Outcome decisions that needed judgement

**A printed computation is not necessarily an explicit answer.** In
depth-first P04a, both derivations are still elaborating: one holds
`loop(x)`, the other has `x = 1` **to do**. The latter has no x binding.
Nevertheless, Absys reports its retained state through the standard mechanism,
and these are actual queued processes, not an adapter echoing the question.
Under the specified least relation, `loop(x)` has no instances. The finite
printed disjunction therefore denotes exactly `x=1`: complete / residual /
reducible / budget, identical to the posed query. It has obtained 0/1
explicit answers. In P04b, and in P04a with the other two configurations,
`x=1` has executed and is readable: I classify the more explicit valid form,
as Outcomes 2 instructs, and record the still-running loop separately. The
alternative count is 2, but these are not “alternatives pending” in the
specification's request-for-more-answers sense; the harness contract says
Absys has no such stop state.

This distinction is classification-sensitive. Treating every running
derivation as no report would give “none reported” for depth-first P04a.
Treating a queued binding as already executed would incorrectly give an
explicit answer. My choice uses the reported residual's denotation and
records explicit answer completeness separately. `check_equivalence.py`
checks the actual printed obligations rather than accepting an unbound x as
an unrestricted solved-form answer.

**P04d/P04f have no observable infinite enumeration.** All six behaviour
runs end after an unrequested SIGKILL with no state printed. They are reached,
none reported / representation null / error. The harness attributes the
signal to container memory exhaustion; the signal itself is the observation,
not independent proof of its cause. No answer sequence, retained-store count
or fairness result can be reconstructed from these missing states. The
finite P04c/P04e recognition queries finish successfully in every configuration.

**Negation with an unknown is decided too early.** P06a stage 1 and P06c
stage 1 report no derivations, although every value other than 1 is valid.
P06a stage 2 also reports none although x=2 is valid. These are unsound,
not “none reported”: the system explicitly reports emptiness. P06c stage 2
is complete because its valid set is now empty. P06b holds x=2 at both
stages. The matching cost traces in every configuration show stage 1
starting `not(x=1)`, the independent computation binding its x to 1 and
hibernating, then the parent failing. Stage 1 takes five measured machine
steps. The trace does not number the four printed events by machine step,
so I do not invent an exact machine-step number for the fail event. In
P06e3 all negations begin with both person and course ground; BROWN alone
survives. P06d and both set variants report `<1,3>`.

**Zero work in an empty computation is not a stage never reached.** Every
behaviour stage here is delivered incrementally. This includes P06a/P06c
stage 2 and literal P08c stage 4 after their derivations have disappeared.
Their measurement runs replay and deliver the same sections, sometimes doing
zero steps in the final section. No record in this slice says a requested
stage was not reached because replay stopped earlier. I checked the attempt
notes for such statements. This applies AMENDMENTS 3.2 without converting a
delivered assertion into a skipped stage.

**P07 holds meaningful integer constraints.** P07b retains
`x+y=10; 4+y=x`, equivalent to the requested two equations and therefore
complete, but reducible to (7,3). Its identical flag is false because the
second equation is reoriented. P07c holds exactly its single input equation,
complete / residual / reduced. P07f holds both contradictory equations,
complete / residual / inconsistency undetected, rather than unsound merely
because it did not detect the empty set. P07g's `x*x=9` denotes both roots,
so is complete, but reducible to the two explicit alternatives. It has not
enumerated either root. P07e detects its integer inconsistency. No imposed
finite domain or rational solution is present. These conclusions use exact
algebra, not a bounded sample of integers.

**Waiting for code chooses an open operational state.** In P08 the
uninstantiated procedure identifier is a variable awaiting a lambda value,
not an extensional relation fixed to the empty set. I therefore classify
the held missing-code application as complete under open and unsound under
closed before the relevant case arrives. This is the basis for the
reading-specific semantics, not a claim that suspension itself is an error.
There is a real interpretive boundary here: if a reader interprets the
printed missing-code obligation as the *closed reading's false relation*,
its denotation would instead be empty and could be called complete with
inconsistency undetected. I did not use that reading of a free procedure
variable; the record explicitly says it waits for a definition and later
acts on that value. Known `loop` code in P04 does have the specified least
relation, unlike this still-unknown procedure value.

For an open application awaiting code, I call a single pending application
reduced when no known definition can simplify it. Although dropping that
application leaves the same current bindings (and P08 explicitly allows
that to be a complete *current* solved form), dropping is not a reduction
preserving the retained obligation for later stages. The specification does
not fully explain how simplification should treat this case; this is my
operationally preserving reading. Actual drops and failures are recorded
separately. No application is silently dropped in the primary programs.

In P08a, stage 4 resumes the application on arrival of actual rev/conc code.
Stage 4 still holds seven equality processes between unknowns, and stage 5
holds eight. I classify these as residual / reducible rather than solved
form: the printer says they are suspended processes and the machine has not
substituted their equality classes into the list terms. Existentially
eliminating local h variables gives exactly the valid solved forms.
`check_equivalence.py` checks the components in all three behaviour records:

* Stage 4: `{x,y,h1,h2,h6}` and `{z,h3,h4,h5}`; consequently
  `a=<y,y,z>, b=<z,y,y>`.
* Stage 5: all nine variables join one component; consequently
  `x=y=z, a=b=<z,z,z>`.

Stage 6 binds the component to 42, gives c=<42,42>, and finishes. P08b
retains its missing-code application through the end. Primary P08c first
waits for rev, then waits for revmore after rejecting the empty case, then
resumes when that code arrives. It is code awaited, not permission awaited.
The literal variant also awaits code at stage 2, but applying the partial
definition at stage 3 fails and removes the application. Its stage 3 report
is complete under closed and unsound under open; its final no-solutions
report is unsound under both. All four P08 programs are explicitly described
in `late_definition`, including that limitation of the literal variant.
No run withdraws an earlier no-solutions conclusion or requires manual action.

## Residual sizes and checks

`residual_size` gives numeric input and residual counts side by side. Input
counts data assertions after primitive arithmetic decomposition; procedural
definition cases are not added as new query constraints. Solved list bindings
are shown separately from relations left to decide. Unknown occurrences in
the undecided processes are counted with multiplicity, including fresh local
variables. Thus x*x=9 has one relation and two occurrences; P08a's seven
equality processes have fourteen occurrences. The a/b term bindings are not
counted again as undecided relations. This makes explicit the distinction
between a term binding and Absys's still-held equality processes. Sizes are
about representations, not source token counts or the number of suspensions
registered internally on already-bound variables. `identical_to_posed`
ignores notation and resolving the constants table, but is false after an
equation is reoriented, a bound input is substituted into a call, or an
application is expanded.

`classify.py` constructs the JSON and checks every frozen index exactly once,
in order, without re-tokenizing. `check_equivalence.py` checks 40 behaviour
residuals against the hand arguments (including the equality graphs and exact
P07 residuals). The other residual instances use the same two P08
missing-code obligations under separate readings. All 288 measurement-stage
final state prints were also compared byte for byte with their matching
behaviour-stage state print; every one agrees. This comparison uses `print`,
not the extra question-command suffix that behaviour adds to `observe.raw`.

## Measurement comparisons and harness faults

There are 180 original measurement records and twelve labelled m2 records.
The twelve original P04d/P04f cost/storage stages time out at both safety
limits (60s and 600s), whereas behaviour is SIGKILL/error. Those twelve
execution-state differences, with both classifications, are the only entries
in `mode_differences`. The semantic result is none reported in each case.
The twelve m2 reruns match behaviour: none reported / error, no state or
measurements. Thus they correctly add no difference entry. Each m2 record's
notes identify its original record; both originals and reruns were retained
and compared, and neither replaced a behaviour result. Their comparison is:

| configurations | instances | modes | original vs behaviour | m2 vs behaviour |
|---|---|---|---|---|
| absys, absys-depth-first, absys-wake-back | P04d, P04f | cost, storage | timeout vs error; both none reported | error vs error; both none reported |

All twelve reruns' steps, retained alternatives, suspensions and store are
unavailable; missing measurements are never read as zero. Elsewhere the
classification agrees in every mode. Routine reposing in cost/storage is
the fixed measurement contract, not a new intervention or a semantic
classification difference. The only difference in these limited runs is the
stop mechanism, not evidence that an instrumented model is less expressive.
I found no `*.INVALID.json` and no nonempty `harness_faults` in these 282
records; every outcome entry has `harness_fault: false`.

## Access boundary

No file outside the user's permitted list was read. Directory inventories
displayed filenames, including the excluded `programs/absys/README.md`, but
I did not open that file or any audit, classes, result summary, private
directory or other system. The permitted README/specification/program
comments mention excluded directories and documents; I did not follow those
references. No calibration tool was read. Own checking scripts and their
generated JSON in this authorized output directory were read during checks.

## Totals

The 30 distinct texts contain **1,436 frozen tokens: P 1,421; C 0; R 15;
S 0; H 0**. These same totals apply separately to each of the three
configurations; summing configuration copies would give 4,308 tokens
(P 4,263; R 45). All 90 program/configuration entries use no S mechanism.
Expressibility has 72 entries including the two P08a directions: 69
expressible, three expressible with reformulation (P08c), none not
expressible.

Across 189 outcome entries, including both P08 readings: **144 complete,
39 unsound, six none reported**; no partial or undetermined entries.
Representations are 92 explicit, 24 solved form, 67 residual and six null.
Of the residual entries, 33 are reduced, 31 reducible and three inconsistency
undetected. Execution is 111 finished, 66 suspended, six budget and six
error. Each configuration has 48 complete, 13 unsound and two none reported
entries. The 138 underlying behaviour stages are all reached. There are
**12 measurement classification differences**, and all twelve m2 reruns
agree with behaviour.
