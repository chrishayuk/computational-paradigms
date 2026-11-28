% P13a. Deterministic scale, range, prescribed (problems/13-deterministic-scale.md).
% One stage (a query): range(<k>, n, s), n from the instance (h_param).
%
% range is transcribed as its two cases, in the order written, with
% sequences as Prolog lists (a head and a tail, so that <h> ++ t
% decomposes in constant time, as the problem requires). Each application
% of a case is counted with h_count/1 (harness code, H), placed after the
% case's condition, so that it counts the applications that hold. The same
% text in plain, coroutines, constraints and session; tabling's text adds
% only its table directive (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); sequences as Prolog lists, [] for the empty
%     sequence and [H|T] for <h> ++ t (Clocksin and Mellish, chapter 3;
%     Sterling and Shapiro, The Art of Prolog, 1986, chapter 3); m > n, m
%     =< n and m + 1 by >/2, =</2 and is/2 (ISO 8.6, 8.7; SWI-Prolog
%     manual, section "Arithmetic"); n read with h_param/2 and problem
%     operations counted with h_count/1 (harnesses/swi-prolog/README.md,
%     2.3); the stage's constant read with memberchk/2, as in the harness
%     contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
range_start(1).
% CONSTANTS END

% range(m, n, s): s = <m, m+1, ..., n>, or <> if m > n
range(M, N, []) :- M > N, h_count('range/1').
range(M, N, [M|T]) :- M =< N, h_count('range/2'), M1 is M + 1, range(M1, N, T).

unknowns(main, ['S']).

% stage 1: range(k, n, s)
stage(1, [S], Cs) :- memberchk(range_start(K), Cs), h_param(n, N), range(K, N, S).

query(_, _).
