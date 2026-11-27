% P01c. A self-referential equation (problems/01-unknown-equality.md).
% Stage 1 (a query): x = <seq> ++ x, written as conc(<seq>, x, x), which
% says that x is <seq> followed by x. occurs_check is false, SWI-Prolog's
% default (systems/swi-prolog/README.md); P01c-occurs-check.pl is the
% recorded variant with occurs_check true.
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists; conc/3 as the two clauses of append/3
%     (Clocksin and Mellish, Programming in Prolog, 1981, chapter 3; Sterling
%     and Shapiro, The Art of Prolog, 1986, chapter 3); unification without
%     occurs check, giving a rational tree (Colmerauer, "Prolog and infinite
%     trees", in Clark and Taernlund, Logic Programming, 1982; SWI-Prolog
%     manual, section "Rational trees (cyclic terms)"); the stage's
%     constant read with memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
prefix([1]).
% CONSTANTS END

:- table conc/3.

% conc(a, b, c): c is a followed by b
conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

unknowns(main, ['X']).

% stage 1: x = p ++ x
stage(1, [X], Cs) :- memberchk(prefix(P), Cs), conc(P, X, X).

query(_, _).
