% P01b. An unknown inside a structure (problems/01-unknown-equality.md).
% Stage 1: conc(<seq>, s, t). Stage 2: s = <seq>.
%
% The same text in plain, coroutines, constraints and session; tabling's
% text differs only by its table directive (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t; conc/3 as the two clauses of append/3 (Clocksin and
%     Mellish, Programming in Prolog, 1981, chapter 3; Sterling and Shapiro,
%     The Art of Prolog, 1986, chapter 3); equality as unification, =/2
%     (ISO/IEC 13211-1, 8.2.1); the stage's constants read with memberchk/2,
%     as in the harness contract's example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
conc_first([1, 2]).
% stage 2
s_value([3]).
% CONSTANTS END

% conc(a, b, c): c is a followed by b
conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

unknowns(main, ['S', 'T']).

% stage 1: conc(p, s, t)
stage(1, [S, T], Cs) :- memberchk(conc_first(P), Cs), conc(P, S, T).
% stage 2: s = q
stage(2, [S, _], Cs) :- memberchk(s_value(Q), Cs), S = Q.

query(_, _).
