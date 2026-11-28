% P09a. Concurrent goals, independent computations (problems/09-concurrent-goals.md).
% One stage, two separate computations, each started with spawn(), not
% conjoined and sharing no unknowns: A: loop(x); B: rev(<seq>, b).
%
% One file serves both instances, P09a.AB and P09a.BA: the spawn order is
% the harness's (stages.json, spawn_order), and the computations' text does
% not depend on it. Each computation is a spawned/4 clause (harness
% contract, 2.1 and 2.2). The same text in plain, coroutines, constraints
% and session; tabling's text differs only by its table directive
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, read as the least relation
%     (ISO/IEC 13211-1, 7.5; Clocksin and Mellish, Programming in Prolog,
%     1981, chapter 1); loop/1 as its one clause; sequences as Prolog
%     lists, [] for the empty sequence and [H|T] for <h> ++ t; conc/3 as
%     the two clauses of append/3 and rev/2 as naive reverse by append/3
%     (Clocksin and Mellish, chapter 3; Sterling and Shapiro, The Art of
%     Prolog, 1986, chapter 3; Warren's "naive reverse" benchmark for
%     DEC-10 Prolog); separate computations as the harness's spawned
%     computations, one query each (harnesses/swi-prolog/README.md, 2.1,
%     2.2); the stage's constant read with memberchk/2, as in the harness
%     contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
rev_first([1, 2, 3]).
% CONSTANTS END

% loop(x): loop(x) if loop(x)
loop(X) :- loop(X).

% conc(a, b, c): c is a followed by b
conc([], B, B).
conc([H|A], B, [H|C]) :- conc(A, B, C).

% rev(a, b): b is a in reverse order
rev([], []).
rev([H|L], R) :- rev(L, Q), conc(Q, [H], R).

unknowns('A', ['X']).
unknowns('B', ['B']).

% stage 1, computation A: loop(x)
spawned(1, 'A', [X], _) :- loop(X).
% stage 1, computation B: rev(<seq>, b)
spawned(1, 'B', [B], Cs) :- memberchk(rev_first(P), Cs), rev(P, B).
