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

Qualified on macOS arm64 by the study in
[`measurement.md`](measurement.md). Not yet checked on the Linux CI
image.

- **Step:** one inference. The difference of `statistics(inferences, _)`
  agrees exactly with `call_with_inference_limit/3`, and is the same from
  run to run. Libraries are loaded before measuring, because autoloading
  adds 15,000–23,000 inferences, and a limit reached during autoloading
  leaves the library undefined. Runs are not in debug mode. In *session*,
  the count is read inside the engine, which keeps its own.
- **Alternative:** **retained choicepoints**, the open choicepoints newer
  than a mark taken at the start of the stage, counted by walking
  `prolog_choice_attribute/3`, by type. Exact at answers and stage
  boundaries. A choicepoint records that one call has untried alternatives.
  It may yield no solutions or a million, so it is never equated with one
  derivation of another system. A comparable count of alternatives comes
  only from a quantity the problem defines, such as P12's candidates
  examined.
- **Store:** a vector, as for Absys:
  - live global data, read after `garbage_collect/0` at each boundary;
  - local and trail stack in use;
  - `table_space_used`, for *tabling*;
  - attributed variables (`term_attvars/2`, which includes the solvers'
    internal ones) and projected residual goals (`copy_term/3`), for
    *coroutines*, *constraints* and *session*.

  SWI-Prolog has no true peak of any of these. A maximum within a stage is
  taken with the `heartbeat` flag, and reported as a **sampled maximum**
  with its interval, never as a peak. The sampler misses deterministic
  tail-recursive loops, and its own inferences are counted. The operating
  system's maximum resident set size is a true peak, but of the whole
  process, and is reported as such.

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
