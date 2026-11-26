# SWI-Prolog

**Evidence class: modern.** SWI-Prolog 11.0.1, pinned in CI with the
`swipl:11.0.1` container image.

SWI-Prolog stands for Prolog the language, not Prolog in 1972. No result
here is attributed to Marseille Prolog or to DEC-10 Prolog. A historical
Prolog, rehosted or reconstructed, would be a separate system.

## Configurations

Each configuration adds to *plain* and is reported separately, so that a
capability added later is not credited to the earlier model.

| configuration | adds to plain | class |
|---|---|---|
| **plain** | nothing | modern |
| **tabling** | `:- table` (SLG resolution) | modern, with external mechanisms |
| **coroutines** | `when/2`, `freeze/2`, `dif/2` | modern, with external mechanisms |
| **constraints** | coroutines, and `library(clpfd)`, `library(clpq)` | modern, with external mechanisms |
| **session** | constraints, and engines (`engine_create/3`, `engine_post/3`, `engine_fetch/1`, `engine_yield/1`), with supporting code that makes an application wait for an undefined procedure | modern, extended |

In *session*, the supporting code is counted as S (`METRICS.md`).
*constraints* is judged on the problem's own domain. A clpq answer over the
rationals is unsound where the problem is over the integers.

## The core of plain

ISO Prolog:

- unification, with SLD resolution in textual order and backtracking;
- the cut;
- `\+` (negation as failure), `=`, `\=`;
- `is/2` and arithmetic comparison;
- `findall/3`, `call/N`, `catch/3`, `throw/1`;
- `assertz/1`, `retract/1` and `dynamic/1`, for posing definitions and
  replacing state between stages.

Flags:

- `occurs_check` is `false`, SWI's default; P01c is also run with `true`,
  as a recorded variant;
- `unknown` is `error`, ISO's default. P08 records the result, and a
  variant with `fail`, which corresponds to the closed reading.

## Units

- **Step:** one inference, as `statistics(inferences, _)` and
  `call_with_inference_limit/3` count them.
- **Alternative:** one open choicepoint. To be settled before the freeze is
  how it is counted, for instance by `prolog_current_choice/1` and walking
  `prolog_choice_attribute/3` at each observation point. A choicepoint may
  yield no solutions or many, so the count is recorded with that caveat.
- **Store:** the bytes of the global, local and trail stacks in use, from
  `statistics/2`. They are sampled at stage boundaries and at each answer.
  A true peak within a stage needs further instrumentation, to be settled
  before the freeze.

## The same computation

- **plain, tabling, coroutines, constraints:** each stage after the first
  is posed by reposing stages 1 to k together. That is counted under
  restart cost.
- **session:** one engine holds the computation, and each stage is posted
  into it.

## Prior work, not results

`research/e07/` in the absys repository ran versions of P01–P08 on
*plain*, *coroutines*, *constraints* and *session*, before this
specification existed. They will be written again from the problem files
after the freeze.
