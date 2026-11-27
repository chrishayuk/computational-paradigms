% Made-up problem X08 (constraints): m and n over the integers.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
:- use_module(library(clpfd)).
% CONSTANTS BEGIN
% stage 1
low(3).
% stage 2
high(6).
% stage 3
m_value(5).
% CONSTANTS END
unknowns(main, ['M', 'N']).
stage(1, [M, _], Cs) :- memberchk(low(L), Cs), M #> L.
stage(2, [M, N], Cs) :- memberchk(high(H), Cs), M #< H, N #= M + 1.
stage(3, [M, _], Cs) :- memberchk(m_value(M), Cs).
query(_, _).
