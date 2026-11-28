% P09d. Concurrent goals, an unbounded producer (problems/09-concurrent-goals.md).
% One stage, one computation: genu(<k>, s) and sum3(s, total), in that order.
% Run once and classified under two readings (P09d1, finite; P09d2, stream).
%
% The coroutines text, with the arithmetic as constraints of
% library(clpfd) over the integers (no domain imposed, no labeling), as in
% every constraints program here. The producer waits for demand by
% freeze/2, as in the coroutines text. constraints and session share this
% text (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses (ISO/IEC 13211-1, 7.5;
%     Clocksin and Mellish, Programming in Prolog, 1981, chapter 1);
%     sequences as Prolog lists, [H|T] for <h> ++ t, and [P, Q, R|M] for
%     <p, q, r> ++ m (Clocksin and Mellish, chapter 3; Sterling and
%     Shapiro, The Art of Prolog, 1986, chapter 3); integer arithmetic as
%     constraints of library(clpfd), #=/2, over the unbounded integers
%     (SWI-Prolog manual, section "library(clpfd)"; Triska, FLOPS 2012,
%     LNCS 7294); a producer that waits for its consumer's demand, by
%     freeze/2 on the sequence it produces (SWI-Prolog manual, section
%     "Coroutining", freeze/2; the freeze of Prolog II, Colmerauer, 1982;
%     the lazy producers of IC-Prolog, Clark, McCabe and Gregory,
%     "IC-PROLOG language features", in Clark and Taernlund (eds.), Logic
%     Programming, 1982); the stage's constant read with memberchk/2, as
%     in the harness contract's example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 1
genu_start(1).
% CONSTANTS END

% genu(n, s): s = <n> ++ rest, where genu(n + 1, rest); the rest is
% produced when it is demanded
genu(N, [N|Rest]) :- N1 #= N + 1, freeze(Rest, genu(N1, Rest)).

% sum3(s, total): total is the sum of the first three elements of s
sum3([P, Q, R|_], Total) :- P + Q + R #= Total.

unknowns(main, ['S', 'Total']).

% stage 1: genu(k, s) and sum3(s, total)
stage(1, [S, Total], Cs) :-
    memberchk(genu_start(K), Cs), freeze(S, genu(K, S)), sum3(S, Total).

query(_, _).
