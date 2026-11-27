% P04a. Unbounded alternative, loop first (problems/04-unbounded-alternative.md).
% One stage (a query): loop(x) or x = <k>, in that order.
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, read as the least relation
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); disjunction by ;/2, its alternatives tried in the
%     order written (ISO 7.8.6; SWI-Prolog manual, section "Control
%     Predicates"); equality as unification, =/2 (ISO 8.2.1); the stage's
%     constant read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
alternative_value(1).
% CONSTANTS END

:- table loop/1.

% loop(x): loop(x) if loop(x)
loop(X) :- loop(X).

unknowns(main, ['X']).

% stage 1: loop(x) or x = k
stage(1, [X], Cs) :- memberchk(alternative_value(K), Cs), ( loop(X) ; X = K ).

query(_, _).
