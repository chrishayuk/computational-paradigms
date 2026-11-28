% P09c. Concurrent goals, communication through a shared unknown
% (problems/09-concurrent-goals.md).
% One stage, one computation: gen(<k>, s) and sum3(s, total), in that order.
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, in the order written (ISO/IEC
%     13211-1, 7.5; Clocksin and Mellish, Programming in Prolog, 1981,
%     chapter 1); sequences as Prolog lists, [] for the empty sequence and
%     [H|T] for <h> ++ t, and [P, Q, R|M] for <p, q, r> ++ m (Clocksin and
%     Mellish, chapter 3; Sterling and Shapiro, The Art of Prolog, 1986,
%     chapter 3); n + 1 and p + q + r by is/2, and n > 5, n =< 5 by
%     arithmetic comparison (ISO 8.6, 8.7; SWI-Prolog manual, section
%     "Arithmetic"); the stage's constant read with memberchk/2, as in the
%     harness contract's example (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
gen_start(1).
% CONSTANTS END

:- table gen/2, sum3/2.

% gen(n, s): s = <n, n+1, ..., 5>
gen(N, []) :- N > 5.
gen(N, [N|Rest]) :- N =< 5, N1 is N + 1, gen(N1, Rest).

% sum3(s, total): total is the sum of the first three elements of s
sum3([P, Q, R|_], Total) :- Total is P + Q + R.

unknowns(main, ['S', 'Total']).

% stage 1: gen(k, s) and sum3(s, total)
stage(1, [S, Total], Cs) :- memberchk(gen_start(K), Cs), gen(K, S), sum3(S, Total).

query(_, _).
