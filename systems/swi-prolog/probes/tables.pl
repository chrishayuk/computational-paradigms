% Section 3: table storage.
:- use_module(common).
:- use_module(library(tables)).
:- use_module(library(tableutil)).
:- use_module(library(aggregate)).

:- table path/2.
edge(X, Y) :- between(1, 200, X), Y is (X*7+3) mod 200 + 1.
edge(X, Y) :- between(1, 200, X), Y is X mod 200 + 1.
path(X, Y) :- edge(X, Y).
path(X, Y) :- path(X, Z), edge(Z, Y).

tstats(Tag) :- statistics(table_space_used, U),
   aggregate_all(count, current_table(_:_, _), NT),
   aggregate_all(sum(C), (current_table(_:_, T), trie_property(T, value_count(C))), NA),
   aggregate_all(sum(B), (current_table(_:_, T), trie_property(T, size(B))), SB),
   atom_concat(Tag, '_table_space_used', K1), out(i, K1, U),
   atom_concat(Tag, '_tables', K2), out(i, K2, NT),
   atom_concat(Tag, '_answers', K3), out(i, K3, NA),
   atom_concat(Tag, '_sum_trie_size', K4), out(i, K4, SB).

main(usage) :- tstats(before),
   delta(aggregate_all(count, path(1,_), N1), D1), out(i, path1_answers, N1), out(i, path1_inferences, D1),
   tstats(after_path1),
   delta(aggregate_all(count, path(1,_), _), D2), out(i, path1_completed_table_inferences, D2),
   aggregate_all(count, path(_,_), N2), out(i, path_open_answers, N2), tstats(after_path_open),
   forall(table_statistics(Stat, V), (atom_concat(table_statistics_, Stat, K), out(i, K, V))),
   abolish_all_tables, tstats(after_abolish),
   current_prolog_flag(table_space, TS), out(d, table_space_flag, TS).
main(limit) :- set_prolog_flag(table_space, 100000),
   catch((aggregate_all(count, path(_,_), N), R = N), error(E, _), R = E), out(i, limit_100000_result, R),
   statistics(table_space_used, U), out(i, limit_after_table_space_used, U).
