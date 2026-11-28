% P12a. Large alternative space, two solutions, at depth 1 and depth n
% (problems/12-large-alternative-space.md).
% One stage: choice(n, s) and accept(s), in that order, accept given by
% facts in a closed world: <r>, and l repeated n times. Posed at n = 8, 12 and 16, for all
% solutions (answers(20)) and for any one (answers(1)).
%
% One file serves the sub-problem's six instances: n comes from the
% harness (h_param/2), and the answer mode is the harness's cap. choice is
% transcribed as clauses, its cases and its disjunction in the order
% written; s is searched by the configuration's own strategy. accept's
% facts depend on n, so the CONSTANTS block holds them for each n the
% problem poses, as accept_fact(n, s), and accept(s) is membership among
% the facts for this n, by member/2 over the stage's constants, as pick is
% in this system's P05 programs. Each candidate is counted (h_candidate/0)
% just before accept(s) is evaluated on it.
% The tabling text: the plain text with the relation the problem defines
% (choice) tabled, as in every tabling program here; accept's facts are
% constants, and are not tabled (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a definition by cases as clauses, in the order written, read
%     as the least relation and searched depth-first by SLD resolution
%     with backtracking (ISO/IEC 13211-1, 7.5, 7.7; Clocksin and Mellish,
%     Programming in Prolog, 1981, chapters 1 and 3); sequences as Prolog
%     lists, [] for the empty sequence and [E|T] for <e> ++ t (Sterling
%     and Shapiro, The Art of Prolog, 1986, chapter 3); the atoms L and R
%     as l and r; disjunction by ;/2, tried in the order written (ISO
%     7.8.6); n > 0 by arithmetic comparison and n - 1 by is/2 (ISO 8.6,
%     8.7); a relation given by facts in a closed world, its facts the
%     stage's constants, matched with member/2 of library(lists), as in the
%     harness contract's example (harnesses/swi-prolog/README.md, 2.7) and
%     this system's P05 programs; n read with h_param/2 and candidates
%     counted with h_candidate/0, the harness's calls (2.3)
%   tabling: the table/1 directive on the problem's relation (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
accept_fact(8, [r]).
accept_fact(8, [l, l, l, l, l, l, l, l]).
accept_fact(12, [r]).
accept_fact(12, [l, l, l, l, l, l, l, l, l, l, l, l]).
accept_fact(16, [r]).
accept_fact(16, [l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l]).
% CONSTANTS END

:- table choice/2.

% choice(n, s): s is a sequence over l and r, of length at most n
choice(_, []).
choice(N, [E|T]) :- N > 0, ( E = l ; E = r ), N1 is N - 1, choice(N1, T).

unknowns(main, ['S']).

% stage 1: choice(n, s) and accept(s), with accept's facts for this n
stage(1, [S], Cs) :-
    h_param(n, N), choice(N, S), h_candidate, member(accept_fact(N, S), Cs).

query(_, _).
