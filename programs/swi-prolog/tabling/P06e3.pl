% P06e3. Clark's students, open query (problems/06-negation.md).
% One stage (a query): nonmajor(p), over the closed world of <facts>.
%
% The closed world's facts are the stage's constants. The stage asserts
% them as clauses of student/1, maths/1 and takes/2 (declared dynamic, so
% that a relation with no facts has no instances, as the closed world
% says), and then poses the query. not takes(p, k) is negation as
% failure; p and k are known when it is reached, by the order of the
% conjuncts as written.
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
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
%     negation as failure, \+/1 (ISO 8.15.1; Clark, 1978)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
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
% CONSTANTS END

:- dynamic student/1, maths/1, takes/2.

:- table nonmajor/1.

% nonmajor(p): p is a student who does not take some maths course
nonmajor(P) :- student(P), maths(K), \+ takes(P, K).

unknowns(main, ['P']).

% stage 1: the closed world, then nonmajor(p)
stage(1, [P], Cs) :-
    forall(member(F, Cs), assertz(F)),
    nonmajor(P).

query(_, _).
