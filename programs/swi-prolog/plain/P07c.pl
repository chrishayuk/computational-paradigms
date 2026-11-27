% P07c. Simultaneous constraints, one relation, two unknowns (problems/07-simultaneous-constraints.md).
% One stage (a query): x + y = <k>. All unknowns are integers.
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
sum_xy(10).
% CONSTANTS END

% sum(a, b, c): a + b = c, over the integers
sum(A, B, C) :- nonvar(A), nonvar(B), !, C is A + B.
sum(A, B, C) :- nonvar(A), !, B is C - A.
sum(A, B, C) :- A is C - B.

unknowns(main, ['X', 'Y']).

% stage 1: x + y = k
stage(1, [X, Y], Cs) :- memberchk(sum_xy(K), Cs), sum(X, Y, K).

query(_, _).
