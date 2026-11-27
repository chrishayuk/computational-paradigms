% P08a. Late definition, a definition that arrives (problems/08-late-definition.md).
% Stage 1: a = <x, y, z>. Stage 2: rev(a, b), with rev not yet defined.
% Stage 3: x = y. Stage 4: the definitions of rev and conc. Stage 5: y = z.
% Stage 6: b = <seq> ++ c, written as conc(<seq>, c, b), which says that b
% is <seq> followed by c (the reading of P01c in batch 1A).
%
% No declaration of rev or conc is made before its definition arrives:
% the stage that brings a definition asserts its clauses. An application
% of a relation not yet defined is a call of an undefined procedure, which
% SWI-Prolog treats as the unknown flag says (error, the ISO default, in
% the primary). In session, the configuration's S mechanism
% (harnesses/swi-prolog/S/session-wait.pl) makes that call wait in the
% engine until a stage gives the procedure a clause.
% The same text in all five configurations (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: sequences as Prolog lists, [] for the empty sequence and [H|T]
%     for <h> ++ t; conc/3 as the two clauses of append/3 (Clocksin and
%     Mellish, Programming in Prolog, 1981, chapter 3; Sterling and Shapiro,
%     The Art of Prolog, 1986, chapter 3); rev/2 as naive reverse, by
%     append/3 (the same chapter of Sterling and Shapiro); a definition
%     that arrives at a stage added to the database by assertz/1, clause by
%     clause in the order written (ISO/IEC 13211-1, 8.9.2; SWI-Prolog
%     manual, section "Database"; systems/swi-prolog/README.md, "The core
%     of plain": assertz/1 "for posing definitions"); an application of a
%     procedure with no definition left to the unknown flag, at error, its
%     ISO default (ISO 7.11.2, the flag unknown; SWI-Prolog manual, section
%     "Environment Control (Prolog flags)", unknown); equality as
%     unification, =/2 (ISO 8.2.1); the stage's constants read with
%     memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 6
b_prefix([42]).
% CONSTANTS END

unknowns(main, ['A', 'B', 'C', 'X', 'Y', 'Z']).

% stage 1: a = <x, y, z>
stage(1, [A, _, _, X, Y, Z], _) :- A = [X, Y, Z].
% stage 2: rev(a, b), with rev not yet defined
stage(2, [A, B, _, _, _, _], _) :- rev(A, B).
% stage 3: x = y
stage(3, [_, _, _, X, Y, _], _) :- X = Y.
% stage 4: the definitions of rev and conc, as in P03, in that order
stage(4, _, _) :-
    assertz(rev([], [])),
    assertz((rev([H|L], R) :- rev(L, Q), conc(Q, [H], R))),
    assertz(conc([], B, B)),
    assertz((conc([G|A], B1, [G|C]) :- conc(A, B1, C))).
% stage 5: y = z
stage(5, [_, _, _, _, Y, Z], _) :- Y = Z.
% stage 6: b = p ++ c
stage(6, [_, B, C, _, _, _], Cs) :- memberchk(b_prefix(P), Cs), conc(P, C, B).

query(_, _).
