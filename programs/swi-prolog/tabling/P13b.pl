% P13b. Deterministic scale, range and sum, prescribed
% (problems/13-deterministic-scale.md).
% One stage (a query): range(<k>, n, s) and sum(s, k), n from the instance.
%
% range and sum are transcribed as their cases, in the order written, with
% sequences as Prolog lists. Each application of a case is counted with
% h_count/1 (harness code, H), after the case's condition where it has
% one. The tabling text: the plain text with the relations the problem
% defines tabled, as in every tabling program here
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); sequences as Prolog lists, [] for the empty
%     sequence and [H|T] for <h> ++ t (Clocksin and Mellish, chapter 3;
%     Sterling and Shapiro, The Art of Prolog, 1986, chapter 3); the sum
%     of a list by recursion on its tail, then is/2 (Sterling and Shapiro,
%     chapter 8, "Arithmetic"); >/2, =</2 and is/2 (ISO 8.6, 8.7;
%     SWI-Prolog manual, section "Arithmetic"); n read with h_param/2 and
%     problem operations counted with h_count/1
%     (harnesses/swi-prolog/README.md, 2.3); the stage's constant read
%     with memberchk/2, as in the harness contract's example (2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
range_start(1).
% CONSTANTS END

:- table range/3, sum/2.

% range(m, n, s): s = <m, m+1, ..., n>, or <> if m > n
range(M, N, []) :- M > N, h_count('range/1').
range(M, N, [M|T]) :- M =< N, h_count('range/2'), M1 is M + 1, range(M1, N, T).

% sum(s, k): k is the sum of the elements of s
sum([], 0) :- h_count('sum/1').
sum([H|T], K) :- h_count('sum/2'), sum(T, J), K is H + J.

unknowns(main, ['S', 'K']).

% stage 1: range(k, n, s) and sum(s, k)
stage(1, [S, K], Cs) :-
    memberchk(range_start(M), Cs), h_param(n, N), range(M, N, S), sum(S, K).

query(_, _).
