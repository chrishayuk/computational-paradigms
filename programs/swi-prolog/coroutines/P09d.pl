% P09d. Concurrent goals, an unbounded producer (problems/09-concurrent-goals.md).
% One stage, one computation: genu(<k>, s) and sum3(s, total), in that order.
% Run once and classified under two readings (P09d1, finite; P09d2, stream).
%
% genu and sum3 are transcribed as clauses, as in the plain text. The
% producer is made to wait for demand: each application of genu, the
% query's and the recursive one, waits by freeze/2 until its sequence is
% bound, that is, until the consumer asks for an element. sum3's head
% binds s to <p, q, r> ++ m, which wakes genu three times; the application
% of genu not yet demanded at the end of the stage is held as a goal. This
% text is coroutines' only (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses (ISO/IEC 13211-1, 7.5;
%     Clocksin and Mellish, Programming in Prolog, 1981, chapter 1);
%     sequences as Prolog lists, [H|T] for <h> ++ t, and [P, Q, R|M] for
%     <p, q, r> ++ m (Clocksin and Mellish, chapter 3; Sterling and
%     Shapiro, The Art of Prolog, 1986, chapter 3); n + 1 and p + q + r by
%     is/2 (ISO 8.6; SWI-Prolog manual, section "Arithmetic"); a producer
%     that waits for its consumer's demand, by freeze/2 on the sequence it
%     produces (SWI-Prolog manual, section "Coroutining", freeze/2; the
%     freeze of Prolog II, Colmerauer, 1982; the lazy producers of
%     IC-Prolog, Clark, McCabe and Gregory, "IC-PROLOG language features",
%     in Clark and Taernlund (eds.), Logic Programming, 1982); the stage's
%     constant read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
genu_start(1).
% CONSTANTS END

% genu(n, s): s = <n> ++ rest, where genu(n + 1, rest); the rest is
% produced when it is demanded
genu(N, [N|Rest]) :- N1 is N + 1, freeze(Rest, genu(N1, Rest)).

% sum3(s, total): total is the sum of the first three elements of s
sum3([P, Q, R|_], Total) :- Total is P + Q + R.

unknowns(main, ['S', 'Total']).

% stage 1: genu(k, s) and sum3(s, total)
stage(1, [S, Total], Cs) :-
    memberchk(genu_start(K), Cs), freeze(S, genu(K, S)), sum3(S, Total).

query(_, _).
