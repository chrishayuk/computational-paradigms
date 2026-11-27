% Made-up problem X02: choose an option, emit it, commit, then exclude.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
option(1).
option(2).
option(3).
% stage 3
excluded(1).
% CONSTANTS END
unknowns(main, ['P']).
stage(1, [P], Cs) :- member(option(P), Cs), emit(chose(P)).
stage(2, [P], _) :- ( h_commitment(V) -> replayed_value(V, P) ; true ), emit(committed(P)).
stage(3, [P], Cs) :- \+ memberchk(excluded(P), Cs), emit(kept(P)).
query(_, _).
% the commit stage's answer, as the harness passes it back: "P = 1 "
replayed_value(V, P) :- term_string(T, V, [variable_names(Bs)]), memberchk('P'=P, Bs), call(T).
