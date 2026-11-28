# ALGOL 60, P11 and P12, batch 1C: notes of classifier 1C-A

Files in this folder:

- `algol-60.json`: the classes, outcomes, expressibility and S mechanisms.
- `classify_tokens.py`: the token classes. Each construct starts at an anchor (a line and a token there). Rule 20 is applied mechanically, and the script checks that every token is covered exactly once.
- `make_output.py`: builds `algol-60.json` from the records.
- `summarize.py` and `compare_modes.py`: read-only helpers for the records.

## What was read

I read only the files the brief allows:

- `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md` and `AMENDMENTS.md`;
- `problems/README.md`, and the problem files 11, 12 and 05;
- `systems/algol-60/README.md`;
- `harnesses/README.md`, `harnesses/stages.json` (the P11 and P12 entries and the header) and `harnesses/algol-60/{README.md, QUESTIONS.md, S-mechanisms.md}`. I did not need `run`, `check` or `qualification/` and did not open them;
- the P11 and P12 programs and `.constants` files in `programs/algol-60/{report,x1,x1sim}/`;
- the raw records and effects logs in `results/algol-60/{report,x1,x1sim}/{P11,P12}/raw/`;
- `results/algol-60/logs/1C-*-P11.tsv` and `1C-*-P12.tsv`, and `batch-log.tsv`, which has no P11 or P12 row;
- the token files and `TEXTS-1C-P11-P12.tsv`.

I read no file outside that list. I did not touch any other system, `calibration/`, `reviews/`, `variants/`, `transcripts/` or any class or result file. I ran no program and no system. I also never opened `record.schema.json`: the records themselves show its fields.

Some expected files do not exist:

- `results/algol-60/rerun-m2-log.tsv` is missing, and no `raw-rerun-m2/` folder exists for P11 or P12. So there are no measurement reruns to compare.
- No `*.INVALID.json` record exists for P11 or P12. So no entry has `harness_fault: true`.

## Texts classed

There are 10 distinct texts. Each x1 text is also the x1sim text. I classed each once under the x1 path, because no token would take a different class in x1sim: neither configuration has an S mechanism, and `read`, `print`, `PRINTTEXT` and `NLCR` are the X1 system's own procedures in both. Each configuration's 24 P12 files are one text, classed under `P12a.n12.all`.

| text | tokens | P | C | R | H | S |
|---|---|---|---|---|---|---|
| report/P11a.alg | 561 | 96 | 14 | 0 | 451 | 0 |
| report/P11b.alg | 559 | 95 | 13 | 0 | 451 | 0 |
| report/P11c.alg | 871 | 119 | 12 | 87 | 653 | 0 |
| report/P11d.alg | 871 | 119 | 12 | 87 | 653 | 0 |
| report/P12a.n12.all.alg (the 24 P12 files) | 901 | 408 | 27 | 13 | 453 | 0 |
| x1/P11a.a60 (and x1sim) | 506 | 87 | 14 | 0 | 405 | 0 |
| x1/P11b.a60 (and x1sim) | 504 | 86 | 13 | 0 | 405 | 0 |
| x1/P11c.a60 (and x1sim) | 792 | 110 | 12 | 87 | 583 | 0 |
| x1/P11d.a60 (and x1sim) | 792 | 110 | 12 | 87 | 583 | 0 |
| x1/P12a.n12.all.a60 (the 48 x1 and x1sim P12 files) | 853 | 399 | 26 | 13 | 415 | 0 |
| **all 10 texts** | 7210 | 1629 | 155 | 374 | 5052 | 0 |

## Constructs that were hard to class

1. **The stop at the first outcome (P11a to P11d; P12 any).** In P11 this is the flag `ok`, its `false` and `true` assignments, and the `¬ok ∧` condition of the loop over pick's facts. In P12 it is `anyone`, `cap`, `if anyone then go to done` and the label `done:`.
   - I classed all of these C. In P11 it is an any-one query, but nothing in ALGOL collects one answer: the program stops itself, as `once/1` or a cut would.
   - In P11, removing the condition also changes the effects: later facts would be emitted too. So it changes meaning as well as operation, and rule 2 makes it C.
   - In P12 it is purely operational (rule 1), because the harness collects only the first `cap` answers either way.
   - A classifier who reads the any-one query as P would class these as P.

2. **The P12 enumeration: P, R or S?** The P12 rules say "a search written by hand is supporting code".
   - I classed `choice` as P (rule 3): it is a mode-faithful transcription of its two cases in order. The query uses it with n known and s unknown. The disjunction e = ʟ or e = ʀ is two statements in its stated order (rule 6). s gets its value through a name parameter.
   - The depth-first order is ALGOL's own sequential execution and recursion. No frontier, choice-point stack or general backtracking was written, so I counted no S.
   - The procedure parameter `found` is R (rule 3: an argument the problem does not give). So is `accept` passed as that argument in the query: 13 tokens in all. They carry the conjunction "and accept(s)" into the generator.
   - This is the most classification-sensitive point. Classing the enumeration as S would make P12 *not expressible* in core ALGOL 60, since `S-mechanisms.md` lists none.

3. **`top := top - 1` in `choice`.** It frees the cell for reuse, so I classed it C by rule 16.

4. **P11c and P11d holding (rule 19).**
   - I classed as R: the flags of the relations posed (`picked`, `xk`, `r2`/`r3`, `committed`), the heading and tail of `holds`, the heading of `advance` and its `xk := ok`, the initialisation, and the re-test after each stage that resumes the untried facts (`if xk then begin if ¬ … then advance end`). That is 87 tokens.
   - Under rule 19's evaluator split, the tests of the relations themselves (`x ≠ c`, `x = cv`, the conjunction `∧`, and `holds(xv)` where it is applied) are P.
   - The loop inside `advance` (the next fact, x's value, `emit(x)`) is classed as in P11a: P, with its stop-at-first parts C.
   - The commit stage's `cv := xv; committed := true` is P ("emit and commit are problem tokens"). So is `committed := true` after a replayed commitment (harness README 2.7.1 leaves turning v into x = v to METRICS.md). Its guard `if xk then` is R: a test of what is known.
   - The *declaration* of `committed` is R, with the other holding flags. Another classifier might class the flag P with the commit.

5. **Variables that are read but unused.** In P11, `n` and `cap` are read from the instance line and never used. I classed them H, since they hold only harness words (2.7.5). In P12, `n` is P: an instance parameter the program uses. `cap` is C, because it is used only to decide the any-one stop.

6. **`untried`, `nsol` and the P12 depth and pending counters.** I classed these H: they are computed only for the observe block. `nsol` also prints "no solution", but it decides nothing that is reported.

7. **The program block's `begin`/`end`, and the P12 inner block.** I classed these P under rule 10, as the blocks that hold the query. The identifier after `end` (`end num`, `end choice`) is a comment in ALGOL 60, but the frozen tokenizer counts it. It takes the class of the procedure it closes.

## Outcomes

There are 96 behaviour stage entries:
- P11: 3 configurations, 8 stages (P11a 1, P11b 1, P11c 3, P11d 3), 24 entries;
- P12: 3 configurations, 24 instances, 72 entries.

**P11.** All three configurations behaved the same, entry for entry and stage for stage. In x1sim the computation is one live process. In report and x1 it was re-created for its budget (harness README 3.1). That re-ran the earlier stages, and for P11d stage 3 it carried out the commit of stage 2 again (`prefix_commit_stages_carried_out_again: [2]`). Their emits were not appended to L again, so no entry in L is a reposing duplicate. x1sim, with no re-creation, gives the same L, which corroborates this.

| sub-problem | answers by stage | semantic | L | effects |
|---|---|---|---|---|
| P11a | 2 | complete | ⟨2⟩ | exact |
| P11b | 2 | complete | ⟨1, 2⟩ | extra |
| P11c | 1, 2, 2 (commit) | complete at every stage | ⟨1, 2⟩ | extra |
| P11d | 1, 1 (commit, v = 1), none ("no solution") | complete at every stage | ⟨1, 2, 3⟩ | extra |

- **P11b:** entry 1 was emitted on a provisional outcome that the test refuted in the same stage.
- **P11c:** entry 1 belongs to x = 1, which stage 2 refuted and was never committed. Entry 2 was emitted at stage 2, before the commitment, on the outcome that was then committed.
- **P11d stage 3:** x ≠ 1 contradicts the committed x = 1. The program resumed pick's untried facts and emitted 2 and 3 *after* commitment, each before testing it. It found none valid and reported no solution. The committed entry 1 stays in L.

All semantic results are complete and every representation is explicit. P11d stage 3 is the empty outcome reported as empty: I classed its representation explicit, with no solutions.

**Execution state in P11c and P11d.** I classed the stages where pick has untried facts as *alternatives pending*: P11c stages 1 to 3, and P11d stages 1 and 2.
- The program says it keeps them for backtracking (`[held-as backtracking]`, `[problem-alternatives x N]`).
- The harness recorded *finished*, because the program prints no `[alternatives]` or `[suspended]` tag.
- Only later information resumes these alternatives, not a request for more answers. So *suspended* is also defensible. This is a likely point of disagreement.
- P11d stage 3, with no untried fact left, is *finished*.

**P12, report and x1.**
- All 48 behaviour runs are complete, explicit and finished. Every "all" run reported every valid solution, ⟨ʟⁿ⟩ before ⟨ʀ⟩ in P12a (depth-first order), with no invalid answer, and finished after the last.
- Candidates examined match depth-first in the order written:
  - all runs: 2ⁿ⁺¹ − 1;
  - P12a and P12d any: n + 1;
  - P12b any: 2ⁿ + 1;
  - P12c any: 2ⁿ⁺¹ − 1.
- The partial sequence held is at most n cells, with at most n alternatives (e = ʀ) kept for backtracking on ALGOL's own recursion stack.
- Steps (cost runs) and peaks (storage runs) are in each entry's observations.

**P12, x1sim.** All 24 runs stopped at stage 1 with `Error: Unknown descriptor of formal procedure: 40600011`, and no output at all.
- I classed each as *none reported* / *error*. The stage was posed and failed, so it is an error of the stage, not *not reached* (AMENDMENTS 3.2).
- The same text runs to completion in x1. So this is a fault of the x1sim compiler or of its reconstructed run-time with procedure (or name) parameters, not of the problem.
- The record cannot show exactly where the error happened, because nothing was printed before it. The program's only formal procedure is `found`, which is first called on the first candidate.

**Cost and storage runs.** I compared 112 records with their behaviour runs: report and x1, P11 and P12, on answers, `ended_by`, execution state, the observe text and the entries emitted. No stage differs, so `mode_differences` is empty. Cost and storage runs write their entries to the observation log, which holds the same entries per stage as the classification log.

**Residual equivalence.** No stage reports a residual or a solved form. Every reported outcome is explicit, and I checked it by `make_output.py`'s assertions against the valid outcomes. So residual equivalence does not apply.

**Domain (AMENDMENTS 3.4).** No program imposes a domain on an unknown beyond the problem's own:
- pick is a closed world of facts;
- s ranges over choice's sequences;
- the fixed store sizes (`fv[1:1000]`, 2000 cells for facts) bound the constants a program can read, not the unknowns.

## Rules I found ambiguous

- **P12's "a search written by hand is supporting code".** In a language whose only strategy is sequential execution, a transcription of a disjunctive generator *is* a depth-first search written by hand. The rule does not say whether it means a general mechanism (a frontier, a backtracking engine) or any enumeration code. I read it as the former (point 2 above).
- **The any-one stop in an imperative program.** No rule says whether the program's own stop at the first answer stands in for `answers(1)` (H or P) or is control (C). I read it as C (point 1).
- **Execution state for alternatives that only later information resumes.** In an ALGOL program that holds untried alternatives for a later stage, these fall between *alternatives pending* (resumed by "a request for more answers") and *suspended* (resumed by "later information").
- **Rule 20 with ALGOL's `;`.** Taken literally, every statement's trailing `;` takes the class of the next statement, which moves single tokens between classes at every boundary. I applied it literally, and the scripts do it mechanically.

## Summary

**Tokens** (10 texts, 7210 tokens): P 1629, C 155, R 374, H 5052, S 0.
- R is only in P11c and P11d (87 each, rule 19 holding) and in P12 (13 per text, the continuation argument).
- S is 0 for every program, and no mechanism is listed or supplied.

**Expressibility:**
- P11a and P11b are *expressible* in all three configurations.
- P11c, P11d and P12a–d are *expressible with reformulation*. In x1sim the P12 transcription is not demonstrated, because every run errs.

**Outcomes** (96 behaviour stage entries):
- P11: 24 entries, all complete and explicit. Effects are exact for P11a and extra for P11b, P11c and P11d, the same in report, x1 and x1sim.
- P12: 48 entries (report and x1), all complete, explicit and finished. The 24 x1sim entries are none reported, with a run-time error.
- No stage was not reached, no harness fault, no manual action, and no difference between modes.
