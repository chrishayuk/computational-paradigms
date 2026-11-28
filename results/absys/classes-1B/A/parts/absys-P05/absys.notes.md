# Classifier A: absys, batch 1B, P05: notes

Clone `/Users/christopherhay/cp-roles/classifier-1B-A3` (commit 1f291be), read only. The output is `absys.json` here. My checking scripts are here too:

- `p05b_denote.py` checks residual equivalence for P05b. Its output is in `p05b_denote.out` and `p05b_denote_m2.out`.
- `check.py` checks that every token is covered exactly once.
- `build.py` writes the JSON.
- `summ.py`, `compact.py`, `derivs.py` and `uninst.py` read the records.

## Tokens

- There are three texts. Each is shared by absys, absys-depth-first and absys-wake-back. The token files are byte-identical across the three, and no class differs between configurations, since there is no S, C or H. So each text is classed once, under `absys/`.
- **Stage applications of reformulated relations are P.** These are `gt(x, gtk)` and `ne(x, nek)`. The construct is the stage's information x > 1 or x ≠ 2, and removing it changes the solutions (rule 1). Only the definitions of gt, pos and ne are R (rules 3 and 14). Another reading would class the call R too, because it names a relation the problem does not give. That is a possible point of dispute: 6 tokens in each of P05a and P05b.
- **The constants block is P.** These lines are `pk1 = 1` … `nek = 2`. They are the facts of pick and the stages' constants, which the harness substitutes. The harness README (3.9) never gives the block to the system, but the tokenizer counts it. I classed it as problem information rather than H: it is a table, and no harness call. This is another possible point of dispute (15, 12 and 15 tokens).
- **pick as `{p = pk1 or p = pk2 or p = pk3}` is P.** Rule 6: facts the problem states, in its order.
- **ne's `or` is R.** It is the program's disjunction (x ≠ k as x > k or k > x), not the problem's, so rule 6 does not apply.
- **No S, C or H.** This agrees with `harnesses/absys/S-mechanisms.md` (none) and with README 3.12 (no H without emit).

## Outcomes: hard cases

1. **P05b, both stages: complete or undetermined?**
   - The budget ran out with hundreds of derivations still elaborating, holding suspended chains and pending "to do" items.
   - I took the report to be the union of all derivations, since held bindings are reported at the budget (SPECIFICATION, Outcomes 1). I computed each derivation's denotation with `p05b_denote.py`.
   - At stage 1 the union is exactly {x > 1}: explicit values, plus one open tail `x = N + e, pos(e)`, which is x ≥ N+1 because pos's least relation is the positive integers. There is no gap.
   - At stage 2 the union is {2, 3}. Every other derivation conjoins pick(x) with a value outside {1, 2, 3}, or with x ≥ 1821 (1411 in depth-first), which is empty.
   - So I classed both stages *complete / residual / reducible*.
   - Limits of the check: the "to do" lists are printed truncated ("… N more"). The script relies on bindings, suspended chains and visible items. For stage 2 it relies on the fact that pick(x) is conjoined into every derivation, not on seeing it printed.
   - Another classifier could say *undetermined*, or could class only the hibernating derivations as an *explicit* form (stage 2's {2, 3} alone is valid; the two-forms clause of Representation).
2. **P05b stage 2, absys and wake-back.** The incremental attempt was killed at 60 s. The rerun reposed stage 1 and ended at the budget. I classed the stage from the rerun: its execution state is *budget*, not *timeout*, because the rerun did not time out.
3. **P05a stage 3 is *not reached* in all three configurations**, although the record says timeout. Both attempts reposed stages 1–2, and the replay printed only stage 1's result: ne(x, 2) was never given. This follows the brief and AMENDMENTS 3.2. All P05a behaviour records are `.INVALID.json`, so `harness_fault: true` is set on them.
4. **P05a stage 2 is a final *timeout*, with nothing reported.** The separate restart-cost run shows that this stage's assertion would go on to the 10⁶ budget (1000016 steps). Without a time limit, then, it would be *budget*, not *finished*. The cause is the R definition pos, whose recursive case stays open in every derivation, even for a known argument.
5. **Expressibility of P05a and P05b is *expressible with reformulation*.** The reformulation keeps the meaning over the integers but never terminates. I read non-termination as an execution outcome, not as a change of meaning (unlike the systems file's range example, which dropped a guard).
   - Caveat: ne is equivalent to ≠ only on integers. A hidden variant whose stage-3 constant is not an integer would make ne fail where ≠ holds.
6. **Empty outcomes (P05c stages 2 and 3) are *explicit*** (the empty set, reported as "No derivation survives"), with simplification null. The schema has no class for an empty report, so another classifier might write null.

## Mode differences

- **Original P05b cost and storage records** (build 5450449, peak after every step), all three configurations:
  - Stage 1 is *timeout*, nothing reported, against *complete / budget* in the behaviour run.
  - Stage 2 is *not reached*: its process must first redo stage 1, which alone exceeded 600 s.
  - This is a limit of the measurement (PROTOCOL, Modes of running).
- **m2 reruns:** they agree with the behaviour runs. They have the same derivation and suspended counts, and `p05b_denote.py` gives the same unions. So they are not listed.
- **P05a and P05c cost and storage:** no differences. P05a's cost and storage records are INVALID, except absys's storage record. P05c's stage 3 takes 0 steps.

## Rules I find ambiguous

- **Whether "the report" of a budget-stopped Absys stage is every printed derivation** (my reading), or only the hibernating ones.
- **How to class the constants block** under METRICS: it is program text that the system never receives.
- **Whether a reformulation that keeps meaning but cannot terminate on any input** is still "expressible with reformulation."

## Log anomaly

`results/absys/batch-log.tsv` has interleaved, garbled lines, for example line 208, where the P04d and P05a entries run together. It has **no entries for the absys configuration's P05 runs**, although records exist for them in `results/absys/absys/P05/raw/`. I classed those records.

## Files read outside the brief's list

- `results/absys/RERUN-M2.md`: its first 5 lines, read by accident while listing the m2 log. I stopped there. It is not on the allowed list, and nothing in my classes depends on it.
- A directory listing of `/Users/christopherhay/cp-roles/classes-1B-A/`, taken when I checked that my output folder existed. It showed only the names of other batches' folders. I opened none of them and saw no classes.
- Nothing else. No `calibration/`, `reviews/`, `variants/` (top level), `transcripts/`, earlier classes, author's notes, web or other systems.

## Summary

**Tokens**, by text (each shared by all three configurations):

| text | P | R | C | S | H | total |
|---|---|---|---|---|---|---|
| P05a | 50 | 61 | 0 | 0 | 0 | 111 |
| P05b | 41 | 38 | 0 | 0 | 0 | 79 |
| P05c | 44 | 0 | 0 | 0 | 0 | 44 |
| **all** | **135** | **99** | **0** | **0** | **0** | **234** |

**Outcomes** (24 stage entries; the three configurations agree on every class):

| instance | stage 1 | stage 2 | stage 3 |
|---|---|---|---|
| P05a | complete / explicit / finished | none reported / timeout | not reached |
| P05b | complete / residual / reducible / budget + suspended | complete / residual / reducible / budget + suspended | — |
| P05c | complete / explicit / finished | complete, empty reported as empty / finished | complete, empty reported as empty / finished |

- P05a entries are harness faults (INVALID records).
- Depth-first holds far fewer derivations than the other two configurations: 999 and 4, against 1288 and 731.

**Expressibility:** P05a and P05b are *expressible with reformulation*; P05c is *expressible*.

**Mode differences:** P05b's original cost and storage runs only; there are 12 entries.

**S mechanisms:** none.

**Late definition:** not applicable; there is no P08 in this batch.
