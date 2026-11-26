# SWI-Prolog

**Evidence class: modern.** SWI-Prolog 11.0.1, pinned in CI with the
`swipl:11.0.1` container image.

SWI-Prolog stands for Prolog the language, not Prolog in 1972. No result
here is attributed to Marseille Prolog or to DEC-10 Prolog. A historical
Prolog, rehosted or reconstructed, would be a separate system.

## Configurations

Each configuration adds to the one before it. Results are kept separate,
so that a capability added later is not credited to the earlier model.

| configuration | core | adds | classes |
|---|---|---|---|
| **plain** | ISO Prolog: unification, resolution in textual order with backtracking, cut, negation as failure (`\+`), `findall`, `is` | nothing | modern |
| **coroutines** | plain | `when/2`, `freeze/2`, `dif/2` | modern, with external mechanisms |
| **constraints** | coroutines | `library(clpfd)`, `library(clpq)` | modern, with external mechanisms |
| **session** | constraints | engines (`engine_create/3`, `engine_post/3`), with supporting code that makes an application wait for an undefined procedure | modern, extended |

In *session*, the supporting code is counted as S, token by token
(`METRICS.md`).

## Prior work, not results

`research/e07/` in the absys repository ran versions of P01–P08 on all
four configurations, before this specification. They will be written again
from the problem files after the freeze.
