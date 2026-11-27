% P08c. Late definition, a definition that arrives in parts
% (problems/08-late-definition.md).
% Stage 1: the definition of conc. Stage 2: rev(<seq>, b), with rev not
% yet defined. Stage 3: rev, case 1 only: rev(<seq>, <seq>). Stage 4: rev,
% case 2.
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
% stage 2
rev_argument([1, 2]).
% stage 3
rev_case_1([], []).
% CONSTANTS END

unknowns(main, ['B']).

% stage 1: the definition of conc
stage(1, _, _) :-
    assertz(conc([], B, B)),
    assertz((conc([H|A], B1, [H|C]) :- conc(A, B1, C))).
% stage 2: rev(<seq>, b), with rev not yet defined
stage(2, [B], Cs) :- memberchk(rev_argument(P), Cs), rev(P, B).
% stage 3: rev, case 1 only: rev(s, t), as its constants give it
stage(3, _, Cs) :- memberchk(rev_case_1(S, T), Cs), assertz(rev(S, T)).
% stage 4: rev, case 2
stage(4, _, _) :- assertz((rev([H|L], R) :- rev(L, Q), conc(Q, [H], R))).

query(_, _).
