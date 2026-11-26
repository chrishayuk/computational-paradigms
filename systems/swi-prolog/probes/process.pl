% Section 6: process-level figures.  CPU and wall time are not printed:
% they vary from run to run and have no stable expected value.
:- use_module(common).
main :- statistics(memory, M), out(d, statistics_memory, M),
   statistics(core, C), out(d, statistics_core, C),
   forall(member(K, [cputime, self_cputime, process_cputime]),
          ( statistics(K, V), ( number(V) -> R = number ; R = V ), atom_concat(key_, K, Key), out(i, Key, R) )),
   current_prolog_flag(version, Ver), out(i, version, Ver),
   current_prolog_flag(bounded, B), out(i, bounded, B),
   current_prolog_flag(max_tagged_integer, MT), out(d, max_tagged_integer, MT),
   current_prolog_flag(arch, A), out(d, arch, A),
   current_prolog_flag(gc, G), out(i, flag_gc, G),
   current_prolog_flag(table_space, TS), out(d, flag_table_space, TS).
