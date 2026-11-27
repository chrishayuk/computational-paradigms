# CPython: what can be measured, and how to word it

This is a measurement-qualification note, not a benchmark. Every figure
below comes from a small probe run locally on macOS (Darwin 27, arm64). The
probes are in [`probes/`](probes), run by [`probes/run.sh`](probes/run.sh),
and their full output for each interpreter is in `probes/out/<version>.txt`.
No program for any of the study's problems was written. The cons-cell
functions in `p2_algops.py` and `p5_recursion.py` are probes of counting
and of recursion depth; they fix no representation or idiom for the study.

**Versions.** The study's local interpreter is CPython 3.12.2 (python.org
build, `python3`). Five more were found on the machine and used for the
cross-version comparisons: 3.10.15, 3.11.10, 3.12.11 and 3.13.7
(python-build-standalone builds installed by `uv`) and 3.14.6 (Homebrew).
The study proposes CPython 3.13 in the `python:3.13` container image.
Docker was not available, so **nothing here was run in that image or on
Linux**. The 3.13 figures are from 3.13.7 on macOS, a different build of the
same release line. Where this note says "3.12+" it means 3.12.2, 3.12.11,
3.13.7 and 3.14.6, each of which was run.

All probes were run as `python -B -s probe.py` with `PYTHONHASHSEED=0`,
except where a probe varies the seed. `-s` excludes user site-packages.

## Summary

| measurement | how | exact / sampled / approximate / unavailable | perturbation |
|---|---|---|---|
| Python instructions executed | `sys.monitoring` INSTRUCTION events, one global callback that increments a counter | exact count of bytecode instructions executed in Python code (3.12+); RESUME and CACHE entries are not reported; C code executes no instructions | results unchanged; 12 to 25 times slower; reachable recursion depth 2 frames less; a few hundred bytes of tracemalloc peak |
| the same, through `sys.settrace` with `f_trace_opcodes` | `'opcode'` trace events | the same count when it works, but on 3.12+ whole calls are missed depending on history (P1b); usable on 3.10 and 3.11 only | 18 to 41 times slower |
| operations the problem defines (applications of conc, rev, racc, range, sum) | `sys.monitoring` PY_START events enabled locally on the code objects of the functions that transcribe the definitions | exact count of calls, which for these definitions is the count of applications | no change to the program text; step count changes only by a fixed setup cost (269 instructions); no extra frames |
| the same, by counters written into the program | `OPS["conc"] += 1` | exact | adds instructions to every call (70,112 became 124,725 at n = 100); classed H or S |
| the same, by wrappers | rebinding each name to a counting wrapper | exact | one extra Python frame per call: halves the reachable recursion depth |
| traced memory, current and peak | `tracemalloc.get_traced_memory()`, `reset_peak()` | exact for allocations through Python's allocators after `start()`; peak is a true high-water mark of those allocations | about 7 to 16 times slower with 1 frame of traceback; roughly 49 bytes of tracemalloc's own memory per live traced block; step count unchanged |
| memory outside Python's allocators (mmap, some C libraries) | none in-process | unavailable to tracemalloc (64 MiB mmap: 96 bytes traced) | — |
| process peak memory | `resource.getrusage(RUSAGE_SELF).ru_maxrss` | true peak of resident memory for the whole process; bytes on macOS, KiB on Linux; never decreases | none; but includes tracemalloc's own tables if tracemalloc is on |
| live allocator blocks | `sys.getallocatedblocks()` | exact count of blocks at a point; differences are reproducible, absolute values vary by a few dozen between runs | none measured |
| program's own alternative structure | `len()` of the stack, queue or frontier the program keeps | exact at a point; a peak only if the program records it (harness code) | the peak bookkeeping is code in the program |
| suspended generators | `gc.get_objects()` filtered on generators with a frame, after `gc.collect()` | exact count of suspended generator frames at a point | cost proportional to the heap; a collection |
| all objects | `gc.get_objects()` | unavailable as an object count: untracked objects (ints, strs, tuples of atoms, and dicts of atoms before 3.14) are not listed | — |
| recursion limit | `sys.setrecursionlimit`, `RecursionError` | exact limit for Python frames; a separate C limit or stack check for recursion through C, which differs by patch release | — |
| instruction budget | an INSTRUCTION callback that raises a `BaseException` subclass after B instructions | exact: stops after exactly B instructions | same cost as counting; the program can catch the exception unless the budget is "sticky" |
| budget with continuation | the callback blocks the computation's thread at B; the harness grants a new budget | exact; the same computation continues | needs `threading` in the harness |
| CPU time | `time.process_time()` | measured; varies from run to run | — |

## 1. Instruction counts

### Mechanisms

- **`sys.monitoring`** (PEP 669, 3.12+). A tool registers a callback for
  `events.INSTRUCTION` and enables it globally with `set_events`. The
  callback receives `(code, offset)` before each instruction. The callback's
  own instructions were not counted in any probe (section 2, methods C and
  D), so the counter does not count itself.
- **`sys.settrace`** with `frame.f_trace_opcodes = True`, set in the
  `'call'` event, delivers an `'opcode'` event per instruction. On 3.12+
  `settrace` is implemented on top of the monitoring machinery.

The meter is `probes/meter.py`. `count_mon(fn, *args)` returns
`(result, instructions)`. The meter's own frame executes 12 instructions
between enabling and disabling the events; the callback ignores the meter's
code object, so these are excluded and the count is that of `fn` alone
(`count_mon(lambda: None)` is 1, the function's one return instruction).

### Work hidden inside one instruction (p1_instructions.py)

Instructions counted for each function at n = 10⁵ (3.12.2; identical figures
at n = 10², 10³ and 10⁴ for the built-in rows), and the result compared with
an uncounted run:

```
workload              n       mon     trace same_result
rev_method       100000        10        10 True     ys = xs.copy(); ys.reverse()
rev_slice        100000         7         7 True     xs[::-1]
rev_reversed     100000         6         6 True     list(reversed(xs))
rev_loop         100000   1600013   1600013 True     while i >= 0: ys.append(xs[i]); i -= 1
sum_builtin      100000         4         4 True     sum(xs)
sum_loop         100000    700007    700007 True     for x in xs: k += x
sorted_builtin   100000         6         6 True     sorted(xs, reverse=True)
```

The built-in forms take the same handful of instructions at every n. The
explicit loops take 16n + 13 and 7n + 7. Summing 10⁵ numbers is 4
instructions with `sum` and 700,007 with a loop, a ratio of 175,000, and
the ratio grows with n. The instruction count therefore measures how much
of the work is done in Python code, not how much work is done.
`sorted(xs, key=lambda x: -x)` over 1,000 elements counts 3,009, against 6
without the key (p1e_scope.py): Python code called back from C is counted,
and the C code around it is not.

Consequences for the study:

- P13e and P13f (native) will typically be a few instructions for any n.
  Their step counts are not comparable with P13a to P13d, and should be
  reported with the built-ins used, not as a measure of cost.
- Within P13a to P13d, a transcription that uses a built-in for any part
  of a definition (Python list `+` for ⟨h⟩ ++ t, for instance) moves that
  part's work out of the count. For a prescribed definition, the
  instruction count is meaningful only if every relation of the definition
  is a Python function.

### Exactness and agreement

When both meters deliver events they agree exactly (all rows above). The
count includes instructions in every thread (two threads each running a
7,008-instruction loop counted 14,720 on 3.12, the extra being thread
start-up and join code in the standard library) and in Python code called from C.

### `settrace` misses calls on 3.12+ (p1b_first_call.py)

Each line counts the same 28-instruction function three times (25 on 3.13,
26 on 3.14), starting from a fresh code object:

```
3.12.2   trace first, never run before : [0, 28, 28]
         plain call, then trace        : [28, 28, 28]
         monitoring first              : [28, 28, 28]
3.13.7   trace first, never run before : [0, 25, 25]
         plain call, then trace        : [0, 25, 25]
         monitoring first              : [25, 25, 25]
         plain, trace, trace, mon, trace, trace:
             [('trace', 0), ('trace', 25), ('mon', 25), ('trace', 0), ('trace', 0)]
3.10.15  trace first, never run before : [28, 28, 28]
3.11.10  trace first, never run before : [28, 28, 28]
```

On every 3.12+ version, `settrace` delivered no `'opcode'` events at all for
some calls. On 3.13.7 and 3.14.6, once `sys.monitoring` had been used by
another tool in the process, no further opcode events arrived for that
function (the `trace` column of p1_instructions.py is 0 throughout on 3.13
and 3.14 for this reason). In a scratch run on 3.12.2, a plain call followed
by a traced call also gave 0. The pattern depends on the history of the
process and was not reduced to a rule. `sys.monitoring` counted correctly
from the first call in every case, including after 1,000 uncounted calls
had let the specialising interpreter adapt the code. **`settrace` is not
usable as an instruction meter on 3.12+.**

### Determinism (p1c_determinism.py)

The same probe, run as separate processes, gave identical output every time
(md5 of p1_instructions.py output equal over three runs on 3.12.2, two on
3.13.7). The count depends on what the program iterates over:

```
3.12.2 PYTHONHASHSEED=0       list of str  position=101 instructions=1623
                              set of str   position= 63 instructions=1015
                              set of objects (id hash) position=184 instructions=3135
3.12.2 PYTHONHASHSEED=0 again set of str   position= 63 instructions=1015
                              set of objects (id hash) position=196 instructions=3339
3.12.2 PYTHONHASHSEED=1       set of str   position=  6 instructions=103
3.12.2 seed unset (twice)     set of str   position=177, then 200
```

- Iteration over a list is fixed by the program.
- Iteration over a set or dict keyed by strings depends on the string hash,
  which is randomised per process unless `PYTHONHASHSEED` is fixed.
- Iteration over a set of objects hashed by identity depends on memory
  addresses, and varied between runs **with the seed fixed** (positions 184
  and 196 for the same seed).
- With threads, the count includes start-up and joining code whose path
  depends on timing: 12,600 in six runs on 3.13.7 and 12,699 in one.

### Across CPython versions

Instructions for the same source (p1_instructions.py at n = 10⁵, and the
n = 100 workload of p2_algops.py; 3.10 and 3.11 by `settrace`, which works
there):

| version | `rev_loop` | `sum_loop` | `rev_method` | p2 workload |
|---|---|---|---|---|
| 3.10.15 | 15n + 14 | 7n + 7 | 10 | — |
| 3.11.10 | 16n + 15 | 7n + 7 | 12 | — |
| 3.12.2, 3.12.11 | 16n + 13 | 7n + 7 | 10 | 70,112 |
| 3.13.7 | 15n + 13 | 6n + 7 | 10 | 75,364 |
| 3.14.6 | 16n + 14 | 6n + 8 | 10 | 75,468 |

The per-iteration cost changes between minor versions in both directions
(3.13 is cheaper for the loops, dearer for the recursive workload), as the
compiler adds and removes superinstructions. 3.12.2 and 3.12.11 agreed on
every count compared. Counts are comparable only within one pinned
version, and the pin should include the patch release (see 5 for a
patch-level change elsewhere).

### Cost and perturbation (p1d_cost.py)

A loop of 10⁶ iterations, process CPU time, best of runs 2 and 3:

| version | plain | monitoring | settrace |
|---|---|---|---|
| 3.12.2 | 0.020 s | 0.50 s (25×) | 0.82 s (41×) |
| 3.13.7 | 0.019 s | 0.22 s (12 to 13×) | 0.32 s (18 to 19×) |
| 3.14.6 | 0.026 s | 0.39 s (15×) | 0.51 s (20×) |
| 3.10.15 | 0.021 s | — | 0.71 s (35×) |

Run 1 under `settrace` is fast because it counted 0 (above); taking a
minimum over all runs would have reported that. Timings vary by about 10%
between invocations of the runner.

The result was the same with and without either meter in every probe.
Other effects of the monitoring meter on 3.12.2:

- tracemalloc peak of the same loop: 144 bytes plain, 686 with monitoring,
  1,094 with settrace (the callback closure and transient ints);
- deepest recursion before `RecursionError` at the default limit: 998
  plain, 996 under either meter (995 under `settrace` on 3.10.15);
- instruction counts are unchanged by tracemalloc (70,012 with it off and
  on).

### Recommended wording

"Python instructions: bytecode instructions executed in Python code
(`sys.monitoring` INSTRUCTION events, CPython <version>, all threads), the
meter's own frame excluded. Work done inside built-in functions and types
is not counted." Exact and deterministic for a fixed version, program and
input, with `PYTHONHASHSEED=0`, and with no iteration over identity-hashed
sets or dicts and no threads; otherwise state which of these applies.

## 2. Operations the problem defines

### Methods compared (p2_algops.py)

The probe transcribes range, sum, conc, rev, revacc and racc over cons cells
(`()` is ⟨⟩, `(h, t)` is ⟨h⟩ ++ t), runs a P13-shaped workload (build the
range, then sum, rev and revacc it), and counts calls to each function four
ways. Expected counts, from the definitions: range n + 1, sum n + 1, rev
n + 1, conc n(n + 1)/2, revacc 1, racc n + 1.

```
3.12.2, n=1000 expected {'conc': 500500, 'racc': 1001, 'rev': 1001, 'revacc': 1, 'rng': 1001, 'sm': 1001}
  none          result=(500500, 1000, 1000) same=True counts_match=-    cpu=0.024s
  A counters    result=(500500, 1000, 1000) same=True counts_match=True cpu=0.062s
  B wrappers    result=(500500, 1000, 1000) same=True counts_match=True cpu=0.087s
  C monitoring  result=(500500, 1000, 1000) same=True counts_match=True cpu=0.138s
  D setprofile  result=(500500, 1000, 1000) same=True counts_match=True cpu=0.200s
instructions of the n=100 workload, counted by meter.count_mon:
  none          70112
  A counters    124725
  B wrappers    152234
  C monitoring  70381
  D setprofile  70224
recursionlimit 1500, n=1000:
  B wrappers    RecursionError: maximum recursion depth exceeded   (the others: ok)
```

| method | program text | effect on steps | effect on depth | cost at n = 1000 |
|---|---|---|---|---|
| A: counters in the functions | one line per counted function | +78% here; grows with every call | none | 2.6× |
| B: wrappers bound to the same names | none in the functions; the names are rebound | +117% | one extra frame per call: depth doubles | 3.6× |
| C: `sys.monitoring` PY_START, local events on the chosen code objects | none | a fixed setup cost (+269) | none | 5.8× |
| D: `sys.setprofile`, filtered by code object | none | a fixed setup cost (+112) | none | 8.3× |

All four counts were exact and matched the closed forms on 3.12.2, 3.12.11,
3.13.7 and 3.14.6 (B, A and D also on 3.10 and 3.11, which lack C). The
results were identical with and without counting.

**Least intrusive: C.** It needs no change to the program, adds no frames,
leaves the instruction count unchanged apart from its setup, and can run in
the same process as the instruction meter (it uses a different tool id).
Its cost is paid only on calls to the chosen functions, since the events
are enabled on those code objects alone. The harness names the functions to
count; that list is H, fixed per problem before any run. Method A puts
counting code in the program and inflates the step count, so a program
with counters cannot also be the one whose steps are reported. Method B is
unsafe for recursive definitions because it doubles the depth.

### Making the counts comparable across systems

For prescribed-algorithm problems (P13a to P13d), the problem file fixes
the definitions, so the number of times each definition is applied is a
property of the definition and the input, not of the system. It is the one
work figure that can be compared across systems directly. To make it so:

1. **Define the unit by the problem.** One *application* of a relation is
   one use of one of its cases to reduce a goal or a call: for conc, one
   step from conc(⟨h⟩ ++ a, b, ...) to conc(a, b, ...), or one use of the
   base case. The closed forms above are then the expected values. For
   P13c, rev(⟨1..n⟩) applies rev n + 1 times and conc n(n + 1)/2 times.
2. **Count it in each system's own terms, mapped to the unit.** In Python,
   one call of the function that transcribes the relation (method C). In
   SWI-Prolog, a candidate is the call port of the predicate, which counts
   one per goal however many clauses are tried; failed head unifications
   are not applications. Each systems file states its mapping.
3. **Require transcription as functions.** The count exists only if every
   relation the problem defines is a function (a predicate, a procedure)
   in the program. If ⟨h⟩ ++ t is written with Python's `+` on lists, there
   is no conc call to count, and the work of each concatenation (copying
   len(a) + 1 elements) is inside one instruction.
4. **Check against the closed form.** A count that differs from the
   expected value is a finding about the transcription (an extra case, a
   relation computed twice) and should be recorded as such.
5. **Report it beside the system's own steps, not instead of them.** The
   ratio of steps to applications shows each model's bookkeeping cost per
   application, which is what P13 asks for.

For problems that do not prescribe an algorithm, such a count exists only
where the problem file defines the operation (answers, nodes of a search
tree the problem defines). Comparisons and similar operations inside
built-ins (`sorted`, `min`, `in` on a list) cannot be counted without
replacing the values with instrumented objects, which changes the program;
that was not probed.

### Recommended wording

"Applications of <relation> (calls of its transcribing function, counted by
`sys.monitoring` PY_START on that function's code object; no change to the
program). Expected from the definition: <closed form>."

## 3. Allocated memory

### Mechanisms

- `tracemalloc.start(nframes)` installs hooks on Python's three allocator
  domains (raw, mem, object). `get_traced_memory()` returns `(current,
  peak)` in bytes of traced blocks; `reset_peak()` (3.9+) sets the peak to
  the current value.
- `resource.getrusage(RUSAGE_SELF).ru_maxrss`: the OS's maximum resident
  set size of the process.

### Probe (p3_memory.py, 3.12.2)

```
[outside] mmap of 64 MiB, every page touched
  tracemalloc current growth=96 peak growth=216
  ru_maxrss before=21020672 after=88064000 growth=67043328
[peak] build and drop 10^6 ints inside a call
  current growth=84 peak growth=40000208
[ints/strings] lists of 100000 elements kept (current growth, bytes)
  keep_small_ints  current=   800960 peak=   801064 per_element=8.0
  keep_large_ints  current=  4000960 peak=  4001032 per_element=40.0
  keep_same_obj    current=   800032 peak=   800040 per_element=8.0
  keep_const_str   current=   800960 peak=   801064 per_element=8.0
  keep_built_str   current=  5392960 peak=  5393096 per_element=53.9
[freelist] 10^5 floats created and freed one at a time
  current growth=32 peak growth=152
[maxrss of a child process] keep_large_ints(10^6), tracemalloc off/on
  off maxrss growth=39960576 traced_peak=0        tracemalloc_own=624
  on  maxrss growth=118685696 traced_peak=40449336 tracemalloc_own=48777968
[steps] instructions of keep_large_ints(10^4), tracemalloc off/on
  off=70012 on=70012
```

The tracemalloc figures were identical in three runs (md5 of the output
without the rss and timing lines) and the same on 3.13.7 except
`keep_small_ints` (800,928). 3.10.15 reported a traced peak of 36,449,500
for the 10⁶ build against 40,449,336 on 3.11+.

### What tracemalloc sees

- **A true peak.** The peak is updated on every allocation: a 10⁶-element
  list built and freed inside a call left a peak of 40,000,208 bytes (8 for
  the pointer and 32 for each int), with current memory back to 84. No
  sampling is involved.
- **Only allocations through Python's allocators, after `start()`.** A
  64 MiB anonymous `mmap`, every page touched, was 96 bytes in tracemalloc
  (the mmap object) and 67 MB in `ru_maxrss`. C libraries that call
  `malloc` directly are likewise invisible. Allocations made before
  `start()` are not traced, and their frees are ignored; start it with
  `-X tracemalloc` to trace from interpreter start-up.
- **Shared objects cost nothing.** Small ints (−5 to 256), `None`, and a
  constant string are shared: a list of 10⁵ of them costs 8 bytes per
  element, the list's own pointers. 10⁵ distinct ints cost 40 bytes each,
  distinct short strings 54. A count of "elements held" and a count of
  bytes therefore disagree depending on the values.
- **Free lists.** 10⁵ floats created and freed one at a time showed 32
  bytes of growth: the interpreter reuses freed objects, and objects kept on
  a free list remain traced.
- **Requested sizes only.** tracemalloc counts the sizes requested, not
  pymalloc's arena and pool overhead or fragmentation. That is documented
  behaviour; it was not separately probed.

### Overhead

- CPU: building 10⁶ ints took 7 to 16 times as long with tracemalloc on
  (1 frame), and 24 to 220 times with 25 frames, depending on the version
  and the run.
- Memory: tracemalloc's own tables held 48,777,968 bytes for 10⁶ live
  traced blocks, about 49 bytes per block, and the child's `ru_maxrss`
  growth went from 40 MB to 119 MB. With tracemalloc on, `ru_maxrss`
  measures tracemalloc as much as the program.
- Steps: none. The instruction count was the same with it on and off.

### `ru_maxrss`

A true peak of resident memory for the whole process: interpreter, loaded
modules, allocator arenas, mmaps, and tracemalloc if on. About 16 to 21 MB
at start on these builds. It never decreases, so within one process only the
first stage's peak can be read unless the stage starts above every earlier
peak; one process per measured stage is needed. The unit is bytes on macOS
and KiB on Linux (the Linux unit is documented, not checked here). Resident
size also depends on the OS's paging, so it is a measurement of the run,
not of the program.

### Recommended wording

"Traced memory, current and peak (bytes, `tracemalloc`, 1 frame, started
before the stage, peak reset at the stage start): memory requested through
Python's allocators. Excludes allocator overhead and memory allocated
outside Python's allocators." Exact for what it covers; the peak is a true
peak. Separately, if needed: "process maximum resident set size
(`ru_maxrss`, one process per stage, tracemalloc off)", labelled a
whole-process peak.

## 4. Retained logical state

Python has no store of suspended goals or choicepoints of its own. What a
computation holds is in the program's own objects. The probes
(p4_retained.py) looked at what can be counted at an observation point.

```
[stack] dfs_bits(k): answers, peak length of the program's stack
  k= 4 (16, 5)   k= 8 (256, 9)   k=16 (65536, 17)
[gens] bits(k) suspended after its first answer
  k=16 live generators (gc)=17 chain via f_locals=1 chain via gc.get_referents=17
  after del: 0
[gcobjs] which objects gc.get_objects() lists
  int 10**9 False; str False; tuple of ints False; tuple holding a list True;
  list True; dict of str->int False (True on 3.14.6); cons cell (1, ()) False
[blocks] sys.getallocatedblocks() around keeping 10^4 cons cells
  before=63442 kept=83443 (+20001) after del=63444 (+2)
```

- **The program's own structure.** The length of an explicit stack,
  queue, frontier or agenda is exact at any point the program or harness
  can reach it. A peak exists only if the program records it as it goes,
  which is code in the program: harness-class (H) if the harness interface
  fixes it, otherwise classed by the token rules. The figure counts
  entries, and what an entry stands for depends on the program (a pending
  branch, a partial solution), so the structure is named with the count.
- **Suspended generators.** A nested generator suspended after its first
  answer holds one frame per level: 17 for depth 16, found by filtering
  `gc.get_objects()` for generators with a live `gi_frame`, after
  `gc.collect()`. Following the program's own references from the outer
  generator also gives 17 through `gc.get_referents()` on 3.11+ (it gave 1
  on 3.10.15). It does not work through `gi_frame.f_locals`, since a
  suspended `for` keeps its iterator on the value stack, not in a local.
  The `gc` scan costs time proportional to the heap and runs a collection;
  use it only at observation points.
- **`gc.get_objects()` is not an object count.** It lists only
  GC-tracked objects. Ints, strings, tuples of atoms (including cons cells
  whose tail is an atom-only tuple, after a collection untracks them) and,
  before 3.14, dicts of atoms are not listed. A count of retained cons
  cells cannot be had from it.
- **`sys.getallocatedblocks()`** counts live allocator blocks: keeping
  10⁴ cons cells with distinct int heads added 20,001 blocks (10⁴ tuples,
  10⁴ ints, 1 other), and freeing them returned to +2. Differences were
  the same in every run and version; the absolute value varied by a few
  dozen between runs. It is a usable count of objects retained, in blocks,
  but it includes interpreter-internal blocks and is shared by all threads.
- **Frame depth** at a point: walking `sys._getframe().f_back` (2 at top
  level of the probe, 53 inside 50 nested calls). Exact.

### Recommended wording

"Retained alternatives: entries in the program's <stack / queue / frontier
of …> (count at <point>; peak recorded by harness code)." "Suspended
generators: generator frames not finished, `gc.get_objects()` after
`gc.collect()`, at <point>." "Live allocator blocks (`sys.getallocatedblocks()`
difference from stage start)." Never "objects" for `gc.get_objects()`.

## 5. Recursion

### Probe (p5_recursion.py)

Each case runs in a child process so that a crash is observed. `range` and
`sum` are the recursive transcriptions of P13 over cons cells; `eq` and
`repr` apply `==` and `repr` to a cons list of length n (recursion inside
C); `viaC` is a Python recursion whose every level passes through a C call
(`list(map(f, …))`).

At the default limit (1000), every case failed with `RecursionError` at
n = 10⁴ and 10⁵, on every version. With `sys.setrecursionlimit(10**7)`:

| version | range, sum: 10⁴, 10⁵ (range also 10⁶) | eq / repr: largest n | viaC: largest n | beyond those |
|---|---|---|---|---|
| 3.10.15 | **crash, signal 11** at 10⁴ | 10⁴ ok, 10⁵ crash | crash at 10⁴ | segmentation fault |
| 3.11.10 | ok | 10⁴ ok, 10⁵ crash | crash at 10⁴ | segmentation fault |
| 3.12.2 | ok | 1,497 / 1,496 | 749 | `RecursionError` |
| 3.12.11 | ok | 9,997 / 9,996 | 4,999 | `RecursionError` |
| 3.13.7 | ok | 9,998 / 9,997 | 4,999 | `RecursionError` |
| 3.14.6 | ok | 47,540 / 80,453 | 7,366 | `RecursionError: Stack overflow (used 16352 kB)` |

(Largest n found by bisection in one child. At the default limit the
bisection gave 997 / 996 for eq / repr and 996 or 997 for viaC on every
version except 3.12.2, which gave 1,497 / 1,496 / 749 at both limits.)

Points to note:

- From 3.11, a Python-to-Python call does not use the C stack, so a pure
  Python recursion of depth 10⁶ works once the limit is raised. Its frames
  are on the heap and count towards traced memory.
- Recursion that passes through C is limited separately. In 3.12 and 3.13
  this is a fixed C recursion limit, which **changed between 3.12.2 and
  3.12.11** (about 1,500 to about 10,000 C levels). In 3.14 it is a check on
  the remaining C stack, so the depth depends on the frame sizes of the C
  functions involved (eq and repr differ) and on the thread's stack size,
  which differs between the main thread and others and between platforms.
- On 3.10 and 3.11 a raised limit lets deep recursion overflow the C stack
  and kill the process.
- The harness must not use `==`, `repr`, `print` or `copy.deepcopy` on a
  nested answer such as a cons list of length 10⁴; on 3.12 and 3.13 these
  raise `RecursionError` whatever the limit. Comparison and printing of
  answers must be iterative.
- Building a 10⁶-deep cons list and exiting, which frees it, did not crash
  on 3.11 to 3.14 (the deallocator of nested containers avoids deep C
  recursion). On 3.10 the build itself crashed.

### Classification

A `RecursionError` is an *error* in the classes of `SPECIFICATION.md`,
recorded verbatim. It is not *budget*: it is a limit on the depth of the
Python stack, not on steps, and it is raised whether or not the budget has
been spent. A segmentation fault is also *error*, recorded with the signal.

The recursion limit is a flag of the configuration and must be fixed
before the freeze, not raised for one problem (that would be an
intervention, or a control declaration tailored to one stage). Two choices
are coherent:

- keep the default (1000): P13a to P13d by the recursive definitions then
  end in *error* at n = 10⁴, which is a finding about the configuration;
- fix one large limit for every problem (for example 10⁷) in the pinned
  3.13 configuration, where pure Python recursion to 10⁶ then works and C
  recursion still stops with `RecursionError` rather than a crash.

Either way the limit is listed under the configuration's flags.
Reformulating a definition into a loop to avoid the limit is R.

## 6. A budget in Python's own unit

### Probe (p6_budget.py)

`run_with_budget(fn, B)` counts INSTRUCTION events and raises
`BudgetExhausted` (a `BaseException` subclass) from the callback at
instruction B + 1. On 3.12.2:

```
[stop]
  endless, budget 10:      ('budget', None, 10)
  endless, budget 1000000: ('budget', None, 1000000)
  finite(100), budget 708: ('budget', None, 708)
  finite(100), budget 709: ('finished', 4950, 709)
[catch]
  except Exception: ('budget', None, 1000)
  bare except     : ('finished', 'caught by bare except', 1001)
  finally         : ('budget', None, 1000) cleanup ran: True
  sticky, except Exception: ('budget', None, 1000)
  sticky, bare except     : ('budget', None, 1000)
  sticky, finally         : ('budget', None, 1000) cleanup ran: False
[pause] finite(1000) pausing at 2000, 4000 and 6000 instructions, then unlimited
   ('paused at', 2000) ('paused at', 4000) ('paused at', 6000)
   ('finished', 499500, 'instructions', 7009)
  finite(1000) under meter.count_mon: (499500, 7009)
[C loop] budget 1000 around any(itertools.repeat(0)), 5 s timeout
  not stopped by the budget; killed by the 5 s timeout
[cost] finite(10**6)
  plain 0.022s  under budget meter 0.652s  ratio 29.3
```

The same behaviour was seen on 3.12.11, 3.13.7 and 3.14.6 (with 609 and 610
instructions for `finite(100)` on 3.13.7 and 3.14.6).

- **Exact.** An exception raised in an INSTRUCTION callback propagates
  into the monitored code before the instruction runs. A computation
  needing exactly 709 instructions finishes with a budget of 709 and stops
  with 708.
- **The program can catch it.** `except Exception` does not, because the
  exception derives from `BaseException`. A bare `except:` (or `except
  BaseException`) does. If the meter switches itself off as it raises, the
  program then runs on unmetered (`finished`, 1001). The remedy is a
  *sticky* budget: once exhausted, every further instruction raises again,
  so no handler or `finally` block can run a single instruction. The cost
  is that the program's `finally` clean-up does not run either; a harness
  that needs it to run must allow it explicitly and count it.
- **Stopping destroys the computation.** The exception unwinds the
  frames; a generator it passes through is finished. A computation stopped
  this way cannot be continued, so after *budget* the next stage is posed
  by reposing, under restart cost.
- **Continuation is possible with a thread.** If the callback blocks
  instead of raising, the computation's thread waits at exactly the budget
  while the harness observes, grants a new budget, and releases it. The
  count across three pauses (7,009) equalled the uninterrupted count. This
  meets `PROTOCOL.md`'s "after budget" rule (the same computation, with a
  new budget), at the price of running the computation in a thread: the
  harness uses `threading`, which must be declared in the harness, and the
  callback must ignore other threads' instructions and the thread's own
  start-up code, as the probe does.
- **C code is outside the budget.** An endless loop inside one C call
  (`any(itertools.repeat(0))`) executes no Python instruction, so no event
  ever fires. Signal handlers in Python also run only between instructions.
  Only an external limit stops it: the 60-second safety limit must kill
  the process from outside (a parent process or `subprocess` timeout),
  and the stage is classified *timeout*.
- **Cost.** The same as counting: 16 to 29 times slower than the plain run.
  For P13's budget of 10⁸ steps that is up to 10⁸ callbacks, about 4 to
  7 s on this machine at the observed rate of 14 to 27 million callbacks
  per second (3.12.2 and 3.13.7); within P13's 600 s limit, but a cost to
  plan for.

### Recommended wording

"Budget: 10⁶ Python instructions (`sys.monitoring` INSTRUCTION, sticky),
per stage. Stops after exactly the budget; work inside built-in functions
is not counted, and a computation that loops inside one built-in is stopped
only by the safety limit." If the pausing harness is used: "continued after
budget in the same computation (thread paused at the budget)".

## Recommendations for the study

### Unit of step

**One CPython bytecode instruction executed in Python code**, counted by
`sys.monitoring` INSTRUCTION events (global, the meter's own frame
excluded), on the pinned version including its patch release. Do not use
`settrace`. Fix `PYTHONHASHSEED=0` and record it. Record whether the
program iterates over identity-hashed sets or dicts, or uses threads, since
either makes the count vary between runs. State in every table that the
count excludes work inside built-ins, and that it is not comparable between
a program that uses a built-in and one that does not, so P13e and P13f are
reported with the built-ins they use rather than as a cost.

### Unit of store

Report separately:

1. **Traced memory**, current at the stage boundary and true peak during
   the stage (`tracemalloc`, 1 frame, started before the stage, peak reset
   at the stage start), in bytes. Not a sampled maximum. Excludes allocator
   overhead and memory outside Python's allocators.
2. **Live allocator blocks** at the boundary, as a difference from the
   stage start (`sys.getallocatedblocks()`), as a count.
3. **Process maximum resident set size** (`ru_maxrss`), only if a
   whole-process figure is wanted, from a separate run with tracemalloc
   off, one process per stage, unit stated.

These are bytes and blocks of CPython's object representation and compare
only within Python.

### Unit of alternative

None native. **An entry in the program's own structure of pending
alternatives**, named in each program (a stack of partial solutions, a list
of generators, a frontier), counted with `len()` at stage boundaries and
answers, with a peak only if harness code records it. Where alternatives
are held as suspended generators, the count of suspended generator frames
(`gc.get_objects()` after `gc.collect()`) at the same points. As with
SWI-Prolog's choicepoints, these counts get their own row and are not
equated with another system's alternatives.

### Algorithmic-operation count

**Applications of each relation the problem defines**, counted as calls of
the transcribing function by `sys.monitoring` PY_START events enabled
locally on that function's code object, with no change to the program
text. For P13a to P13d this is the comparable figure across systems, with
the closed forms of section 2 as the expected values, provided every system
transcribes each relation as a definition of its own and states how its
count maps to "one application". Report it beside the instruction count.

### Fixed run conditions

`python3 -B -s` (and `-E` if no environment variable is needed),
`PYTHONHASHSEED=0`, the recursion limit fixed for the configuration and
recorded, tracemalloc started before the stage when store is measured, one
process per measured stage when `ru_maxrss` is reported, the safety limit
enforced from outside the process, answers compared and printed
iteratively.

## Not verified

- **The `python:3.13` container, and Linux.** Docker was not available.
  The 3.13 figures are from 3.13.7 built by python-build-standalone on
  macOS arm64. Instruction counts are produced by the compiler and the
  interpreter, so the same counts are expected from the same patch release
  on Linux. That is reasoned, not tested. Not expected to carry over: the
  C-stack depths of 3.14 (stack size differs), `ru_maxrss` values and unit
  (KiB on Linux is documented, not checked), absolute allocator block
  counts, and timings.
- **The patch release to be pinned.** Only 3.13.7 was run from the 3.13
  line. The C recursion limit changed between 3.12.2 and 3.12.11, so a
  similar change within 3.13 cannot be ruled out.
- **The cause of the `settrace` failures** on 3.12+ was not found. The
  observed pattern is reported; the C source and the CPython issue tracker
  were not read.
- **Whether INSTRUCTION events miss any instruction.** The count agreed
  with `settrace` on 3.12 where both worked, and with the closed forms of
  the loops, but was not checked against an independent count of
  instructions such as a build with `LLTRACE`.
- **Free-threaded builds** (3.13t, 3.14t) were not run. Monitoring and
  tracemalloc behave differently there.
- **pymalloc overhead and fragmentation** were not measured: tracemalloc
  reports requested sizes, `ru_maxrss` the whole process, and nothing in
  between was looked at (`sys._debugmallocstats()` was not tried).
- **C-extension allocations other than `mmap`.** Only `mmap` was shown to
  be invisible to tracemalloc. Which standard-library modules allocate
  through `malloc` directly was not surveyed.
- **Counting comparisons or other operations inside built-ins** (by
  instrumented values with counting `__lt__` and `__eq__`) was not probed.
- **`asyncio`** (configuration *stdlib-concurrency*): how instruction
  counts, budgets and retained tasks behave under an event loop was not
  probed. Threads were looked at only as far as section 1 and the pausing
  budget.
- **CPU-time reproducibility** was not studied. Timings are as measured,
  and varied by about 10% between runs.

## Reproducing on Linux

The workflow `.github/workflows/python-measurement.yml` runs `probes/run.sh`
in the `python:3.13.7` image on ubuntu-latest, and shows the difference
from the macOS run of the same release.

### First Linux result

Run 45916373754, 27 November 2026, CPython 3.13.7 on Linux x86_64,
compared with 3.13.7 on macOS arm64. 219 lines were produced. The figures
the study relies on were identical:

- instruction counts (for example, 6,000,009 for the loop of P1);
- every problem-operation count, by all four methods (500,500 for conc
  at n = 1,000);
- traced Python peaks (40,449,336 bytes);
- the recursion depths.

What differed:

- times, as expected;
- `ru_maxrss`, which Linux reports in KiB, as documented, where macOS
  reports bytes;
- the order of iteration over sets of objects hashed by identity, which
  P1c had already shown to vary between runs, and over sets of strings
  under a random hash seed;
- counts of objects tracked by the collector, which differ by a few dozen
  between builds.

So the step unit, problem operations and traced memory are portable
between these platforms for the pinned release. Resident-set figures are
compared within a platform only, and identity-hashed iteration is kept out
of anything counted.
