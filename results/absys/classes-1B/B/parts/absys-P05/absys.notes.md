# Independent classification: absys, batch 1B, P05

Classifier: Codex, independent classifier B. The source repository is the clone named in the brief, `~/cp-roles/classifier-1B-B3`, at the user-stated commit `1f291be`. I did not write the programs, inspect another classifier's work, run a program, run the system, or modify the source clone. All generated files are in the authorized output directory.

## Scope and evidence

The text manifest contains P05a.ab1, P05b.ab1 and P05c.ab1 under `absys/`; each is shared byte for byte by `absys-depth-first` and `absys-wake-back`. Token classes do not depend on configuration, so the JSON classes only those first paths. Frozen token TSV indices are used directly; no re-tokenization was performed. No P08 or named P05 program variant occurs in the permitted records inspected. `late_definition` is therefore empty.

I inspected all 27 P05 raw records (nine behaviour, nine cost, nine storage), including INVALID records, and all six labelled m2 measurement reruns. Large gzip records were decoded and summarized by the local `summarize_records.py`; they were not dumped wholesale. `build_classification.py` builds the JSON and checks token coverage, behaviour-stage coverage, fault flags, and agreement of the m2 classifications. The supporting `record_summaries.json` contains extracted evidence, not another classifier's judgements.

The principal normative files consulted were README.md, SPECIFICATION.md, METRICS.md, PROTOCOL.md, AMENDMENTS.md, problems/README.md and problems/05-late-contradiction.md. Contract evidence came from systems/absys/README.md, harnesses/README.md, harnesses/stages.json, harnesses/record.schema.json, harnesses/absys/README.md, harnesses/absys/S-mechanisms.md and relevant sections of harnesses/absys/absys_harness.py. The three P05 programs in each configuration, their frozen token files, the text manifest, permitted P05 records, and the two permitted batch logs supplied the remaining evidence.

**Files read outside the allowed list: none.** References to prohibited files within allowed documents and program comments were not followed. No web access was used.

## Token decisions

`pick` transcribes the stated three closed-world facts in the specified order. Its definition and its applications are P (class P, rules 1 and 6). The constants-table assignments are P: their contents are the problem's stage information, even though the harness substitutes them and does not send the table itself. Absys harness section 3.12 explicitly says that such a table is not automatically H.

In P05a, gt tokens 19–35, pos 36–56, ne 57–79, and their stage applications 99–104 and 105–110 are R. In P05b, gt 19–35, pos 36–56 and the stage application 69–74 are R. The introduced arithmetic differences, positive-integer cases, intermediate names, and alternative definition of integer disequality are not definitions given by P05. They implement semantic reformulations, rather than a general constraint mechanism. These are R constructs throughout; arithmetic on an invented intermediate is not an unchanged P05 conjunct merely because addition is primitive. Rule 10 is applied by the roles of the nested constructs.

The closest token ambiguity is pos versus C under rule 6's “An enumeration that the problem does not state is C.” I classify pos as R: its least-relation definition supplies the missing semantic condition that a difference is positive. Removing it admits nonpositive differences and changes the relation, rather than just scheduling or enumerating an already constrained set. There is no independent search directive, labelling call, or imposed finite domain here. Treating every invented inductive relation as a C generator would conflict with the R definition and the reference-semantics distinction. This is a potential rule ambiguity, not an amendment I have applied.

Calls to gt/ne are R replacements of the primitive queries; the corresponding named constants remain P. No case or conjunct was moved or omitted. There are no H calls, external mechanisms, or S mechanisms. In particular, definitions of gt/pos/ne are problem-specific mathematical relations, not a reusable interpreter, propagator or scheduler (rules 12 and 19). The empty `s_mechanisms` array means none for every P05 program in every configuration; the phase-4 mechanism list is also empty.

## Residuals, reported bindings and representation

The difficult outcome is P05b, not P05c. Stage 1 has both a finite explicit prefix and a finite stored representation of the infinite remaining computation. A cap of twenty derivation blocks does not truncate observe(): the system retains and later acts on all derivations. Classifying only the first twenty integer answers would incorrectly discard that held residual.

The equivalence argument is by hand. Under the specified least-relation semantics, pos(q) is exactly q in the positive integers: the base produces 1 and the recursive case adds 1. Thus `exists d: x=1+d and pos(d)` is exactly integer x>1. Expanding a case and propagating an arithmetic equation preserve that disjunction's solutions. A suspended arithmetic chain ending in pos preserves the unbounded tail. Consequently the entire held state is complete/residual, but reducible to the single comparison x>1, and is not identical to the posed information. This does not infer a finite domain from the observed prefix.

At stage 2, the finished derivations explicitly bind x=2 and x=3. The remaining unfinished derivations include arithmetic work and a pending pick(x). A branch which already binds x=1093 (defaults and wake-back) or x=1410 (depth-first) has not removed that pending constraint: it denotes no solution, since pick is closed-world {1,2,3}. Those bindings are observable, but their branch conditions must accompany them; stripping those conditions would manufacture an unsound answer. The union of the finished branches and the unfinished conditional branches is exactly {2,3}.

I apply SPECIFICATION Outcomes 2's instruction to classify the more explicit valid form, so stage 2 is complete/explicit. The unfinished inconsistent branches, their sizes and their reducibility are recorded as observations. This is an interpretive edge of the “two forms” provision because both forms occur within one derivation-state report. A reading that requires the representation of every retained branch, even redundant empty ones, would instead call the whole stage-2 state complete/residual/reducible. The semantic equivalence is the same. It would be wrong to label the whole residual “inconsistency undetected”: the union has two solutions. A literal reading of the observable-binding sentence as making *every* bound x unconditional would conflict with residual semantics; I preserve its attached pending constraints.

Absys abbreviates some to-do queues as “... N more” even with --full. Therefore the exact deduplicated primitive-relation and unknown-occurrence counts cannot be recovered from every printed state. The JSON gives the available suspended primitive-addition occurrences, exact top-level queue occurrence counts including N, and derivation counts beside the input's one primitive comparison. A recursive pos call has no fixed finite primitive expansion. Queue reactivations may also duplicate an arithmetic relation held as suspended, so the two counts are not summed into a fabricated constraint size. This is a measurement limitation, explicitly marked unavailable where appropriate.

Final behaviour boundary observations for P05b are:

| configuration | stage | finished x values | derivations | printed suspended processes | queued top-level relations |
|---|---:|---|---:|---:|---:|
| absys | 1 | 2–773 | 1288 | 208914 | 248649 |
| absys | 2 | 2, 3 | 731 | 415635 | 497643 |
| absys-depth-first | 1 | 2–998 | 999 | 1992 | 7 |
| absys-depth-first | 2 | 2, 3 | 4 | 1409 | 370 |
| absys-wake-back | 1 | 2–773 | 1288 | 332692 | 1286 |
| absys-wake-back | 2 | 2, 3 | 731 | 663318 | 2549 |

These are retained-state counts, not counts of valid distinct integer solutions. Depth-first keeps all derivations but elaborates one running derivation at a time. No configuration offers a request for further answers, so this is not the execution class “alternatives pending.” All six final P05b stages are budget+suspended. The default and wake-back stage-2 first attempts timed out; their raised-limit attempts reached the budget and determine the final classification. The default's first stage-2 stdout has a UTF-8 harness fault; the final attempt's structured state is available.

## Reachability, timeouts and measurements

For P05a, all configurations finish stage 1 with {1,2,3}, then time out at stage 2 under both limits. There is no observed post-comparison state: none reported, not an empty report and not proof that the mathematical relation is inexpressible. Stage 3's behaviour replay completes only the prelude and stage 1 before timing out again inside stage 2. The repl completion replies and the harness's line-by-line contract establish this. Stage 3 is **not reached**, with semantic and representation fields null. Its raw timeout belongs to the replay, not to ne's own evaluation (AMENDMENTS 3.2). A separately completed restart-count run does not establish that the actual replay completed.

All behaviour P05a records are INVALID because a restart measurement was unavailable for stage 3 attempt 1. Every one of their entries has `harness_fault: true`, including their valid stage-1 observations. The corresponding invalid cost/storage records are retained as evidence. The default P05a storage record validates; its mathematical and execution classifications otherwise agree. Missing restart figures and behaviour step figures remain unavailable.

For P05b, all six original cost/storage records time out at both stages with no reported state. These twelve stage differences are in `mode_differences`. The measured whole-text stage-2 attempts expose no assertion-progress information. Although their own stage-1 attempts time out, that is not conclusive evidence locating the stop inside each separate stage-2 attempt. `this_mode.reached` is null there, with an explicit reachability note; its timeout describes the enclosing measurement attempt, not an asserted independent stage-2 failure. This uncertainty is preferable to claiming an unobserved stage was reached or not reached. Behavioural reachability is known.

All six labelled m2 reruns preserve both original measurement records and their meaning. Their twelve final stage classifications match behaviour, including residual equivalence and explicit {2,3}; no differing m2 stage is therefore listed. Cost uses --peak-every 0; storage uses sampled --peak-every 1000. Sampling figures are not exact peaks. These reruns resolve measurement overhead, not mathematical expressibility. P05a and P05c have no m2 reruns. P05c's cost/storage and behaviour classifications agree throughout.

P05c explicitly prints “No derivation survives: the assertions are unsatisfiable.” at stage 2 and accepts stage 3 incrementally without restoring alternatives. The earlier three answers disappear from the surviving set. No manual interventions are recorded; automatic safety reruns and reposing are harness operations.

## Expressibility

All configurations have the same judgement. P05a and P05b are expressible with reformulation: positive integer differences express > over the entire integer domain, and the two directions of > express != on the integer domain already enforced by stage 2 of P05a. This is a declarative equivalence, not a claim of operational completion. P05c is directly expressible. No hidden variants were read, and none were inferred to have passed from these primary runs.

## Totals

| distinct text (first path) | P | C | R | S | H | total |
|---|---:|---:|---:|---:|---:|---:|
| absys/P05a.ab1 | 38 | 0 | 73 | 0 | 0 | 111 |
| absys/P05b.ab1 | 35 | 0 | 44 | 0 | 0 | 79 |
| absys/P05c.ab1 | 44 | 0 | 0 | 0 | 0 | 44 |
| total, counted once per distinct text | 117 | 0 | 117 | 0 | 0 | 234 |

Each configuration uses those same 234 tokens; expanding to all configuration copies would give P=351 and R=351, total 702, without changing the distinct-text totals above. Every frozen token index is covered exactly once, and each manifest text is represented.

The 24 behaviour stages comprise 18 complete, 3 none reported, and 3 not reached. Representations are 15 explicit and 3 reducible residuals, with 6 stages having no applicable representation. Execution states are 12 finished, 6 budget+suspended, 3 timeout, and 3 not reached. There are 12 original measurement-stage differences; all 12 m2 stages agree with final behaviour classifications. Supporting mechanisms and late-definition cases: none.
