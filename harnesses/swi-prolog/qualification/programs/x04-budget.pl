% Made-up problem X04: a stage of a known number of steps, under a small
% budget (5000 inferences, made up); stage 3 never ends.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['S']).
burn(0) :- !.
burn(N) :- N1 is N-1, burn(N1).
stage(1, [S], _) :- h_param(n, N), burn(N), S = N.
stage(2, [S], _) :- S > 0.
stage(3, [_], _) :- forever.
forever :- forever_(0).
forever_(I) :- I1 is I+1, forever_(I1).
query(_, _).
