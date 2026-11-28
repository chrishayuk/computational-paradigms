% P09b. Concurrent goals, isolation from failure (problems/09-concurrent-goals.md).
% One stage, two separate computations, each started with spawn():
% A: x = <k> and x = <k>; B: y = <k>.
%
% Each computation is a spawned/4 clause (harness contract, 2.1 and 2.2).
% The problem defines no relation, and has nothing to delay or constrain,
% so this one text serves every configuration
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: equality as unification, =/2 (ISO/IEC 13211-1, 8.2.1; SWI-Prolog
%     manual, section "Comparison and Unification of Terms"); a conjunction
%     by ,/2 in the order written (ISO 7.8.5); separate computations as the
%     harness's spawned computations, one query each
%     (harnesses/swi-prolog/README.md, 2.1, 2.2); the stage's constants
%     read with memberchk/2, as in the harness contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
a_first_value(1).
a_second_value(2).
b_value(3).
% CONSTANTS END

unknowns('A', ['X']).
unknowns('B', ['Y']).

% stage 1, computation A: x = k1 and x = k2
spawned(1, 'A', [X], Cs) :-
    memberchk(a_first_value(K1), Cs), X = K1,
    memberchk(a_second_value(K2), Cs), X = K2.
% stage 1, computation B: y = k
spawned(1, 'B', [Y], Cs) :- memberchk(b_value(K), Cs), Y = K.
