% P09e. Concurrent goals, mutual waiting (problems/09-concurrent-goals.md).
% One stage, one computation of two parts: x = y + <k> and y = x - <k>.
% Each part needs a value only the other can give. All unknowns are integers.
%
% Each primitive relation a + b = c and a - b = c waits, with
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
x_is_y_plus(1).
y_is_x_minus(1).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers. It waits until two of its
% three places are known, and then computes the third, or tests it.
sum(A, B, C) :-
    when(( nonvar(A), nonvar(B) ; nonvar(A), nonvar(C) ; nonvar(B), nonvar(C) ),
         sum_known(A, B, C)).

sum_known(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum_known(A, B, C) :- nonvar(A), !, B is C - A.
sum_known(A, B, C) :- A is C - B.

% diff(a, b, c): a - b = c, over the integers. It waits until two of its
% three places are known, and then computes the third, or tests it.
diff(A, B, C) :-
    when(( nonvar(A), nonvar(B) ; nonvar(A), nonvar(C) ; nonvar(B), nonvar(C) ),
         diff_known(A, B, C)).

diff_known(A, B, C) :- nonvar(A), nonvar(B), !, C is A - B.
diff_known(A, B, C) :- nonvar(A), !, B is A - C.
diff_known(A, B, C) :- A is B + C.

unknowns(main, ['X', 'Y']).

% stage 1: x = y + k1 and y = x - k2, as y + k1 = x and x - k2 = y
stage(1, [X, Y], Cs) :-
    memberchk(x_is_y_plus(K1), Cs), sum(Y, K1, X),
    memberchk(y_is_x_minus(K2), Cs), diff(X, K2, Y).

query(_, _).
