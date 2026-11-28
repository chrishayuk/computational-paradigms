# Independent classifier B: SWI-Prolog, batch 1C, P12

The classification is in `swi-prolog.json`. `check_classification.py` reads only the permitted source evidence and the local output, generates the JSON, and checks its serialized token coverage and outcomes. `validation-summary.json` records the checks and totals. I did not write the Prolog programs, consult another classifier, run Prolog, or run any study program. No subagents were used.

## Scope and evidence

The eight first paths in `results/swi-prolog/tokens/TEXTS-1C-P12.tsv` cover twenty physical programs. The four `constraints/P12?.pl` texts are byte-identical to their `coroutines`, `plain`, and `session` counterparts. Their frozen token sequences also agree. They receive the same classes in these configurations; no configuration-specific duplicate is needed. The four tabling texts add one six-token table directive each.

The five `results/swi-prolog/logs/1C-*-P12.tsv` logs contain 360 jobs, all with exit 0: 120 behaviour, 120 cost, and 120 storage runs. Each log job matches exactly one raw record by configuration, instance, program, and mode. There are four subproblems, three sizes, two answer modes, and five configurations, each with one stage. No named program variants, invalid records, safety reruns, or P12 measurement reruns occur. The earlier batch log contains no P12 jobs. The permitted `rerun-m2-log.tsv` does not exist in this checkout, and there are no P12 `raw-rerun-m2` records.

The checking script verifies each record's program hash against the corresponding permitted program, checks every answer, and compares each measurement run with its own behaviour run. It does not infer classifications from exit status alone.

## Construct decisions and ambiguities

- **The accept facts and the size key are P.** `accept_fact(n, s)` stores the facts that P12 explicitly gives at each of its three sizes. Its n field selects a parameterized problem instance. It is not an accumulator, efficiency argument, new search algorithm, or restriction of the domain. For example, `constraints/P12a.pl` tokens 0–119 contain its six facts; `constraints/P12b.pl` tokens 0–26 contain its three facts. The wording about “extra arguments” in class R/rule 3 could be read literally to include this key, but that would count the faithful parameterization of the problem's own size-dependent data as reformulation. I use the P reading and make this decision explicit.
- **The recursive choice clause is P throughout.** For example, `constraints/P12b.pl` tokens 35–72 transcribe the second case. Its `N > 0` is the problem's own guard (rule 2), and its l/r disjunction is explicitly stated (rule 6), not an added enumerator. `N1 is N - 1` serves the direction actually used: n is known at every recursive call (rules 3 and 8). This temporary names the given arithmetic expression; it does not add a relation argument or change the algorithm. The empty-sequence case is P too. Both cases and the conjunction retain presentation order; there are no moves or omissions.
- **The table declarations are C.** Their token ranges are 120–125 in `tabling/P12a.pl`, 27–32 in `tabling/P12b.pl`, and 93–98 in each of `tabling/P12c.pl` and `tabling/P12d.pl`. Tabling changes execution of the same finite least relation (rule 1); it does not change the accept facts or add a semantic case.
- **`member/2` is P and an external mechanism.** For example, `constraints/P12b.pl` tokens 108–119, including the preceding comma, implement the query's accept test by exact membership in the supplied closed-world facts. The n key excludes other instances' facts. This preserves the relation for both answer modes (rules 3 and 9). `member/2`, from `library(lists)`, lies outside the configuration's plain core and is listed in the observations. It is not experiment-written supporting code (rule 12).
- **Harness shells and calls are H, with nested goals separated.** The fixed contract expressly classes whole `unknowns/2` facts, stage heads with `:-`, trivial `query/2` facts, `h_param/2`, and `h_candidate/0` as H. The body query goals remain P (rule 10). In `constraints/P12b.pl`, these are H at 73–98, 106–107, and 120–127; the P query spans are 99–105 and 108–119. Commas between goals take the following goal's class (rule 20). I class the terminal period of the stage clause, token 120, as H punctuation closing the interface shell. Rule 10 explicitly discusses introducers but does not specify closing punctuation of a mixed-class clause; attaching that period to the final P goal would move one token per text from H to P. This is a punctuation ambiguity, not a semantic difference.

I found no rule requiring amendment for these programs. The two potentially consequential interpretation points are the size key and mixed-clause closing punctuation above; I have not invented a new rule for either.

## Outcomes and equivalence

Every behaviour stage is **complete / explicit**. Every answer binds S to a finite ground list of l/r atoms, of length at most n, in the specified accept set. In P12a the all-mode answer order is l repeated n times, then `[r]`; the any-mode answer is l repeated n times. P12b reports `[r]`, P12c reports r repeated n times, and P12d reports l repeated n times. The script checks these facts and, for all-mode runs, exact set equality and absence of duplicates. A single valid answer satisfies an any-one query under SPECIFICATION.md, Outcomes 1, even when P12a has another valid solution.

There is no residual, solved form with free variables, or cyclic term to establish equivalent. The explicit answer sets are checked directly against the P12 table, rather than against facts copied out of the program. The residual-equivalence, simplification, identical-to-posed, and residual-size fields are consequently null, not claims that the residual has size zero. No unstated finite domain is imposed: the bounded sequence length and two atoms are exactly the problem's domain.

All sixty all-mode runs finish after exhaustive answer collection. Fifty-nine any-mode runs stop with **alternatives pending**. The exception is `tabling`, `P12c.n16.any`, which is **finished**: the reported answer ends with a period, `ended_by` is `exhausted`, and the storage run finds zero retained choicepoints at that answer. At n=8 and n=12 this same subproblem still leaves a choicepoint; so do the other configurations at n=16. I do not infer operational state solely from knowing the mathematical answer is the last valid solution. A retained choicepoint can yield failure only, as the systems measurement document explains. The exception agrees across all three modes.

For exhausted queries, `observe.raw` is usually empty because backtracking has consumed the last binding. That does not erase previously collected answers. Suspended work is absent: the boundary count is zero, and the reported answers contain no unknowns or residual goals. There are no earlier-stage conclusions to withdraw, no manual actions, no error/budget/timeout, and no unreached stage. Each outcome has `harness_fault: false`; none of the records reports a harness fault.

## Measurements, expressibility, and support

All 240 cost/storage comparisons agree with behaviour on every classification field, answer sequence, query ending, and candidate total. Therefore `mode_differences` is empty. There is no labelled P12 m2 rerun to compare. Storage-mode evidence is separately attributed to its record in each behaviour outcome; it is not used as the source of the behavioural classification or cost steps.

In all-mode runs the candidate totals are 511, 8,191, and 131,071 at n=8, 12, and 16. In any-mode runs P12a and P12d examine n+1 candidates, P12b examines 2^n+1, and P12c examines 2^(n+1)-1. These are observed final totals, checked against the problem's reference formulas. The records do not provide cumulative candidate counts at each individual answer. The reference ranks of the answers in textual depth-first order are noted separately and not presented as measurements.

Choicepoint counts are retained backtracking frames, not counts of simultaneously live branches or partial sequences. Each outcome includes the corresponding storage run's answer/boundary choicepoints and store vector. The records supply no problem-defined partial-sequence count, so it remains unavailable. Available heartbeat maxima are labelled sampled and retain their interval and GC setting; a true peak is unavailable. Tabling has no within-stage sampler, and its null peaks are unavailable. Short nonsampled runs also retain null peaks. Missing figures are never converted to zero. Table answers retained after exhaustion are stored results, not necessarily runnable work; they do not change a finished execution state to suspended or alternatives pending.

All twenty configuration/subproblem combinations are **expressible**: the definitions and ordered query are transcribed, with no R tokens. Both answer modes and all three sizes share this judgement; no additional relation direction is posed. `late_definition` is empty because this brief contains no P08 program.

Every program's S-mechanism entry explicitly records none, with zero S tokens. There is no hand-written search, scheduler, suspension, propagator, or meta-interpreter. The phase-4 session wait-for-undefined-procedure hook is preloaded as part of that configuration, but these P12 programs apply no undefined procedure and make no use of it. Its pre-existing implementation is not a new P12 text in the supplied manifest, and I do not re-tokenize it or assign its advertised size to these programs. This distinguishes a mechanism being installed from being used by the problem. Session engine operations are fixed harness infrastructure; the library membership test and tabling declaration are external mechanisms, not S.

## Access disclosure

No file outside the user's permitted list was read. No prohibited contents were encountered. File names printed while listing the permitted system, harness, and token directories were not followed into restricted paths. References within permitted documents to reviews, calibration, variants, author notes, or earlier classes were not followed. No web access was used. All writes were confined to the requested output directory; the source clone was not modified.

## Totals

| Distinct text | P | C | R | S | H | Total |
|---|---:|---:|---:|---:|---:|---:|
| constraints/P12a.pl | 185 | 0 | 0 | 0 | 36 | 221 |
| constraints/P12b.pl | 92 | 0 | 0 | 0 | 36 | 128 |
| constraints/P12c.pl | 158 | 0 | 0 | 0 | 36 | 194 |
| constraints/P12d.pl | 158 | 0 | 0 | 0 | 36 | 194 |
| tabling/P12a.pl | 185 | 6 | 0 | 0 | 36 | 227 |
| tabling/P12b.pl | 92 | 6 | 0 | 0 | 36 | 134 |
| tabling/P12c.pl | 158 | 6 | 0 | 0 | 36 | 200 |
| tabling/P12d.pl | 158 | 6 | 0 | 0 | 36 | 200 |
| **Counted once per distinct text** | **1,186** | **24** | **0** | **0** | **288** | **1,498** |

Expanding the shared texts to all twenty physical program paths gives P=2,965, C=24, R=0, S=0, H=720, total 3,709; these expanded figures do not replace the distinct-text totals. Every frozen token index is covered exactly once. All 120 behaviour stages are complete and explicit: 61 finished, 59 alternatives pending. All twenty expressibility judgements are expressible. The 240 measurement comparisons have zero classification differences.
