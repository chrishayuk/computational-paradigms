% Section 5: engines keep their own inference counter and stacks.
:- use_module(common).
:- use_module(cpcount).
:- use_module(library(lists)).
p(1). p(2). p(3).
loop(0) :- !.
loop(N) :- N1 is N-1, loop(N1).
g(I0-I1) :- statistics(inferences, I0), loop(100000), statistics(inferences, I1).
inner(X-N-G) :- prolog_current_choice(M), numlist(1, 100000, L), p(X), cp_since(M, N),
   statistics(globalused, G), length(L, _).
main :-
   statistics(inferences, A0), engine_create(X, g(X), E), engine_next(E, I0-I1), statistics(inferences, A1),
   engine_destroy(E), statistics(inferences, A2), DI is I1-I0, D1 is A1-A0, D2 is A2-A0,
   out(i, inside_engine_delta, DI), out(i, caller_delta_across_engine_next, D1), out(i, caller_delta_after_destroy, D2),
   engine_create(R, inner(R), E2), engine_next(E2, X1-N1-G1), statistics(globalused, GO),
   engine_next(E2, X2-N2-_), statistics(engines, NE), engine_destroy(E2),
   out(i, answer1, X1-N1), out(i, answer2, X2-N2), out(i, engines_alive, NE),
   out(d, inside_engine_globalused, G1), out(d, caller_globalused, GO).
