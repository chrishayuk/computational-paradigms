# Python batch 1A — independent classifier B

Classifier: Codex, independently of the implementation author and classifier A. I did not write, import, or execute any program of the study, run its system, consult another classifier's classes, or use the web. The repository was read only. All created files are in `~/cp-roles/classes-B/python`.

`python.json` contains the classifications. `classify.py` is the reproducible construction and checking script; it parses source to locate constructs but takes every token, index, and line from the frozen TSVs. It never calls a tokenizer. `validation.json` records the coverage totals and the mathematical check of P02's ten triples. Running `python3 classify.py` regenerates these artifacts without executing study programs.

## Coverage and conventions

There are 30 distinct texts in TEXTS.tsv: 12 core, 12 extended, and six additional concurrency texts. The six concurrency P03 texts are byte-for-byte identical to core's, with identical frozen TSVs. Their classifications are the same; they appear only under the first paths. There are no configuration-dependent exceptions for these shared texts.

The batch log contains 153 runs: 51 behavior, 51 cost, 51 storage. Every log tuple (configuration, instance, program, mode) has a matching raw record. Behavior has 102 stages. All were reached. P01c has two readings for each of three configurations, so the JSON has 105 outcome entries. `reading` distinguishes those entries; other instances retain their exact record identifiers, including each of P02b's six arrival orders. There are 36 expressibility entries, one per configuration/subproblem, with the P03 direction stated.

All raw records were read through JSON tools, rather than dumped wholesale. The stage classification uses registered held state as well as answers. Cost and storage classifications were recomputed and compared on all outcome axes. They agree with behavior at every stage, including the exceptional observed binding discussed below; `mode_differences` is empty. Measurements do not have to be identical to have the same classification. Each outcome also carries the corresponding cost/storage record and applicable measurements. Null figures remain unavailable. There are no harness_faults entries, manual actions, error stages, timeout stages, or unreached stages in these records.

Sizes count remaining undecided relation occurrences and occurrences of unknown places after substituting observed bindings. Free variables and solved bindings are not counted as undecided relations. Input sizes use the accumulated posed information, not only the newest stage. Arithmetic is already decomposed into the primitive + and multiplication relations. A held conc call counts as one undecided relation; constructing a sequence with ++ is a term operation. This convention is stated beside each size, since a recursive definition is not a finite syntactic primitive expansion on arbitrary unknown sequences.

## Difficult token decisions

**Evaluator versus holding code (rule 19).** Each equality, addition, multiplication, and conc-place evaluator is split. Tests of which places have values, interface/layout for that dispatcher, and `return None` are R. The returned mathematical evaluation or fully known test is P, including inverse arithmetic, divisibility, and zero-factor cases. These bodies are P even where this batch never takes a branch. The direct conc and forward rev functions follow the problem cases and are P under rules 2–3. The plus/times functions are not inverse-direction reformulations under rule 14: the specific evaluator clause of rule 19 applies.

**Problem-specific stores versus generic S (rules 12,19).** I treated core's `place`/`decide` machinery as R for its closed, hard-wired problem vocabulary. Its table of evaluators is not an argument supplied by a caller. The concurrency equivalents likewise hold that vocabulary; holding/bookkeeping is R, with thread creation, condition locking, notification, waits, and synchronization counters C. `threading` is an external mechanism, not native suspension and not experiment-written S. The header of a wrapper that both dispatches and holds remains R; its nested thread/wait operations are separately C.

This boundary is debatable: replacing the hard-wired evaluator table would reuse much of core's or concurrency's loop for another problem. I read “general over relations” as requiring an actual generic interface rather than the possibility of editing a program. On a broader interpretation, much of this R would become S and the recorded configurations would require additional mechanism names. Rule 19 does not specify how editable tables affect generality, so I flag this as a classification-sensitive boundary.

Extended P02's `Relation` class is more clearly generic: its constructor accepts an arbitrary evaluator and places; its call method dereferences, evaluates, suspends, and binds without referring to the three problem relations. I class that mechanism S. Its `__repr__` is H by the explicit output-adapter exception. The extra evaluator argument at each posting is R. The relation/places posted are P, nested inside a C queue directive (rules 3,10,20).

**Additional S in extended P03.** `unify` is a general term unifier with a trail. `children`/`done` implement generic goal-list resolution. They are S under rules 12 and 15, not P merely because they are used to implement conc and rev. The actual relation cases, including their head-unification tests, are P under rule 2. These extra mechanisms are not among the three supplied phase-4 modules. They must accompany the reported extended results as named mechanisms: “term unification” and “goal-list resolution.” The JSON retains the raw configuration names so every outcome can be matched to its record.

Each extended P03 text contains 172 S tokens for unification and 58 for resolution, 230 together. Each extended P02 text contains 179 S tokens for the relation adapter. All occurrences are classed for complete token coverage, but rule 12 credits each mechanism only once in extended: **409 additional S tokens**, rather than the **1,917 S occurrences** across the distinct program texts. These mechanisms are shared by P03a–f and P02a–c, respectively.

The supplied mechanisms have their already-published sizes: suspension/variables 537, search 176, propagator 1,260. Suspension is used by all extended texts; search by extended P03a–f; the propagator is unused in this batch. Thus the used supplied mechanisms contribute 713 S tokens separately, and used supplied plus additional mechanisms contribute **1,122 S tokens credited once**. These supplied sources have no program-token TSV in TEXTS.tsv and are not inserted as invented token streams in `tokens`.

**Encoding (rules 3,15).** Extended's added `cons` conversion is R. The Python systems file does not define a cons-cell encoding as P, which is rule 15's condition. The direct case expressions on the chosen representation remain transcriptions. Calls of the added conversion are R, including inside otherwise P queries. An alternative reading that treats all faithful representation conversions as P would change these totals; the conditional wording of rule 15 led me to R.

**Directions (rules 3,14).** The separately written split, rest, front, and unrev functions are R throughout, including their case-head tests. Calling them is R, enumerating their answers is C, and collecting/rendering computed answers for the harness is H. P03f reverses the given rev/conc conjunct order: one move under rule 4. The other three inverse functions introduce no additional case moves or omissions. No native algorithm exception from P13 applies here.

**Harness and nested punctuation (rules 10,13,20).** The documented stage loop and dispatch, replay tests, fixed calls, and input reads are H. Posed arguments remain P inside R storing or C scheduling calls. Commas separating arguments take the following argument's class. Statement newlines belong to statements; INDENT and its matching DEDENT belong to the enclosing header, including when the first body item is a tokenizer-excluded docstring. Output-only dictionaries, renderers, and answer collectors are H. Tests of `failed`/`known`/`told` that select whether a result is reported are R under rule 13's exclusion for tests of held state. Imports enabling mechanisms are C call-site code; the implementations are counted separately as S or external mechanisms.

## Difficult outcomes and residual checks

**Held equality versus solved identification.** Core and concurrency hold undecided equality tuples, rather than aliasing unknowns. Their early P01a results are residual and reducible: aliasing would remove the remaining equality tests. They are complete and identical to the posed information. Extended actually aliases Vars, so its early P01a results are solved forms and finished, despite free unknowns. Being free does not imply suspended work.

**P01b.** Core/concurrency retain the actual conc goal and later act on it, so it is a reported residual, not an echo of input. It is reducible to the solved term `t=⟨1,2⟩++s`. Extended reports that solved term directly. I interpret its free sequence tail in the problem's sequence domain, as the ++ notation requires. This is a domain convention, not an imposed finite integer domain. A reading that admitted improper cons tails as additional problem values would make the extended solved form unsound; the reported mathematical ++ term does not admit them. At stage 2 all configurations observe both determined sequences.

**P01c, two readings.** Core/concurrency retain the actual self-referential relation. Over finite sequences its size equation is |x|=1+|x|, impossible: complete residual, inconsistency undetected. Over rational trees, repeatedly unfolding the equation forces the unique all-1 cycle: complete residual, reducible. Extended binds x to a cycle without an occurs check and explicitly prints it as cyclic: complete for the rational reading, unsound for the finite reading. No inconsistency is silently treated as a reported empty answer set.

**P02.** All configurations retain the same mathematical relations over all integers; none uses the finite-domain propagator or imposes a finite domain. R1 alone is reduced, following the specification's express example. R2 alone is also reduced. R1+R2 is equivalent but reducible to the ten explicit triples. The check eliminates v to obtain u(w+1)=16, then enumerates the signed divisors of 16; this is exhaustive because every such divisor has absolute value at most 16. The script checks exactly the ten triples in the problem file. It is not a bounded approximation to an infinite integer domain.

R3 fixes u=2. With R1, v=14 and w is free: solved form. With R2, a multiplication relation remains, v=2w: reduced residual, with fewer unknown occurrences and no longer identical to the posed information. The printed `u=2` alone at these latter stages is not the whole report: the registered multiplication remains and is included. With all three relations the unique observed assignment is (2,14,7) in every arrival order. Execution is finished wherever the registered waiting structures are empty, including stages that leave legitimately free unknowns.

**P03 and the binding-observation tension.** Every direction prints all valid answers, with the three P03b splits in increasing prefix length. Core and concurrency finish all directions. Extended exhausts P03a–e; undoing a search leaves free Vars visible afterward, which are not additional value bindings or withdrawals of the valid printed answers.

Extended P03f prints `a=⟨3,2,1⟩`, then reaches 1,000,000 instructions while holding 108 search choice points. However, `observe.bindings.a` at that stop is a finite cons sequence of **length 17**, with unbound h places. Every instantiation has a different length from the sole valid sequence. The specification explicitly says a binding held at the budget is reported even if the answer mechanism would not deliver it, with only a P09d1 exception. I therefore class this report **unsound / explicit / budget**: the valid explicit answer is the more explicit valid representation, but the additional observed binding is invalid. The unregistered unresolved goal list cannot serve as a reported residual qualifying that binding.

This is the hardest decision. P03's example says reporting its one answer and then exhausting the budget is complete/budget. Under an answer-only interpretation this record would indeed be complete/budget. I give priority to the explicit held-binding rule because this record has an additional binding. The rules should clarify whether speculative backtracking bindings are exempt, or require observing their qualifying goals as well. My JSON preserves the literal-rule judgement and both the answer and held binding, so the alternative can be reconstructed without rereading the program. Cost and storage expose the same binding and classification.

## Expressibility scope

Expressibility is a capability judgement, not simply whether the submitted program happened to include S. The core forward conc/rev transcriptions are available in every configuration. The separate meaning-preserving inverse functions are likewise available in extended, even though its actual programs choose extra generic mechanisms. I therefore do not infer “not expressible” merely from that choice. The actual extra S and R code must still be credited. There are seven expressible entries and 29 expressible-with-reformulation entries, and no not-expressible entry. These judgements concern the public programs and problem shapes; no hidden variants were inspected or claimed to have passed.

## Read boundaries

No file content was read outside the user's permitted list or this output directory. In particular, I did not read calibration, reviews, variants, other systems, either prohibited author-notes file, another classifier's outputs, private/home configuration files, or repository git internals. Permitted top-level documents mention forbidden paths as links; I did not follow them. No disallowed file was accidentally opened. Some multi-file tool displays were truncated; the relevant rules, problem outcomes, program bodies, and compact record summaries were subsequently read separately. Tools and the provided environment supply their own system context; this was not obtained by opening files outside the allowed paths.

## Totals

Frozen token occurrences across the 30 distinct texts, each index covered exactly once: **18,215**.

| class | tokens |
|---|---:|
| P | 4,080 |
| C | 1,552 |
| R | 5,123 |
| S | 1,917 |
| H | 5,543 |

These are coverage totals, with repeated inline S occurrences included; rule-12 mechanism totals are separately deduplicated above. No shared P03 text is double-counted for concurrency.

Outcomes, counting the two P01c readings separately: **103 complete, two unsound**. Representations: **48 explicit, 15 solved form, 40 residual, two cyclic**. Residuals: **21 reduced, 17 reducible, two inconsistency undetected**. Execution: **64 finished, 40 suspended, one budget**. All stages reached; no classification differences in cost/storage modes.
