# Classifier 1C-A: absys, P09, P10, P11 — notes

Output: `absys.json` beside this file. Checking scripts (read-only, run only on records and token files):
`summarise.py`, `biglist.py`, `compare_modes.py` (its output `compare_modes.out`) and `build.py`, which
writes `absys.json` and checks that every token of every text is covered exactly once. Also
`records_index.json` and `token_totals.json`. No program and no part of the system was run.

## Texts

There are 16 texts (TEXTS-1C-P09-P11.tsv). Each one is byte-identical in absys, absys-depth-first and
absys-wake-back. This holds for both the program files and the token files, and `build.py` checks it.
Each text is classed once, under its absys path. No token's class differs between configurations,
because no configuration has an S mechanism.

## Constructs that were hard to class

1. **The constants block** (`NAME = VALUE` lines). These are tokens, but the harness reads them and never
   gives them to the system. I classed them P, as the stage's information (README 3.9: the block is
   classed by the METRICS rules). There is one exception: `gelo = 1` in P11a.ne and P11b.ne is R. It is a
   constant the author derived for the meaning-changing reformulation, and the problem does not state it.
2. **emit: H or P.** problems/11, Rules, says "emit and commit are problem tokens". harnesses/absys/README
   3.12 classes `tout ( "emit" , )` as H. I followed the frozen problem file, so emit is P and every text
   has 0 H. **This is the rule I think is in conflict.** If the README is followed instead, there are 5 H
   tokens per P11 text, 20 in all, moved from P to H.
3. **Applications of reformulated comparisons.** In P09c these are `gt(g, gmax)` and `le(g, gmax)`; in
   P10d it is `gt(x, gtk)`. I classed the definitions (gt, le, pos, nonneg) R. I classed each application
   P, reading rule 9 by analogy: the application stands in the problem's place for its comparison, and
   the relation is equivalent over the integers. Classing the calls R would move 12 tokens in P09c and 6
   in P10d from P to R. This is a likely point of dispute.
4. **P10's begin ... end.** In each replacing stage, begin/end join the history-list cell (R) to the new
   value (P). I classed them R as part of the reformulated construct (rule 10). Classing them P would move
   2 tokens per stage.
5. **P10b's `dbl(b, d)`.** I classed it R, because it applies the reformulated relation over encoded
   lists. Only `e = dk * r` inside it is P. `key p` is C.
6. **The or of the P09 variants.** I classed `{`, `or` and `}` R (3 tokens). Rule 20 (separators) does not
   apply, because or is the connective of the reformulated construct.
7. **The commit stages of P11c and P11d.** They have no tokens. I recorded each as one omission under rule
   4, and I did not class the commit stage as R or as a change of expressibility.

## Outcomes that were hard to class

- **P09a and P09b, the or variants.** The harness puts every derivation under both computations, because
  the SPAWN sections are empty. I judged each computation on its own disjunct's derivation. In P09a this
  makes A *none reported* rather than *unsound*. B's hibernating derivation (x does not occur) is not
  read as an answer of A. In P09b this makes A *complete*: its derivation failed and disappeared. Another
  reader could class A by the harness's per-computation list.
- **The mismatched variants.** The AB.or variant was run on P09a.BA and the BA.or variant on P09a.AB. The
  or is given before the empty SPAWN sections, so the instance's spawn order has no effect. I classed
  them as the variant's own order.
- **P09b primary, B.** A's failure leaves no derivation, so the system says "no derivation survives" for
  y. That reports there are no solutions when y = 3 is valid, so I classed it *unsound*.
- **P09c in absys and wake-back.** There is 1 hibernating derivation with the valid answer, and 15 that
  are still elaborating. Those 15 hold partial bindings of s, conditional on to-do lists that cannot be
  satisfied (pos of negative numbers). I classed the result *complete / residual / reducible*. An
  alternative is *explicit*, treating the 15 as unfinished work. A third view is *unsound*, if a held
  conditional binding such as s = [] is read as reported.
- **P10 representation.** b = [10&bt1] is a solved form by the letter, since it has an unknown tail. I
  classed it *explicit* through the reformulated encoding, where the value is the last bound element
  (SPECIFICATION 2: "a form derived by reformulation keeps its R tokens").
- **P10d (records marked INVALID).** All three configurations, all modes; every entry has
  `harness_fault: true`.
  - Stage 2 is *timeout*, final, with nothing reported.
  - Stage 3 is *not reached*. Both attempts were killed while replaying stage 2, and their stdout ends
    after stage 1's state.
  - The separate replay run shows stage 2 spends its full 10⁶ budget. So this is the time limit on a slow
    stage, not proven nontermination.
- **P11d stage 3.** No v was selected, so I classed it against x in {2,3}, which makes it *complete*. If
  the first printed answer at the commit (x = 1) were read as v, it would be *unsound*. I recorded this
  as an alternative reading.
- **P11a and P11b.** The test is written before emit in P11a, yet it does not prevent the effect: tout
  fired in derivation x = 1 before not(x = 1) failed it. Both are *extra*.

## Rules I think ambiguous

- emit H versus P (item 2 above).
- SPECIFICATION's "a binding held is reported" rule, applied to derivations that are still elaborating
  and carry unsatisfiable to-do lists (P09c).
- P11's "classified against the outcomes before the commit" does not say how to judge stages *after* a
  commit that never happened (P11d stage 3).
- The brief asks for one classification per stage. I added `computation` (P09a, P09b) and `reading`
  (P09d) fields, because PROTOCOL gives each spawned computation its own classification.

## Files read outside the brief's list

None. A directory listing of `results/absys/` showed the names `classes`, `classes-1B` and `RERUN-M2.md`.
I did not open them. My checking scripts globbed only `results/absys/<config>/P09|P10|P11/raw/`. Output
from large tool results was saved under the session's own tool-results folder and read from there; that
is my own output, not a repository file.

## Summary

**Tokens** (16 distinct texts, 1143 tokens): P 864, R 277, C 2, S 0, H 0.
Primary texts only (11, 782 tokens): P 532, R 248, C 2.

| text | P | R | C |
|---|---|---|---|
| P09a, P09b, P09d, P09e | all | 0 | 0 |
| P09c | 91 | 71 | 0 |
| P10a | 20 | 27 | 0 |
| P10b | 28 | 72 | 2 |
| P10c | 28 | 36 | 0 |
| P10d | 41 | 42 | 0 |
| P11c, P11d | 52 each | 0 | 0 |
| P09 or variants | — | 3 each | — |
| P11 .ne variants | 43 each | 10 each | 0 |

**Outcomes** (126 entries over 57 behaviour runs):
- absys and absys-wake-back: complete 30, none reported 10, unsound 1, not reached 1 each.
- absys-depth-first: complete 27, none reported 13, unsound 1, not reached 1.

Depth-first differs on:
- P09c: final timeout instead of complete.
- P09a with the AB.or variant: B is never elaborated.

The P11 effects are *extra* in every instance and configuration. L = ⟨1,2,3⟩, and every entry was
performed before commitment.

**Cost and storage runs** differ from behaviour on no stage. The only exception is attempt history in
P09d, where behaviour needed the safety rerun.

**Expressibility**, the same in every configuration:
- expressible: P09d, P09e, P11c, P11d
- expressible with reformulation: P09a, P09b, P09c, P10a–d
- not expressible: P11a, P11b

**Other sections:** S mechanisms: none. Late definition: not applicable, since there is no P08 in this
batch.
