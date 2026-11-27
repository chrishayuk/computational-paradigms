% P06d. Set difference (problems/06-negation.md).
% One stage (a query): setdiff(<seq>, <seq>, d).
%
% not mem(h, s2) is negation as failure, \+ mem(H, S2). Both sequences are
% given, so h and s2 are known when each negation is reached, by the order
% of the conjuncts as written.
% The tabling text: the plain text with the relations the problem defines
% tabled, as in every tabling program here (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t (Clocksin and Mellish, Programming in Prolog, 1981,
%     chapter 3; Sterling and Shapiro, The Art of Prolog, 1986, chapter 3);
%     mem/2 as the two clauses of member/2 in those chapters; each
%     definition as clauses in the order written, their conjuncts in the
%     order written (ISO/IEC 13211-1, 7.5 and 7.7); not R as negation as
%     failure, \+/1 (ISO 8.15.1; Clark, "Negation as failure", 1978); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (harnesses/swi-prolog/README.md, 2.7)
%   tabling: the table/1 directive on the problem's relations (SWI-Prolog
%     manual, section "Tabled execution (SLG resolution)")
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
setdiff_first([1, 2, 3, 4]).
setdiff_second([2, 4, 6]).
% CONSTANTS END

:- table mem/2, setdiff/3.

% mem(e, s): e is an element of the sequence s
mem(E, [E|_]).
mem(E, [_|T]) :- mem(E, T).

% setdiff(s1, s2, d): d is the elements of s1 that are not elements of s2,
% in their order in s1
setdiff([], _, []).
setdiff([H|T], S2, D) :- mem(H, S2), setdiff(T, S2, D).
setdiff([H|T], S2, [H|D]) :- \+ mem(H, S2), setdiff(T, S2, D).

unknowns(main, ['D']).

% stage 1: setdiff(<seq>, <seq>, d)
stage(1, [D], Cs) :-
    memberchk(setdiff_first(S1), Cs),
    memberchk(setdiff_second(S2), Cs),
    setdiff(S1, S2, D).

query(_, _).
