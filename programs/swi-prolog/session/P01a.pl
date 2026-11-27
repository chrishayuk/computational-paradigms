% P01a. A chain of equations (problems/01-unknown-equality.md).
% Stage 1: x = y. Stage 2: y = z. Stage 3: z = <k>.
%
% The same text in every configuration: plain, tabling, coroutines,
% constraints, session (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: equality of values as unification, =/2 (ISO/IEC 13211-1, 8.2.1;
%     SWI-Prolog manual, section "Comparison and Unification of Terms");
%     the stage's constant read with memberchk/2, as in the harness
%     contract's example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 3
z_value(2).
% CONSTANTS END

unknowns(main, ['X', 'Y', 'Z']).

% stage 1: x = y
stage(1, [X, Y, _], _) :- X = Y.
% stage 2: y = z
stage(2, [_, Y, Z], _) :- Y = Z.
% stage 3: z = k
stage(3, [_, _, Z], Cs) :- memberchk(z_value(K), Cs), Z = K.

query(_, _).
