% P06b. A value, then negation (problems/06-negation.md).
% Stage 1: x = <k>. Stage 2: not (x = <k>).
%
% not (x = k) is dif/2, held as a condition while x is unknown.
% coroutines, constraints and session share this text
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: equality as unification, =/2 (ISO/IEC 13211-1, 8.2.1);
%     not (x = k) by dif/2, the sound negation of equality, which holds
%     the inequality as a condition while x is unknown (SWI-Prolog manual,
%     section "Coroutining", dif/2; the dif of Prolog II, Colmerauer,
%     1982); the stage's constant read with memberchk/2, as in the
%     harness contract's example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
value(2).
% stage 2
negated_value(1).
% CONSTANTS END

unknowns(main, ['X']).

% stage 1: x = k
stage(1, [X], Cs) :- memberchk(value(K), Cs), X = K.
% stage 2: not (x = k)
stage(2, [X], Cs) :- memberchk(negated_value(K), Cs), dif(X, K).

query(_, _).
