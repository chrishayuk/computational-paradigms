% P16d2. Shared information at scale, contradiction without a value
% (problems/16-shared-information.md). All unknowns are integers.
% Stage 1: every succ for both chains, ascending. Stage 2 (the problem
% file's stage 3): x_n = x_1.
% n from the instance (h_param).
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
%     equality as unification, =/2 (ISO 8.2.1); n read with h_param/2, and
%     problem operations counted with h_count/1
%     (harnesses/swi-prolog/README.md, 2.3)
% END PROVENANCE

% succ(a, b): b = a + 1, over the integers
successor(A, B) :- nonvar(A), !, h_count('succ/1'), B is A + 1.
successor(A, B) :- h_count('succ/1'), A is B - 1.

% succ_chain(xs): succ(x_i, x_{i+1}) for every i, ascending
succ_chain([X|Xs]) :- succ_chain(Xs, X).
succ_chain([], _).
succ_chain([B|T], A) :- successor(A, B), succ_chain(T, B).

unknowns(main, ['Xs', 'Ys']).

% stage 1: every succ(x_i, x_{i+1}), then every succ(y_i, y_{i+1}), ascending
stage(1, [Xs, Ys], _) :-
    h_param(n, N), length(Xs, N), length(Ys, N), succ_chain(Xs), succ_chain(Ys).
% stage 2: x_n = x_1
stage(2, [Xs, _], _) :- Xs = [X1|_], last(Xs, Xn), Xn = X1.

query(_, _).
