# ALGOL 60

The historical imperative baseline: a mainstream programming model of the
same period as Absys, with structured control, recursion, procedures, call
by name and mutable variables.

The system is the reconstruction at https://github.com/chrishayuk/algol-60
(the `algol60` interpreter, built from the *Revised Report*, 1962),
provisionally pinned at commit `6e8740c`. The commit is fixed at the
freeze. That repository is not changed for this study; a change it needed
would make a new configuration.

## Configurations

| configuration | what it is | class |
|---|---|---|
| **report** | the Revised Report, as the interpreter implements it | reconstructed |
| **x1** | `--x1`: the Dijkstra–Zonneveld system for the Electrologica X1, as its documents describe it | reconstructed |
| **x1sim** | the surviving 1964 X1 compiler, in a C translation, on a simulator of the X1. The run-time routines it calls do not survive, and are a separate reconstruction | rehosted (compiler), reconstructed (run-time) |

The Report defines no input or output. The interpreter's `ininteger`,
`outinteger` and related procedures are from the IFIP proposals of 1964,
and are listed under external mechanisms for *report*.

ALGOL 60 has no unknowns, no relations and no alternatives of its own. As
with Python, a program uses the algorithm natural to the language, and
records its departures from the problem's definitions as reformulation.
Some problems may be *not expressible* without supporting code. That is a
result.

## The core

The Revised Report: its statements, declarations, procedures with value
and name parameters, arrays, own variables, switches and labels, and its
standard functions `abs`, `sign`, `sqrt`, `sin`, `cos`, `arctan`, `ln`,
`exp` and `entier` (3.2.4–3.2.5). The input and output procedures are
IFIP's (1964), and are external mechanisms in *report*.

## Values

ALGOL 60 has integers, reals and Booleans, and arrays of them. Atoms are
encoded as integer codes, fixed per problem, and sequences as an integer
array with a length, or as parallel arrays of heads and tail indices for a
sequence that is built up. These encodings are part of transcribing a
problem, and count as P. Stages are read from input as integers in the
same encoding.

## Units

- **Step:** the interpreter's own `tick`, as `--max-steps` counts it
  (`src/interp.rs`, at `6e8740c`). One step is any one of:
  - the execution of one compiled statement: an assignment, a procedure
    statement, a `go to`, the test of a conditional statement, the jump past
    its `else` branch, the entry of a block, or a `for` statement;
  - one test of a `step … until` or `while` element, once for every time
    round and once more for the test that ends it;
  - one activation of a declared procedure, by a procedure statement or a
    function designator, and one more where its body is a single block.

  Nothing else is a step: evaluating an expression (its operators, its
  subscripts, the standard functions, a name parameter), a call of an
  input or output procedure, a compound statement without declarations, a
  dummy statement, and the elements of a `for` list that are plain
  expressions. So `i := 1; i := 2` in a block is 3 steps; a procedure
  statement whose body is one assignment is 3 (the statement, the
  activation, the assignment); `for i := 1 step 1 until 3 do ;` is 5 (the
  statement and four tests); `for i := 1, 2, 3 do ;` is 1. Each of these
  was checked against `--max-steps` on ten small programs. Work done
  inside expressions, which call by name can make large, is therefore not
  in the step count. It is measured by `name_evaluations` (below).
- **Store:** a vector, from `--measure` on the instrumented commit
  `151cdff` (branch `measure`). Each quantity has its value at the end of
  the run and its peak, updated as objects are made and dropped, so the
  peak is exact:

  | quantity | what it counts |
  |---|---|
  | frames | activation records alive, including those kept by procedures and name parameters |
  | slots | variables in the live activation records |
  | arrays | arrays alive |
  | array_elements | elements of the live arrays |
  | names | name parameters alive, each an expression with its environment |
  | call_depth | procedure calls in progress |
  | frames_made, calls, name_uses, name_evaluations | totals over the run |
  | name_first_evaluations, name_repeat_evaluations | evaluations of an actual parameter for the first time, and again, for the same parameter of the same call |

  Temporary values are not measured: the tree-walking interpreter holds
  them on its own call stack, which cannot be counted without changing how
  it runs. call_depth is the nearest measure.

  The instrumented commit's stdout, stderr and exit code were identical to
  the baseline's on all 100 programs in the repository, in both dialects,
  with measurement on and off (200 runs, checked for `2589d00` and again
  for `151cdff`). That is observational equivalence over that corpus.
- **Repeated work:** `name_repeat_evaluations`. Call by name evaluates an
  actual parameter again at every use, and each actual parameter keeps its
  own count, so a repeat is told apart from a first evaluation. Jensen's
  device makes 8 procedure calls and 392 name evaluations: 16 first, 376
  repeats. A repeat is not always wasted work. Jensen's device relies on
  it, since the parameter's value changes between evaluations.
- **Alternative:** as Python: whatever structure the program keeps, named.
- **x1sim: behaviour only.** The simulator (Vakulenko's, commit
  `938fa03`) counts the X1 instructions it executes, but it reports the
  count only in a progress message every five seconds, not at the end of a
  run, so reading it would mean changing the simulator. And the count would
  not measure the X1's work. The run-time routines that the object code
  calls (procedure entry, `for` statements, real arithmetic, input and
  output) do not survive, and the simulator carries them out as 105
  operations written in C++, each counted as one instruction however much
  it does. x1sim is therefore run in behaviour mode only, for its
  outcomes. No step, store or cost figure is taken from it.

## The same computation

A program may read each stage with `ininteger` or `insymbol` as it
arrives, which counts as the same computation. Otherwise each stage is
posed by rerunning with stages 1 to k.
