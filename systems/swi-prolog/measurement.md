# SWI-Prolog 11.0.1: what can be measured, and how to word it

This is a measurement-qualification note, not a benchmark. Every figure
below comes from a small probe run locally on SWI-Prolog 11.0.1 for
arm64-darwin (Homebrew build, `swipl --version` prints `SWI-Prolog version
11.0.1 for arm64-darwin`). The CI image `swipl:11.0.1` (Linux) was not
available locally, so nothing here has been checked on Linux. The probe
files are in the session scratchpad
(a scratch folder, not kept);
the code needed to reproduce each result is quoted in this note.

All probes were run as `swipl -q -g Goal -t halt file.pl </dev/null`. The
options must come before the file name: arguments after the file name are
passed to the program as `argv`, and the system then starts the interactive
toplevel. No user init file was present (`user_app_config('init.pl')` does
not exist), so none was loaded.

## Summary

| measurement | how | exact / sampled / unavailable | perturbation |
|---|---|---|---|
| open choicepoints at a point the program chooses (answer, stage boundary) | `prolog_current_choice/1`, then walk `prolog_choice_attribute(C, parent, P)` down to a mark taken at stage start | exact count of choicepoint frames at that point | about 3 inferences per frame walked, plus 5; no choicepoint added if the counter is written as below |
| open choicepoints inside a running goal | the same walk, called from `prolog:heartbeat/0` (flag `heartbeat` = N) | sampled; blind to some purely deterministic code | about 45 to 55 inferences per sample, counted in `inferences`; sample positions depend on the absolute inference counter |
| global, local, trail bytes in use at a point | `statistics(globalused / localused / trailused, B)` | exact at that point; `globalused` includes uncollected garbage unless `garbage_collect/0` runs first | 1 inference per call; 8 bytes of global stack per call |
| live global data at a stage boundary | `garbage_collect/0`, then `statistics(globalused, B)` | exact and independent of the earlier GC schedule | 3 inferences; changes the timing of later GCs |
| peak (high-water mark) of any Prolog stack | none: no `max_*` key, `prolog_stack_property/2` reports only limits and policy | unavailable; only a sampled maximum can be had (heartbeat), or an allocation bound (`global`, `local`, `trail` keys) | sampling as above |
| table storage | `statistics(table_space_used, B)`; `current_table/2` with `trie_property(T, value_count(N))` and `size(B)`; `table_statistics/2` (library(tableutil)) | exact at that point; does not shrink while tables are kept, so the value at a boundary is the maximum so far | the listing calls cost inferences of their own |
| attributed variables reachable from a term | `term_attvars/2` | exact, but counts solver-internal attributed variables too | 3 inferences, cost linear in the term |
| attributed variables created by a goal, reachable or not | `call_residue_vars/2` around the goal | exact | about 9 to 12 inferences in the probes |
| residual constraints | `copy_term/3` (length of goal list) | exact count of projected goals, which is not a count of suspended goals or propagators | 46 to 10,040 inferences in the probes, growing with the store |
| inferences | `statistics(inferences, I)` before and after | exact and deterministic for a fixed build, flags and load state | 1 inference per `statistics/2` call; the toplevel adds 587 between queries |
| inference limit | `call_with_inference_limit/3` | exact; agrees with the `statistics/2` difference minus 1 | none if libraries are loaded beforehand (see 5.4) |
| process CPU time | `statistics(process_cputime, T)`, `statistics(cputime, T)`, `call_time/2` | measured; not reproducible to the digit | negligible |
| process peak memory | `/usr/bin/time -l` (macOS) or GNU `time -v` (Linux): maximum resident set size | true peak, but of the whole process (stacks, heap, code, tables) | none inside Prolog |
| `statistics(memory, _)` | getrusage `ru_idrss` | unavailable on macOS: returns `[0,-1]` | none |

## 1. Choicepoints

### Predicates

- `prolog_current_choice(-C)`: an integer reference to the newest
  choicepoint of the current environment.
- `prolog_choice_attribute(+C, Key, -V)` with `Key` one of `parent`, `type`,
  `frame`, `pc`, `clause`. `type` is one of `clause` (the goal has
  alternative clauses), `foreign` (a nondeterministic foreign predicate such
  as `between/3`), `jump` (a choice inside a clause: disjunction,
  if-then-else), `top`, `catch`, `debug`, `none`.
- There is no `statistics/2` key for choicepoints.
- Related: `deterministic/1`; the `Result` of `call_with_inference_limit/3`
  (`!` = no choicepoint left, `true` = choicepoint left).

### Counting relative to a mark

The walk must start from a mark. Under `-g` there are already four harness
choicepoints (`top`, `catch`, `jump` in `'$toplevel':run_init_goal/2`,
`catch`) before the program runs (cp1.pl):

```
baseline: 4 [catch-(system:catch/3),jump-('$toplevel':run_init_goal/2),catch-(system:catch/3),top-(system:'$c_call_prolog'/0)]
```

A counter with a mark (cpcount.pl):

```prolog
cp_mark(M) :- prolog_current_choice(M).
cp_since(M, N) :- prolog_current_choice(C), cnt(C, M, 0, N).
cnt(C, M, N0, N) :- C =< M, !, N = N0.
cnt(C, M, N0, N) :- N1 is N0+1,
    ( prolog_choice_attribute(C, parent, P) -> cnt(P, M, N1, N) ; N = N1 ).
```

`prolog_current_choice/1` must be the first goal of a single-clause
predicate. A first version read it inside `( prolog_current_choice(C) -> ...
; ... )`: it returned the if-then-else's own choicepoint, which the `->`
then removed, and the walk failed with `choice '198' does not exist`. The
stop test `C =< M` relies on newer choicepoints having larger references.
That held in every walk observed (for example 159 > 128 > 77 > 48, newest
first), but the manual does not state it.

### What a choicepoint is

One choicepoint is one record on the local stack. It says that one call
still has untried alternatives: further clauses (`clause`), further
solutions of a foreign predicate (`foreign`), or an untaken branch of a
disjunction inside a clause (`jump`). It is not one alternative solution,
and it is not a count of untried clauses. From cp3.pl, the open choicepoints
after the first answer, and the number of solutions the goal has in all:

```
r(5)  [cp left, yields nothing more]: open_cps_at_first_answer=1 types=[clause] total_solutions=1
between(1,1000000,X) [one cp, 999999 more]: open_cps_at_first_answer=1 types=[foreign] total_solutions=1000000
c(a,Y) [first-arg index]: open_cps_at_first_answer=1 types=[clause] total_solutions=2
c(b,Y): open_cps_at_first_answer=0 types=[] total_solutions=1
d(X,y) [2nd-arg JIT index]: open_cps_at_first_answer=1 types=[clause] total_solutions=1
d(X,x): open_cps_at_first_answer=1 types=[clause] total_solutions=2
member(X,[1,2,3]): open_cps_at_first_answer=1 types=[clause] total_solutions=3
nth1(I,[a,b,c],b) [library pred, internal cps]: open_cps_at_first_answer=1 types=[clause] total_solutions=1
```

So one choicepoint may stand for no further solutions (`r(5)`, `d(X,y)`,
`nth1/3`) or for 999,999 of them (`between/3`). For `p(1). p(2). p(3).` at
`p(1)` there is one choicepoint, although two clauses remain. When the last
clause is tried the choicepoint is gone (`p(3)`, the last element of
`member/2`):

```
p(1): 6 [clause-p/1, jump-t1/0, ...harness 4]
p(3): 5 [jump-t1/0, ...harness 4]
```

The count depends on clause indexing (first-argument indexing removed the
choicepoint for `c(b,Y)` but not for `c(a,Y)`), on how library predicates
are written (`member/2` is deterministic on its last element; `nth1/3`
leaves one), and on the control constructs of the caller (`;` adds a `jump`
choicepoint). Within one build and set of flags it is a well-defined
property of the execution. It is not a property of the problem.

### Counting at answers and inside a running goal

At each answer of `gen(4, L)` (four nested calls to `p/1`, 81 answers,
cp2.pl), measured inside `findall/3`, which itself adds 2 choicepoints, so
the values run from 2 to 6:

```
answers=81 first=6-[1,1,1,1] last=2-[3,3,3,3]
histogram(cp->count)=[2-1,3-8,4-24,5-32,6-16]
types at first answer: [clause,clause,clause,clause]
```

Inside a running goal, the same walk called from `prolog:heartbeat/0` sees
the choicepoints of the interrupted computation. With `gen(9, _)` the
sampled maximum was 9, which is the true maximum for that program (samp.pl;
see section 2 for the sampler). The debugger hook
`prolog_trace_interception/4` can also be used, but it runs the program in
debug mode, which is a different execution: that run showed a maximum of 10
choicepoints, 24,948,314 inferences against 275,563 without the hook, and
0.88 s of CPU time. Inside the hook, `prolog_current_choice/1` returned a
context with 1 choicepoint; the walk had to start from the hook's third
argument.

### Cost and determinism

Cost of `cp_since/2` (cp2.pl), as the difference between two
`statistics(inferences, _)` readings around it:

```
depth=0 probe_inferences=5
depth=10 probe_inferences=35
depth=100 probe_inferences=305
depth=1000 probe_inferences=3005
```

In debug mode this is 4 per frame plus 6. The walk allocates 24 bytes of
global stack (pert.pl). Running the same probe twice gave byte-identical
output (md5 of the cp3.pl output was the same on both runs).

### Recommended wording

"Open choicepoints (SWI-Prolog choicepoint frames newer than the stage
mark), counted at <answers | stage boundaries>, by type. One choicepoint
records that one call has untried alternatives; it may yield no further
solutions or many." Inside a running stage: "sampled maximum of open
choicepoints (heartbeat every N inferences)".

## 2. Global, local and trail stacks

### Keys

Probed on 11.0.1 (a sweep over candidate keys):

- In use, bytes: `globalused`, `localused`, `trailused`.
- Allocated, bytes: `global`, `local`, `trail`. `stack` is the total
  memory for stacks in all threads and engines; it read 172,000 when the
  three allocated sizes summed to 145,216.
- Compatibility: `global_stack` = `[used, free]`, `local_stack` = `[used,
  free]`, `trail` (the compatibility form shares the name), `stacks`.
- Events: `garbage_collection` = `[count, bytes gained, time, bytes left
  summed]`, `global_shifts`, `local_shifts`, `trail_shifts`,
  `stack_shifts`, `shift_time`, `minor_collections`.
- Limit: `stack_limit` (combined, default 1,073,741,824).
- No peak key exists. `max_global`, `max_local`, `max_trail`, `globalmax`,
  `localmax`, `trailmax`, `globallimit`, `locallimit`, `traillimit`,
  `trail_stack` and `heap` all raise `domain_error(statistics_key, _)`.
  `prolog_stack_property/2` reports only `limit`, `spare`, `min_free`,
  `low` and `factor`, all of them policy settings.

### No true peak; what the allocated size means

The allocated size grows when a stack is expanded and shrinks only at
`trim_stacks/0` (which the toplevel runs after each query, and GC may run).
alloc.pl, a non-tail recursion to depth 1,000,000 followed by a 500,000
element list:

```
start:       local used/alloc=1672/20344     global=10704/77792       trail=592/47080       shifts=[0,0,0]
after_deep:  local used/alloc=1672/134205304 global=11112/77792       trail=592/47080       shifts=[0,12,14]
after_gc:    local used/alloc=1672/134205304 global=216/77792         trail=16/47080        shifts=[0,12,14]
after_trim:  local used/alloc=1672/20344     global=624/45024         trail=16/47080        shifts=[1,13,18]
after_list:  local used/alloc=1672/20344     global=11619592/33566688 trail=3873120/4208616 shifts=[3,13,21]
after_gc2:   local used/alloc=1600/20344     global=208/33566688      trail=0/8402920       shifts=[3,13,21]
```

After the recursion returned, the local stack still showed 134 MB
allocated against 1,672 bytes in use. The allocation is therefore evidence
that a large peak occurred, but it is rounded up by the growth policy, and
any trim after the peak discards it. It is not a peak and should not be
reported as one.

### `globalused` and GC

`globalused` counts all cells on the global stack, collected or not. The
figure at a given point therefore depends on when GC last ran. From stk.pl
(20,000 iterations that each build and discard a 50 element list, then a
100,000 element list that stays live), run twice in each mode:

```
gc flag=true
result=25500000 work_inferences=2280009 gcs_during=147
before_gc: global=2400552 local=1720 trail=0 gcs=148 inf=2333196
after_gc: global=2400200 local=1720 trail=0 gcs=149 inf=2333206
--- gc=false
result=25500000 work_inferences=2280009 gcs_during=0
before_gc: global=27464864 local=1720 trail=640 gcs=0 inf=2333205
after_gc: global=27465208 local=1720 trail=640 gcs=0 inf=2333215
```

and with GC disabled during the run and enabled for one collection at the
end:

```
off_before: global=27464088 ... gcs=0
on_after_gc: global=2400200 ... gcs=1
```

From these runs:

- GC does not change the inference count of the work (2,280,009 in both
  modes) or the result.
- With `gc=false`, `garbage_collect/0` does nothing. `globalused` then
  measures everything allocated since the last backtrack, 27.4 MB here
  against 2.4 MB live.
- After `garbage_collect/0`, `globalused` (2,400,200) was the same whatever
  the GC history. This is the reproducible figure for live global data.
- Each configuration gave identical figures, including the GC count, on
  both runs.

### Sampling inside a stage

The least intrusive in-process sampler found is the `heartbeat` flag. When
the flag is N > 0, `prolog:heartbeat/0` is called about every N inferences
(N is rounded to a multiple of 16). Behaviour observed:

1. **Blind spots.** hb1.pl and hb2.pl (hook = `flag(hb, N, N+1)`, N = 1000):

   ```
   loop: hb calls=0 inferences=100002          (tail recursion: is/2 and !)
   nontail: hb calls=0 inferences=100002
   backtrack: hb calls=200 inferences=201203
   loop_debug: hb calls=216 inferences=217641  (same loop in debug mode)
   foreign_det: hb calls=100 inferences=100602 (loop that also calls atom_length/2)
   prolog_backtrack: hb calls=39 inferences=39601
   det_with_open_cps: hb calls=200 inferences=201202
   ```

   A deterministic loop of pure Prolog calls with only VM-compiled builtins
   never fired the hook in 100,000 iterations. Code that backtracks, calls
   foreign predicates, or leaves choicepoints fired it about once per N
   inferences. The exact rule is in the C source, which was not read here.
   This is an observation for 11.0.1 on macOS, not a documented contract.
2. **Reentrancy.** A hook that stores its samples with `nb_setval/2` and
   restores the flag with `set_prolog_flag/2` inside the hook either
   recursed until the 1 GB stack limit or looped without end. A hook that
   keeps running maxima with `flag/3` and does not touch the `heartbeat`
   flag ran correctly, with a nesting depth of 1. With N = 16, which is less
   than the hook's own cost of about 50 inferences, the run did not finish
   in 60 s.
3. **Sample storage perturbs the store.** With samples held in an
   `nb_setval/2` list, the sampled maximum of `globalused` was 2,108,544
   bytes at N = 112, nearly all of it the sampler's own data. With running
   maxima in `flag/3`, which lives off the Prolog stacks, it was 44,520.
4. **Hook inferences are counted.** For `work` (275,563 inferences without
   the hook; samp.pl):

   ```
   hb(10000): inferences=277100 samples=28  max_cp=8 max_global=62872 max_local=4224 max_trail=768
   hb(1008):  inferences=291673 samples=290 max_cp=9 max_global=43400 max_local=4472 max_trail=184
   hb(112):   inferences=549826 samples=4909 max_cp=9 max_global=44520 max_local=4312 max_trail=288
   --- gc=false
   hb(10000): inferences=277103 samples=28  max_cp=8 max_global=63168 max_local=4224 max_trail=776
   hb(1008):  inferences=291661 samples=290 max_cp=9 max_global=119376 max_local=4472 max_trail=792
   hb(112):   inferences=549826 samples=4909 max_cp=9 max_global=120528 max_local=4312 max_trail=912
   ```

   The sampled maxima do not rise steadily with density: with GC on,
   `max_global` was 62,872 at N = 10,000 and 43,400 at N = 1,008. The
   sampler's work moves the GC points, and the sample points fall at
   different moments.
5. **Phase.** Running 0, 1, 7 or 300 extra inferences before the same
   sampled run (`phase(K)` in samp.pl) changed the outcome:

   ```
   hb(1008): inferences=291641 samples=289 max_cp=9 max_global=62840 max_local=4000 max_trail=776
   hb(1008): inferences=291647 samples=289 max_cp=9 max_global=62848 max_local=4000 max_trail=784
   hb(1008): inferences=291629 samples=289 max_cp=9 max_global=62848 max_local=4000 max_trail=840
   hb(1008): inferences=291686 samples=290 max_cp=9 max_global=62832 max_local=4000 max_trail=3200
   ```

   The sample points are tied to the absolute inference counter, not to the
   moment the flag is set. An identical program, load sequence and command
   line reproduces the figures exactly. Any change before the stage moves
   them.

The other candidates are worse. `alarm/4` (library(time)) samples on wall
time, so the sample points are not reproducible. `prolog_trace_interception/4`
needs debug mode, which turns off last-call optimisation and adds
choicepoints (local stack maximum 5,336 against about 4,472; choicepoint
maximum 10 against 9). No prolog_event_hook-style event for GC or stack
growth was found that reports usage: the predicate has no help entry, and
it was not probed further.

### Recommended wording

- At a point: "global / local / trail stack in use (bytes, `statistics/2`)
  at <answer | stage boundary>". For global, prefer "live global data after
  `garbage_collect/0`" and say which one is reported.
- Within a stage: "sampled maximum of <stack> in use, heartbeat every N
  inferences, GC <on | off>". Never "peak". Add that deterministic tail
  loops are not sampled, and that the sampler's own inferences are included
  in or removed from the step count (say which).
- Allocation: if reported at all, "allocated stack size (bytes); an upper
  envelope rounded by the growth policy, reset by `trim_stacks/0`".

## 3. Table storage

### Predicates and flags

- `statistics(table_space_used, B)`: bytes in this thread's answer tables.
  `shared_table_space_used` covers shared tables.
- Flags `table_space` and `shared_table_space` (default 1,073,741,824 each)
  are limits.
- `current_table(:Variant, -Trie)` enumerates tables, one per call variant;
  `trie_property(Trie, value_count(N))`, `size(B)`, `node_count(N)`.
- `table_statistics/2,3` and `tstat/2,3` from library(tableutil): keys
  `tables`, `answers`, `duplicate_ratio`, `space_ratio`, `complete_call`,
  `space`, `compiled_space`, `wait`, `deadlock`.
- `abolish_all_tables/0`.

### Probe (tab.pl: left-recursive `path/2` over 200 nodes, 400 edges)

```
before: table_space_used=0 tables=0 answers=0 sum_trie_size=0
path(1,_) answers=200 inferences=1851
after_path1: table_space_used=22360 tables=1 answers=200 sum_trie_size=22008
second call (completed table) inferences=404
path(_,_) answers=40000
after_path_open: table_space_used=2863488 tables=2 answers=40200 sum_trie_size=2862992
  table_statistics tables=2
  table_statistics answers=40200
  table_statistics duplicate_ratio=1.01
  table_statistics space_ratio=0.9949753743594846
  table_statistics complete_call=5
  table_statistics space=2862992
  table_statistics compiled_space=8080
  table_statistics wait=0
  table_statistics deadlock=0
after_abolish: table_space_used=456 tables=0 answers=0 sum_trie_size=0
```

Two runs gave identical output. Points to note:

- `path(1,_)` and `path(_,_)` are separate tables: tabling is by variant,
  so the 200 answers of the first appear again among the 40,000 of the
  second. Count tables and answers per variant, not per predicate.
- `table_space_used` is slightly larger than the sum of the answer tries
  (2,863,488 against 2,862,992). It does not return to 0 after
  `abolish_all_tables/0` (456).
- Reading a completed table costs inferences (404 for 200 answers), unlike
  evaluation, which cost 1,851 for the first call.
- Tables only grow until they are abolished, so the value at a stage
  boundary is the maximum so far for completed tables. Working storage used
  during evaluation outside the tries (worklists, stacks) is not in this
  figure. Whether it all goes to the ordinary stacks was not established.
- Exceeding the limit raises a resource error and discards the incomplete
  table (tablim.pl, `table_space` = 100,000):

  ```
  ERROR: [Thread main] '$tbl_reset'/6: Not enough resources: private_table_space
  after=424
  ```

  Bisecting the limit could bound a peak from above and below. That means
  many runs and was not tried.

### Recommended wording

"Answer-table storage (bytes, `statistics(table_space_used)`) at stage
boundary; tables and answers by `current_table/2` and
`trie_property/2`, by call variant." Exact. It is a high-water figure only
because tables are not freed during a stage.

## 4. Attributed variables and residual constraints

### Predicates

- `term_attvars(+T, -Vs)`: the attributed variables in `T` and, working
  recursively, in their attributes.
- `call_residue_vars(:G, -Vs)`: the attributed variables created during
  `G`, whether or not they can still be reached.
- `copy_term(+T, -C, -Gs)`: residual goals, obtained by projecting the
  attributes through each module's `attribute_goals//1`.
- `frozen(@T, -G)`: the goals suspended on `T`. In 11.0.1 it also reports
  goals from `dif/2` and clpfd.

### Probe (attv.pl; inference costs are the `statistics/2` difference minus 1)

```
none:    attvars=0 residual_goals=0 frozen_nontrivial=0 | inf: term_attvars=4 copy_term/3=7 frozen=218
freeze:  attvars=2 residual_goals=3 frozen_nontrivial=2 | inf: term_attvars=3 copy_term/3=46 frozen=99
   residual goals: [freeze(_A,user:writeln(x)),freeze(_A,user:true),freeze(_B,user:writeln(y))]
when:    attvars=1 residual_goals=1 frozen_nontrivial=1 | inf: term_attvars=3 copy_term/3=50 frozen=71
dif:     attvars=4 residual_goals=2 frozen_nontrivial=4 | inf: term_attvars=3 copy_term/3=95 frozen=463
   residual goals: [dif(_X,_Y),dif(_X,a)]
dif(f(X,Z),f(Y,b)), term f(X,Y):   attvars=4 residual_goals=1 | copy_term/3=2838 (first call: autoload)
dif(f(X,Z),f(Y,b)), term f(X,Y,Z): attvars=4 residual_goals=1 | copy_term/3=112
clpfd:   attvars=3 residual_goals=5 frozen_nontrivial=3 | inf: term_attvars=3 copy_term/3=195 frozen=662
   residual goals: [X in 4..9, X+Y#=Z, X#=<Y+ -1, Y in 5..10, Z in 9..19]
clpfd_200_alldiff: attvars=200 residual_goals=201 | inf: term_attvars=3 copy_term/3=10040 frozen=2249811
```

`call_residue_vars/2` (crv.pl), with a goal that leaves `freeze(_Lost,
true)` on a variable that cannot be reached once the goal returns:

```
hidden: plain inferences=71 term_attvars(X)=2
hidden: under call_residue_vars inferences=83 residue_vars=3
g200: plain inferences=21253, under crv=21262, residue_vars=200 term_attvars=200
```

Points to note:

- None of these counts is "number of constraints". `dif(X,Y), dif(X,a)` on
  the two variables of `f(X,Y)` gives 4 attributed variables, because
  `dif/2` attributes internal variables of its own. `freeze/2` twice on one
  variable gives 2 attributed variables and 3 residual goals. The clpfd
  goals `X #> 3, X #< Y, Y in 0..10, Z #= X+Y` give 5 residual goals, the
  first constraint having been absorbed into a domain. One `all_different/1`
  over 200 variables is a single residual goal. The number of clpfd
  propagators is not exposed by any public predicate.
- `term_attvars/2` is cheap (3 inferences of the caller's count, cost in C
  linear in the term) but misses attributed variables that cannot be
  reached from the term.
- `call_residue_vars/2` finds unreachable ones too. It must wrap the goal,
  so it has to be in place from the start of the stage. It cost 9 to 12
  inferences in these probes.
- `copy_term/3` runs Prolog code in each solver, at a cost that grows with
  the store (10,040 inferences for one 200-variable `all_different/1`). The
  first call includes autoloading.
- `frozen/2` is too expensive to call once per variable on a large store
  (2,249,811 inferences for 200 clpfd variables) and should not be used for
  counting.
- All of these are taken at points the program chooses. They can be called
  from the heartbeat hook, but `copy_term/3` there would add Prolog work to
  a sample.

### Recommended wording

"Attributed variables reachable from the answer (`term_attvars/2`),
including solver-internal ones" and "residual goals in the projected answer
(`copy_term/3`)". Under `call_residue_vars/2`: "attributed variables
created by the stage". Exact counts of those things, not of constraints or
suspended goals.

## 5. Inference counts

### Definition and agreement

The manual defines an inference as a pass through the call or redo port.
Built-ins compiled to VM instructions (`is/2`, `=/2`, comparison, `!`,
`true`) are not counted. A foreign predicate counts 1 however much work it
does (`sort/2`, `msort/2`).

inf.pl, run three times with identical output:

```
work: cold=291137 warm=275563,275563 | w2: cold=69213 warm=45758 | delta(true)=2
min call_with_inference_limit: work=275562 w2=45757
self_inferences=7335683 inferences=7335684
delta(garbage_collect)=3
optimise=false debug=false
```

`delta(G, D)` is `statistics(inferences, I0), call(G), statistics(inferences,
I1), D is I1-I0`. The smallest limit at which `call_with_inference_limit/3`
did not report `inference_limit_exceeded`, found by bisection, was exactly
`delta - 1` for both programs, so the two agree. `call_time/2`
(library(statistics)) reported `inferences:275560` for the same `work`,
having subtracted its own overhead. State which harness was used, because
the constant differs between them.

### What changes the count

- **Autoloading.** The first call of `work` cost 15,574 more inferences
  than later calls (`sum_list/2` being autoloaded), and the first `w2`
  23,455 more. Load the libraries explicitly and warm the code up, or count
  only on a fresh process with identical loading.
- **`-O` (optimise).** `work` took 255,880 with `-O` and 275,563 without.
  `w2` was unchanged (45,758). The flag must be fixed and reported.
- **Debug mode.** `work` took 324,769 in debug mode. The cost per frame of
  the choicepoint counter went from 3 to 4. Do not count in debug mode.
- **GC** does not change the count: 2,280,009 with `gc=true` and with
  `gc=false` (stk.pl). `garbage_collect/0` itself costs 3 in the `delta`
  harness.
- **The toplevel** adds 587 inferences between queries (two consecutive
  `statistics(inferences, _)` queries read 586,671 and 587,258). A
  difference taken inside one query is the same as under `-g` (275,563 in
  both).
- **Hooks.** Heartbeat hooks are counted (section 2).
- **Engines** have their own counter. A goal run in an engine counted
  100,009 - 7 inside the engine, while the caller's count rose by 7 across
  `engine_next/2` and by 10 including `engine_destroy/1` (eng2.pl). For the
  *session* configuration the count has to be read inside the engine.
  `statistics(globalused)` is per engine too: 2,400,200 inside, 18,952
  outside, with `stack` covering both (eng.pl).
- `inferences` includes joined child threads; `self_inferences` does not.
  They differed by 1 here.

### Two hazards of `call_with_inference_limit/3`

- If the limit is reached while a library is being autoloaded, the load is
  abandoned and the predicate stays undefined. A second call then raised
  `Unknown procedure: sum_list/2`. Load libraries before any limited call.
- In debug mode, with the limit reached during autoloading, the system
  printed `foreign predicate system:=/2 did not clear exception:
  inference_limit_exceeded` and returned `Result = !` for a goal that had
  not finished. Warm and outside debug mode it behaved correctly.

### Determinism across runs and platforms

With the same program, flags, load sequence and harness, the count was the
same on every repeated run on macOS arm64 (3 runs of inf.pl; 2 of stk.pl,
samp.pl and tab.pl). The count is produced by the virtual machine and does
not depend on GC or timing, so the same count is expected on Linux x86_64 or
arm64 with the same 11.0.1 sources, flags and libraries. That has not been
checked. Things that could make it differ: a different set of libraries or
packs autoloaded, a different `optimise` default, an init file in the
container, and library code that branches on the platform.

### Recommended wording

"Inferences (SWI-Prolog call and redo ports; VM-inlined built-ins
excluded), difference of `statistics(inferences)` within the stage,
libraries preloaded, `optimise=false`, not in debug mode." Exact.

## 6. Peaks and process resources

- No in-process true peak exists for the Prolog stacks (section 2) or for
  choicepoints (section 1). Table space has no peak key, but in practice it
  does not shrink during a stage.
- `statistics/0` prints the same in-use and allocated figures (Limit /
  Allocated / In use) and no maximum:

  ```
  % Local  stack:           -       20 Kb    2,000  b
  % Global stack:           -       76 Kb       42 Kb
  % Trail  stack:           -       46 Kb       72  b
  %        Total:    1,024 Mb      142 Kb       44 Kb
  ```

- `statistics(memory, M)` and `core` return `[0,-1]` on macOS: getrusage
  `ru_idrss` is not maintained there.
- The OS gives a true peak for the whole process. `/usr/bin/time -l` on
  macOS reported a maximum resident set size of 155,238,400, then
  155,189,248 twice, for a 2,000,000 element `numlist/3` and `msort/2`
  (ct.pl); `swipl -g true` alone showed 11,272,192. This covers the stacks,
  atom and clause heap, tables, and the C runtime together. On Linux, GNU
  `time -v` ("Maximum resident set size") or `/proc/self/status` `VmHWM`
  give the same kind of figure; neither was tried here.
- CPU time: `cputime` (this thread plus joined children), `self_cputime`,
  `process_cputime`; `call_time/2,3` returns `time{cpu, inferences, wall}`.
  These are measured values that vary from run to run. Report them as
  timings, not as steps.
- GC and measurement: GC does not change the result or the inference count.
  It does change `globalused` at any moment, the allocated sizes, and where
  the heartbeat samples fall. Recommendations:
  - Leave `gc=true` for the run itself. With `gc=false` the stacks hold
    every byte allocated since the last backtrack, which can exhaust the
    1 GB limit on runs that would otherwise succeed, and the store measured
    is no longer what the program needs.
  - At stage boundaries and answers, call `garbage_collect/0` before
    reading `globalused`, and report that figure as live data. It was
    identical whatever the GC history (2,400,200 in both histories
    tried: GC on throughout, and GC off until the boundary).
  - If an in-stage sampled maximum is reported, give N and the GC setting.
    `gc=false` makes the sampled figure an allocation figure (allocated
    since the last backtrack), which is easier to reproduce than a figure
    taken at moments set by the GC schedule. That is a different
    measurement and needs a different label.

## Recommendations for the cross-system study

### Unit of "alternative"

For SWI-Prolog the unit is **one open choicepoint frame**, counted by
walking `prolog_choice_attribute/3` from `prolog_current_choice/1` down to a
mark taken at the start of the stage, so that the harness's own frames are
excluded. Report it by type (`clause`, `foreign`, `jump`, `catch`, `debug`),
at answers and stage boundaries, with the in-stage figure labelled a sampled
maximum.

It must not be equated with one derivation, one pending branch, or one
alternative of another system. A choicepoint can yield no further solutions
or a million of them. Indexing, library code and the caller's control
constructs add or remove choicepoints without changing the search. A
choicepoint also does not stand for one untried clause. In a cross-system
table, give SWI-Prolog's figure its own row with this unit named ("retained
choicepoints"). If the study needs a comparable count of alternatives, take
it from a quantity defined by the problem (answers produced, or the nodes of
a search tree that is defined in the problem file and counted by each
implementation's own code), not from choicepoints.

### Unit of "store"

For SWI-Prolog, report these as separate figures:

1. **Live global data at the observation point**: `garbage_collect/0`, then
   `statistics(globalused)`, in bytes. Exact and reproducible.
2. **Local and trail in use** at the same point: `localused`, `trailused`,
   in bytes. Exact at the point. The local stack includes choicepoint and
   environment frames, so it partly overlaps the choicepoint count.
3. **Answer-table storage** (configuration *tabling*): `table_space_used`,
   with tables and answers by variant.
4. **Constraint store** (configurations *coroutines* and *constraints*):
   attributed variables (`term_attvars/2` on the answer, or
   `call_residue_vars/2` over the stage) and residual goals (`copy_term/3`).
   These are counts, not bytes. Their bytes are inside figure 1.
5. **Within-stage maxima**, if reported: "sampled maximum, heartbeat every
   N inferences, GC on", with the blind spot and phase caveats. A
   whole-process true peak, if needed, comes from the OS (maximum resident
   set size) and is labelled as such.

Store figures are 64-bit cell bytes of SWI-Prolog's own term
representation. They compare across SWI-Prolog configurations, but not
directly with another system's bytes or cells.

### Fixed run conditions

`swipl` options before the file; `-q`; no init file (or `-f none` in CI);
libraries loaded explicitly before measuring; `optimise=false` (the
default) recorded; never in debug mode; `gc=true`; one fresh process per
measured stage, or an identical load sequence, so that the autoload state
and the heartbeat phase are the same.

## Not verified

- **Linux / the `swipl:11.0.1` image.** Docker was not available locally.
  None of these results has been checked on Linux, on x86_64, or in the
  container: inference counts, stack bytes, GC counts, heartbeat behaviour,
  table bytes, the `memory` key, or the two `call_with_inference_limit/3`
  hazards. The equal-count expectation in 5 is reasoned, not tested.
- **The heartbeat rule.** Which code paths check the heartbeat counter was
  observed, not read from the C source. The behaviour may differ between
  builds.
- **The ordering of choice references.** The rule that a newer choicepoint
  has a larger reference was observed in every walk but is not documented.
- **True peaks.** No method was found for an exact in-stage peak of any
  stack or of the choicepoint count, so none was compared against the
  sampled maxima. Only the 9-choicepoint maximum of `gen(9, _)` is known
  exactly, from the structure of the program.
- **Tabling working storage** during evaluation (outside the answer tries),
  shared tables, incremental tabling and well-founded semantics (delay
  lists) were not probed.
- **clpfd internals.** No public predicate exposes the number of
  propagators. `clpq` was not probed.
- **Event hooks.** `prolog_event_hook/1` has no help entry in 11.0.1, and
  no hook reporting GC or stack-growth events with usage figures was found.
  Using the `trace_gc` flag (messages at each GC) as a sampling point was
  not tried.
- **Multi-threaded runs.** Only `inferences` against `self_inferences` and
  one engine were looked at.
- **CPU-time reproducibility** was not studied. Timings are reported as
  measured.
