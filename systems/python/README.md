# Python

**Evidence class: modern.** The modern imperative baseline. The version is
to be pinned at the freeze. The proposal is CPython 3.13 in the
`python:3.13` container image, at a fixed patch release. 3.12.2 is
installed locally.

Python is not forced into a logic-programming style. Where a problem is
expressed more naturally in Python by another algorithm, the program uses
it, and the change from the problem's definitions is recorded as
reformulation, construct by construct, as `METRICS.md` says.

## Configurations

| configuration | adds | class |
|---|---|---|
| **core** | the language and its built-in functions and types, with no imports. Generators, exceptions and mutable state are part of the core | modern |
| **stdlib-concurrency** | `threading`, `queue` and `asyncio` | modern, with external mechanisms |
| **extended** | mechanisms written for the experiment: for instance a backtracking search, a suspension queue, a constraint propagator. Counted as S, once per mechanism | modern, extended |

Other standard-library modules used in any configuration are listed under
external mechanisms. No third-party package is used.

## Units

To be qualified before the freeze, as SWI-Prolog's were:

- **Step:** the proposal is one bytecode instruction, counted through
  `sys.monitoring` (Python 3.12 and later) INSTRUCTION events. That count
  is exact and changes no result, but slows the run. It depends on the
  CPython version, which is pinned.
- **Store:** `tracemalloc`'s current and peak traced memory. This gives a
  true peak of the memory Python allocates, not a sampled maximum.
- **Alternative:** Python has none of its own. A program that keeps
  alternatives keeps them in its own structures (a stack, a frontier, a
  list of generators), and the count of their entries is reported, with
  the structure named.

## The same computation

A program may run as one process that reads each stage from its input as
it arrives, which counts as the same computation. Otherwise each stage is
posed by rerunning with stages 1 to k, counted under restart cost.
