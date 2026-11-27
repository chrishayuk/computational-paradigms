% The systems file's inference probe (probes/inferences.pl, work/0) as a
% made-up one-stage program: the stage's body is work/0's body.
% PROVENANCE
%   author: harness-swi-prolog; the goal is the probe's, verbatim
% END PROVENANCE
:- use_module(library(lists)).
unknowns(main, ['S']).
p(1). p(2). p(3).
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
stage(1, [S], _) :- gen(9, L), sum_list(L, S), S > 26, !.
query(_, _).
