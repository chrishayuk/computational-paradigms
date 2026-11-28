% P16a. Shared information at scale, propagation along a chain
% (problems/16-shared-information.md). All unknowns are integers.
% Stage 1: succ(x_i, x_{i+1}) for i = 1, ..., n - 1, in the instance's
% arrival order. Stage 2: x_j = <k>, where j = ceil(n/2).
% n and the arrival order from the instance (h_param).
%
% The unknowns of a chain are held as one list (Xs, Ys), made with
% length/2 at stage 1. succ(a, b), b = a + 1, is a constraint of
% library(clpfd), #=/2, over the unbounded integers (no domain imposed, no
% labeling), as the arithmetic of every constraints program here; the
% solver propagates a value given at a later stage. The solver's
% examinations of a relation are internal to it; no problem operations are
% counted. constraints and session share this text
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: integer arithmetic as constraints of library(clpfd), #=/2,
%     over the unbounded integers (SWI-Prolog manual, section
%     "library(clpfd)"; Triska, "The finite domain constraint solver of
%     SWI-Prolog", FLOPS 2012, LNCS 7294); the unknowns of a chain as a
%     list of fresh variables made by length/2, and its elements reached
%     by nth1/3, last/2 and unification with [X|_] (SWI-Prolog manual,
%     sections "Built-in list operations" and "library(lists): List
%     Manipulation"); a walk over the consecutive pairs of a list,
%     carrying the previous element as an argument so that first-argument
%     indexing keeps it deterministic (O'Keefe, The Craft of Prolog, 1990,
%     chapter 3); equality as unification, =/2 (ISO 8.2.1); n and the
%     order read with h_param/2 (harnesses/swi-prolog/README.md, 2.3); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 2
xj_value(0).
% CONSTANTS END

% succ(a, b): b = a + 1, over the integers
successor(A, B) :- B #= A + 1.

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
