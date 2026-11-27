% P07e. Simultaneous constraints, a product, u and v given (P07e's constants) (problems/07-simultaneous-constraints.md).
% One stage (a query): w * u = v, u = <k>, v = <k>. All unknowns are integers.
%
% Each primitive relation a + b = c, a - b = c and a * b = c waits, with
% when/2, until two of its three places are known; it then computes the
% third by is/2, or tests the relation when all three are known, as the
% plain text does. A relation still waiting at the end of the stage is held
% as a when/2 goal. A compound expression is its conjunction of primitive
% relations, with a fresh unknown. This text is coroutines' only
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: arithmetic by is/2 and =:=/2 (ISO/IEC 13211-1, 8.6 and 8.7;
%     SWI-Prolog manual, section "Arithmetic"); a relation of three
%     integers that computes any one place from the other two, after
%     SWI-Prolog's plus/3 (same section, "Special purpose integer
%     arithmetic"), dispatching on nonvar/1 (ISO 8.3.3) with the cut; the
%     relation delayed until it can be computed, by when/2 with a
%     disjunction of nonvar/1 conditions (SWI-Prolog manual, section
%     "Coroutining", when/2; the delaying arithmetic of MU-Prolog and
%     NU-Prolog, after Naish, Negation and Control in Prolog, LNCS 238,
%     1986); equality as unification, =/2 (ISO 8.2.1); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
u_value(2).
v_value(15).
% CONSTANTS END

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

unknowns(main, ['W', 'U', 'V']).

% stage 1: w * u = v, u = k1, v = k2
stage(1, [W, U, V], Cs) :-
    product(W, U, V),
    memberchk(u_value(K1), Cs), U = K1,
    memberchk(v_value(K2), Cs), V = K2.

query(_, _).
