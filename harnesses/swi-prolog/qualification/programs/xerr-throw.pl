% Made-up problem X06, raised error: stage 2 throws.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['E']).
stage(1, [E], _) :- E = 1.
stage(2, [E], _) :- throw(made_up_error(E)).
stage(3, [_], _).
query(_, _).
