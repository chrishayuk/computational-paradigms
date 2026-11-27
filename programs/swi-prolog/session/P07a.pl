% P07a. Simultaneous constraints, three relations, every order (problems/07-simultaneous-constraints.md).
% One stage (a query): x + y + z = <k>, y + z = <k>, z = <k>, in the instance's order,
% which h_param(order, _) gives as a list of the relations' positions as
% written ('1', '2', '3'). This file serves all six instances, P07a,
% P07a.132, P07a.213, P07a.231, P07a.312 and P07a.321. All unknowns are integers.
%
% Each relation is posted as a constraint of library(clpfd) over the
% integers, with no domain imposed and no labeling: the solver holds what
% it cannot decide and propagates what it can. constraints and session
% share this text (programs/swi-prolog/README.md).
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
%     SWI-Prolog", FLOPS 2012, LNCS 7294); a compound expression written
%     as one constraint, as SPECIFICATION.md, "Arithmetic", allows;
%     equality as unification, =/2 (ISO/IEC 13211-1, 8.2.1); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (harnesses/swi-prolog/README.md, 2.7)
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 1
sum_xyz(12).
sum_yz(7).
z_value(3).
% CONSTANTS END

% relation 1: x + y + z = k
relation('1', [X, Y, Z], Cs) :- memberchk(sum_xyz(K), Cs), X + Y + Z #= K.
% relation 2: y + z = k
relation('2', [_, Y, Z], Cs) :- memberchk(sum_yz(K), Cs), Y + Z #= K.
% relation 3: z = k
relation('3', [_, _, Z], Cs) :- memberchk(z_value(K), Cs), Z = K.

% relations(order, vs, cs): the relations the order names, in that order
relations([], _, _).
relations([N|Ns], Vs, Cs) :- relation(N, Vs, Cs), relations(Ns, Vs, Cs).

unknowns(main, ['X', 'Y', 'Z']).

% stage 1: the three relations, in the instance's order
stage(1, Vs, Cs) :- h_param(order, Order), relations(Order, Vs, Cs).

query(_, _).
