% P13d. Deterministic scale, range and revacc, prescribed
% (problems/13-deterministic-scale.md).
% One stage (a query): range(<k>, n, s) and revacc(s, r), n from the
% instance.
%
% range and revacc (with racc) are transcribed as their cases, in the
% order written, with sequences as Prolog lists. Each application of a
% case is counted with h_count/1 (harness code, H), after the case's
% condition where it has one, under the problem's numbers for revacc's
% three cases (revacc/1, racc/2, racc/3). The tabling text: the plain text
% with the relations the problem defines tabled, as in every tabling
% program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); sequences as Prolog lists, [] for the empty
%     sequence and [H|T] for <h> ++ t (Clocksin and Mellish, chapter 3;
%     Sterling and Shapiro, The Art of Prolog, 1986, chapter 3); reverse
%     with an accumulator (Sterling and Shapiro, chapter 3, reverse/3;
%     O'Keefe, The Craft of Prolog, 1990, chapter 3); >/2, =</2 and is/2
%     (ISO 8.6, 8.7; SWI-Prolog manual, section "Arithmetic"); n read with
%     h_param/2 and problem operations counted with h_count/1
%     (harnesses/swi-prolog/README.md, 2.3); the stage's constant read
%     with memberchk/2, as in the harness contract's example (2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
range_start(1).
% CONSTANTS END

:- table range/3, revacc/2, racc/3.

% range(m, n, s): s = <m, m+1, ..., n>, or <> if m > n
range(M, N, []) :- M > N, h_count('range/1').
range(M, N, [M|T]) :- M =< N, h_count('range/2'), M1 is M + 1, range(M1, N, T).

% revacc(a, b): b is a in reverse order, with an accumulator
revacc(A, B) :- h_count('revacc/1'), racc(A, [], B).
racc([], B, B) :- h_count('racc/2').
racc([H|T], C, B) :- h_count('racc/3'), racc(T, [H|C], B).

unknowns(main, ['S', 'R']).

% stage 1: range(k, n, s) and revacc(s, r)
stage(1, [S, R], Cs) :-
    memberchk(range_start(K), Cs), h_param(n, N), range(K, N, S), revacc(S, R).

query(_, _).
