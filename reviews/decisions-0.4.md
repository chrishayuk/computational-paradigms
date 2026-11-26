# Decisions on draft 0.4

*27 November 2026. Taken by the project's owner on the questions draft 0.4
left open, and applied in draft 0.5.*

| question | decision | what draft 0.5 does |
|---|---|---|
| Hidden variants and classifiers | Separate roles with isolated contexts; Claude and Codex as the two classifiers, neither having written the program; variants inaccessible, generated and hashed before the freeze, revealed after the results | `PROTOCOL.md`, Roles: six roles; the variants encrypted with a key the owner holds, with only ciphertext and hash committed |
| Calibration programs | P03 and P13 in all four systems, as development examples, not results | `METRICS.md`, Calibration, and `calibration/` |
| P16 | Included: many independently contributed relations over shared unknowns, stated as relations and outcomes, with no mechanism prescribed | `problems/16-shared-information.md`: propagation, contributors, localised updates, contradiction |
| A third review | Approved, of draft 0.5 | Pending |

Four refinements were also applied:

- **Correctness and simplification are kept apart.** An equivalent residual
  is *complete*, however unreduced. Simplification (reduced, reducible,
  inconsistency undetected) is recorded separately. *Undetermined* now
  means only that equivalence cannot be established.
- **Growth** is fitted by linear, polynomial and exponential models. Three
  sizes are evidence over their range, not proof of asymptotic complexity.
- **A reposed run preserves a commitment**, replaying it as x = v rather
  than selecting again.
- **Repeated work in ALGOL 60** separates first evaluations of an actual
  parameter from repeats (absys-style measurement branch `151cdff`), and
  notes that a repeat is not always wasted.

Still held: the freeze, the full benchmark, and PLANNER.
