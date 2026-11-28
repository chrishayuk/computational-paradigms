# Classifier A: Python, batch 1B, P04 to P06. Notes

Classifier A is a Claude agent (Opus 5.5). The repository clone was at commit 3c7c778. I wrote nothing inside the clone. All my output is in this folder:

- `python.json`: the result.
- `classify_tokens.py`: the token rules, applied by context and source line, with a coverage check.
- `outcomes.py`: the judgements for each stage.
- `assemble.py`: builds `python.json`.
- `residuals.py`: the residual equivalence check.
- `lines.py`, `show.py`, `summ.py`, `modecmp.py`: reading aids.

## Scope

- **Texts.** I classed 38 texts, the list in `TEXTS-1B-P04-P06.tsv`. Ten texts are shared between core and stdlib-concurrency: P04a to P04f, P06d and P06e1 to P06e3. Each is classed once, under its `core/` path. No token's class would differ between the two configurations, since neither uses an S mechanism and the files are identical. So none is classed a second time.
- **Records.** There are 144 records, 48 for each mode. None is `*.INVALID.json`, no record has a `harness_faults` entry, and there is no `raw-rerun-m2/` folder and no `rerun-m2-log.tsv` for these problems. Every attempt is attempt 1, posed fresh or incrementally, with no reposing and no timeout.
- **Cost and storage runs.** `modecmp.py` compared all 96 with their behaviour runs on the following fields:
  - answers and `ended_by`;
  - the execution state and the error's last line;
  - `observe.raw`, with addresses normalised;
  - `print`;
  - budget exhaustion;
  - the alternatives and suspended counts at the boundary.

  No stage differs, so `mode_differences` is empty. Steps are identical across the modes as well. Only the measurements differ. For example, extended P04c's storage run traced 853 MB at the budget.
- **P08.** There is no P08 in this batch, so `late_definition` is empty.

## Constructs that were hard to class, and the reading I took

1. **`for x in answers:` and `for _ in search(...)`, the loops that draw a query's answers.** I classed the loop header as H, as a stand-in for the harness's `answers()` (rule 13, "a stand-in for the fixed harness calls"). Python has no enumeration mechanism of its own (harness README 3.3). The `search(query, children, done, trail, stack)` call inside the extended header is C: S-mechanisms.md says "a search ... directive is C". The case against: rule 13 also says code that computes something the report depends on is not an adapter, and the loop does drive the generator. Rule 1 would make it P. This is the construct I am least sure of, and it touches every P04 and P06d/e text.
2. **Rule 19's boundary between R and S in core P06a to P06c.** `decide()` with `place()` and an `EVALUATOR` table is close to general over relations. I classed it R, as written for the program's own two relations, unlisted and not reused. If it is read as S (a small propagator), the program would belong to *extended*, so this is classification-sensitive. The same applies to stdlib-concurrency's `hold()`.
3. **Rule 19's split in P05.** The following are P:
   - the relations' tests (`pick`, `greater`, `different`, `equal`);
   - the returns of `holds`/`test`;
   - `source`'s computing returns;
   - `keep`'s comprehension (rule 7);
   - the arriving relation's application (`keep(name, k)` / `post(name, k)`).

   The following are R:
   - the name dispatch;
   - `source`'s `return None` (wait);
   - `arrive`'s holding and release code;
   - the cross-stage `values` / `x_has_values` / `held` state.

   Some readers may count `values` (the held solution set) as P. I took it as the holding state.
4. **Extended P05.**
   - `values` and `failed` are H: they only collect the store's domain for the harness and printing.
   - `store.relation(...)` and `store.var(X, given)` are P, as the constraints posted.
   - The `if not ...:` around the post is H, a failure note for printing.
   - `on_x()` is R, the relation recast as a one-place predicate.
   - `store = Store()` and the import are S.
5. **Extended P06a to P06c.**
   - `q.wait(...)` is C, both inside `Relation.__call__` and around the stage's goal, as a freeze call (S-mechanisms.md).
   - The `Relation(...)` expression that states the stage's relation is P.
   - `q.run()` is C.
   - `Relation`'s evaluation, bind and record code is R (rule 19), and `__repr__` is H.
6. **stdlib-concurrency.** All `threading` constructs are C: the import, `Condition`, `Thread(...).start()`, `wait_for`, `notify_all`, the `busy`/`news` counters, `settle()`, `told()`, `with changed:` and `new` flags. Within `hold()`, the evaluation, wait verdict, `waiting.append` and the bindings are R, as in core. `threading` is an external mechanism, not S.
7. **The extended resolution layer.**
   - `unify` with its `binder = Queue()`, `children`/`done`, and `negation` are S, as the program's own mechanisms (rule 15, general over terms and goals). I agree with the program's header there.
   - `trail = []` is S, with the listed search.
   - `stack = []` is H: it is given only so that it can be registered.
   - `cons()` is R, as the conversion of tuple constants to the cons-cell encoding. Rule 15 makes encoding operations P only where a systems file defines the encoding, and `systems/python` does not.
   - `NIL = ()` is P where a case uses it (⟨⟩). In extended P04a/b it is unused and R, and so is `cons` in P04a/b/d/f and P06e1 to P06e3. That dead code is the same text as in the P03 programs. Dead code fits no class well. I took it as R, a definition the problem does not give.
8. **Core `if x is None or x == k:` and the `s is None` tests in alist and student/maths.** I took these as P: the case and direction dispatch of a mode-faithful transcription (rule 3) serving the directions the program itself uses. P04c calls `alist(None)` internally, and P04d makes a ground recursive test.
9. **`known = {}` and `known["x"] = x`.** In P04, P06d and P06e3 these only feed `observe()`, so they are H. In core and stdlib P06a to P06c, `known` is the binding store the evaluators read, so it is R.
10. **Layout tokens.** INDENT and DEDENT take the class of the compound statement whose block they open or close, found with a stack. A comma before an argument takes that argument's class (rule 20). This matters for `s.constants[...]` reads (H) and for `cons(...)` (R) inside P statements.

## Outcomes that were hard to class

- **P06c stage 2 in all three configurations.** `observe()` reads the binding x = 1 next to the relation recorded as not holding, and the program prints "no solution". Taken alone, the binding would be a reported solution, which would make the stage unsound. I classed it *complete*: the observed state as a whole (x = 1 together with a failed not (x = 1)) denotes the empty set, and the program reports it as none.
- **P04f.** I classed it partial, explicit, budget: 20 answers collected and more printed after the cap. No finite representation was given. The order is fair by length, so every solution would be reached given enough steps. In core and stdlib, the one suspended generator is the computation stopped at the budget, not a separate held alternative.
- **P04a, P04c and P04d.**
  - In core and stdlib they end in `RecursionError`, classed *error*, not *budget* (systems file): about 995 `loop`/`alist` applications.
  - In extended the search is iterative, so they run to the budget with 12,768 or 10,267 choice points. Nothing is reported.
  - The endless alternative hides x = 1 in P04a. alist-left reaches no solution in either direction.
- **P04b.** It is complete, with x = 1 reported first, and its execution state is error (core/stdlib) or budget (extended).
- **Residuals.** The residual stages are P05b stage 1 (x > 1) and P06a/P06c stage 1 (not (x = 1)). Each is held, registered, acted on at the next stage and identical to the posed information. Each is reduced, at 1 relation and 1 occurrence. Each is equivalent to the valid outcome, checked by hand and on a sample by `residuals.py`. Extended P05b holds the comparison in the program's own list until pick gives x a finite domain, so no domain is imposed (AMENDMENTS 3.4).
- **Withdrawals.** P05a drops x = 1 at stage 2 and x = 2 at stage 3. P05c stage 2 withdraws x = 1, 2, 3 by reporting no solution. None of these is shown explicitly; the value is simply not reported again.
- **Record notes.** Two records (core P04b behaviour and stdlib P06e1 behaviour) carry a harness note that the program "is not committed unchanged at 1c758fd ...; program.repo_commit is null". I did not judge this. It is recorded here only.

## Rules I think ambiguous

- **Rule 13 against rule 1** for loops that both drive and collect answers, as in note 1. Python has no enumeration call, so some program code must stand in for `answers()`.
- **Rule 19's "general over relations".** It gives no test for a dispatch table plus a fixpoint loop written inside one program.
- **Rule 15's "where a systems file defines an encoding as P".** The extended programs' cons-cell encoding is cited to `systems/python/measurement.md` section 2. That section uses cons cells in probes but defines no encoding as P, so encoding conversions fall back to R.
- **Dead code.** No rule classes code that changes neither meaning nor behaviour.

## Files read outside the list

- My brief, `/Users/christopherhay/cp-roles/briefs/classifier-1B-A-python-P04-P06.md`, which I was given.
- One file in the tool's own output store under `~/.claude/projects/.../tool-results/`. It held this session's own printout of `harnesses/python/README.md`, saved there by the tool because it was long. I read it as that README and nothing else.

I read no other file outside the permitted list. In particular, I did not read `calibration/`, `reviews/`, `variants/`, `transcripts/`, `results/python/classes/`, the author's notes, or the other classifier's work.

## Summary

**Tokens.** 38 texts, 21,469 tokens, every one covered exactly once.

| | P | C | R | S | H | total |
|---|---|---|---|---|---|---|
| all texts | 5,538 | 1,557 | 4,241 | 2,900 | 7,233 | 21,469 |
| core (16 texts) | 2,141 | 0 | 1,374 | 0 | 2,242 | 5,757 |
| stdlib-concurrency (6 own texts) | 828 | 1,314 | 1,125 | 0 | 985 | 4,252 |
| extended (16 texts) | 2,569 | 243 | 1,742 | 2,900 | 4,006 | 11,460 |

Extended's S tokens are the program text's own:

- unify: 178 tokens in each of 10 texts;
- resolution: 58 in each of 10;
- negation: 50 in each of 4;
- imports, trail and instances of the listed search, queue and propagator.

The listed mechanisms are counted once for the configuration: search 176, queue 537, propagator 1,260.

**Outcomes.** 72 stage entries from 48 behaviour runs.

| semantic | representation | execution state | stages |
|---|---|---|---|
| complete | explicit | finished | 48 |
| complete | residual (reduced, identical to the posed information) | suspended | 9 |
| complete | explicit | error (P04b, core and stdlib) | 2 |
| complete | explicit | budget (P04b, extended) | 1 |
| partial | explicit | budget (P04f, all three) | 3 |
| none reported | none | error (P04a/c/d, core and stdlib) | 6 |
| none reported | none | budget (P04a/c/d, extended) | 3 |

- No stage is unsound, every stage was reached, and there are no harness faults.
- No cost or storage run differs from its behaviour run.

**Expressibility.**

- P04a to P04f, P06d and P06e1 to P06e3 are *expressible* in every configuration.
- P05a to P05c and P06a to P06c are *expressible with reformulation* in every configuration: the rule-19 holding code is R.
