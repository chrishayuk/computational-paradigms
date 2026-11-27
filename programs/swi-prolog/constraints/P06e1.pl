% P06e1. Clark's students, a ground query (problems/06-negation.md).
% One stage (a query): nonmajor(<atom>), over the closed world of <facts>.
%
% The closed world's facts are the stage's constants. The stage asserts
% them as clauses of student/1, maths/1 and takes/2 (declared dynamic, so
% that a relation with no facts has no instances, as the closed world
% says), and then poses the query. not takes(p, k) is negation as
% failure; p and k are known when it is reached, by the order of the
% conjuncts as written. The queried atom's entry is asserted with the
% facts, as queried/1, which nothing calls; it is read with memberchk/2.
% The same text in plain, coroutines, constraints and session; tabling's
% text differs only by its table directive (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a closed world as facts (Clark, "Negation as failure", 1978;
%     the example as rendered by Elcock, 1990), put into the database by
%     assertz/1 with a dynamic/1 declaration, as the harness contract
%     advises for constants needed as clauses (harnesses/swi-prolog/README.md,
%     2.5; ISO/IEC 13211-1, 7.4.2.1 and 8.9.2; SWI-Prolog manual, section
%     "Database"), each entry taken by forall/2 and member/2 (SWI-Prolog
%     manual, sections "forall/2" and "library(lists)"); nonmajor/1 as one
%     clause, its conjuncts in the order written (ISO 7.7); not R as
%     negation as failure, \+/1 (ISO 8.15.1; Clark, 1978); the
%     queried atom read with memberchk/2, as in the harness contract's
%     example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
student(brown).
student(smith).
maths(c101).
maths(c301).
takes(brown, c101).
takes(smith, c101).
takes(smith, c301).
queried(brown).
% CONSTANTS END

:- dynamic student/1, maths/1, takes/2.

% nonmajor(p): p is a student who does not take some maths course
nonmajor(P) :- student(P), maths(K), \+ takes(P, K).

unknowns(main, []).

% stage 1: the closed world, then nonmajor(<atom>)
stage(1, [], Cs) :-
    forall(member(F, Cs), assertz(F)),
    memberchk(queried(P), Cs),
    nonmajor(P).

query(_, _).
