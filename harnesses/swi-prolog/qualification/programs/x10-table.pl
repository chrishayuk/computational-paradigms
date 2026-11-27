% Made-up problem X10 (tabling): the places reachable in a made-up cyclic
% graph, by a left-recursive relation that only tabling makes terminate.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
edge(a, b).
edge(b, c).
edge(c, a).
edge(c, d).
% CONSTANTS END
:- dynamic edge/2.
:- table reach/2.
reach(X, Y) :- reach(X, Z), edge(Z, Y).
reach(X, Y) :- edge(X, Y).
unknowns(main, ['W']).
stage(1, [W], Cs) :- forall(member(E, Cs), assertz(E)), reach(a, W).
query(_, _).
