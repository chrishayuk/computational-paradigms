% P15d. Merge and committed choice, one resource, over time
% (problems/15-merge-and-committed-choice.md).
% Stage 1: <atom> requests. Stage 2: <atom> requests. Stage 3: <atom>
% releases. Each stage replaces.
%
% holder and queue are named quantities, as in P10, held in the database
% as the facts holder(H) and queue(Q), starting as none and <>. A request
% and a release are the problem's replacing cases, each "if ... otherwise"
% an if-then-else on its condition; "q becomes e" is retractall/1, then
% assertz/1, as in this system's P10 programs. A release applies only
% where holder = p. queue ++ <p> is append/3. B's waiting is held as its
% place in the queue. In a reposed run every stage is replayed and carried
% out in order, from a fresh process's none and <>. Nothing to table,
% delay or constrain, so this one text serves every configuration; in
% session the quantities stay in the one process between stages
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
%     a case "if c, then ..., otherwise ..." as if-then-else (ISO 7.8.8);
%     a sequence followed by another by append/3 (library(lists);
%     SWI-Prolog manual, section "library(lists): List Manipulation");
%     equality as unification, =/2 (ISO 8.2.1); a query that reads the
%     held values (harnesses/swi-prolog/README.md, 2.1); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
requests(1, a).
% stage 2
requests(2, b).
% stage 3
releases(3, a).
% CONSTANTS END

% holder and queue, starting as none and <>
:- dynamic holder/1, queue/1.
holder(none).
queue([]).

holder_becomes(H) :- retractall(holder(_)), assertz(holder(H)).
queue_becomes(Q) :- retractall(queue(_)), assertz(queue(Q)).

% p requests: if holder = none, holder becomes p; otherwise queue becomes
% queue ++ <p>
request(P) :-
    holder(H),
    (   H = none
    ->  holder_becomes(P)
    ;   queue(Q), append(Q, [P], Q1), queue_becomes(Q1)
    ).

% p releases, where holder = p: if queue = <>, holder becomes none;
% otherwise, with queue = <h> ++ t, holder becomes h and queue becomes t
release(P) :-
    holder(P),
    queue(Q),
    (   Q = []
    ->  holder_becomes(none)
    ;   Q = [H|T], holder_becomes(H), queue_becomes(T)
    ).

unknowns(main, ['Holder', 'Queue']).

% stage 1: p requests
stage(1, _, Cs) :- memberchk(requests(1, P), Cs), request(P).
% stage 2: p requests
stage(2, _, Cs) :- memberchk(requests(2, P), Cs), request(P).
% stage 3: p releases
stage(3, _, Cs) :- memberchk(releases(3, P), Cs), release(P).

% the query: the current values of holder and queue
query(_, [Holder, Queue]) :- holder(Holder), queue(Queue).
