% Section 2: in-stage sampling with the heartbeat flag.  Everything the
% heartbeat produces is classed D: which code paths fire it, and where the
% samples fall, are build- and phase-dependent.
:- use_module(common).
:- use_module(cpcount).
:- use_module(library(lists)).
:- use_module(library(apply)).
:- use_module(library(yall)).

:- multifile prolog:heartbeat/0.
prolog:heartbeat :- nb_getval(mode, Mode), beat(Mode).
beat(count) :- flag(hb, N, N+1).
beat(sample) :- nb_getval(mark, M), sample(M).
beat(off).
sample(M) :- cp_since(M, N), upd(cp, N),
   statistics(globalused, G), upd(g, G), statistics(localused, L), upd(l, L),
   statistics(trailused, T), upd(t, T), flag(n, K, K+1).
upd(K, V) :- flag(K, Old, max(Old, V)).

p(1). p(2). p(3).
loop(0) :- !.
loop(N) :- N1 is N-1, loop(N1).
fl(0) :- !.
fl(N) :- atom_length(abc, _), N1 is N-1, fl(N1).
bt :- between(1, 100000, _), p(_), fail.
bt.
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
prbt :- gen(9, _), fail.
prbt.
cps(0) :- !.
cps(N) :- p(_), N1 is N-1, cps(N1).
work :- gen(9, L), sum_list(L, S), S > 26, !.

% Which patterns fire the hook (hook = one flag/3 call, N = 1000).
fires(Name, G) :- nb_setval(mode, count), flag(hb, _, 0), set_prolog_flag(heartbeat, 1000),
    delta(G, D), set_prolog_flag(heartbeat, 0), flag(hb, H, H),
    atom_concat(Name, '_inferences', K1), out(d, K1, D),
    atom_concat(Name, '_hook_calls', K2), out(d, K2, H).

% Running maxima of a sampled run of work/0.
sampled(HB) :- forall(member(K, [cp,g,l,t,n]), flag(K, _, 0)),
    prolog_current_choice(M), nb_setval(mark, M), nb_setval(mode, sample),
    set_prolog_flag(heartbeat, HB), delta(work, D), set_prolog_flag(heartbeat, 0), nb_setval(mode, off),
    maplist([K,V]>>flag(K, V, V), [cp,g,l,t,n], [CP,G,L,T,N]),
    format(atom(P), "hb~d_", [HB]),
    forall(member(Key-Val, [inferences-D, samples-N, max_cp-CP, max_globalused-G, max_localused-L, max_trailused-T]),
           ( atom_concat(P, Key, K), out(d, K, Val) )).

burn(0) :- !.
burn(N) :- atom_length(a, _), N1 is N-1, burn(N1).

main(patterns) :- nb_setval(mode, off), work,
    fires(tail_loop, loop(100000)), fires(foreign_det, fl(50000)), fires(between_backtrack, bt),
    fires(prolog_backtrack, prbt), fires(det_with_open_cps, cps(100000)),
    nb_setval(mode, off), delta(work, D), out(i, work_inferences_no_hook, D).
main(sampled) :- nb_setval(mode, off), work, forall(member(H, [10000, 1008, 112]), sampled(H)).
% The same sampled run after K extra inferences (sample phase).
main(phase(K)) :- nb_setval(mode, off), work, burn(K), sampled(1008).
