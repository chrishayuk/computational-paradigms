% P08b. Late definition, a definition that never arrives (problems/08-late-definition.md).
% Stages 1 to 3 of P08a, and no more. Stage 1: a = <x, y, z>.
% Stage 2: rev(a, b), with rev not yet defined. Stage 3: x = y. No constants.
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
%     unification, =/2 (ISO 8.2.1)
% END PROVENANCE

unknowns(main, ['A', 'B', 'X', 'Y', 'Z']).

% stage 1: a = <x, y, z>
stage(1, [A, _, X, Y, Z], _) :- A = [X, Y, Z].
% stage 2: rev(a, b), with rev not yet defined
stage(2, [A, B, _, _, _], _) :- rev(A, B).
% stage 3: x = y
stage(3, [_, _, X, Y, _], _) :- X = Y.

query(_, _).
