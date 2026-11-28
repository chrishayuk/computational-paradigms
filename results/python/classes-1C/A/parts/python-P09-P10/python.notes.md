# Classifier 1C-A, python, P09 and P10: notes

Classes are in `python.json`. They were built from `specs.py` (construct by construct, with
the rule) by `build.py`, assembled by `gen.py` and checked by `verify.py`. Every token of
the 20 texts in `TEXTS-1C-P09-P10.tsv` is covered exactly once. `check_residuals.py` checks
the residuals by enumeration. The helper scripts `view.py`, `tview.py`, `cview.py`,
`summarize.py` and `modecmp.py` only read the token files and the records. I ran no program
and no part of the system.

## Files read outside the brief's list

- The brief itself, `~/cp-roles/briefs/classifier-1C-A-python-P09-P10.md`. I had to read it
  to start.
- None other. My session context showed the index of the user's auto-memory (two
  one-line entries). I did not open it, and it has nothing to do with this study.
- Inside the clone I read only files on the list. Directory listings showed the names of
  `results/python/classes*/`, `results/python/*/P0x.md` and `calibration/`, but I opened
  none of them. `results/python/rerun-m2-log.tsv` does not exist at this commit, and there
  is no `raw-rerun-m2/` or `*.INVALID.json` for P09 or P10.

## Conventions I fixed before classing (they apply to every text)

1. **Layout tokens.** I read rule 20 as covering significant layout. An INDENT or DEDENT
   takes the class of the construct that follows it. An INDENT on a line that holds only a
   docstring also takes the next construct's class. The DEDENTs at the end of a file take
   the class of the last construct. NEWLINE ends its statement and takes that statement's
   class. The other classifier may instead give DEDENTs to the block they close, which
   would move a few tokens per text between classes.
2. **`s.constants`.** Every read of `s.constants` or `s.constants[...]` is H (harness
   README 7.3), applied automatically.
3. **Constants kept by the program.** This covers `C = {}`, `C.update(...)`,
   `C["..."]`, `definition = {}` and `definition["last"]`. I classed them P, because they
   hold the stage's information. I followed the harness README's own example, where
   `known["a"] = s.constants[...]` is not H except for the read. The other possible reading
   treats them as H stand-ins for the harness calls (rule 13). That would move about 10 to
   30 tokens per P09 text from P to H.
4. **Bindings holders.** A dict that is the program's real store of values (`known`,
   `quantities`) is P. A dict that only names Vars for `cp.bindings` and the answer
   (`unknowns` in extended P09e) is H. `UNKNOWNS` and `NAMES`, which only set the print
   order, are H.
5. **Report tests.**
   - `if failed:` (no solution) and its `return` are P.
   - `elif known:`, `and quantities` and `if told:` are P, because removing them would
     report an empty answer (rule 1).
   - The test that s is known to its end and total is bound (extended and stdlib P09c/P09d
     `report()`) is R. It is the holding's known-places test (rule 19), and rule 13 excludes
     it from adapters, since it decides what is reported.
   - The `for v in values: cp.answer(...)` loops and `report()` calls are H.
6. **S in extended.**
   - An `from S... import` line is S. The mechanism's own tokens are counted once in `S/`.
   - An instance of a mechanism or a trail (`q = Queue()`, `store = Store(trail)`,
     `trail = []`) is C (rules 1 and 16).
   - `search(...)` is a search directive and is C. Its goal argument is P. The `stack`
     argument and `stack = []` are H, because they exist only so that `cp.pending` can
     count them.
   - In extended P09a, `binder = Queue()` serves only the program's unifier, so it is S
     with `unify`.
7. **Posting a relation.**
   - The relation itself (the tuple, `Goal(...)` or `Relation(...)`) is P.
   - The posting wrapper is C when the receiving mechanism is S, as a freeze-like call or a
     thread call: `q.wait(`, `pose(`, and `held.append(` in core P09e. The calls that run
     the mechanism (`q.run()`, `settle()`, `decide()`) are C as well.
   - The wrapper is R when the holding is the program's own problem-specific code
     (`standing.append(` in core P10b).
   - Calls in the stage loop that state a stage's information through a function of the
     program are P: `tell(1, "pick")`, `tell(2, ">", k)`, `withdraw(2)` and `become(...)`.
     The function bodies are classed separately (rule 10).
8. **Evaluators** (plus, minus, equal, and the waiting branches of gen, genu and sum3) are
   split by rule 19.
   - Computing a place, or testing a relation whose places are all known, is P.
   - Tests of which places are known, and `return None` or `return t` as the verdict to
     wait, are R.
   - The `def` line of the evaluator of a primitive relation is P.

## Constructs that were hard to class

- **The generic holding code in core P09e (`decide`, `place`, `held`), classed S.** It is
  general over relations: it dispatches through the `EVALUATOR` table and never names + or
  −. The author also reuses it from P02 and P07. Rule 19, second bullet, makes such code S
  and **puts the program in *extended***, so core P09e, as written, is not a core program
  under rule 19. The alternative reading takes the first bullet ("written for the
  problem's own relations") and classes it R. That would move 165 tokens from S to R, and
  the 18 C tokens of posting and calling would become R. This is
  **classification-sensitive**. I classed `EVALUATOR` R, because it lists this problem's
  relations.
- **The program-supplied "relation threads" in stdlib-concurrency P09c, P09d, P09e, P10b
  and P10d, classed S.** These are `told`, `hold`, `pose`/`arrive`, `settle`, `place`, the
  condition, the waiting list and the busy count. They form a hand-written scheduler and
  suspension layer, reused (by the authors' own provenance) from P02, P05 and P08. Rule 19
  and `S-mechanisms.md` again put these programs in *extended*.
  - In P10b and P10d, `hold()` is problem-specific. There I split it: the holding tests are
    R, the evaluation is P, and the waiting protocol (`waiting.append`, busy count,
    `notify_all`, `wait_for`) is S.
  - `import threading` is S here, because it serves only that layer. threading itself
    remains an external mechanism of the configuration.
- **unify and resolution (`children`, `done`) in extended P09a, classed S.** The author
  names them program-supplied S, and I agree: they are general mechanisms (rule 15, last
  sentence). They are not listed in `S-mechanisms.md`.
- **`Goal` (extended P09c/P09d) and `Relation` (extended P09e), classed S.** They are
  adapters from any relation to the queue. Their `__repr__` methods are H as output
  adapters.
- **The waiting branch of sum3 in extended and stdlib P09c/P09d, classed R.** This makes
  P09c and P09d *expressible with reformulation* in those configurations. Core P09c, which
  runs gen to its end first, is *expressible*. The verdict follows rule 19 as written, but
  it means that a suspension-based program is charged R for the very waiting the problem
  probes. I think rule 19's evaluator split may be too broad here (see "Rules I find
  ambiguous").
- **Core P09a `for x in answers:`, classed P.** It is the query's enumeration of the
  relation's own solutions, not a generator of values the problem does not state (rule 6).
- **Extended P09b `undo(trail, 0)`, classed P.** Without it, observe() would report the
  failed conjunction's binding x = 1 (rule 1). In core P09c/P09d, `del known["s"]` is P for
  the same reason.
- **P10d.**
  - The machinery of withdrawal (`information`, `tell`, `withdraw`, and `marks` and
    `undo(trail, ...)` in extended) is R. P10's observations say that indexing written for
    the purpose is reformulation.
  - `holds`/`test` and `source` are R for the dispatch and the wait verdict, and P for
    evaluating pick and >.
  - In extended P10d, `on_x()` is R: an adapter the problem does not give. Line 158, which
    reads the store's domain into `values`, is H, as collecting for the harness an answer
    already computed.
- **The core P10b standing relation, classed R.** `standing`, `maintain()` and the source
  test are R (rule 19, problem-specific). The evaluation `quantities[target] = times(...)`
  is P.

## Shared texts

The 20 distinct texts are classed once each, under their first paths. No token's class
differs between the configurations that share a text:

- core/P09a and core/P09b are also stdlib-concurrency's. Spawning side by side changes the
  behaviour, not any construct.
- core/P10a, P10b and P10c are also extended's (and P10a and P10c stdlib's). Neither
  extended copy uses S.

So no text is classed again under another path.

## Outcomes that were hard to class

- **P09b, A (empty valid outcome).** The program gives no answer and prints "no solution".
  I classed it *complete*: the report denotes exactly the empty set, and answer
  completeness records that it reported none (yes). I recorded the representation as
  *explicit*, but for an empty set it could reasonably be null.
- **P09d.** One run is classified under both readings.
  - Extended and stdlib run to the budget with total = 6 bound and no answer. Under
    P09d1 that is *none reported*, *budget*, with the binding as an observation, as the
    problem file says. Under P09d2 it is *complete* (for total), *solved form*, *budget*.
    s is bound to a finite prefix with an unbound tail: 5,008 cells in extended, 1,129 in
    stdlib.
  - Core errs with a RecursionError before sum3 runs, so it is *none reported* / *error*
    under both readings.
- **P09a, A.** Core and stdlib end in a RecursionError, so *none reported* / *error*.
  Extended reaches the budget with 12,821 search choice points registered, so *none
  reported* / *budget*. I did not add *alternatives pending*: the state is defined as
  "stopped after an answer".
- **Extended P09a, B.** b = ⟨3,2,1⟩ is reported during the search. At observe(), b is
  unbound again, because the exhausted search undid its trail. The answer stands
  (*complete*).
- **stdlib-concurrency P09a.AB, B: steps 0.** The behaviour and cost runs record B's steps
  as 0 and its first answer at 0, while the storage run and order BA give 219. B evidently
  ran while A's traceback was being formatted, when instruction events are off (harness
  confound 5). I read the 0 as unavailable (AMENDMENTS 3.1), although no harness fault is
  recorded.
- **P10b, stages 2 to 4.** These have two forms: the explicit values, and the standing
  relation still held. I classed them on the explicit form, with the residual as an
  observation (SPECIFICATION, Outcomes 2). Their execution state is *suspended* (1 item):
  work that later information resumes.
- **P09e.** The residual is held exactly as posed (identical: true). It is *reducible*,
  since x = y + 1 alone is smaller. It is suspended with 2 items in all three
  configurations, and none of them reports a deadlock.

## Mode differences

I compared every cost and storage record with its behaviour run. The comparison covered
each computation's states, answers, ended_by, suspended and alternatives counts and
problem-defined alternatives, observe.raw (with object addresses normalised) and stdout.
**No classification differs**, so `mode_differences` is empty. The only differences are
measurements: the stdlib P09a.AB B steps above, and the cost-mode problem operations, which
are quoted in the observations.

## Late definition

There is no P08 in this batch, so `late_definition` is empty.

## Rules I find ambiguous or wrong

- **Rule 19, "general over relations".** The threshold is not stated. A five-line fixpoint
  loop over an evaluator table (core P09e) or a thread layer (stdlib) qualifies on its
  face, which pushes core and stdlib programs into *extended*. The rule needs a test (for
  example, "names no relation of the problem") and a statement of what happens to a
  program whose configuration then changes.
- **Rule 19, the evaluator split, applied to suspension in extended.** Charging R for
  "wait on this Var" inside a relation that the S queue holds makes every suspension-based
  transcription *expressible with reformulation*. The sequential core program avoids that
  only because it never waits.
- **Rule 20 and layout.** The rule does not say which construct a DEDENT belongs to.
- **Posting calls.** Whether a freeze-like posting into a program's own (R) holding code is
  C or R is not stated, and neither is whether a stage-loop call such as `tell(...)` is P.
- **The representation of an empty outcome** has no class of its own.

## Summary

**Tokens:** 11,229 tokens in 20 distinct texts.

| class | tokens |
|---|---|
| P | 3,577 |
| H | 3,572 |
| S | 2,301 |
| R | 1,540 |
| C | 239 |

**Per configuration, counting shared texts in each configuration that uses them:**

| configuration | tokens | P | C | R | S | H |
|---|---|---|---|---|---|---|
| core | 2,864 | 1,102 | 18 | 379 | 165 | 1,200 |
| extended | 4,850 | 1,520 | 149 | 672 | 678 | 1,831 |
| stdlib-concurrency | 5,002 | 1,552 | 72 | 530 | 1,458 | 1,390 |

**Per text:**

| text | tokens | P | C | R | S | H |
|---|---|---|---|---|---|---|
| core/P09a.py | 330 | 181 | 0 | 0 | 0 | 149 |
| core/P09b.py | 179 | 89 | 0 | 0 | 0 | 90 |
| core/P09c.py | 314 | 165 | 0 | 0 | 0 | 149 |
| core/P09d.py | 267 | 124 | 0 | 0 | 0 | 143 |
| core/P09e.py | 599 | 167 | 18 | 112 | 165 | 137 |
| core/P10a.py | 133 | 43 | 0 | 0 | 0 | 90 |
| core/P10b.py | 278 | 87 | 0 | 41 | 0 | 150 |
| core/P10c.py | 217 | 77 | 0 | 0 | 0 | 140 |
| core/P10d.py | 547 | 169 | 0 | 226 | 0 | 152 |
| extended/P09a.py | 911 | 355 | 33 | 0 | 255 | 268 |
| extended/P09b.py | 243 | 107 | 15 | 0 | 18 | 103 |
| extended/P09c.py | 814 | 264 | 31 | 67 | 103 | 349 |
| extended/P09d.py | 761 | 216 | 32 | 67 | 103 | 343 |
| extended/P09e.py | 684 | 185 | 26 | 100 | 185 | 188 |
| extended/P10d.py | 809 | 186 | 12 | 397 | 14 | 200 |
| stdlib-concurrency/P09c.py | 1097 | 384 | 13 | 104 | 349 | 247 |
| stdlib-concurrency/P09d.py | 1046 | 338 | 14 | 104 | 349 | 241 |
| stdlib-concurrency/P09e.py | 773 | 167 | 14 | 112 | 347 | 133 |
| stdlib-concurrency/P10b.py | 488 | 105 | 10 | 29 | 195 | 149 |
| stdlib-concurrency/P10d.py | 739 | 168 | 21 | 181 | 218 | 151 |

**Outcomes:** 72 stage entries from 30 behaviour records, one entry per computation for
P09a and P09b and one per reading for P09d.

- Semantic: 62 *complete*, 10 *none reported*. None is *unsound*, *partial* or
  *undetermined*.
- Execution state: 45 *finished*, 15 *suspended*, 6 *error*, 6 *budget*.
- Representation: 54 *explicit*, 6 *residual*, 2 *solved form*, and 10 with none.
  - Residuals: P09e ×3 is *reducible* and identical to the posed information; P10b
    stage 1 ×3 is *reduced* and identical to the posed information.
  - Solved form: P09d2 in extended and stdlib.
- The 10 *none reported*:
  - P09a A in every configuration: error in core and stdlib, budget in extended.
  - P09d in core: error under both readings.
  - P09d1 in extended and stdlib: budget, with total = 6 bound as an observation.
- P10 is *complete* at every stage in every configuration. P10d's withdrawal restates in
  core and stdlib, and undoes the trail in extended.

**Other sections:**

- No harness faults and no measurement reruns. Cost and storage runs add no
  classification differences.
- Expressibility: 33 entries.
- S mechanisms: 20 entries. 9 are listed at phase 4, and 11 are supplied by the programs
  (core P09e; stdlib P09c, P09d, P09e, P10b and P10d; extended P09a ×2, P09c, P09d and
  P09e).
