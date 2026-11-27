% P02b.R1R2R3. Late information, every order: this instance's order is
% R1, R2, R3, one relation per stage (problems/02-late-information.md).
% R1: u + v = <k>. R2: w * u = v. R3: u + <k> = <k>. All unknowns are integers.
%
% Each relation is posted as a constraint of library(clpfd) over the
% integers, with no domain imposed and no labeling: the solver holds what
% it cannot decide and propagates as information arrives.
% P02b: one file per order, since each relation's constants are tagged
% with the stage that brings it (harnesses/swi-prolog/README.md, 2.5); the
% files of a configuration differ only in their CONSTANTS block and their
% stage/3 clauses.
% constraints and session share this text (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: integer arithmetic as constraints with #=/2 of library(clpfd),
%     over the unbounded integers (no domain imposed, no labeling), the
%     library's own advice to use #= in place of is/2 for integer
%     arithmetic in every direction (SWI-Prolog manual, section
%     "library(clpfd): CLP(FD): Constraint Logic Programming over Finite
%     Domains"; Triska, "The finite domain constraint solver of
%     SWI-Prolog", FLOPS 2012, LNCS 7294); the stage's constants read with
%     memberchk/2, as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 1
r1_sum(16).
% stage 3
r3_addend(10).
r3_sum(12).
% CONSTANTS END

% R1: u + v = k
r1([U, V, _], Cs) :- memberchk(r1_sum(K), Cs), U + V #= K.
% R2: w * u = v
r2([U, V, W], _) :- W * U #= V.
% R3: u + k1 = k2
r3([U, _, _], Cs) :- memberchk(r3_addend(K1), Cs), memberchk(r3_sum(K2), Cs), U + K1 #= K2.

unknowns(main, ['U', 'V', 'W']).

stage(1, Vs, Cs) :- r1(Vs, Cs).
stage(2, Vs, Cs) :- r2(Vs, Cs).
stage(3, Vs, Cs) :- r3(Vs, Cs).

query(_, _).
