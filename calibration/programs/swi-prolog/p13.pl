% P13. Deterministic scale, n = 100. SWI-Prolog 11.0.1, configuration plain.
% Transcribed from problems/13-deterministic-scale.md, cases and conjuncts
% in the order given. Sequences are Prolog lists: [H|T] gives the head and
% the tail in constant time.

range(M, N, []) :- M > N.
range(M, N, [M|T]) :- M =< N, M1 is M + 1, range(M1, N, T).

sum([], 0).
sum([H|T], K) :- sum(T, J), K is H + J.

conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

rev([], []).
rev([H|L], R) :- rev(L, Q), conc(Q, [H], R).

revacc(A, B) :- racc(A, [], B).

racc([], B, B).
racc([H|T], C, B) :- racc(T, [H|C], B).

% Native (P13e, P13f): SWI-Prolog's own list library. numlist/3 builds
% the list, sum_list/2 sums it with an accumulator, reverse/2 reverses it
% with an accumulator (linear). All three are library(lists), outside the
% core of plain, and are external mechanisms.

:- use_module(library(lists), [numlist/3, sum_list/2, reverse/2]).

% The queries, each one stage, at n = 100.

n(100).

query(p13a, S,  (n(N), range(1, N, S))).
query(p13b, K,  (n(N), range(1, N, S), sum(S, K))).
query(p13c, R,  (n(N), range(1, N, S), rev(S, R))).
query(p13d, R,  (n(N), range(1, N, S), revacc(S, R))).
query(p13e, K,  (n(N), numlist(1, N, S), sum_list(S, K))).
query(p13f, R,  (n(N), numlist(1, N, S), reverse(S, R))).

% ---------------------------------------------------------------------
% Harness (H), as in p03.pl, with P13's budget of 10^8 inferences.

answers(Name, Template, Goal) :-
    format("~w~n", [Name]),
    nb_setval(count, 0),
    (   call_with_inference_limit(Goal, 100000000, Result),
        (   Result == inference_limit_exceeded
        ->  format("  budget: 10^8 inferences ran out~n"), !
        ;   nb_getval(count, N0), N is N0 + 1, nb_setval(count, N),
            format("  answer ~w: ~q~n", [N, Template]),
            (   Result == !
            ->  format("  finished (no choicepoint left)~n"), !
            ;   N >= 20
            ->  format("  cap of 20 reached, alternatives pending~n"), !
            ;   fail
            )
        )
    ;   format("  no more answers: finished~n")
    ).

main :-
    forall(query(Name, Template, Goal), answers(Name, Template, Goal)).

:- initialization((main, halt)).
