% Made-up problem X08 (session): stage 1 needs a relation that only stage 2
% defines; supporting code (S) waits for it with h_wait/0.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
:- use_module(library(clpfd)).
% CONSTANTS BEGIN
% stage 2
given(5).
% CONSTANTS END
unknowns(main, ['M', 'N']).
:- dynamic rel/1.
stage(1, [M, _], _) :- waiting_call(rel(M)).
stage(2, _, Cs) :- memberchk(given(G), Cs), assertz(rel(G)).
stage(3, [M, N], _) :- N #= M + 1.
query(_, _).
% S: a call that waits for the next stage while its relation has no clauses
waiting_call(G) :- ( clause(G, _) -> call(G) ; h_wait, waiting_call(G) ).
