% P14b. A process over a message stream, messages as one sequence
% (problems/14-message-stream.md).
% One stage (a query): the counter receives <INC, INC, READ(r1), INC,
% READ(r2)>, posed as run(m, 0).
%
% run/2 is transcribed as its three cases, in the order written, with the
% sequence of messages as a Prolog list. The messages that are atoms are
% the stage's constants, by their position in the sequence, as P14a's are
% by their stage. The tabling text: the plain text with the relations the
% problem defines tabled, as in every tabling program here
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, tried in the order written
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); sequences as Prolog lists, recursion on the list's
%     tail (Clocksin and Mellish, chapter 3; Sterling and Shapiro, The Art
%     of Prolog, 1986, chapter 3); c + 1 by is/2 (ISO 8.6); equality as
%     unification, =/2 (ISO 8.2.1); the stage's constants read with
%     memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
message(1, inc).
message(2, inc).
message(4, inc).
% CONSTANTS END

:- table run/2.

% run(m, c): the counter, with count c, receives the messages m
run([], _).
run([inc|S], C) :- C1 is C + 1, run(S, C1).
run([read(R)|S], C) :- R = C, run(S, C).

unknowns(main, ['R1', 'R2']).

% stage 1: run(<k1, k2, READ(r1), k4, READ(r2)>, 0)
stage(1, [R1, R2], Cs) :-
    memberchk(message(1, M1), Cs), memberchk(message(2, M2), Cs),
    memberchk(message(4, M4), Cs),
    run([M1, M2, read(R1), M4, read(R2)], 0).

query(_, _).
