% Made-up problem X08 (coroutines): n is twice m, posed before m is known.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
factor(2).
% stage 3
m_value(4).
% CONSTANTS END
unknowns(main, ['M', 'N']).
stage(1, [M, N], Cs) :- memberchk(factor(F), Cs), freeze(M, N is F*M).
stage(2, [_, N], _) :- freeze(N, N > 0).
stage(3, [M, _], Cs) :- memberchk(m_value(M), Cs).
query(_, _).
