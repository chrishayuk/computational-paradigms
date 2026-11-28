% P15a1. Merge and committed choice, merge, any one
% (problems/15-merge-and-committed-choice.md).
% One stage (a query): merge(<seq>, <seq>, m), any one.
%
% merge is transcribed as its four cases, in the order written, with
% sequences as Prolog lists; b /= <> and a /= <> by \=/2, the core's test
% that two terms do not unify (here both are always known). The
% interleavings are the answers of merge's table, returned one by one; the
% harness collects one or all, as the instance asks. P15a1 and P15a2 have
% the same text. The tabling text: plain's, with the relations the problem
% defines tabled (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written,
%     its alternatives found by backtracking (ISO/IEC 13211-1, 7.5, 7.7;
%     Clocksin and Mellish, Programming in Prolog, 1981, chapters 1 and
%     4); sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t (Clocksin and Mellish, chapter 3; Sterling and Shapiro,
%     The Art of Prolog, 1986, chapter 3); /= by \=/2 (ISO 8.2.3); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
merge_first([1, 2]).
merge_second([3, 4]).
% CONSTANTS END

:- table merge/3.

% merge(a, b, m): m is an interleaving of a and b that keeps the order of each
merge([], B, B).
merge([H|A], [], [H|A]).
merge([H|A], B, [H|M]) :- B \= [], merge(A, B, M).
merge(A, [H|B], [H|M]) :- A \= [], merge(A, B, M).

unknowns(main, ['M']).

% stage 1: merge(a, b, m)
stage(1, [M], Cs) :-
    memberchk(merge_first(A), Cs), memberchk(merge_second(B), Cs), merge(A, B, M).

query(_, _).
