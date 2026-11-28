% P16d. Shared information at scale, contradiction
% (problems/16-shared-information.md). All unknowns are integers.
% Stage 1: every succ for both chains, ascending. Stage 2: x_1 = <k>.
% Stage 3: x_n = <k>.
% n from the instance (h_param).
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
%     chapter 3); equality as unification, =/2 (ISO 8.2.1); n read with
%     h_param/2 (harnesses/swi-prolog/README.md, 2.3); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 2
x1_value(0).
% stage 3
xn_value(0).
% CONSTANTS END

% succ(a, b): b = a + 1, over the integers
successor(A, B) :- B #= A + 1.

% succ_chain(xs): succ(x_i, x_{i+1}) for every i, ascending
succ_chain([X|Xs]) :- succ_chain(Xs, X).
succ_chain([], _).
succ_chain([B|T], A) :- successor(A, B), succ_chain(T, B).

unknowns(main, ['Xs', 'Ys']).

% stage 1: every succ(x_i, x_{i+1}), then every succ(y_i, y_{i+1}), ascending
stage(1, [Xs, Ys], _) :-
    h_param(n, N), length(Xs, N), length(Ys, N), succ_chain(Xs), succ_chain(Ys).
% stage 2: x_1 = k
stage(2, [Xs, _], Cs) :- memberchk(x1_value(K), Cs), Xs = [X1|_], X1 = K.
% stage 3: x_n = k
stage(3, [Xs, _], Cs) :- memberchk(xn_value(K), Cs), last(Xs, Xn), Xn = K.

query(_, _).
