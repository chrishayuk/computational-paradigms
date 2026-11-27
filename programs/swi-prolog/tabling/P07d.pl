% P07d. Simultaneous constraints, a product, u and v given (problems/07-simultaneous-constraints.md).
% One stage (a query): w * u = v, u = <k>, v = <k>. All unknowns are integers.
%
% Each primitive relation a + b = c, a - b = c and a * b = c is written
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
u_value(2).
v_value(14).
% CONSTANTS END

% product(a, b, c): a * b = c, over the integers
product(A, B, C) :- nonvar(A), nonvar(B), !, C is A * B.
product(A, B, C) :- nonvar(A), !, factor(C, A, B).
product(A, B, C) :- factor(C, B, A).

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
