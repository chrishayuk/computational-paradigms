# Classifier A: notes

Coverage: every token of all 18 programs is covered exactly once (checked
with check.py against calibration/tokens/). Docstrings and layout tokens
(NEWLINE, INDENT, DEDENT) take the class of the construct they sit in. The
DEDENT that closes a function goes with that function.

## Constructs that were hard to class

1. **Printing helpers (ALGOL `outseq`, `show`, `showpair`; Python `as_list`)
   are S, not H.** Rule 13 says code in the harness beyond the fixed harness
   calls is not H, and must be C or S. These helpers walk the encoded
   sequence to print it. That is a mechanism the configuration lacks, so S
   (rule 12). The program comments label them "Harness (H)". Under rule 10
   the fixed print calls inside them (`outstring`, `outinteger`) stay H. The
   procedure headings, the loop label and test, the step to the tail and
   `go to` are S. The calls to these helpers at the query sites are also S.
   This one decision moves about 150 ALGOL tokens and 50 Python tokens
   between H and S. **Rule 13 needs to say whether formatting a
   problem-level value for print() is part of print().** I expect this is
   where most disagreement will come from.
2. **The same, for the P13f element-printing `for` header in ALGOL**: S
   (rules 13 and 10), with the `outinteger` inside it H.
3. **The Prolog `answers/3` stand-in harness**: H as a whole, including its
   cuts, `nb_setval` counters and the `call_with_inference_limit` budget.
   It stands in for the fixed answers(cap) operation, so I did not apply
   rule 13 to its inside. That is inconsistent in spirit with item 1, but
   answers(cap) and the budget are named harness operations. A
   sequence-printer is not.
4. **ALGOL `same` (sequence equality)**: S. It implements structural
   equality, which ALGOL lacks, and is used only by the reformulated
   `prefix`. Two other readings are defensible: P, as part of the
   sequence encoding that the systems file counts as P; or R, as part of
   P03d's reformulation (Python's `b == c` is R only because it sits inside
   `conc_prefix`).
5. **ALGOL p13 `free := 0` between queries**: C by rule 1. The arrays are
   large enough without these resets, so removing them changes nothing the
   program reports, only how much store it reuses. "Store reuse" is not on
   C's list in the class table. Rule 1's list ("efficiency") is what makes
   it C. The first `free := 0` in each program is P, because without it
   the encoding's allocator is uninitialised.
6. **Queries that call a reformulated function** (Python
   `conc_split([1,2])`, ALGOL `splits(cons(1, ...), ...)`): P, as the query
   of the stage. The reformulation is counted once, in the definition. The
   continuation argument passed to collect answers (`show`, `showpair`) is
   S, as in item 1.
7. **Query wrappers.** In Prolog `query(p03a, C, Goal)`, the fact head,
   name and answer template are H. The goal is P (rule 10). In Python and
   ALGOL, `print(...)` / `outstring` are H, and the call inside is P.
8. **Absys range (p13a-d)**: only the test `m = n + 1`, written in place of
   `m > n`, is R (rule 3, changed condition). Case 2 has its guard
   `m <= n` left out. That omission has **no tokens**, so the remaining
   tokens of case 2 are P, as a transcription. For the query
   range(1, 100, s) the solution set is unchanged and only termination
   differs (case 2 runs on past m = 101). So under rule 1 the omission
   would be C-like, but it cannot be counted. **Rule gap: an omitted
   guard or conjunct gets no tokens and no move. The rules should count
   it, perhaps as one move under R the way rule 4 counts moves.**
9. **Absys p13e and p13f (native)**: P throughout, including `m = n + 1`.
   The program's comment says "REFORMULATED", but P13 states that the
   native algorithm "is not reformulation".
10. **SWI `:- use_module(library(lists), [...])`**: P. It is how the
    native tasks' library is invoked, counted as call tokens (rule 12) and
    listed as an external mechanism. With autoloading, removing it changes
    nothing. Without autoloading, removing it causes only an error, which
    rule 1 would make C. It is neither order nor search, so I kept it with
    the construct it serves.
11. **Program frames and declarations in ALGOL** (outer `begin`/`end`,
    inner blocks, `integer n`, the `hd`/`tl` arrays, `cons`): P, as the
    sequence encoding (systems file, Values) and the required frame.
12. **Unused vocabulary** (rev in Absys p03a-d; sum, conc, rev and racc in
    p13a): P, as the problem's vocabulary, even though under rule 1
    removing it changes nothing.
13. **Moves**: Python `rev_inverse` and ALGOL `revinverse` reorder rev
    case 2's conjuncts (conc before rev). That is one move each under
    rule 4, besides the R tokens.

## Rules I think are ambiguous

- **Rule 13 versus the class table's "printing" under H**: see item 1.
- **Rule 1 has no class for constructs that change neither meaning nor
  operational behaviour** (unused definitions, docstrings, imports that
  autoload would supply).
- **There is no way to count an omission** (item 8).
- **Rule 3 does not say whether a query that calls a separately written
  inverse function is P (the query) or R (part of the reformulation).**
