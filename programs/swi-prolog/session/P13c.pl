% P13c. Deterministic scale, range and rev, prescribed
% (problems/13-deterministic-scale.md).
% One stage (a query): range(<k>, n, s) and rev(s, r), n from the instance.
%
% range is transcribed as its two cases; rev is as in P03, the quadratic
% one, by conc, and both are this system's P03 text (programs/swi-prolog/
% plain/P03e.pl). Sequences are Prolog lists. Each application of a case
% is counted with h_count/1 (harness code, H), after the case's condition
% where it has one. The same text in plain, coroutines, constraints and
% session; tabling's text adds only its table directive
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); sequences as Prolog lists, [] for the empty
%     sequence and [H|T] for <h> ++ t; conc/3 as the two clauses of
%     append/3 (Clocksin and Mellish, chapter 3; Sterling and Shapiro, The
%     Art of Prolog, 1986, chapter 3); rev/2 as naive reverse, by append/3
%     (Sterling and Shapiro, chapter 3; Warren's "naive reverse" benchmark
%     for DEC-10 Prolog); >/2, =</2 and is/2 (ISO 8.6, 8.7; SWI-Prolog
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

% conc(a, b, c): c is a followed by b
conc([], B, B) :- h_count('conc/1').
conc([H|A], B, [H|C]) :- h_count('conc/2'), conc(A, B, C).

% rev(a, b): b is a in reverse order
rev([], []) :- h_count('rev/1').
rev([H|L], R) :- h_count('rev/2'), rev(L, Q), conc(Q, [H], R).

unknowns(main, ['S', 'R']).

% stage 1: range(k, n, s) and rev(s, r)
stage(1, [S, R], Cs) :-
    memberchk(range_start(K), Cs), h_param(n, N), range(K, N, S), rev(S, R).

query(_, _).
