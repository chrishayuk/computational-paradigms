% P03b. Reversible relations, conc, splitting (problems/03-reversible-relations.md).
% One stage (a query): conc(a, b, <seq>).
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t; conc/3 as the two clauses of append/3 (Clocksin and
%     Mellish, Programming in Prolog, 1981, chapter 3; Sterling and Shapiro,
%     The Art of Prolog, 1986, chapter 3); one definition used in every
%     direction, by unification (the same sources); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
conc_whole([1, 2]).
% CONSTANTS END

:- table conc/3.

% conc(a, b, c): c is a followed by b
conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

unknowns(main, ['A', 'B']).

% stage 1: conc(a, b, <seq>)
stage(1, [A, B], Cs) :- memberchk(conc_whole(R), Cs), conc(A, B, R).

query(_, _).
