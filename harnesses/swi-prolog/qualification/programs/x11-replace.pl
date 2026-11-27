% Made-up problem X11: a named quantity v takes a new value at stages 2, 3.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
value(1, 10).
% stage 2
value(2, 20).
% stage 3
value(3, 30).
% CONSTANTS END
:- dynamic v/1.
unknowns(main, ['V']).
stage(K, _, Cs) :- retractall(v(_)), memberchk(value(K, X), Cs), assertz(v(X)).
query(_, [V]) :- v(V).
