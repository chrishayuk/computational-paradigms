% P04e. Unbounded alternative, alist-right, ground (problems/04-unbounded-alternative.md).
% One stage (a query): alist(<seq>), with alist-right.
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
%     unification, =/2 (ISO 8.2.1); the stage's constant read with
%     memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
alist_argument([a, a]).
% CONSTANTS END

:- table alist/1.

% alist(s), alist-right: s is a finite sequence of the atom A
alist([]).
alist([a|M]) :- alist(M).

unknowns(main, []).

% stage 1: alist(<seq>)
stage(1, [], Cs) :- memberchk(alist_argument(S), Cs), alist(S).

query(_, _).
