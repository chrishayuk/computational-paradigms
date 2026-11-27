% P04f. Unbounded alternative, alist-right, open (problems/04-unbounded-alternative.md).
% One stage (a query): alist(s), with alist-right. No constants.
%
% The same text in plain, coroutines, constraints and session; tabling's
% text differs only by its table directive (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t (Clocksin and Mellish, Programming in Prolog, 1981,
%     chapter 3; Sterling and Shapiro, The Art of Prolog, 1986, chapter 3);
%     the atom A as the Prolog atom a; a definition by cases as clauses in
%     the order written, read as the least relation, its conjuncts in the
%     order written (ISO/IEC 13211-1, 7.5 and 7.7); equality as
%     unification, =/2 (ISO 8.2.1)
% END PROVENANCE

% alist(s), alist-right: s is a finite sequence of the atom A
alist([]).
alist([a|M]) :- alist(M).

unknowns(main, ['S']).

% stage 1: alist(s)
stage(1, [S], _) :- alist(S).

query(_, _).
