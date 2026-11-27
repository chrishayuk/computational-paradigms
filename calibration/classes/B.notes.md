# Classifier B notes

I used the supplied token indices without re-tokenizing. The specification,
metrics, protocol, three requested problem files, four system descriptions,
program sources and token TSVs were the evidence. I did not read the author’s
calibration README, other classifier output, calibration/classes/, or reviews/.
Source comments calling something reformulation or harness were not decisive.

- **Inverse definitions (P03, Python and ALGOL).** Rule 3 explicitly calls a
  separate splitting function R. I extend that reading to the separate suffix,
  prefix and reverse-inverse definitions, their answer collections, recursive
  traversal and reconstruction callbacks. Their own case-head tests remain P
  under rules 2 and 10, including equal heads and singleton suffix tests.
  Traversing the recursive relation’s answers does not enumerate an unstated
  domain, so I did not apply rule 6’s C classification. These specialized
  algorithms are R, rather than reusable search mechanisms S. The tension is
  that rule 3’s opening sentence also seems to permit every queried direction
  when transcribed by cases; its explicit splitting example narrows that
  permission without saying exactly where the boundary lies.
- **Reordering the inverse reverse.** The Python and ALGOL programs take conc
  before rev. Rule 4 records one move per implementation and adds no tokens.
  Those calls/traversals are already R as parts of separate inverse definitions;
  their R class is not a charge for the move itself.
- **Absys prescribed range (P13a–d).** Replacing m > n by m = n + 1 is R under
  rule 3. Omitting m <= n also changes the stated case, even though the finite
  answers agree for the queried direction and the given positive sizes. Under
  rule 10 I class that altered case’s introduction/closing tokens R and its
  unchanged sequence construction and recursive goal P. There is no token for
  the missing guard itself. The metrics need a clearer convention for omissions
  and for the class of case wrappers; assigning the whole case R would conflict
  with classing its nested unchanged goals independently.
- **Native P13e/f.** The problem expressly permits the native algorithm and
  says it is not reformulation. I therefore class native building, summing,
  reversing, accumulators and computational loop headers P. This includes
  Absys’s direction-correct native range, despite its comments calling it
  reformulated. The prescribed versions still receive the R classifications
  above. The problem-specific exception should be stated in METRICS as well.
- **Representations.** ALGOL’s head/tail arrays, allocation index, cons and
  recursive sequence equality are P encodings, following its system description
  and rules 2–3, not S for supplying a general logic mechanism. Python P13’s
  pair decomposition is constant-time P. Python P03 list slicing is still P
  where rule 3 permits forward transcription: P13’s additional representation
  restriction is task-specific. The prescribed racc accumulator is given by
  the problem, so rule 5 does not make it R.
- **Harness boundary.** Query goals and input constants are P, including goals
  nested inside print calls or Prolog query registrations. Labels, answer
  templates, printing callbacks at query sites, and registration shells are H.
  Inverse procedure declarations’ extra callbacks belong to their R definitions;
  the actual show/showpair arguments at stage sites implement printing (H).
  Arena resets implement pose and are H. Pure output adapters (as_list,
  outseq, show, showpair), fixed-cap/budget answer collection (including its
  cuts/fail), and the generic stage driver implement PROTOCOL’s print, answers
  and pose operations, so are H. They introduce no problem-specific scheduler
  or solver. Rule 13 is ambiguous before a fixed harness exists; I treated
  these stand-ins as implementations of the specified operations, not as a
  license to hide arbitrary computation under H.
- **Libraries.** SWI’s library(lists), numlist/3, sum_list/2 and reverse/2 are
  external mechanisms, counted at their import/call tokens under rule 12, not
  S. Native calls are P under P13’s permission. SWI formatting, non-backtrackable
  answer counters, inference limits, forall and initialization here serve H.
  ALGOL’s IFIP output procedures are also external and their printing calls H.
- **Layout and documentation.** I retained every supplied Python docstring and
  significant layout token. A docstring takes its containing definition’s
  class; INDENT/DEDENT closes or opens its owning construct even when the TSV
  puts it on the next source line. Documentation literals have no explicit
  independent class in the metrics. Wrapper fragments split by nested children
  keep the parent’s class under rule 10.

No C or S constructs were identified under these interpretations. In
particular, case dispatch is P, native workload loops are P, specialized inverse
answer traversal is R, and fixed answer-collection control is H.
