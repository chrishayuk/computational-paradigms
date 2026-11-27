% The systems file's attributed-variable probe (probes/attvars.pl, the
% freeze case) as a made-up one-stage program (coroutines).
% PROVENANCE
%   author: harness-swi-prolog; the goals are the probe's, verbatim
% END PROVENANCE
unknowns(main, ['X', 'Y']).
stage(1, [X, Y], _) :- freeze(X, writeln(x)), freeze(X, true), freeze(Y, writeln(y)).
query(_, _).
