% P07a. Simultaneous constraints, three relations, every order (problems/07-simultaneous-constraints.md).
% One stage (a query): x + y + z = <k>, y + z = <k>, z = <k>, in the instance's order,
% which h_param(order, _) gives as a list of the relations' positions as
% written ('1', '2', '3'). This file serves all six instances, P07a,
% P07a.132, P07a.213, P07a.231, P07a.312 and P07a.321. All unknowns are integers.
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
sum_xyz(12).
sum_yz(7).
z_value(3).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers
sum(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum(A, B, C) :- nonvar(A), !, B is C - A.
sum(A, B, C) :- A is C - B.

% relation 1: x + y + z = k, that is (x + y) + z = k, with a fresh t
relation('1', [X, Y, Z], Cs) :- memberchk(sum_xyz(K), Cs), sum(X, Y, T), sum(T, Z, K).
% relation 2: y + z = k
relation('2', [_, Y, Z], Cs) :- memberchk(sum_yz(K), Cs), sum(Y, Z, K).
% relation 3: z = k
relation('3', [_, _, Z], Cs) :- memberchk(z_value(K), Cs), Z = K.

% relations(order, vs, cs): the relations the order names, in that order
relations([], _, _).
relations([N|Ns], Vs, Cs) :- relation(N, Vs, Cs), relations(Ns, Vs, Cs).

unknowns(main, ['X', 'Y', 'Z']).

% stage 1: the three relations, in the instance's order
stage(1, Vs, Cs) :- h_param(order, Order), relations(Order, Vs, Cs).

query(_, _).
