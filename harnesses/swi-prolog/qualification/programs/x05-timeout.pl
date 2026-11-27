% Made-up problem X05: stage 2 runs until the safety limit stops it.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['T']).
stage(1, [T], _) :- T = start, format("stage one ran~n").
stage(2, [_], _) :- spin(0).
stage(3, [_], _).
spin(I) :- I1 is I+1, spin(I1).
query(_, _).
