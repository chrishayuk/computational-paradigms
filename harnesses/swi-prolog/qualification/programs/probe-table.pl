% The systems file's table probe (probes/tables.pl, path(1, _)) as a
% made-up one-stage program (tabling).
% PROVENANCE
%   author: harness-swi-prolog; the goals are the probe's, verbatim
% END PROVENANCE
:- table path/2.
edge(X, Y) :- between(1, 200, X), Y is (X*7+3) mod 200 + 1.
edge(X, Y) :- between(1, 200, X), Y is X mod 200 + 1.
path(X, Y) :- edge(X, Y).
path(X, Y) :- path(X, Z), edge(Z, Y).
unknowns(main, ['Y']).
stage(1, [Y], _) :- path(1, Y).
query(_, _).
