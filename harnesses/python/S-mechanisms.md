# Supporting-code (S) mechanisms of the Python configurations

*Phase 4, before any program is run (`PROTOCOL.md`, "Recording a result":
every configuration's S mechanisms are listed, with their size, at phase
4). Source: `systems/python/README.md`, "Configurations". The mechanisms of
extended were written on 2026-11-27 by `s-python-extended` (an agent), from
the systems file's description only ("for instance a backtracking search, a
suspension queue, a constraint propagator"), before any program of the
study, and tested on made-up examples only.*

| configuration | admits S? | S mechanisms it provides | size |
|---|---|---|---|
| **core** | no: the language and its built-ins, no imports | none | — |
| **stdlib-concurrency** | no: core plus `threading`, `queue`, `asyncio`, which are external mechanisms (listed by name), not S | none | — |
| **extended** | yes: "mechanisms written for the experiment: for instance a backtracking search, a suspension queue, a constraint propagator. Counted as S, once per mechanism" | the three below, as the package `S` | below |

## The S mechanisms of extended (listed 2026-11-27)

Code in [`S/`](S), plain CPython 3.13 with no import except from each other
(`propagate` imports `search`). Each module's docstring is its interface,
and states its order. A program imports them as `from S.search import
search` (README.md, section 2).

| mechanism | file | provides | lines (all / code) | tokens |
|---|---|---|---|---|
| **backtracking search** | [`S/search.py`](S/search.py) | `search(root, children, is_solution, trail=None, stack=None)`: depth-first, chronological backtracking over choice points given by the caller's `children` (tried in order, lazily); a generator of solutions, one at a time, so a caller takes one or many. Iterative (depth not limited by the recursion limit). Owns the **trail** (a list of undo callables) and `undo(trail, mark)`: every child starts from its parent's state; an exhausted search restores the start. `stack` exposes the pending choice points for registration | 51 / 17 | **176** |
| **suspension queue** | [`S/suspend.py`](S/suspend.py) | **owns the variables** of the S mechanisms: `Var` (logic variable: unbound, aliased to another Var, or bound to a value), `deref`. `Queue`: `wait(goal, *vars)` holds a goal until any of its vars is bound; `bind(v, x, trail=None)` binds (False if two values differ) and wakes the goals waiting on v; `run()` runs ready goals. Stated fair order: ready goals first in, first out; goals woken by a binding join the back in the order they suspended. `held` and `ready` can be registered; bindings can be undone through search's trail | 108 / 60 | **537** |
| **constraint propagator** | [`S/propagate.py`](S/propagate.py) | `Store(trail=None)`: finite integer domains per variable (any hashable, e.g. a `Var`); `linear(terms, op, c)` (exact integer `==`, `<=`, `>=`, bounds consistency) and `relation(vars, pred)` (any predicate, arc consistency); propagation queued first in, first out to a fixpoint; `fix()` False on an empty domain; `residual()` the constraints not yet decided, each readable by `repr`; `value(v)`; `label(vars)`: solutions by `search`, values in increasing order, undone through the trail | 158 / 96 | **1,260** |
| | | **total** | 317 / 173 | **1,973** |

**Size.** Tokens by `METRICS.md`, "Tokens": the lexical tokens of Python's
`tokenize`, with comments, docstrings (rule 17), non-significant line ends
(`NL`), the encoding and the end marker not counted; each `NEWLINE`,
`INDENT` and `DEDENT` (significant layout) counted as one token. Code lines
are lines holding a counted token other than layout. Measured by
[`S/tests/size.py`](S/tests/size.py), printed at the end of
[`S/tests/output.txt`](S/tests/output.txt). Each mechanism is counted once
for the configuration, whichever programs use it (`METRICS.md` rule 12),
and a program that uses one lists it and is named by it (`PROTOCOL.md`,
"Recording a result"). A mechanism that imports another (`propagate.label`
uses `search`) uses it; the imported one is still counted once.

**Tests.** [`S/tests/run.py`](S/tests/run.py), on made-up examples only (bit
strings, subset sums, small linear systems, dataflow goals), run in the
pinned image:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \
        cp-agent-python:spec-1.0 python3 harnesses/python/S/tests/run.py

Output: [`S/tests/output.txt`](S/tests/output.txt) (21 of 21 passed, CPython
3.13.7).

## What this means for programs

- A program for **extended** may use these three mechanisms, through their
  interfaces as their docstrings state them, and nothing else beyond core.
  The code it writes around them (the choice of children, the goals, the
  constraints posted) is classed in the program by `METRICS.md` as usual
  (a search or labelling directive, a freeze call, is C). This supersedes
  the phase-4 reading in [`QUESTIONS.md`](QUESTIONS.md), Q3 ("none
  defined").
- Code a program writes for itself that is general over relations, and
  reusable from one problem to another (a constraint store, a propagator,
  a scheduler), is still S by `METRICS.md` rules 12 and 19 wherever it is
  kept, and puts the program in *extended*, named by that mechanism; it is a
  mechanism not listed here, and is classed by the classifiers.
- The harness's own machinery (the step meter, the pause at the budget, the
  threads that run spawned computations, the watcher for quiescence, the
  `cp` calls) is harness code, not S, and is not available to a program as a
  mechanism: it is listed in [`README.md`](README.md) as H tokens and as
  confounds.
