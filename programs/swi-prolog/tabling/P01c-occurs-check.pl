% P01c, named variant "occurs-check": the primary P01c.pl with the flag
% occurs_check set to true, the variant the systems file records for P01c
% (systems/swi-prolog/README.md, "Flags"). Not the primary.
% Stage 1 (a query): x = <seq> ++ x, written as conc(<seq>, x, x).
%
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: as P01c.pl; the occurs_check flag (SWI-Prolog manual, section
%     "Environment Control (Prolog flags)", flag occurs_check), set by a
%     directive as the harness contract asks of the systems file's recorded
%     variants (harnesses/swi-prolog/README.md, 1)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

:- set_prolog_flag(occurs_check, true).

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
