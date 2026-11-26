% Section 2 and 6: stack figures, GC, allocation, missing peak keys.
:- use_module(common).
:- use_module(library(lists)).
:- use_module(library(apply)).

churn(0, Acc, Acc) :- !.
churn(N, Acc0, Acc) :- numlist(1, 50, L), sum_list(L, S), Acc1 is Acc0 + S, N1 is N-1, churn(N1, Acc1, Acc).
snap(Tag) :- statistics(globalused, G), statistics(localused, L), statistics(trailused, T),
    statistics(garbage_collection, [GC|_]),
    atom_concat(Tag, '_globalused', K1), out(d, K1, G),
    atom_concat(Tag, '_localused', K2), out(d, K2, L),
    atom_concat(Tag, '_trailused', K3), out(d, K3, T),
    atom_concat(Tag, '_gc_count', K4), out(d, K4, GC).

% gc(on): GC throughout; gc(off): GC disabled; off_then_gc: GC disabled
% for the work, enabled for one collection at the boundary.
gc_probe(Mode) :-
    ( Mode == on -> true ; set_prolog_flag(gc, false) ),
    churn(10, 0, _),
    statistics(garbage_collection, [G0|_]),
    delta((churn(20000, 0, S), numlist(1, 100000, K)), D),
    statistics(garbage_collection, [G1|_]), GCs is G1-G0,
    out(i, result, S), out(i, work_inferences, D), out(d, gcs_during_work, GCs),
    snap(before_gc),
    ( Mode == off_then_gc -> set_prolog_flag(gc, true) ; true ),
    garbage_collect, snap(after_gc), length(K, _).

% Allocated sizes against usage (alloc.pl).
deep(0) :- !.
deep(N) :- N1 is N-1, deep(N1), N1 >= 0.
asnap(Tag) :- forall(member(K, [localused, local, globalused, global, trailused, trail]),
    ( statistics(K, V), atomic_list_concat([Tag, '_', K], Key), out(d, Key, V) )),
    statistics(stack_shifts, SS), atom_concat(Tag, '_stack_shifts', KS), out(d, KS, SS).
alloc :- asnap(start), deep(1000000), asnap(after_deep), garbage_collect, asnap(after_gc),
    trim_stacks, asnap(after_trim), length(L, 500000), maplist(=(x), L), asnap(after_list),
    garbage_collect, asnap(after_gc2).

% Keys that would hold a peak do not exist; perturbation of statistics/2.
keys :- forall(member(K, [max_global, max_local, max_trail, globalmax, localmax, trailmax,
                          globallimit, locallimit, traillimit, trail_stack, heap]),
          ( catch((statistics(K, _), R = exists), error(E, _), R = E), atom_concat(key_, K, Key), out(i, Key, R) )),
    % limit(_) is skipped: querying it prints a deprecation warning.
    Props = [spare(_), min_free(_), low(_), factor(_)],
    findall(S-P, (member(P0, Props), prolog_stack_property(S, P0), functor(P0, P, 1)), SPs), msort(SPs, SPs1),
    out(i, stack_property_names, SPs1),
    findall(S-P0, (member(P0, Props), prolog_stack_property(S, P0)), SV), msort(SV, SV1), out(d, stack_property_values, SV1),
    statistics(stack_limit, SL), out(d, stack_limit, SL),
    statistics(globalused, A), statistics(globalused, B), DG is B-A, out(d, globalused_delta_per_statistics_call, DG).

main(gc(M)) :- gc_probe(M).
main(alloc) :- alloc.
main(keys) :- keys.
