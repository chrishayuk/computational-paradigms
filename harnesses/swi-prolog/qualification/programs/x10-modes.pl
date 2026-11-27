% Made-up problem X10: one query, all answers or any one.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
w(1). w(2). w(3).
% CONSTANTS END
unknowns(main, ['W']).
stage(1, [W], Cs) :- member(w(W), Cs).
query(_, _).
