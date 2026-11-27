# Classifier A notes, held-out P02

Totals: python/p02.py P 357, C 28, R 522, S 0, H 666 (1573 tokens).
algol-60/p02.alg P 234, C 30, R 563, S 0, H 1046 (1873 tokens).
Both programs are core / report. No S: the holding code is written for R1 to R3 only (rule 19, first bullet).

## Hard constructs

1. **Multi-direction relation functions (r1/r2/r3, rel1/rel2/rel3).** I classed the relation tests and the
   directions the runs reach as P (rules 3 and 8). I classed the directions that are never reached as R
   (rule 3, "a direction the queries do not use"): R1 with v known before u, R2 with w and u known, R2 with
   w and v known, and R2 with w = 0. w is only ever bound by R2 from u and v, and v only from u, so these
   branches are dead for every order and for every constant variant. The problem states each relation
   "with any place unknown", so another classifier could reasonably class every direction P, as a
   transcription of a primitive relation. **Disagreement is likely here.** R2's u-known, u = 0 branch is
   reached only on a variant with R3 giving u = 0. I classed it P.
2. **The "waits" verdict branches.** I classed these R under rule 19, as part of the holding mechanism, and
   left the rest of each relation function P. That splits one function between two classes, and rule 19
   does not say where the "decides them" code ends and the relation itself begins.
3. **Known flags (ku/kv/kw) and Python's `known` dict.** I classed them R (rule 19). The integer
   variables u, v, w are P (vocabulary). The direction dispatch on the flags inside the relation
   procedures is P (rule 3). This is arguably inconsistent.
4. **Enumeration in the R1∧R2 reformulation.** The divisor loops and the (d, −d) loops are C under rule 6
   and the C row ("generators of values the problem does not state"). The rest of that function is R
   (rule 3, changed algorithm). Someone could class the whole function R as one changed algorithm.
5. **Printing interleaved with computing (ALGOL solutions12).** The output calls are H. The arguments
   `c - s` and `c ÷ s - 1` compute v and w for the report, so I classed them R (rules 10 and 13). The
   count n is R and its print is H. Python separates computing from printing, so the split is clean there.
6. **The report's dispatch to the reformulation.** In Python this is `sorted(held) == [R1, R2]` and the
   call. In ALGOL it is the has1, has2 and c bookkeeping and `else if nalive = 2 ∧ … then solutions12(c)`.
   I classed both R, not H, because the report's content depends on them (rule 13). nalive alone is
   H, since it also drives "held: none".
7. **Stage data.** Python's stage lists in the `run(...)` calls (and the six-order tuple) are P, as
   information of the stages. The surrounding calls and labels are H. ALGOL keeps its stage data in
   p02.in, so its reading code (`ininteger`) is H as a pose stand-in, but adding to the held store and
   calling `resume` are R. The result is that ALGOL has no P tokens for stage information. Rule 15 and
   the README's "Stages are read from input as integers in the same encoding" could support classing
   the decode (`if code = 1 then ininteger(ca)…`) as P.
8. **Observation counters** (`examined`, trace, and their resets) are H, from METRICS "counters that are
   harness code (H)". I applied rule 16 (reset is C) only to store resets, not to these.
9. **ALGOL separators.** I applied rule 20 literally: a `;` between constructs of different classes moves
   to the following construct. In an else-if chain, `else` goes with the case it introduces, as Python's
   DEDENT/elif does. Read strictly, rule 10 would give `else` to the enclosing conditional, and with it
   every nested `else if` header. Python NEWLINE is a statement terminator, so it stays with its own
   statement. INDENT/DEDENT go with the following construct (rule 20).
10. **The outer `begin` … `end`** of the ALGOL program has no obvious class. I gave it P (rule 10).
11. **Python `break` on failure** in resume does not change any result (only efficiency), so rule 1
    reads it as C. I left it R under rule 19, which covers the whole holding loop.

## Hard outcomes

- **Stage with R1 and R2 held (P02a s2, P02b R1,R2,R3 s2, R2,R1,R3 s2).** The program prints the ten
  triples explicitly, but computes them with a report-only reformulation. The state it holds and acts on
  is R1 and R2 as posed. I classed it complete / explicit. On "A residual counts as reported only if it
  is state … held and acts on", one could instead class the held state, complete / residual / reducible,
  identical to the posed information, and treat the explicit list as derived output. The spec does not
  say which of the two is "the report" when a program prints both. **Likely disputed.**
- **u = 2 with w·2 = v held (R2,R3,R1 s2; R3,R2,R1 s2).** I classed it residual / reduced, because ·
  cannot appear in a solved-form term (§2). It is not identical to the posed information, since u has
  been substituted.
- **Solved-form and explicit stages.** These have no simplification. I wrote "n/a (not residual)" in the
  simplification field.
- Every run of both programs is complete at every stage. All six P02b orders end at u = 2, v = 14,
  w = 7. The ALGOL and Python outputs agree line for line in content.

## Rules I think are ambiguous

- **Rule 19 against rules 3 and 8:** where the relation's own decision code ends and the holding
  mechanism begins.
- **Rule 3, "direction the queries do not use":** whether this is judged on the runs actually made,
  including the variants, or on the relation as stated "with any place unknown".
- **Rule 20 against rule 10** for `else` in chained conditionals.
- **SPECIFICATION §1/§2:** which output is "the report" when a program prints both an explicit list and
  a held residual.
