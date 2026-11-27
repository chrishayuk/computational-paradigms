% P03e. Reversible relations, rev, forwards (problems/03-reversible-relations.md).
% One stage (a query): rev(<seq>, b).
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
%     The Art of Prolog, 1986, chapter 3); rev/2 as naive reverse, by
%     append/3 (the same chapter of Sterling and Shapiro; Warren's "naive
%     reverse" benchmark for DEC-10 Prolog); one definition used in the
%     direction the query poses, by unification (the same sources); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
rev_first([1, 2, 3]).
% CONSTANTS END

% conc(a, b, c): c is a followed by b
conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

% rev(a, b): b is a in reverse order
rev([], []).
rev([H|L], R) :- rev(L, Q), conc(Q, [H], R).

unknowns(main, ['B']).

% stage 1: rev(<seq>, b)
stage(1, [B], Cs) :- memberchk(rev_first(P), Cs), rev(P, B).

query(_, _).
