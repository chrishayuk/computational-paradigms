# Python

**Evidence class: modern.** The modern imperative baseline. The version is
pinned at the freeze, to a patch release. The proposal is CPython 3.13.7,
the 3.13 release studied, in a `python:3.13.7` container image.

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

Qualified on macOS arm64 with CPython 3.10 to 3.14 by the study in
[`measurement.md`](measurement.md), with probes in [`probes/`](probes).
Not yet run in the `python:3.13` image or on Linux.

- **Pinning.** The **patch** release is pinned, not only 3.13. Instruction
  counts per loop differ between minor versions, and the depth to which
  recursion through C works differs between patch releases (1,497 levels on
  3.12.2, 9,997 on 3.12.11). Runs set `PYTHONHASHSEED=0`.
- **Step:** one bytecode instruction, counted by `sys.monitoring`
  INSTRUCTION events. The count is exact and repeatable, and results are
  unchanged, at 12–25 times the time. It sees no work inside built-ins:
  at n = 10⁵, `sum(xs)` is 4 instructions and a loop 700,007. So P13 also
  records CPU time and maximum resident set size, for growth only
  (`METRICS.md`).
- **Budget:** a `BaseException` raised from the monitoring callback stops
  the computation after exactly B instructions. Where a stage must be
  continued after its budget, the computation's thread is instead blocked
  at B and resumed with a new budget, with the same total count. A loop
  inside one C call is never seen, so the safety limit kills the process
  from outside.
- **Problem operations:** applications of each defined relation, counted by
  `sys.monitoring` PY_START events on the functions that transcribe the
  definitions. No change is made to the program, and the count matched the
  closed forms exactly (conc: 500,500 at n = 1,000). Each defined relation
  is therefore written as a function of its own.
- **Store:** `tracemalloc`'s current and peak **traced Python
  allocations**, a true peak of what Python's own allocators hand out, not
  the memory the process uses; and `sys.getallocatedblocks()`.
  Memory outside Python's allocators is not seen. The process's
  `ru_maxrss` is taken only from a separate run with `tracemalloc` off, one
  process per stage, since it never falls.
- **Alternative:** the entries of the program's named pending structure (a
  stack, a queue, a frontier), and suspended generator frames, counted
  exactly with `gc.get_objects()` after a collection.
- **Recursion:** the recursion limit is a configuration flag, fixed per
  configuration. A `RecursionError` is classed *error*, not *budget*. The
  harness compares and prints deep answers iteratively, not with `==` or
  `repr`, which recurse through C.
- **Repeated work:** only problem operations, as counted above.

## The same computation

A program may run as one process that reads each stage from its input as
it arrives, which counts as the same computation. Otherwise each stage is
posed by rerunning with stages 1 to k, counted under restart cost.
