% P13f. Deterministic scale, build and reverse, native
% (problems/13-deterministic-scale.md).
% One stage (a query): build <1, ..., n> and reverse it, n from the
% instance.
%
% Native: SWI-Prolog's own list predicates. The sequence is built as a
% list by numlist/3, and reversed by reverse/2 (library(lists)); both are
% written in Prolog in the library, so their inferences are counted. The
% list is built in full before it is reversed. Algorithm: build the list
% by counting up, then reverse with an accumulator (linear). The problem's
% relations are not used, so nothing is tabled, delayed or constrained,
% and this one text serves every configuration
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: numlist/3 and reverse/2 of library(lists) (SWI-Prolog manual,
%     section "library(lists): List Manipulation"); n read with h_param/2
%     (harnesses/swi-prolog/README.md, 2.3); the stage's constant read
%     with memberchk/2, as in the harness contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
range_start(1).
% CONSTANTS END

unknowns(main, ['R']).

% stage 1: build <k, ..., n> and reverse it
stage(1, [R], Cs) :-
    memberchk(range_start(M), Cs), h_param(n, N), numlist(M, N, S), reverse(S, R).

query(_, _).
