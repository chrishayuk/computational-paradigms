% P16a. Shared information at scale, propagation along a chain
% (problems/16-shared-information.md). All unknowns are integers.
% Stage 1: succ(x_i, x_{i+1}) for i = 1, ..., n - 1, in the instance's
% arrival order. Stage 2: x_j = <k>, where j = ceil(n/2).
% n and the arrival order from the instance (h_param).
%
% The unknowns of a chain are held as one list (Xs, Ys), made with
% length/2 at stage 1. succ(a, b), b = a + 1, is written as integer
% arithmetic, as P07's relations are in this system's plain programs: it
% computes whichever place is unknown from the other, or tests the
% relation when both are known; where neither is known, is/2 raises its
% instantiation error. Plain Prolog cannot hold the relation. Each
% decision of a succ relation is counted with h_count/1 (harness code, H):
% the problem operations. plain and tabling share this text: succ is
% arithmetic, and the problem defines no other relation to table
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: arithmetic by is/2 (ISO/IEC 13211-1, 8.6; SWI-Prolog manual,
%     section "Arithmetic"); a relation that computes either place from
%     the other, after SWI-Prolog's succ/2 and plus/3 (same section,
%     "Special purpose integer arithmetic"), dispatching on nonvar/1 (ISO
%     8.3.3) with the cut; the unknowns of a chain as a list of fresh
%     variables made by length/2, and its elements reached by nth1/3,
%     last/2 and unification with [X|_] (SWI-Prolog manual, sections
%     "Built-in list operations" and "library(lists): List Manipulation");
%     a walk over the consecutive pairs of a list, carrying the previous
%     element as an argument so that first-argument indexing keeps it
%     deterministic (O'Keefe, The Craft of Prolog, 1990, chapter 3);
%     equality as unification, =/2 (ISO 8.2.1); n and the order read with
%     h_param/2, and problem operations counted with h_count/1
%     (harnesses/swi-prolog/README.md, 2.3); the stage's constants read
%     with memberchk/2, as in the harness contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 2
xj_value(0).
% CONSTANTS END

% succ(a, b): b = a + 1, over the integers
successor(A, B) :- nonvar(A), !, h_count('succ/1'), B is A + 1.
successor(A, B) :- h_count('succ/1'), A is B - 1.

% pairs(xs, ps): the pairs x_i-x_{i+1}, for i = 1, ..., n - 1, ascending
pairs([X|Xs], Ps) :- pairs(Xs, X, Ps).
pairs([], _, []).
pairs([B|T], A, [A-B|Ps]) :- pairs(T, B, Ps).

% arrival(order, ps, as): the pairs in the instance's arrival order
arrival(ascending, Ps, Ps).
arrival(descending, Ps, As) :- reverse(Ps, As).
arrival(interleaved, Ps, As) :- odd_even(Ps, Os, Es), append(Os, Es, As).

% odd_even(ps, os, es): os the pairs with odd i, es those with even i,
% each ascending
odd_even([], [], []).
odd_even([P|Ps], [P|Os], Es) :- odd_even(Ps, Es, Os).

% post(as): succ(a, b) for each pair a-b, in that order
post([]).
post([A-B|As]) :- successor(A, B), post(As).

unknowns(main, ['Xs']).

% stage 1: succ(x_i, x_{i+1}) for i = 1, ..., n - 1, in the arrival order
stage(1, [Xs], _) :-
    h_param(n, N), h_param(order, [Order]), length(Xs, N),
    pairs(Xs, Ps), arrival(Order, Ps, As), post(As).
% stage 2: x_j = k, where j = ceil(n/2)
stage(2, [Xs], Cs) :-
    memberchk(xj_value(K), Cs), h_param(n, N), J is (N + 1) // 2,
    nth1(J, Xs, Xj), Xj = K.

query(_, _).
