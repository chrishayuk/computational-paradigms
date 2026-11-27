% Made-up problem X03: two computations sharing one database.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
item(a).
item(b).
% CONSTANTS END
:- dynamic seen/1.
unknowns('U', ['P']).
unknowns('V', ['Q']).
spawned(1, 'U', [P], Cs) :- member(item(P), Cs), assertz(seen(P)).
spawned(1, 'V', [Q], _) :- findall(X, seen(X), Q).
