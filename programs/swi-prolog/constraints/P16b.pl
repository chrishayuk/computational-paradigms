% P16b. Shared information at scale, several contributors
% (problems/16-shared-information.md). All unknowns are integers.
% Stage 1: the four contributions, contributor c giving succ(x_i, x_{i+1})
% for i = (c - 1)m + 1, ..., cm, m = n/4, ascending; posed as one
% conjunction (no configuration lets separate computations share
% unknowns: harness, 2.2). Stage 2: total = x_1 + x_{m+1} + x_{2m+1} +
% x_{3m+1} + x_{4m+1}. Stage 3: x_1 = <k>.
% n from the instance (h_param).
%
% The unknowns of a chain are held as one list (Xs, Ys), made with
% length/2 at stage 1. succ(a, b), b = a + 1, is a constraint of
% library(clpfd), #=/2, over the unbounded integers (no domain imposed, no
% labeling), as the arithmetic of every constraints program here; the
% solver propagates a value given at a later stage. The sum of stage 2 is
% one #=/2 constraint. The solver's examinations of a relation are
% internal to it; no problem operations are counted. constraints and
% session share this text (programs/swi-prolog/README.md).
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
%     chapter 3); a segment counted down by if-then-else (ISO 7.8.8);
%     equality as unification, =/2 (ISO 8.2.1); n read with h_param/2
%     (harnesses/swi-prolog/README.md, 2.3); the stage's constants read
%     with memberchk/2, as in the harness contract's example (2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 3
x1_value(0).
% CONSTANTS END

% succ(a, b): b = a + 1, over the integers
successor(A, B) :- B #= A + 1.

% contribution(m, xs, rest): succ(x_i, x_{i+1}) for the first m pairs of
% xs, ascending; rest is xs from the last unknown of the segment on (the
% unknown at the boundary, shared with the next contributor)
contribution(M, Xs, Rest) :-
    (   M =:= 0
    ->  Rest = Xs
    ;   Xs = [A, B|T], successor(A, B), M1 is M - 1, contribution(M1, [B|T], Rest)
    ).

unknowns(main, ['Xs', 'Total']).

% stage 1: the four contributions, of m = n/4 relations each, over the
% n + 1 unknowns x_1, ..., x_{n+1}, as one conjunction
stage(1, [Xs, _], _) :-
    h_param(n, N), M is N // 4, N1 is N + 1, length(Xs, N1),
    contribution(M, Xs, R1), contribution(M, R1, R2),
    contribution(M, R2, R3), contribution(M, R3, _).
% stage 2: total = x_1 + x_{m+1} + x_{2m+1} + x_{3m+1} + x_{4m+1}
stage(2, [Xs, Total], _) :-
    h_param(n, N), M is N // 4,
    I2 is M + 1, I3 is 2 * M + 1, I4 is 3 * M + 1, I5 is 4 * M + 1,
    Xs = [X1|_], nth1(I2, Xs, X2), nth1(I3, Xs, X3), nth1(I4, Xs, X4),
    nth1(I5, Xs, X5),
    Total #= X1 + X2 + X3 + X4 + X5.
% stage 3: x_1 = k
stage(3, [Xs, _], Cs) :- memberchk(x1_value(K), Cs), Xs = [X1|_], X1 = K.

query(_, _).
