% P05a. Late contradiction, choice first (problems/05-late-contradiction.md).
% Stage 1: pick(x), a closed world of <facts>. Stage 2: x > <k>.
% Stage 3: x /= <k>.
%
% x > k is compared by >/2 and x /= k by \=/2, which decide at once:
% with x unknown, >/2 raises an instantiation error and \=/2 fails.
% plain and tabling share this text (programs/swi-prolog/README.md): the
% problem defines no relation but pick, which is given by facts.
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
%     8.2.1); x > k by arithmetic comparison, >/2 (ISO 8.7; SWI-Prolog manual,
%     section "Arithmetic"); x /= k as "not unifiable", \=/2 (ISO 8.2.3)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
pick(1).
pick(2).
pick(3).
% stage 2
greater_than(1).
% stage 3
not_equal_to(2).
% CONSTANTS END

unknowns(main, ['X']).

% stage 1: pick(x), over the closed world of the pick facts
stage(1, [X], Cs) :- member(pick(X), Cs).
% stage 2: x > k
stage(2, [X], Cs) :- memberchk(greater_than(K), Cs), X > K.
% stage 3: x /= k
stage(3, [X], Cs) :- memberchk(not_equal_to(K), Cs), X \= K.

query(_, _).
