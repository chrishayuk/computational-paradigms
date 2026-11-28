% P15b2. Merge and committed choice, fairness to an unbounded source
% (problems/15-merge-and-committed-choice.md), under the stream reading of
% P09d2. One stage, an any-one query:
% zeros(z) and merge(<seq>, z, m) and position(<k>, m, i), in that order.
%
% zeros, merge and position are transcribed as their cases, in the order
% written, with sequences as Prolog lists, and the conjunction is posed in
% the order written. The producer of the unbounded sequence waits for
% demand, as P09d's producer does in this system's coroutines programs:
% each application of zeros, the query's and the recursive one, waits by
% freeze/2 until its sequence is bound, that is, until merge takes an
% element of z. merge and position are not delayed. /= is dif/2, which
% waits where a place is not yet known. No fairness is added: merge is the
% definition's, tried in its clauses' order. coroutines, constraints and
% session share this text (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written,
%     and a conjunction executed left to right (ISO/IEC 13211-1, 7.5, 7.7;
%     Clocksin and Mellish, Programming in Prolog, 1981, chapter 1);
%     sequences as Prolog lists, [] for the empty sequence and [H|T] for
%     <h> ++ t (Clocksin and Mellish, chapter 3; Sterling and Shapiro, The
%     Art of Prolog, 1986, chapter 3); a producer that waits for its
%     consumer's demand, by freeze/2 on the sequence it produces
%     (SWI-Prolog manual, section "Coroutining", freeze/2; the freeze of
%     Prolog II, Colmerauer, 1982; the lazy producers of IC-Prolog, Clark,
%     McCabe and Gregory, "IC-PROLOG language features", in Clark and
%     Taernlund (eds.), Logic Programming, 1982); /= by dif/2 (SWI-Prolog
%     manual, section "Coroutining"); j + 1 by is/2 (ISO 8.6); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
merge_first([9]).
position_of(9).
% CONSTANTS END

% zeros(z): z = <0, 0, 0, ...>; the rest is produced when it is demanded
zeros([0|S]) :- freeze(S, zeros(S)).

% merge(a, b, m): m is an interleaving of a and b that keeps the order of each
merge([], B, B).
merge([H|A], [], [H|A]).
merge([H|A], B, [H|M]) :- dif(B, []), merge(A, B, M).
merge(A, [H|B], [H|M]) :- dif(A, []), merge(A, B, M).

% position(e, m, i): the i-th element of m is e
position(E, [E|_], 1).
position(E, [H|T], I) :- dif(H, E), position(E, T, J), I is J + 1.

unknowns(main, ['I', 'M', 'Z']).

% stage 1: zeros(z), merge(a, z, m), position(e, m, i)
stage(1, [I, M, Z], Cs) :-
    memberchk(merge_first(A), Cs), memberchk(position_of(E), Cs),
    freeze(Z, zeros(Z)), merge(A, Z, M), position(E, M, I).

query(_, _).
