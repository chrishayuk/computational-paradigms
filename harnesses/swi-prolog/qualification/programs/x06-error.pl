% Made-up problem X06: stage 2 calls a relation nothing defines.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['E']).
stage(1, [E], _) :- E = 1.
stage(2, [E], _) :- undefined_relation(E).
stage(3, [_], _).
query(_, _).
