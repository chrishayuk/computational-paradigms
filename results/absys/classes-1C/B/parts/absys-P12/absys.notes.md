# Independent classifier B: absys, batch 1C, P12

This classification was made independently by Codex. I did not write the programs or consult another classifier's classes. The source repository was read only. I ran only my own record/token checking script, `check_and_classify.py`, in the output directory; I did not run a problem program, the harness, or Absys. `absys.json` is the classification; `check-summary.json` gives the validation totals.

## Scope and evidence

The distinct-text manifest has 12 paths, each shared by the three configurations. I checked the source bytes and frozen token sequences against both aliases. Each manifest path is classed once under `absys/`; the classes do not depend on which native search/wake configuration runs it. There are no configuration-specific token exceptions, named P12 program variants, P08 programs, or labelled `raw-rerun-m2/` records here.

There are 216 raw P12 records: 72 behaviour, 72 cost, and 72 storage. I checked the full record objects programmatically, their program hashes against the permitted source files, and their identities against all six P12 batch-1C logs. The initial three logs each contain 24 “no program” entries, before the later `1C-p12-*` jobs. These are not behaviour runs and do not invent additional stages. The later logs account for exactly all 216 records. The permitted batch log through 1B and rerun-m2 log contain no P12 rows. None of the P12 records has an INVALID filename or a nonempty `harness_faults` field; all output entries therefore have `harness_fault: false`.

## Constructs requiring judgement

The difficult construct is `gtz`. Absys lacks the primitive positive comparison in choice's recursive case. Each program introduces `gtz(q)` with the alternatives `q = 1 or ... or q = 16`, and calls it in place of the guard `m > 0`.

I split this by nested construct, following rule 10:

- The extra relation declaration/lambda, including its `begin` and final `end`, is R (6 tokens). The call `gtz(m)` is R (4 tokens).
- The explicit finite enumeration, including its braces, is C (65 tokens), by rule 6: “An enumeration that the problem does not state is C.” Its equalities are the cases of that enumeration, not 16 problem-given facts. This rule applies even though the enumeration implements a semantic guard.
- The original empty/nonempty cases of choice, their head equations, the specified L/R alternatives in their original order, the primitive decrement, and recursion are P. In particular the L/R disjunction *is* stated by the problem and is P under the other half of rule 6.
- The closed-world accept facts, their constants table, and their uses are P. The constants table encodes the stage's problem information; being consumed by the harness does not turn it into H. The parameter declaration and stage markers are comments absent from the TSV. No harness call is written in these programs.

For `P12a.n8.ab1`, the concrete difficult ranges are R 24–28, C 29–93, R 94, and R 115–118. For every other file the same constructs are located relative to `gtz'` and `choice'` in its frozen TSV, and their exact ranges are in `absys.json`. Each span names the applicable rules. Surrounding P constructs are split rather than absorbed into the reformulated guard. The arithmetic temporary is primitive decomposition allowed by the specification, not an efficiency argument under rule 5. The query still presents choice before accept; there is no move or omission.

There is a real overlap in the wording of the rules here: R includes extra definitions and cases, while rule 6 specifically makes an unstated enumeration C. I give the specific enumeration rule effect inside the extra R definition. Classing all of `gtz` as R would miss that split; classing its enclosing declaration as C would miss the extra definition. Rule 14 does not govern this helper: it is not a separately written function for a direction that a relational transcription cannot serve. I do not propose changing a frozen rule, but this interaction should be included in any disagreement record. No other rule appeared wrong for these texts.

## Domain and expressibility

All four subproblems in all three configurations are **expressible with reformulation** at the problem's specified sizes 8, 12 and 16. None can transcribe the missing `>` primitive directly. For each specified n, recursive m ranges from n down to 0, and the enumeration agrees with `m > 0` on every one of those values. The replacement therefore preserves the entire choice relation on all sequences at these n, not just the successful accept facts. It does not restrict s beyond the finite length bound already in P12, so AMENDMENTS 3.4 does not make the finished outcomes partial. This is distinct from imposing an unstated finite domain on an otherwise unbounded query.

The exact helper is not a general comparison for m > 16. No hidden variants were read or are known here, and I cannot attest that these particular texts pass a variant with n > 16. This limitation is recorded in every expressibility reason rather than silently asserting correctness for arbitrary changed size parameters. The judgement follows the stated P12 sizes and the systems file's explicit allowance for finite-value comparison reformulation. Hidden-variant performance remains unassessed.

No S mechanism is used in any of the 36 configuration/program pairs. Native search is used, not a handwritten search; the finite comparison helper is the R/C construct above. The phase-4 S mechanism list also says none for all three configurations. To make the absence explicit per program, the `s_mechanisms` array has one zero-token entry per pair with `mechanism: null`, no token spans, and a note. `listed_at_phase_4` is null because there is no mechanism to label. These entries do not denote 36 mechanisms. There are no external mechanisms in the configuration core declaration.

## Outcome judgements and equivalence

Each actual behaviour run has one stage, and each stage was reached. At n=8 and n=12 all three configurations finish; depth-first also finishes at n=16. At the fixed 600-second limit, the default and wake-back configurations time out at n=16 for all four subproblems and both answer modes.

The 56 finished stages are complete/explicit/finished. The complete observed sets are:

- P12a: L repeated n times, then the one-element R sequence, in that printed order.
- P12b: the one-element R sequence.
- P12c: R repeated n times.
- P12d: L repeated n times.

The script reads every ground s binding from each observation and compares its set with these valid outcomes, checks the number and absence of duplicate observed solutions, and checks the collected answer prefix against the cap. Equivalence also has a short mathematical proof: induction on nonnegative n shows choice denotes exactly the L/R sequences of length at most n; the finite guard is equivalent on the entire recursive domain; conjoining the closed-world accept facts leaves precisely the observed sequences. This proof does not assume a depth-first or breadth-first traversal or execute a problem program.

For P12a's any-one queries, `answers(1)` collects the all-L solution and ends by cap, while observe reads both completed solutions. A cap is not evidence of pending execution. Under this Absys answer mechanism all derivations are elaborated before reporting, and the completed ground derivations print no suspended processes. These stages are finished, with 2 saved answer derivations and 0 suspended work items, not “alternatives pending” or “suspended.” The same rule applies to a single completed ground derivation on the other queries. The printed word “hibernating” alone is not enough to class a computation suspended.

The 16 timeouts are none reported/representation null/timeout. The prelude and n assertion finished, and the stage's conjunction was posed, but query-state observation never arrived. Captured stdout contains only parameter/prelude states, no s answer. Thus these are reached timeouts, not unreported failures, not unreached stages, not an unsound empty answer set, and not a residual reconstructed from the source. The fixed-limit SIGKILL is recorded as timeout, not as an independent process error. The limit is not raised for P12. No available record establishes the bindings, retained derivation count, suspended count, or store at interruption; those figures remain unavailable rather than 0.

No stage reports a residual or a nonground solved form, so residual simplification, identical-to-posed, and residual size are null throughout. Explicit-answer equivalence reasoning is provided in the applicable entries. There are no conclusion withdrawals or manual actions; this is a one-stage problem. Every entry preserves the collected answers, observed state, and print verbatim, and gives the observable alternatives and suspension counts.

## Measurements and limits of observation

I compared all 144 cost/storage stages with their matching configuration, instance and program's behaviour stage. Semantic result, representation, simplification applicability, equivalence, reachability and execution state agree in every case; observed solution order also agrees. Consequently `mode_differences` is empty. The original records stand, including all timeouts. No measurement-only timeout was substituted for a successful behaviour result. There are no labelled measurement reruns beside these records; the use of the m2 build in an original record does not by itself make it a labelled rerun.

For completeness, each behaviour entry links its cost and storage records and copies their step fields, alternatives, store vector and peak labels into its observations. Storage maxima here are sampled, not exact peaks. Behaviour itself provides no step count or peak store. Reporting latency is when all derivations are made available, not the point a candidate first became successful internally. Neither the records nor these texts supply counters of candidates examined, accept evaluations, or problem-defined partial sequences held. Those observations are unavailable. Derivation counts cannot be relabelled as candidate counts or partial-sequence counts. Final solutions do not establish that search was avoided, despite the relational machine's ability to use accept information during elaboration. No growth fit is asserted from missing n=16 measurements in the default and wake-back configurations.

## Read boundary

No file was read outside the user's permitted list, apart from this classifier's own checking script and generated output files in the authorised output directory. No prohibited file was encountered and read. In particular I did not read the author's `programs/absys/README.md`, audits, result narratives, earlier classes, another classifier's classes, calibration, reviews, sealed variants, transcripts, other systems, private directories, or the web. Links and references appearing inside permitted documents were not followed. Program comments, including their author's reformulation labels, were read as permitted source evidence; my C/R split above is my own judgement.

The repository files actually read were `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`, `AMENDMENTS.md`, `problems/README.md`, `problems/12-large-alternative-space.md`, `systems/absys/README.md`, `harnesses/README.md`, `harnesses/stages.json`, `harnesses/record.schema.json`, `harnesses/absys/README.md`, `harnesses/absys/S-mechanisms.md`, the 36 `programs/absys/{configuration}/P12*.ab1` files, `results/absys/tokens/TEXTS-1C-P12.tsv`, their 36 frozen token TSVs, all 216 `results/absys/{configuration}/P12/raw/*.json` files, all six P12 files in `results/absys/logs/`, `results/absys/batch-log.tsv`, and `results/absys/rerun-m2-log.tsv`. An inventory of names within the allowed `systems/absys`, `harnesses/absys`, and tokens trees was also obtained; that did not open the inventoried qualification records or unrelated token files.

## Totals

| First manifest path | All tokens | P | C | R | S | H |
|---|---:|---:|---:|---:|---:|---:|
| absys/P12a.n12.ab1 | 176 | 101 | 65 | 10 | 0 | 0 |
| absys/P12a.n16.ab1 | 184 | 109 | 65 | 10 | 0 | 0 |
| absys/P12a.n8.ab1 | 168 | 93 | 65 | 10 | 0 | 0 |
| absys/P12b.n12.ab1 | 143 | 68 | 65 | 10 | 0 | 0 |
| absys/P12b.n16.ab1 | 143 | 68 | 65 | 10 | 0 | 0 |
| absys/P12b.n8.ab1 | 143 | 68 | 65 | 10 | 0 | 0 |
| absys/P12c.n12.ab1 | 165 | 90 | 65 | 10 | 0 | 0 |
| absys/P12c.n16.ab1 | 173 | 98 | 65 | 10 | 0 | 0 |
| absys/P12c.n8.ab1 | 157 | 82 | 65 | 10 | 0 | 0 |
| absys/P12d.n12.ab1 | 165 | 90 | 65 | 10 | 0 | 0 |
| absys/P12d.n16.ab1 | 173 | 98 | 65 | 10 | 0 | 0 |
| absys/P12d.n8.ab1 | 157 | 82 | 65 | 10 | 0 | 0 |
| **Distinct-text total** | **1947** | **1047** | **780** | **120** | **0** | **0** |

Each configuration uses this same total; counting the shared texts in all three configurations gives 5841 program tokens (P 3141, C 2340, R 360, S 0, H 0). The distinct-text total is the nonduplicated JSON token total. Every frozen index is covered exactly once.

| Configuration | Complete / explicit / finished | None reported / timeout | Behaviour stages |
|---|---:|---:|---:|
| absys | 16 | 8 | 24 |
| absys-depth-first | 24 | 0 | 24 |
| absys-wake-back | 16 | 8 | 24 |
| **Total** | **56** | **16** | **72** |

Final totals: 12 texts, 1947 tokens (P 1047, C 780, R 120, S 0, H 0); 72 behaviour stages, 56 complete/explicit/finished and 16 none reported/timeout; 144 measurement comparisons, 0 classification differences; 0 residuals, 0 supporting mechanisms, 0 harness-fault entries, and 12 expressible-with-reformulation judgements.
