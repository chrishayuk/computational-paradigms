# Classifier A, round 2: notes

Conventions I used everywhere:
- Python layout tokens: an INDENT goes with the block it opens. A DEDENT goes with the construct it closes, even when it sits at the start of the next construct's line.
- ALGOL block `begin`/`end` and statement separators go with the construct they open, close or end.
- Query calls nested inside print statements (Python `print(...)`, ALGOL `outseq(...)`) and inside Prolog `query/3` facts are split by rule 10. The query goal is P. The print call, the label string, the answer template and the printing callback argument are H.

## Hard constructs

1. **Queries posed through a reformulated function** (Python `conc_split([1, 2])`, ALGOL `splits(cons(1, cons(2, 0)), showpair)`, and the others). I classed the call as P because it is the problem's query and carries its constants. The function it names is R (rule 14). You could argue the call is R too, since the query is not written as conc(a, b, ⟨1,2⟩). No rule says which. Rule 14 covers the function, not its call site.

2. **ALGOL `same` (p03.alg)**: equality on encoded sequences. Only `prefix`, an R procedure, uses it. I classed it P by rule 15, which names equality among the encoding operations the problem's relations need. Conc in the P03d direction does need b = c. The other reading is R, as a helper written only for a separately written direction (rule 14). Rule 15 does not say whether "need" is judged against the problem's relations or against the program's own procedures.

3. **ALGOL `free := 0`**: rule 16 classes a reset for store reuse as C. In p13.alg I classed the first `free := 0` P (rule 15), because it initialises the encoding and `free` is otherwise undefined. I classed the three later ones C (rule 16). In p03.alg the single `free := 0` is also P. Rule 16 does not separate initialisation from reset.

4. **Absys range (p13a–d)**:
   - Case 1's `m = n + 1` replaces `m > n`. I classed it R as a changed condition (rule 3, "a changed algorithm").
   - Case 2's missing `m ≤ n` is an omission under rule 4. Its `begin` and `end` are R, and its contents are P by rule 10.
   - I left `or` and the braces P, as the stated disjunction (rule 6). Rule 4 says "tokens that introduce and close the case". In Absys, `or` could also count as introducing the case, and I read it as the connective.

5. **Absys p13e and p13f (native)** contain the same range text as p13a–d. Rule 18 says native tokens are P. Rule 18 also says that where a system has only one way to compute a task, the native and prescribed programs are "the same, recorded once". p13e is exactly p13b's range and sum, so the two rules point different ways for its range. I followed the first sentence and classed everything in p13e and p13f P. Classing p13e's range as R, the same as p13b, would also be defensible. Rule 18 should say which applies when the native program inherits a forced reformulation.

6. **Python range case 2 (p13.py)** has no explicit `m <= n`. The else fall-through after `if m > n: return` expresses it, so I counted it as case dispatch (rules 2 and 3) and P, not an omission. The Absys case is different: its disjunction does not exclude case 1, so there the guard really is missing.

7. **SWI `:- use_module(library(lists), [...])` (p13.pl)**: an import for the native tasks. It is not control, not harness and not S, since it is not written for the experiment. I classed it P under rules 12 and 18, as part of the native program's use of a listed external mechanism. No rule covers import declarations.

8. **Rule 9 and rule 18 overlap**: Python `sum(s)` and the `s[::-1]` slice in native P13e/P13f, and SWI `sum_list`, `reverse` and `numlist`, are P by rule 18. They should still be listed under rule 9 as built-ins, and under external mechanisms for SWI.

9. **Python p03 slicing (`a[1:]`)**: the representation rule about slicing copies applies only to P13, so p03.py's slicing transcription stays P.

## Rules I think are ambiguous

- Rule 14 versus the query call site (item 1).
- Rule 15's "need" (item 2).
- Rule 16 does not separate initialisation from reset (item 3).
- Rule 4 does not say which tokens "introduce" a case in a language with an infix disjunction (item 4).
- Rule 18's two sentences conflict for inherited reformulations (item 5).
- Import declarations are not covered by any rule (item 7).
