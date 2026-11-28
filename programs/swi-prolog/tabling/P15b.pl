% P15b. Merge and committed choice, fairness to an unbounded source
% (problems/15-merge-and-committed-choice.md), under the stream reading of
% P09d2. One stage, an any-one query:
% zeros(z) and merge(z, <seq>, m) and position(<k>, m, i), in that order.
%
% zeros, merge and position are transcribed as their cases, in the order
% written, with sequences as Prolog lists, and the conjunction is posed in
% the order written. /= is \=/2, the core's test that two terms do not
% unify. tabling has no way to wait for demand: zeros(z) is called first,
% and evaluated by SLG resolution, as every relation here is tabled. No
% fairness is added: merge is the definition's, tried in its clauses'
% order. The tabling text: plain's, with the relations the problem defines
% tabled (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written,
%     and a conjunction executed left to right (ISO/IEC 13211-1, 7.5, 7.7;
%     Clocksin and Mellish, Programming in Prolog, 1981, chapter 1);
%     sequences as Prolog lists, [] for the empty sequence and [H|T] for
%     <h> ++ t (Clocksin and Mellish, chapter 3; Sterling and Shapiro, The
%     Art of Prolog, 1986, chapter 3); /= by \=/2 (ISO 8.2.3); j + 1 by
%     is/2 (ISO 8.6); the stage's constants read with memberchk/2, as in
%     the harness contract's example (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
merge_second([9]).
position_of(9).
% CONSTANTS END

:- table zeros/1, merge/3, position/3.

% zeros(z): z = <0, 0, 0, ...>
zeros([0|S]) :- zeros(S).

% merge(a, b, m): m is an interleaving of a and b that keeps the order of each
merge([], B, B).
merge([H|A], [], [H|A]).
merge([H|A], B, [H|M]) :- B \= [], merge(A, B, M).
merge(A, [H|B], [H|M]) :- A \= [], merge(A, B, M).

% position(e, m, i): the i-th element of m is e
position(E, [E|_], 1).
position(E, [H|T], I) :- H \= E, position(E, T, J), I is J + 1.

unknowns(main, ['I', 'M', 'Z']).

% stage 1: zeros(z), merge(z, b, m), position(e, m, i)
stage(1, [I, M, Z], Cs) :-
    memberchk(merge_second(B), Cs), memberchk(position_of(E), Cs),
    zeros(Z), merge(Z, B, M), position(E, M, I).

query(_, _).
