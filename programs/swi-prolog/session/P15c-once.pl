% P15c, named variant "once". Merge and committed choice, one resource,
% two requests at once (problems/15-merge-and-committed-choice.md).
% One stage, an any-one query: grant(<atom>, <atom>, g).
%
% Named variant (programs/swi-prolog/README.md): the primary, P15c.pl,
% with the application of grant committed by once/1, so that the first
% solution is kept and the other case is not tried on backtracking. once/1
% is control (C): commitment beyond the definition. grant is transcribed
% as its two cases, in the order written, as facts. The same text in
% plain, coroutines, constraints and session; tabling's text adds only its
% table directive.
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as facts, tried in the order written
%     (ISO/IEC 13211-1, 7.5, 7.7; Clocksin and Mellish, Programming in
%     Prolog, 1981, chapter 1); don't-care commitment to the first
%     solution by once/1 (ISO 8.15.2; SWI-Prolog manual, section "Control
%     Predicates"); the stage's constants read with memberchk/2, as in the
%     harness contract's example (harnesses/swi-prolog/README.md, 2.7)
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

% stage 1: grant(p, q, g), committed to the first solution
stage(1, [G], Cs) :-
    memberchk(first_request(P), Cs), memberchk(second_request(Q), Cs),
    once(grant(P, Q, G)).

query(_, _).
