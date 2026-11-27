# Classifier A, python, batch 1A (P01–P03): notes

Classifier A (a Claude agent, Claude Opus 5.5), working in the clone at commit
628a324. Output: `python.json` beside this file. Scripts used, all in this folder
and run with `python3 -I` on the records and token files only (no program and
no system was run):

| script | what it does |
|---|---|
| `keys.py` | reads the token files and the program sources; lists each line's enclosing top-level scope and token text (`keys.txt`) |
| `classify.py` | the token classes, as a table from (scope, line) to class, construct and rule; writes `tokens.json` and checks coverage |
| `showspans.py` | prints the spans of one text with their tokens, for checking by eye |
| `summarize.py`, `brief.py` | condensed views of the raw records |
| `modes.py` | compares every cost and storage record with its behaviour record |
| `equivalence.py` (`equivalence.out`) | brute-force checks of the residual and solved-form equivalences |
| `outcomes.py` | the outcome and expressibility judgements, written out by hand; assembles `python.json` and checks that the states it judges are the record's |
| `validate_mine.py` | checks that `python.json` is valid and that every token of every text is covered exactly once; prints the totals |

## Texts

The 30 texts of `TEXTS.tsv` are classed under their first paths. The six P03
texts of core are also those of stdlib-concurrency. They use no threading and
no S mechanism, and every construct has the same class in both
configurations, so they are classed once, under `core/`.

## Conventions I had to fix for the token spans

- **Layout.** A line's leading INDENT goes with the block header it opens, and
  its leading DEDENTs go with the construct before them, which is the block
  they close. A NEWLINE goes with its statement. The DEDENTs at the end of the
  file go with the last statement. The rules do not say where layout tokens
  go. The only choice that matters is a DEDENT that closes an R or C header
  after a P statement: here it is counted with the P statement. That moves at
  most a few tokens in each file.
- **Harness reads inside a construct.** `s.constants["..."]` and
  `s.params[...]` are cut out of the P, R or C construct around them as H
  (harness README, section 7, item 3). The comma before each one goes with it
  (rule 20).
- **Posting a stage's relation.** In `held.append((...))`, `pose((...))` and
  `q.wait(Relation(...))`, the wrapper call is R (holding), C (thread) or
  C+R (freeze call plus the holding wrapper). The argument is the stage's
  information, P. This is rule 10, nested constructs.

## Constructs that were hard to class

1. **The holding code in core and stdlib-concurrency (`decide`, `place`,
   `EVALUATOR`/`RELATION`, `hold`) and the `Relation` wrapper in extended
   P02.** I classed it R under rule 19's first bullet, as code written for the
   problem's own relations. But it is general: `decide` is a fixpoint loop
   over any held (name, places) pair, dispatching through a table, and the
   same text appears in all six P01/P02 programs. If it is read as "general
   over relations, reusable from one problem to another", it is S, and the
   core and stdlib-concurrency P01/P02 programs would belong to *extended*.
   This is the largest place where a classification is sensitive: about 200
   to 270 R tokens per program, and the configuration a program belongs to.
   Rule 19 does not say whether "general" means the program's structure or
   the author's intent to reuse it.
2. **The bindings dict `known`.** It is R in core and stdlib-concurrency
   P01/P02, because it is the store the holding code decides into (rule 19).
   It is H in core P03, because there it only collects an answer already
   computed, for `observe()` (rule 13). The P03a and P03e statements
   `known["c"] = conc(...)` are P as a whole: the assignment is the query.
3. **Failure bookkeeping (`failed`).** It is R in core and stdlib-concurrency,
   and in extended P02, where the holding code fills it. It is P in extended
   P01, where `if not q.bind(...)` and `failed.append(...)` are the stage's
   own equation found false, which changes the report (rule 1). The top-level
   `if failed:`, and its `else:` in extended, are P everywhere: they decide
   which result is reported, so they are not adapters (rule 13). The `print`
   of the "no solution" text is H. No stage in P01–P03 is inconsistent, so
   this code never runs, and the class rests on rule 1 alone.
4. **The relation evaluators (`equal`, `plus`, `times`, `conc_places`).** They
   are split by rule 19: the known-place tests and `return None` are R; the
   `def` header and every computing or testing return are P. The `if a != 0`
   inside `times` is P, because it is part of computing a factor. It is not a
   test of which places are known. `conc_places` computes c only from a and
   b, and waits in every other direction. By rule 19 every direction's
   computation would be P, but here the other directions are simply missing
   code, so no tokens are involved.
5. **Thread code in stdlib-concurrency.** C covers the `Condition`, the
   `busy`/`news` counters, `notify_all`/`wait_for`, `pose`, `settle` and
   `told`, and the `import threading`. Inside `hold`, the evaluation loop,
   the `waiting` record (and its `clear` in `told`) and the binding of
   results are R, as holding. Some lines mix the two roles, so the boundary
   between C and R inside `hold` is a judgement.
6. **The P02b constants block.** Each relation's constants are tagged under
   all three stages, because the harness tags by stage and the order is an
   instance parameter. That makes 9 entries where 3 are distinct. I classed
   all of them P, as block entries are the stages' information (harness
   README, section 7). That is 24 P tokens more than P02a in every
   configuration.
7. **The order dispatch in P02b** (`name = s.params["order"][s.k - 1]`,
   `if name == "R1":`). I classed it H, as dispatch on what the stage brings,
   by analogy with `if s.k == 1:`. The harness README's list names only the
   `s.k` tests and the `s.params` read.
8. **The enumerating loops of core P03b/c/d/f** (`for a, b in answers:`). I
   classed them P: the query asks for every answer, and removing the loop
   changes what is reported (rule 1). The call of the direction function is
   also P (it is the query). The function itself is R (rule 14). In extended,
   the loop `for _ in search(...)` is C, a search directive.
9. **Extended's S.** The `from S... import` lines and the `Queue()`
   instances are S, as the program's link to the configuration's
   mechanisms; C would also be defensible. The program's own `unify` and
   resolution (`children`, `done`) are S under rules 12, 15 and 19, as their
   author declares. They are repeated in each of the six extended P03 texts,
   261 S tokens each: unify 172, resolution 58, the imports 20, `binder` 6,
   `trail` 5. Counted once per mechanism (rule 12), the program's own S is
   unify (172) and resolution (58). The heads of the conc and rev cases, each
   `unify(...)` call that states a head, the case variables and the bodies
   are all P. `stack` is H, because it exists only to expose the choice
   points to `observe()`.
10. **`cons()` and `NIL` in extended.** I classed them P under rule 15, as
    construction of the encoded sequences. Rule 15 applies "where a systems
    file defines an encoding as P". `systems/python/measurement.md` uses this
    cons-cell encoding but does not declare it P, so R is also arguable. That
    would be 48 tokens in extended P01b and P01c, and 53 in each extended P03
    text (with `NIL`), moved from P to R.
11. **`deref` inside extended's `conc` (P01b, P01c).** I classed it P, as a
    decomposition of an encoded term (rule 15).

## Outcomes that were hard to class

1. **Core and stdlib-concurrency P01a, stages 1 and 2: a held equation x = y
   against an identified unknown.** I classed it a residual that is
   *reducible*, because the solved form ("identified with another unknown")
   leaves no relation to decide. Extended's shared Var is a solved form. A
   reader who treats "x = y, recorded" as already the identification would
   call it *reduced*.
2. **P02 with R1 and R2 held, and nothing bound** (P02a/R1R2R3/R2R1R3 stage 2,
   in every configuration): *reducible*, because the ten explicit triples
   leave no relation to decide. This depends on a finite explicit set
   counting as "smaller" under the size rule. If it does not, the
   representation is *reduced*, since no two-relation form has fewer than 5
   occurrences of unknowns.
3. **P01c in core and stdlib-concurrency** (the relation held, never
   decided). Under the finite reading it is *complete*, with simplification
   *inconsistency undetected*: the residual denotes the empty set, and the
   program never says there are none. Under the rational reading it is
   *complete*, *reducible*: a cyclic binding would be smaller, and Python
   tuples cannot hold one.
4. **Extended P03f, after its answer.** At the budget, `observe()` reads the
   binding a = a 17-cell sequence of unbound Vars. That is the search's
   tentative state on a deeper branch. On a literal reading of SPECIFICATION
   ("a binding that the system holds is reported if `observe()` can read it
   ... at the moment a budget runs out"), it would be a reported invalid
   outcome, and the result would be *unsound*. I followed P03's own
   observation, which says a system that reports the solution and then runs
   out of budget is *complete* with *budget*. The rule on reported bindings
   should say whether it covers a backtracking search's tentative bindings.
   The execution state is *budget* alone, though 108 choice points were held
   at the budget. The system had not stopped after an answer, so
   *alternatives pending* does not apply.
5. **Extended P03a–e: bindings unbound at the boundary.** The search is
   exhausted, the trail is undone, and `observe()` shows the query's Var
   unbound. The answers came through `cp.answer` during the search, so the
   semantic class rests on them.
6. **P02 with R2 and R3 (R2R3R1 and R3R2R1, stage 2):** *residual*, *reduced*,
   *not identical to the posed information*. R3 was decided into u = 2. R2 is
   still held: in core and stdlib-concurrency, as `('R2', ('w','u','v'))`
   beside the binding u = 2; in extended, as `R2(w, 2, v)`. P02 with only R3,
   or R1 and R3, is a solved form, with the free unknowns unmentioned or
   unbound.
7. **Execution states.** They are the harness's, and each is determined from
   the program's registrations. None needed quiescence. Every stage was
   reached, and no measurement was missing (AMENDMENTS 3 did not apply).
8. **Cost and storage runs.** `modes.py` compared all 102 of them with their
   behaviour runs. It compared, stage by stage: the answers, `ended_by`, the
   states, the suspended and alternatives counts at the boundary, and
   `observe()` with memory addresses masked. No stage differs, so
   `mode_differences` is empty. Extended P03f reaches the budget at the same
   point in all three modes.

## Rules I think ambiguous

- **Rule 19:** what makes holding code "general over relations" (item 1 above).
- **Rule 15:** whether an encoding the systems file uses, but does not declare
  P, counts (item 10 above).
- **The size rule for "reducible":** whether an explicit finite set, and an
  identification of unknowns, are smaller than the same information held as
  relations (outcomes 1 and 2 above).
- **"Reported" bindings at a budget** in a backtracking search (outcome 4).
- **Layout tokens:** where INDENT and DEDENT go is not stated.

## Files read outside the brief's list

- None in the repository. I read only the files the brief allows. That
  included `systems/python/measurement.md` (grepped), `harnesses/python/S/*.py`,
  `S-mechanisms.md`, `QUESTIONS.md` and README, the stages file, the programs
  other than the author's notes, the records, the batch log and the token
  files.
- Outside the repository: the brief itself
  (`~/cp-roles/briefs/classifier-A-python.md`), which was my task. The agent
  environment also put an auto-memory index from `~/.claude/projects/...` into
  my context at the start: two titles, about Absys sources and commit
  trailers. I did not open it, and it has no bearing on this work. The tool
  harness saved two of my own long command outputs under `~/.claude/...`
  (tool-results). I did not read them; I read the same files from the clone
  instead.
- I did not read `calibration/`, `reviews/`, `variants/`,
  `programs/python/README.md`, `programs/AUDIT-1A.md`, any other system's
  folder, or the web.

## Summary

**Tokens** (30 texts, 18,215 tokens, each covered once):

| configuration (texts) | P | C | R | S | H | total |
|---|---|---|---|---|---|---|
| core (12, the six P03 shared with stdlib-concurrency) | 1,307 | 0 | 1,935 | 0 | 1,882 | 5,124 |
| stdlib-concurrency (6: P01, P02) | 1,051 | 1,321 | 1,405 | 0 | 1,045 | 4,822 |
| extended (12) | 2,585 | 259 | 804 | 1,668 | 2,953 | 8,269 |
| **all** | **4,943** | **1,580** | **4,144** | **1,668** | **5,880** | **18,215** |

Per text (P, C, R, S, H): core P01a 58/0/225/0/195; P01b 159/0/263/0/190;
P01c 104/0/202/0/173; P02a 230/0/322/0/165; P02b 254/0/322/0/175; P02c
230/0/320/0/147; P03a 65/0/0/0/130; P03b 23/0/51/0/151; P03c 30/0/56/0/144;
P03d 30/0/57/0/144; P03e 101/0/0/0/127; P03f 23/0/117/0/141. Extended P01a
100/0/0/17/233; P01b 188/0/0/17/312; P01c 150/0/0/17/402; P02a
255/51/268/17/219; P02b 279/51/268/17/229; P02c 255/49/268/17/201; P03a
196/18/0/261/226; P03b 194/18/0/261/231; P03c/P03d 198/18/0/261/226;
P03e/P03f 286/18/0/261/224. Stdlib-concurrency P01a 70/223/191/0/195; P01b
159/218/219/0/190; P01c 108/213/182/0/173; P02a 230/223/271/0/165; P02b
254/223/271/0/175; P02c 230/221/271/0/147. S is reported apart, once per
mechanism: extended's listed suspension queue and search, and the programs'
own unify (172 tokens) and resolution (58).

**Outcomes** (51 behaviour runs, 102 stages, and 105 entries, since P01c is
classed under both readings):

| class | entries |
|---|---|
| complete / explicit | 48 |
| complete / solved form | 15 |
| complete / residual / reduced | 21 |
| complete / residual / reducible | 17 |
| complete / residual / inconsistency undetected | 2 (P01c finite, core and stdlib-concurrency) |
| complete / cyclic | 1 (extended P01c, rational reading) |
| unsound / cyclic | 1 (extended P01c, finite reading) |

- Of the 40 residual entries, 34 are identical to the posed information.
- Execution states: 64 *finished*, 40 *suspended*, 1 *budget* (extended P03f,
  after its one answer).
- No stage was not reached, no error, no timeout, no manual action, and no
  conclusion was withdrawn.
- No cost or storage run differs from its behaviour run.

**Expressibility** (36 entries):

- *core* and *stdlib-concurrency*: P03a and P03e are *expressible*. The other
  ten, every P01 and P02 sub-problem and P03b/c/d/f, are *expressible with
  reformulation*: the holding code is R (rule 19), and the direction
  functions are R (rule 14).
- *extended*: P01a–c and P03a–f are *expressible*. P02a–c are *expressible
  with reformulation*, because of the Relation holding wrapper (R, rule 19).
