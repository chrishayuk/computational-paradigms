% P14a, named variant "engine". A process over a message stream, messages
% as stages (problems/14-message-stream.md).
% Stage 1: INC. Stage 2: INC. Stage 3: READ(r1). Stage 4: INC.
% Stage 5: READ(r2). Each message is one stage.
%
% Named variant, session only (programs/swi-prolog/README.md). The primary
% is P14a.pl, which holds the count in the database. Here the counter is a
% process: an engine of its own, created at stage 1 holding 0, whose goal
% loops, taking one message at a time with engine_fetch/1 and answering
% with engine_yield/1, as the SWI-Prolog manual's engine that keeps a
% running sum. A stage posts its message to it with engine_post/3, and
% READ(r) makes r equal to its answer, the count. The engine is kept in
% the database between stages (it is one process, the harness's session).
% The engine keeps its own inference count; whether its inferences reach
% the stage's steps and budget is the harness's measurement, and was not
% predicted here.
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: an engine as a process with state that receives terms
%     (engine_create/3, engine_fetch/1, engine_yield/1, engine_post/3),
%     after the summing engine of the SWI-Prolog manual (section
%     "Coroutining using Prolog engines", "State accumulation using
%     engines"); the engine's handle kept as a fact with assertz/1 and
%     dynamic/1 (ISO/IEC 13211-1, 8.9.1; SWI-Prolog manual, section
%     "Database"); a message dispatched by the clause whose head matches
%     it (Clocksin and Mellish, Programming in Prolog, 1981, chapter 1); c
%     + 1 by is/2 (ISO 8.6); the stage's constants read with memberchk/2,
%     as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
message(1, inc).
% stage 2
message(2, inc).
% stage 4
message(4, inc).
% CONSTANTS END

% the counter: a process holding its count, which takes one message at a
% time (engine_fetch/1), and answers each (engine_yield/1)
counter(C) :- engine_fetch(M), take(M, C, C1, Reply), engine_yield(Reply), counter(C1).

% take(message, c, c1, reply): the count c becomes c1, and the reply
take(inc, C, C1, C1) :- C1 is C + 1.
take(read, C, C, C).

% the counter is started holding 0, and its engine kept in the database
:- dynamic counter_engine/1.
start_counter :- engine_create(_, counter(0), E), assertz(counter_engine(E)).

% receive(message): the message is posted to the counter
receive(inc) :- counter_engine(E), engine_post(E, inc, _).
receive(read(R)) :- counter_engine(E), engine_post(E, read, R).

unknowns(main, ['R1', 'R2']).

% stage 1: the counter is started, and takes the message k
stage(1, _, Cs) :- start_counter, memberchk(message(1, M), Cs), receive(M).
% stage 2: the message k
stage(2, _, Cs) :- memberchk(message(2, M), Cs), receive(M).
% stage 3: READ(r1)
stage(3, [R1, _], _) :- receive(read(R1)).
% stage 4: the message k
stage(4, _, Cs) :- memberchk(message(4, M), Cs), receive(M).
% stage 5: READ(r2)
stage(5, [_, R2], _) :- receive(read(R2)).

query(_, _).
