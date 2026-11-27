# Calibration

**Development examples, not results.** These programs exist to test whether
the classification rules of `METRICS.md` give consistent classes across
different styles of program, before the rules are frozen. No figure here
is a result of the study, and none may be cited as one.

## What was done

| role | who | what |
|---|---|---|
| implementation author | a Claude agent, reading only the public specification and each system's own manual | wrote P03 (a–f) and P13 (a–f, n = 10² only) in Absys, SWI-Prolog *plain*, Python *core* and ALGOL 60 *report*, and ran them ([`programs/`](programs), with its notes in `programs/README.md`) |
| tokenizer | `tools/tokens.py` | cut every program into numbered tokens, the same for both classifiers ([`tokens/`](tokens)) |
| classifier A | a fresh Claude agent | classed every token ([`classes/A.json`](classes/A.json), notes in `classes/A.notes.md`) |
| classifier B | Codex (codex-cli 0.166.0) | classed every token independently ([`classes/B.json`](classes/B.json), notes in `classes/B.notes.md`) |

Neither classifier wrote a program. Each wrote its classes outside the
repository, where the other could not read them, and they were copied in
after both had finished. Codex's log shows no access to classifier A's
folder. [`classifier-brief.md`](classifier-brief.md) is the brief both
were given. The comparison is `tools/agreement.py`, and its full output is
[`agreement.txt`](agreement.txt).

Every program that could express a query gave that query's valid outcome.

The token files in `tokens/` are those the classifiers classed. Tabs and
newlines inside a token are escaped, which was fixed during the run and
changed no index. `tools/tokens.py` was amended after the classification to
drop Python docstrings (amendment 6), so running it now gives fewer tokens
for the Python programs than `tokens/` holds.

## Agreement

5,189 tokens in 18 programs, each classed by both classifiers.

| system | tokens | agreed | rate |
|---|---|---|---|
| SWI-Prolog | 900 | 900 | 100.0% |
| Absys | 1,776 | 1,760 | 99.1% |
| Python | 898 | 784 | 87.3% |
| ALGOL 60 | 1,615 | 1,317 | 81.5% |

Disagreements by class, as (A, B):

| A → B | tokens | where |
|---|---|---|
| S → H | 209 | the printing helpers of ALGOL 60 (`outseq`, `show`, `showpair`) and Python (`as_list`) |
| R → P | 123 | the case-head tests inside the separately written inverse functions of P03 in ALGOL 60 and Python |
| S → P | 60 | ALGOL 60's `same`, structural equality of encoded sequences |
| P → R | 16 | the case wrapper of Absys's range in P13a–d, whose guard was omitted |
| C → H | 12 | ALGOL 60's later resets of its allocation index |
| P → H | 8 | small query-site tokens |

## Do the disagreements favour a paradigm?

**Yes, in where they fall.** Almost every disagreement is in imperative
code. The logic programs, Prolog's and Absys's, transcribe the problem's
cases nearly literally, and the rules give their tokens one obvious
class. The imperative programs need code the problem does not describe:

- printers for encoded data;
- separate functions for directions a function cannot run backwards;
- structural equality.

The rules were unclear on exactly that code. Left as they were, the
imperative baselines' classes would have depended on which classifier
read them.

It does not follow that the imperative systems were classed unfairly. On
the code both classifiers read the same way, both put the imperative
programs' extra functions in R. The difference is only over the
boundaries listed above.

## Amendments to the rules

Each is made to give a defensible class, not to bring the systems' totals
closer. All are in `METRICS.md` from draft 0.5.

1. **Output adapters are harness.** Code whose only effect is to print or
   collect answers that the program has already computed is H, however long
   it is. That covers walking an encoded sequence to print it, a callback
   that prints an answer, and a stand-in for the harness's fixed calls
   before the harness exists. Code that computes anything the report
   depends on is not H. This settles the 209 tokens, in B's direction.
2. **A separately written function for a direction is R throughout,**
   including its case-head tests. The guard rule (rule 2), which makes a
   head test P, applies to transcriptions of the problem's own cases, not to
   a new function written because the transcription cannot run that way.
   This settles the 123 tokens, in A's direction.
3. **Operations on an encoding are part of it.** Where a systems file
   defines an encoding as P (ALGOL 60's arrays of heads and tails), the
   operations the problem's own relations need on it (construction,
   decomposition, equality of encoded values) are P. A general mechanism
   beyond the problem's relations (a unifier, a search engine) is S. This
   settles the 60 tokens, in B's direction.
4. **Omissions are counted.** A guard, case or conjunct of the problem left
   out of a program has no tokens. Each is counted as one **omission**
   under reformulation, beside moves. The tokens that introduce and close
   the case it was omitted from are R, and the case's unchanged contents
   are classed on their own. This settles the 16 tokens, in B's direction.
5. **A reset that only reuses store is control,** since removing it
   changes how much is held but not what is computed (rule 1). This
   settles the 12 tokens, in A's direction.
6. **Docstrings are comments.** The Python tokenizer now drops a string
   that stands alone as a statement. Classifier A asked how to class
   constructs that change neither meaning nor behaviour; for these, the
   answer is not to count them.

## Findings about the problems and the protocol

The implementation author found these while writing the programs:

- **Absys has no comparisons in any notation.** P13's range, guarded by
  m > n and m ≤ n, cannot be transcribed. The programs reformulate it,
  with m = n + 1 for the first guard and the second omitted. The answer is
  found, but an endless derivation remains, so every run ends at the
  budget. Under the notation rule, P13a–d are *not expressible* in Absys;
  the reformulation is recorded as a named variant.
- **A timeout could erase an answer already found.** The rule is amended:
  answers reported before a timeout are kept and classified. Only the
  execution state is *timeout*.
- **"Native" is the same as prescribed for a system with one mechanism.**
  Absys's native P13e and P13f use the prescribed algorithms. The study
  records them once, and says so.
- **The Absys printer cuts lists after 32 elements,** in every output
  mode, so `observe()` cannot read a P13 answer at n ≥ 33. A full-output
  option would be an instrumentation-only change to the reconstruction,
  under the rules of `PROTOCOL.md`. It is needed before the freeze.
- **P13b–d named only one outcome,** although s is bound too. Their valid
  outcomes now give both.
- **Constants were written into the programs.** For the genericity rule,
  each program must keep its stage constants in one marked place, or read
  them as input, so that the verifier can substitute the hidden variants.

## Round 2, under the amended rules

Both classifiers classed every program again, independently, under the
amended rules:

- a fresh Claude agent, and Codex (codex-cli 0.166.0);
- the same programs, cut by the tokenizer with docstrings dropped
  (5,163 tokens; [`round-2/tokens/`](round-2/tokens));
- the brief [`round-2/classifier-brief.md`](round-2/classifier-brief.md),
  which forbade reading round 1's classes, its agreement report and this
  write-up. Neither saw how round 1's disagreements were settled, only
  the rules as they now stand. Codex's log shows no read of any forbidden
  file.

Round 1's classes are kept, in `classes/` and `agreement.txt`. Round 2's
are in [`round-2/classes/`](round-2/classes) and
[`round-2/agreement.txt`](round-2/agreement.txt).

| system | round 1 | round 2 |
|---|---|---|
| SWI-Prolog | 100.0% | 100.0% |
| Absys | 99.1% | 100.0% |
| Python | 87.3% | 100.0% |
| ALGOL 60 | 81.5% | 99.8% |
| all | 91.8% | 99.9% (5,159 of 5,163) |

The four tokens still disputed are commas, each between a query's
arguments and a printing callback. Rule 20 (a separator takes the class of
the construct after it) now settles them.

**What this does and does not show.** The rules now give the same classes
to two independent classifiers, on every style of program tried. But the
rules were amended on these same programs, so round 2 tests them on the
cases they were fitted to. It shows the amendments are clear. It does not
show the rules generalise. Programs for a staged problem, where
imperative code must hold undecided relations, were not calibrated, and
review 3 named that as the case where disagreement is most likely
(rule 19 was added for it). A held-out check, P02 in Python and ALGOL 60
classified by both, would test that. It was run before the freeze: see
[`held-out/`](held-out). Outcome classes agreed on all 44 stages; token
classes on 88.9%, with the gap in one boundary, clarified afterwards.

**Rules clarified after round 2.** Round 2's classifier A flagged three
ambiguities. They are clarified in draft 0.6, and round 2 was not rerun
under them:

- rule 18: a system's native and prescribed P13 programs, when the same,
  carry the prescribed classes. Round 2 classed Absys's P13e and P13f as
  all P;
- rule 15 against rule 14: inside a direction function, rule 14 wins.
  Round 2 classed ALGOL 60's `same` as P;
- rule 20: separators.
