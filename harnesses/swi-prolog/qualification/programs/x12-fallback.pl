% Made-up problem X12: two contributors posed as one conjunction.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['X']).
stage(1, [X], _) :- X = [_, _], contributor(1, X), contributor(2, X).
stage(2, [X], _) :- X = [1|_].
contributor(1, [A, _]) :- A = 1.
contributor(2, [A, B]) :- B = A.
query(_, _).
