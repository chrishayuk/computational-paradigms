% The systems file's inference probe (probes/inferences.pl, w2/0) as a
% made-up one-stage program.
% PROVENANCE
%   author: harness-swi-prolog; the goal is the probe's, verbatim
% END PROVENANCE
:- use_module(library(lists)).
unknowns(main, ['R']).
nrev([], []).
nrev([H|T], R) :- nrev(T, RT), append(RT, [H], R).
stage(1, [R], _) :- numlist(1, 300, L), nrev(L, R).
query(_, _).
