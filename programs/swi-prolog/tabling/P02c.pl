% P02c. Late information, all at once (problems/02-late-information.md).
% Stage 1 (a query): R1, R2 and R3 as one stage, in that order.
% R1: u + v = <k>. R2: w * u = v. R3: u + <k> = <k>. All unknowns are integers.
%
% The relations are the text of P02a.pl. plain and tabling share this text.
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: arithmetic by is/2 and =:=/2 (ISO/IEC 13211-1, 8.6 and 8.7;
%     SWI-Prolog manual, section "Arithmetic"); a relation of three
%     integers that computes any one place from the other two, after
%     SWI-Prolog's plus/3 (same section, "Special purpose integer arithmetic"),
%     dispatching on nonvar/1 (ISO 8.3.3) with the cut; the stage's
%     constants read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
r1_sum(16).
r3_addend(10).
r3_sum(12).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers
sum(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum(A, B, C) :- nonvar(A), !, B is C - A.
sum(A, B, C) :- A is C - B.

% product(a, b, c): a * b = c, over the integers
product(A, B, C) :- nonvar(A), nonvar(B), !, C is A * B.
product(A, B, C) :- nonvar(A), !, factor(C, A, B).
product(A, B, C) :- factor(C, B, A).

% factor(c, d, q): d * q = c, q unknown, over the integers
factor(C, 0, _) :- !, C =:= 0.
factor(C, D, Q) :- C mod D =:= 0, Q is C // D.

% R1: u + v = k
r1([U, V, _], Cs) :- memberchk(r1_sum(K), Cs), sum(U, V, K).
% R2: w * u = v
r2([U, V, W], _) :- product(W, U, V).
% R3: u + k1 = k2
r3([U, _, _], Cs) :- memberchk(r3_addend(K1), Cs), memberchk(r3_sum(K2), Cs), sum(U, K1, K2).

unknowns(main, ['U', 'V', 'W']).

stage(1, Vs, Cs) :- r1(Vs, Cs), r2(Vs, Cs), r3(Vs, Cs).

query(_, _).
