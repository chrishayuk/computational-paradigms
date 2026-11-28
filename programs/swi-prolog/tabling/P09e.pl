% P09e. Concurrent goals, mutual waiting (problems/09-concurrent-goals.md).
% One stage, one computation of two parts: x = y + <k> and y = x - <k>.
% Each part needs a value only the other can give. All unknowns are integers.
%
% Each primitive relation a + b = c and a - b = c is written
% as integer arithmetic: it computes whichever single place is unknown
% from the other two, or tests the relation when all three are known.
% A compound expression is its conjunction of primitive relations, with a
% fresh unknown, in the order it is written. plain and tabling share this
% text (programs/swi-prolog/README.md): the problem defines no relation.
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: arithmetic by is/2 and =:=/2 (ISO/IEC 13211-1, 8.6 and 8.7;
%     SWI-Prolog manual, section "Arithmetic"); a relation of three
%     integers that computes any one place from the other two, after
%     SWI-Prolog's plus/3 (same section, "Special purpose integer
%     arithmetic"), dispatching on nonvar/1 (ISO 8.3.3) with the cut;
%     equality as unification, =/2 (ISO 8.2.1); the stage's constants
%     read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
x_is_y_plus(1).
y_is_x_minus(1).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers
sum(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum(A, B, C) :- nonvar(A), !, B is C - A.
sum(A, B, C) :- A is C - B.

% diff(a, b, c): a - b = c, over the integers
diff(A, B, C) :- nonvar(A), nonvar(B), !, C is A - B.
diff(A, B, C) :- nonvar(A), !, B is A - C.
diff(A, B, C) :- A is B + C.

unknowns(main, ['X', 'Y']).

% stage 1: x = y + k1 and y = x - k2, as y + k1 = x and x - k2 = y
stage(1, [X, Y], Cs) :-
    memberchk(x_is_y_plus(K1), Cs), sum(Y, K1, X),
    memberchk(y_is_x_minus(K2), Cs), diff(X, K2, Y).

query(_, _).
