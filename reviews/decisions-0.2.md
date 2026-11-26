# Decisions on draft 0.2

*26 November 2026. Taken by the project's owner on the five questions that
draft 0.2 left open, and applied in draft 0.3.*

| question | decision | what draft 0.3 does |
|---|---|---|
| Which of P10–P15 to keep | All six, in the primary suite. P14 and P15 exercise capabilities where Concurrent Prolog and Oz may do well and Absys badly, which is the reason to include them now | P13, P14 and P15 written. P11 has explicit commitment, so that no system must anticipate information it has not received, and "deferred" is now an observation of when an effect happened, not a class beside exact, extra and missing. P13 has a prescribed algorithm and a native idiom for each task, to separate algorithm from bookkeeping |
| An imperative baseline | Two: Python (modern) and ALGOL 60 (historical, of the same period as Absys) | `systems/python/` and `systems/algol-60/`, with configurations. Neither is forced into a logic-programming style; departures are reformulation |
| Absys store | An instrumentation-only branch, with the baseline kept, output shown identical, and no change to the machine's rules. Store as a vector, current and peak | Done on the absys branch `measure`; see `systems/absys/README.md` |
| SWI-Prolog measurement | A qualification study, not a benchmark. A choicepoint is not equated with a derivation. A sampled maximum is never called a peak | Under way, reported in `systems/swi-prolog/measurement.md` |
| A second review | A fresh reviewer, after draft 0.3, asked also to look for hidden advantages to each model | Pending |

Two further decisions:

- **Budget.** Exhausting the budget no longer forces a restart. Where a
  configuration can keep and continue its computation, the next stage goes
  into it, and that capability is recorded (`PROTOCOL.md`).
- **Dimensions.** Six dimensions of design (information, execution, state,
  search, coordination, commitment), with resources across all of them
  (`SPECIFICATION.md`).

Still held: the freeze, every benchmark program, and PLANNER.
