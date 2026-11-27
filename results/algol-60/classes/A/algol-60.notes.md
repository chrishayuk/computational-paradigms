# Classifier A: algol-60, batch 1A (P01–P03). Notes

Classifier A, a Claude agent (Claude Opus 5.5). Clone at commit 628a324. I wrote only in this folder.

## How the classes were made

- `spec.py` holds the classes as markers: a line and a token (by its position or its text). `spans.py` turns them into spans over the frozen tokens, without re-tokenizing. `build.py` resolves them for every text in `TEXTS.tsv`. `make_output.py` writes `algol-60.json`. `view/` shows every text line by line, each token with its class, for review.
- Rule 20 is applied mechanically. A `;` or `,` that ends a span is moved to the span that follows it.
- Each x1 text has the same lines as its report text, and the same markers are resolved in it. Within each line, the sequence of classes is identical in report and x1 (checked line by line). Only dialect tokens differ: `n := read` against `ininteger(0, n)`, `≠` against `not (… = …)`, and `NLCR` statements against `"\n"`.
- x1sim's texts are byte-identical to x1's. No token would take a different class there, because no S mechanism exists in either (S-mechanisms.md). So they are classed once, under `x1/`. The difference that is real belongs to external mechanisms, not to classes. In x1 and x1sim, `read`, `print`, `PRINTTEXT` and `NLCR` are the X1 system's own procedures. In report, `ininteger`, `outinteger` and `outstring` are IFIP's, an external mechanism. That holds in x1 too, if the classifiers read A14 that way.
- The six P02b texts of a configuration are one text, classed once.
- Checks:
  - every token of every text is covered exactly once;
  - every outcome's execution state equals the record's;
  - `check_residuals.py` checks residual equivalence;
  - `modes.py` compares cost and storage runs against behaviour runs.

## Constructs that were hard to class, and the choice made

1. **Propagation loop: R, not C.** `propagate` examines held relations in order until a pass changes nothing, and its `pass`/`changed` variables go with it. It decides when relations are examined, which reads like "explicit scheduling" (class C). I classed it R by rule 19, the more specific rule: code written for the problem's own relations that holds them and decides them later. If it were read as C, about 38 tokens per P02 text and 60 in P01a would move from R to C (plus the pass and changed declarations). No token is C anywhere in this batch.
2. **The evaluators, split by rule 19.** Within an evaluator:
   - The heading (formal parameters and their specifications), the known-flag tests, `r := false` (release), `changed := true`, and the `begin`/`end` of the dispatch branches are R.
   - Tests of fully known relations, the computation of a place, and assigning a value to the unknown (`bv := av`, `tv := c`) are P.
   - Setting the known flag (`bk := true`) is R.
   - In R2's evaluator, the zero and divisibility cases (`if uv = 0 … else if vv ÷ uv × uv = vv …`) are P. They are the relation's meaning over the integers in that direction, not holding.
3. **`r1 := true` at the stage dispatch is P.** It records that the stage's relation now holds, which is the stage's information. The declaration of r1, and its other uses, are R, as the held flag. The README's X01 example does not class its analogue `haslo := true`. A reading that puts these in R is defensible: about 3 tokens per relation.
4. **`inconsistent`** (declaration and initialisation) is P. It is the verdict of tests of fully known relations, and it decides whether an answer exists. The `if not inconsistent then` that guards the answer printing is H. It only chooses whether to print a verdict already computed (rule 13), and it does not decide which computation's result is reported.
5. **Mixed multiple assignments are split by left part:**
   - `xk := … := r3 :=` is R, and `inconsistent := false` is P;
   - `top :=` is P (the allocator), and `conc1 := conc2 := 0` is H (counter initialisation).

   The final value goes with the last left part.
6. **`held`** counts held relations and is used only in the observe block and its printing, so it is H. **`answers`** in P03b, c, d and f is H for the same reason: it is incremented, and used only to print "no solution" in observe.
7. **P02b's `order` array** is P. The harness README 2.7 says an order as the program uses it is not H, and the presentation order is part of the problem. But `r := order[k]` and the tests `if r = 1 …` are exactly the stage dispatch, which is H (2.7.2), as `if k = 1 …` is in P02a. So `r` and its declaration are H. This is a tension in README 2.7: in this program, the order is used only by the dispatch.
8. **The outer program `begin`/`end` and inner blocks** are P (rule 10: the block that holds the transcription). This includes P01b's `cells := 1000` capacity, and the array bounds of hd/tl in every program (encoding, rule 15). In P03f the bounds are sized for lastsplit's cells, an R function, and I still classed them P as part of the encoding's declaration.
9. **P03b `integer array hd, tl, path[1:lc + 1]`.** One declaration holds encoding arrays and the R extra argument. hd and tl are P, `, path` is R, and the shared bound pair is P.
10. **Calls of a separately written direction function are R:** `split(c0, 0)`, `strip(a0, c0)`, `prefix(c0, 0)` and `unrev(b0, 0)` (rule 14, and rule 5 for the extra argument `0`). The query itself has no other tokens there. P03c's call has no extra argument and is still R, since the goal is computed in a chosen direction. Reading the known sequences (readseq) stays P.
11. **`same` in P03d** is R (rule 15's last sentence: used only inside prefix). In P01b and P01c it is P, used in tests of fully known relations. `cons` stays P wherever readseq also uses it, including P03f, where lastsplit also uses it.
12. **Printing inside the R search functions is H** (rule 13; README 2.7.3). This covers `[answer]` with printpath and printseq inside split, strip, prefix and unrev. The counter increments inside them are H too (2.7.4).

## Outcomes that were hard to class

- **P01a stages 1–2: residual / reduced, not solved form.** The report "x held, y held, z free, where x = y" denotes the same thing as the solved form "x identified with y". But the program holds x = y as an undecided relation (r1, `[suspended held-relations 1]`) and would decide it when a place became known. I classed it residual, reduced. The size rule ("fewer relations left to decide") could instead make it *reducible*, since a solved form identifying x with y has no relation left. The rule does not say whether an identity held as an equation counts as a relation left to decide. **Likely disputed.**
- **P01b stage 1: residual / reducible.** `conc(<1,2>, s, t)` is held as posed. The solved form t = <1,2> ++ s, with no relation left, exists and was not reached.
- **P01c** is classed under each reading, as two entries for stage 1, each with a `reading` field:
  - **finite:** complete, residual, *inconsistency undetected*. The held equation denotes the empty set.
  - **rational:** complete, residual, reduced. It is not *cyclic*, because the program makes no cyclic value.

  Two doubts:
  - SPECIFICATION says a residual counts as reported only if it is state the program "holds and acts on at a later stage", and P01c has one stage. I counted it as reported, because the program holds r1 and its evaluator would act on it, and observe reads it. A stricter reading would give *none reported*.
  - Under the rational reading, the program could never accept the solution: its sequences are finite. The equation still denotes the solution, so I said complete, but *undetermined* is a possible view.
- **P02 stages where the held relations are exactly the posed ones** are flagged identical-to-posed true. P02a stage 2 (and P02b R1R2R3, R2R1R3 stage 2) is residual / *reducible*: the ten explicit triples are smaller (no relation left), as in P07b. With R2 and R3 (P02b R2R3R1 and R3R2R1, stage 2) the residual is u = 2 plus w . 2 = v. That is not identical to the posed information (R3 was decided, u substituted in the printing), and it is reduced (v = 2w is the same size).
- **Solved form** for R3 alone and for R1 with R3: u = 2 (v = 14), with the rest free. The state is *finished*, since nothing is held.
- **Domains.** The programs impose no finite domain (AMENDMENTS 3.4 does not apply). Unknowns are machine integers. P01b's cell arrays have a fixed capacity of 1000 cells, and P01c and P03 size theirs from the stage's lengths. These are capacity limits, not domains, and no run came near them.
- **No stage was not reached.** No run hit a budget, an error before `[end]` or the safety limit, and no record has a harness fault or a manual action. The interpreter's "input is exhausted" error after each `[end]` is the harness closing the input (confound 3), not a stage error.

## Mode differences

None. All 68 cost and storage records (report and x1; x1sim is behaviour only) match their behaviour record, stage by stage, on: answers, ended_by, execution state, suspended items, alternatives, problem operations and the observe text (`modes.py`). So `mode_differences` is empty.

## Rules I think ambiguous

- **Rule 19 against class C** ("explicit scheduling") for the propagation loop (item 1 above).
- **Representation of a held identity x = y:** residual or solved form, reduced or reducible (P01a above).
- **"Acts on at a later stage" for one-stage problems** (P01c).
- **Harness README 2.7:** an order "as the program uses it" is not H, yet its only use here is the stage dispatch, which is H.
- **Rule 20 applied literally** moves the `;` that ends a declaration onto the next statement, even across classes, for example from `integer c;` onto an H counter. That is cosmetic, but it shifts tokens between classes.

## Files read outside the list

- None of the repository's forbidden paths.
- I read the harness's saved output of my own commands, in the session's tool-results folder.
- A copy of the user's auto-memory index (under `~/.claude/projects/…/memory/MEMORY.md`) was put into my context by the environment at the start. I did not open it, and nothing from it was used.
- From the allowed list, I did not open `harnesses/README.md`, `stages.json` or `record.schema.json` beyond what the records themselves contain.

## Summary

**Tokens.** 24 distinct texts. No C and no S tokens in any text.

| texts | P | R | H | total |
|---|---|---|---|---|
| report, 12 texts (P02b once) | 2,653 | 1,524 | 5,678 | 9,855 |
| x1, 12 texts, also x1sim's | 2,512 | 1,509 | 4,928 | 8,949 |

- R comes from two places:
  - the holding code of P01 and P02 (rule 19): 26 to 234 tokens per text;
  - the separately written directions of P03b, c, d and f (rule 14): 63 to 188.
- P03a and P03e have no R.
- H dominates in every text, through the observe and answer printing.

**Outcomes.** 51 behaviour records (17 instances × 3 configurations), 105 stage entries, with P01c entered under both readings.

- Every stage is *complete*, and all three configurations agree on every stage.
- Per configuration (35 entries):
  - 16 explicit / finished;
  - 4 solved form / finished;
  - 15 residual / suspended:
    - 10 reduced: 8 identical to the posed information, 2 transformed (P02b R2R3R1 and R3R2R1, stage 2);
    - 4 reducible: P01b stage 1, and the R1, R2 stage of P02a, P02b R1R2R3 and P02b R2R1R3;
    - 1 inconsistency undetected (P01c, finite reading).
- No alternatives were held, no conclusion was withdrawn, and no manual action was needed.

**Mode differences.** None.

**Expressibility**, the same in all three configurations:
- P03a and P03e are *expressible*.
- Every other sub-problem is *expressible with reformulation*:
  - P01a–c and P02a–c by rule-19 holding code;
  - P03b, c, d and f by separately written directions, with extra arguments, and in P03f one move.
- Nothing is *not expressible*.
