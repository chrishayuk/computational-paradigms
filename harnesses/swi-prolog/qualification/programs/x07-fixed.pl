% Made-up problem X07: stage 1 never ends; the limit is fixed (no rerun).
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['T']).
stage(1, [_], _) :- spin(0).
stage(2, [T], _) :- T = 2.
spin(I) :- I1 is I+1, spin(I1).
query(_, _).
