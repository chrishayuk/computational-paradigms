% Choicepoint counter relative to a mark.  Single-clause predicates, no
% if-then-else before prolog_current_choice/1 is read, so the counter
% itself contributes no choicepoint to what it observes.
:- module(cpcount, [cp_mark/1, cp_since/2, cp_since_types/2]).
cp_mark(M) :- prolog_current_choice(M).
cp_since(M, N) :- prolog_current_choice(C), cnt(C, M, 0, N).
cnt(C, M, N0, N) :- C =< M, !, N = N0.
cnt(C, M, N0, N) :- N1 is N0+1,
    ( prolog_choice_attribute(C, parent, P) -> cnt(P, M, N1, N) ; N = N1 ).
cp_since_types(M, Ts) :- prolog_current_choice(C), typ(C, M, Ts).
typ(C, M, []) :- C =< M, !.
typ(C, M, [T|Ts]) :- prolog_choice_attribute(C, type, T),
    ( prolog_choice_attribute(C, parent, P) -> typ(P, M, Ts) ; Ts = [] ).
