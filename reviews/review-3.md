# Review 3, of draft 0.5

*27 November 2026.* An independent review by a fresh model agent, asked to
separate what blocks the freeze from what a later dated amendment can
fix. It read every file and modified none.

**Verdict: ready to freeze after 7 blocking fixes,** all changes to the
text, none a redesign.

**Checked and correct, by enumeration where possible:**

- P12 at n = 8, 12 and 16: every position and count;
- P15a–d; P16a–d2; P11a–d under the commit rule;
- P13's closed forms; P02's ten triples; P08, P10b and P14;
- every response of review 2, with three exceptions noted below;
- every decision on draft 0.4.

The calibration rules (4, 13–18) are coherent, and do not over-correct
toward either paradigm: two move imperative tokens toward P and H, two
toward R and C, and one moved Absys tokens to R.

## Blocking

| # | finding | response |
|---|---|---|
| 1 | The reformulation rule differs by system: Absys's reformulations are named variants, Python's and ALGOL 60's are the program of record, and rule 3 leaves it to the author | Accepted, with one rule for every system. Expressibility has three values: *expressible*; *expressible with reformulation*, where the reformulation keeps the relation's meaning on every input the problem and its hidden variants use, and is the program of record with R counted; and *not expressible*, where only a reformulation that changes meaning can be written, and is reported as a named variant. Both are always reported. A calibration figure is named for systems without P13b |
| 2 | P12's budget makes n = 12 and 16 unreachable for some systems | Accepted. P12 takes P13's limits |
| 3 | The texts contradict each other on empty results, on timeouts, and on bindings read while running (P09d1) | Accepted, all three |
| 4 | A program that echoes its input is a complete, reduced residual | Accepted. A residual is reported only if it is state the program holds and acts on later. Echoing the posed text is not a report. A flag records a residual identical to the posed information |
| 5 | P16 lets the implementer split computations to make localisation trivial, and does not say how to pose to shared computations | Accepted. P16c and d are one computation, and splitting them is reformulation. P16b's later stages go to the shared instance, are classified jointly, and have one budget. P16a is posed in all three orders at each n |
| 6 | No rule for imperative code that holds undecided relations | Accepted. Code general over relations (reusable across problems) is S, in *extended*. Code written for a problem's own relations is R, in *core* |
| 7 | No one is assigned to classify outcomes | Accepted. Classifiers A and B also classify outcomes independently, from the outputs and the valid outcomes |

## Non-blocking

| # | finding | response |
|---|---|---|
| 8 | "fails a variant" undefined | Accepted. It fails if its semantic or effects class differs from that on the original constants |
| 9 | Sealing: brute force, later waves, owner decryption, harness author | Accepted. A 128-bit nonce; a separate sealed set per wave; the owner holds but does not decrypt; a harness-author role |
| 10 | P11 for a system that cannot select at commit | Accepted |
| 11 | S mechanisms cannot be listed at the freeze | Accepted. Listed at phase 4, before any run |
| 12 | Equivalence "by hand" impossible at P16's sizes | Accepted. A published checking script is allowed |
| 13 | Rule 14 against rule 15 | Accepted. Rule 14 wins inside a direction function |
| 14 | Size of compound expressions | Accepted. Measured on the primitive decomposition |
| 15 | P15b's cap | Accepted. `answers(1)` |
| — | Cosmetic items | Accepted, all |
