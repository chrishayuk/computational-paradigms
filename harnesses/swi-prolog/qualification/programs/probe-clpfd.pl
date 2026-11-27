% The systems file's attributed-variable probe (probes/attvars.pl, the
% clpfd case) as a made-up one-stage program (constraints).
% PROVENANCE
%   author: harness-swi-prolog; the goals are the probe's, verbatim
% END PROVENANCE
:- use_module(library(clpfd)).
unknowns(main, ['X', 'Y', 'Z']).
stage(1, [X, Y, Z], _) :- X #> 3, X #< Y, Y in 0..10, Z #= X+Y.
query(_, _).
