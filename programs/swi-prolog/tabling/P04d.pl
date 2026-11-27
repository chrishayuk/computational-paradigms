% P04d. Unbounded alternative, alist-left, open (problems/04-unbounded-alternative.md).
% One stage (a query): alist(s), with alist-left. No constants.
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
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
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

:- table alist/1.

% alist(s), alist-left: s is a finite sequence of the atom A
alist(S) :- alist(M), S = [a|M].
alist([]).

unknowns(main, ['S']).

% stage 1: alist(s)
stage(1, [S], _) :- alist(S).

query(_, _).
