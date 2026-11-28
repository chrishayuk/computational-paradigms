% P15c. Merge and committed choice, one resource, two requests at once
% (problems/15-merge-and-committed-choice.md).
% One stage, an any-one query: grant(<atom>, <atom>, g).
%
% grant is transcribed as its two cases, in the order written, as facts.
% The choice between them is SLD resolution's: the first case is tried
% first, and the harness collects one answer. Nothing is added to commit
% to it: whether the choice is revisited on backtracking is the system's.
% (The named variant P15c-once.pl commits with once/1.) The same text in
% plain, coroutines, constraints and session; tabling's text adds only its
% table directive (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as facts, tried in the order written
%     (ISO/IEC 13211-1, 7.5, 7.7; Clocksin and Mellish, Programming in
%     Prolog, 1981, chapter 1); the stage's constants read with
%     memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
first_request(a).
second_request(b).
% CONSTANTS END

% grant(p, q, g): of two requests, from p and from q, g is the one granted
grant(P, _, P).
grant(_, Q, Q).

unknowns(main, ['G']).

% stage 1: grant(p, q, g)
stage(1, [G], Cs) :-
    memberchk(first_request(P), Cs), memberchk(second_request(Q), Cs), grant(P, Q, G).

query(_, _).
