% P14c. A process over a message stream, a stream that stays open
% (problems/14-message-stream.md).
% The stages of P14a (INC, INC, READ(r1), INC, READ(r2)), then stage 6:
% INC, and stage 7: READ(r3). No stage closes the stream.
%
% The P14a text, with two more stages. The counter holds its count, 0 at
% first, and receives one message per stage, in the order they arrive. The
% count is a named quantity held in the database as the fact count(C), as
% P10 holds its quantities: INC replaces it by C + 1 (retractall/1, then
% assertz/1); READ(r) makes r equal to it. receive/1 has one clause per
% message, the cases of run/2 that take a message (2: INC; 3: READ).
% Nothing closes the stream: the counter accepts a message after any
% stage. In a reposed run every stage is replayed and carried out in
% order, from the count 0 of a fresh process. Nothing to table, delay or
% constrain, so this one text serves every configuration; in session the
% count stays in the one process between stages
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: state replaced between stages with assertz/1 and retract/1
%     (here retractall/1), declared with dynamic/1, which the systems file
%     names for that purpose (systems/swi-prolog/README.md, "The core of
%     plain"; ISO/IEC 13211-1, 7.4.2.1, 8.9.1, 8.9.3; SWI-Prolog manual,
%     section "Database"), as in this system's P10 programs and the
%     harness's replacing example (qualification program x11-replace.pl);
%     a message dispatched by the clause whose head matches it (Clocksin
%     and Mellish, Programming in Prolog, 1981, chapter 1; Sterling and
%     Shapiro, The Art of Prolog, 1986, chapter 1); c + 1 by is/2 (ISO
%     8.6); equality as unification, =/2 (ISO 8.2.1); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
message(1, inc).
% stage 2
message(2, inc).
% stage 4
message(4, inc).
% stage 6
message(6, inc).
% CONSTANTS END

% the counter's count, 0 at first
:- dynamic count/1.
count(0).

% receive(message): the counter takes one message
receive(inc) :- count(C), C1 is C + 1, retractall(count(_)), assertz(count(C1)).
receive(read(R)) :- count(C), R = C.

unknowns(main, ['R1', 'R2', 'R3']).

% stage 1: the message k
stage(1, _, Cs) :- memberchk(message(1, M), Cs), receive(M).
% stage 2: the message k
stage(2, _, Cs) :- memberchk(message(2, M), Cs), receive(M).
% stage 3: READ(r1)
stage(3, [R1, _, _], _) :- receive(read(R1)).
% stage 4: the message k
stage(4, _, Cs) :- memberchk(message(4, M), Cs), receive(M).
% stage 5: READ(r2)
stage(5, [_, R2, _], _) :- receive(read(R2)).
% stage 6: the message k
stage(6, _, Cs) :- memberchk(message(6, M), Cs), receive(M).
% stage 7: READ(r3)
stage(7, [_, _, R3], _) :- receive(read(R3)).

query(_, _).
