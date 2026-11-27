% P04b. Unbounded alternative, loop second (problems/04-unbounded-alternative.md).
% One stage (a query): x = <k> or loop(x), in that order.
%
% The same text in plain, coroutines, constraints and session; tabling's
% text differs only by its table directive (programs/swi-prolog/README.md).
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
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
alternative_value(1).
% CONSTANTS END

% loop(x): loop(x) if loop(x)
loop(X) :- loop(X).

unknowns(main, ['X']).

% stage 1: x = k or loop(x)
stage(1, [X], Cs) :- memberchk(alternative_value(K), Cs), ( X = K ; loop(X) ).

query(_, _).
