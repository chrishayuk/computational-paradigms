% P05c. Late contradiction, contradiction (problems/05-late-contradiction.md).
% Stage 1: pick(x), a closed world of <facts>. Stage 2: x = <k>.
% Stage 3: x = <k>.
%
% Only pick and equality: the same text in every configuration
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a relation given by facts in a closed world, its facts the
%     constants of the stage that first uses them, in the order the problem
%     gives them, enumerated by backtracking with member/2 of
%     library(lists), as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7; SWI-Prolog manual, section
%     "library(lists)"); the other constants read with memberchk/2, as in
%     the same example; equality as unification, =/2 (ISO/IEC 13211-1,
%     8.2.1)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
pick(1).
pick(2).
pick(3).
% stage 2
first_value(4).
% stage 3
second_value(3).
% CONSTANTS END

unknowns(main, ['X']).

% stage 1: pick(x), over the closed world of the pick facts
stage(1, [X], Cs) :- member(pick(X), Cs).
% stage 2: x = k
stage(2, [X], Cs) :- memberchk(first_value(K), Cs), X = K.
% stage 3: x = k
stage(3, [X], Cs) :- memberchk(second_value(K), Cs), X = K.

query(_, _).
