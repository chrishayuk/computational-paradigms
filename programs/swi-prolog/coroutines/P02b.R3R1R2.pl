% P02b.R3R1R2. Late information, every order: this instance's order is
% R3, R1, R2, one relation per stage (problems/02-late-information.md).
% R1: u + v = <k>. R2: w * u = v. R3: u + <k> = <k>. All unknowns are integers.
%
% Each primitive relation a + b = c and a * b = c waits, with when/2, until
% two of its three places are known; it then computes the third by is/2,
% or tests the relation when all three are known, as the plain text does.
% A relation still waiting at the end of a stage is held as a when/2 goal.
% P02b: one file per order, since each relation's constants are tagged
% with the stage that brings it (harnesses/swi-prolog/README.md, 2.5); the
% files of a configuration differ only in their CONSTANTS block and their
% stage/3 clauses.
% This text is coroutines' only (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: arithmetic by is/2 and =:=/2 (ISO/IEC 13211-1, 8.6 and 8.7;
%     SWI-Prolog manual, section "Arithmetic"); a relation of three
%     integers that computes any one place from the other two, after
%     SWI-Prolog's plus/3 (same section, "Special purpose integer arithmetic"),
%     dispatching on nonvar/1 (ISO 8.3.3) with the cut; the relation
%     delayed until it can be computed, by when/2 with a disjunction of
%     nonvar/1 conditions (SWI-Prolog manual, section "Coroutining",
%     when/2; the delaying arithmetic of MU-Prolog and NU-Prolog, after
%     Naish, Negation and Control in Prolog, LNCS 238, 1986); the stage's
%     constants read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
r3_addend(10).
r3_sum(12).
% stage 2
r1_sum(16).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers. It waits until two of its
% three places are known, and then computes the third, or tests it.
sum(A, B, C) :-
    when(( nonvar(A), nonvar(B) ; nonvar(A), nonvar(C) ; nonvar(B), nonvar(C) ),
         sum_known(A, B, C)).

sum_known(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum_known(A, B, C) :- nonvar(A), !, B is C - A.
sum_known(A, B, C) :- A is C - B.

% product(a, b, c): a * b = c, over the integers. It waits until two of its
% three places are known, and then computes the third, or tests it.
product(A, B, C) :-
    when(( nonvar(A), nonvar(B) ; nonvar(A), nonvar(C) ; nonvar(B), nonvar(C) ),
         product_known(A, B, C)).

product_known(A, B, C) :- nonvar(A), nonvar(B), !, C is A * B.
product_known(A, B, C) :- nonvar(A), !, factor(C, A, B).
product_known(A, B, C) :- factor(C, B, A).

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

stage(1, Vs, Cs) :- r3(Vs, Cs).
stage(2, Vs, Cs) :- r1(Vs, Cs).
stage(3, Vs, Cs) :- r2(Vs, Cs).

query(_, _).
