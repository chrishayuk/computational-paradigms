% P07d. Simultaneous constraints, a product, u and v given (problems/07-simultaneous-constraints.md).
% One stage (a query): w * u = v, u = <k>, v = <k>. All unknowns are integers.
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
u_value(2).
v_value(14).
% CONSTANTS END

unknowns(main, ['W', 'U', 'V']).

% stage 1: w * u = v, u = k1, v = k2
stage(1, [W, U, V], Cs) :-
    W * U #= V,
    memberchk(u_value(K1), Cs), U = K1,
    memberchk(v_value(K2), Cs), V = K2.

query(_, _).
