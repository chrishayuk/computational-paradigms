% P03. Reversible relations. SWI-Prolog 11.0.1, configuration plain.
% Transcribed from problems/03-reversible-relations.md (conc from
% problems/01-unknown-equality.md), cases and conjuncts in the order given.

conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

rev([], []).
rev([H|L], R) :- rev(L, Q), conc(Q, [H], R).

% The six queries, each one stage.

query(p03a, C,      conc([1,2], [3], C)).
query(p03b, A-B,    conc(A, B, [1,2])).
query(p03c, B,      conc([1], B, [1,2,3])).
query(p03d, A,      conc(A, [3], [1,2,3])).
query(p03e, B,      rev([1,2,3], B)).
query(p03f, A,      rev(A, [1,2,3])).

% ---------------------------------------------------------------------
% Harness (H). A stand-in for the harness PROTOCOL.md fixes before the
% freeze: answers(cap) with cap 20, under a budget of 10^6 inferences per
% stage. call_with_inference_limit/3 is SWI's, not ISO; it is harness, not
% program.

answers(Name, Template, Goal) :-
    format("~w~n", [Name]),
    nb_setval(count, 0),
    (   call_with_inference_limit(Goal, 1000000, Result),
        (   Result == inference_limit_exceeded
        ->  format("  budget: 10^6 inferences ran out~n"), !
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
