% Made-up problem X08 (session, with the configuration's S code): stage 1
% calls a relation that nothing defines yet; stage 2 defines it. In
% session the computation waits (S/session-wait.pl); elsewhere it is an
% existence error.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
:- use_module(library(clpfd)).
% CONSTANTS BEGIN
% stage 2
given(5).
% CONSTANTS END
unknowns(main, ['M', 'N']).
stage(1, [M, _], _) :- rel(M).
stage(2, _, Cs) :- memberchk(given(G), Cs), assertz(rel(G)).
stage(3, [M, N], _) :- N #= M + 1.
query(_, _).
