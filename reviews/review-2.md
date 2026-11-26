# Review 2, of draft 0.3

*26 November 2026.* An independent review by a model agent with a fresh
context, which had not written or reviewed earlier drafts. It read every
file and modified none. It checked the enumerations and counts with a
script. Draft 0.4 is the response.

**Checked and correct:**

- P01–P09 under every stated reading;
- P10a, c and d; P12's 8,191 and all six positions; P13's closed forms;
- P14; P15a's six interleavings, each produced once; P15b's fair set.

**The one mathematical error** is P10b (item 6).

Each finding is summarised in a line, with the response. *Accepted* means
changed as proposed. *Adapted* means changed, differently. *Open* means it
needs the owner's decision before the freeze.

## Must-fix

| # | finding | response |
|---|---|---|
| 1 | *undetermined* marks an exactly right residual (P02 stage 1, P07c, P09e) as a failure | Accepted. *Undetermined* only if not equivalent, or if a smaller equivalent solved form exists that the system did not reach. "Smaller" defined; worked examples added |
| 2 | no operation asks for one answer | Accepted. `answers(1)` for any-one queries, `answers(20)` otherwise, stated per query |
| 3 | P11's log under reposing and separate observation runs | Accepted. One log per problem across every judged run, including reposing; observation runs log elsewhere; duplicates from reposing counted |
| 4 | P11 commit undefined, and P11d's outcome depends on an unstated choice | Accepted. Commit selects one current outcome v and adds x = v; a system holding several must select, or is judged on all it emitted |
| 5 | P15b: argument order, z undefined, no consumer, no class for a prefix | Accepted, all four |
| 6 | P10b stage 1 outcome wrong | Accepted. d = 2·b with neither valued; d is defined by a standing relation, not "becomes" |
| 7 | reposing can let the harness do P10's work | Accepted. A reposed run replays every stage in order, withdrawals and replacements included |
| 8 | R makes almost all Python R; Rule 1 undefined for imperative code | Adapted. Mode-faithful transcription is P; R only for added arguments or cases, a changed algorithm, or an unused mode. Case dispatch is P. Calibration examples are required before the freeze (**open**: who writes and classes them) |
| 9 | built-ins hide work from step counts; a loop inside C never hits the budget | Accepted. Problem-defined operation counts for prescribed tasks; CPU time and maximum resident set size as secondary growth measures; a timeout becomes final after one rerun at ten times the limit |
| 10 | P13 prescribed breaks on representation and the recursion limit | Accepted. ⟨h⟩ ++ t must decompose in constant time, representation recorded; the recursion limit is a listed flag, or the error is the result |
| 11 | P12 never lets depth-first win | Accepted. P12d added; P12 posed at n = 8, 12, 16 |
| 12 | comparable retention cost claimed but not delivered | Accepted. Problem-defined quantities (P05, P12, P13) and growth exponents, compared across systems; the claim reworded |
| 13 | cores and units incomplete | Accepted for Absys, SWI-Prolog and ALGOL 60. Python awaits its measurement study |
| 14 | nothing stops hand-solved programs | Accepted. A genericity rule with hidden variants of each problem (**open**: who holds them) |
| 15 | P14, P15c, P15d have no vocabulary by cases | Accepted. Definitions by cases added |
| 16 | guards in committed-choice languages counted as C | Accepted. A guard testing a case's own head, or a stated condition, is P |

## Should-fix and minor

| # | finding | response |
|---|---|---|
| 17 | no way to pose separate computations | Accepted. `spawn(computation)` |
| 18 | budget of a reposed run | Accepted. Restart cost plus 10⁶ |
| 19 | the budget class is not comparable across units | Adapted. *Budget* is marked system-relative; each system's steps for P13b at n = 10³ are recorded as a calibration figure |
| 20 | choicepoints at boundaries are zero by construction | Accepted. Measured at each answer and when the budget runs out |
| 21 | the sampler perturbs counts; README and report disagree | Accepted. Classification from unsampled runs; the wording reconciled ("difference minus 1"); Linux reproduction under way |
| 22 | probes only in a scratchpad | Accepted. Being committed under `systems/swi-prolog/probes/` |
| 23 | repeated work "from a trace" exists only for Absys | Accepted. A source per system, or marked not measured |
| 24 | S is gameable by one large interpreter | Accepted. S reported apart, mechanisms listed with sizes at the freeze, extended results named by mechanism |
| 25 | nested constructs | Accepted |
| 26 | built-ins substituted for defined relations | Accepted |
| 27 | anticipation of later stages | Accepted |
| 28 | which variant stands for the configuration | Accepted. A primary variant chosen before any run |
| 29 | "candidates examined" undefined for interleaving systems | Accepted |
| 30 | Python alternatives held in generator frames | Deferred to the Python measurement study |
| 31 | when a binding counts as reported | Accepted |
| 32 | P08 classes under the open reading | Accepted |
| 33 | dynamic declarations force the closed reading | Accepted. Counted as C, and listed |
| 34 | origins of P10–P15 | Accepted |
| 35 | ALGOL 60 given by local path only | Accepted. URL given |
| 36 | ALGOL 60 value encodings | Accepted |
| 37 | native P13 can avoid building the sequence | Accepted |
| 38–46 | numbering, stale README, racc, P08 x = y, b ≠ ⟨⟩, cumulative variables, P09d one run, status lines, Absys notation rule | Accepted, all |

## Responses of review 1 not carried out

The reviewer found four, items 13, 39, 40 and 1 above, and all four are
now addressed.

## Per model

The reviewer's assessment of where the suite gives each model a chance:

- **imperative:** P10, P11a, P13, P14, P15d. It lost them through items 8–10.
- **logic:** P03 and P06d–e.
- **assertional:** about ten staged problems. Its retention cost was never
  compared (item 12).
- **dataflow:** P09c, P09d2, P14 and P15b. P15b was broken (item 5).
- **concurrent constraints:** P09e, P02 and P15c–d. These were
  misclassified or undefined (items 1, 15, 16), and no problem has many
  agents telling a shared store at scale.
- **backtracking:** P04b and e, P11a, P15a1. P12 never let depth-first win
  (item 11).

That last gap for concurrent constraints, many agents telling one store at
scale, is **open**: a candidate P16 before the freeze.
