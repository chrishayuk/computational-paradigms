% P10a. State replacement, absolute and relative replacement
% (problems/10-state-replacement.md).
% Stage 1: b becomes <k>. Stage 2: b becomes b + <k>. Stage 3: b becomes <k>.
% Every stage replaces.
%
% b is a named quantity, not an unknown: its one current value is held in
% the database as the fact b(V). "b becomes e" reads b's value before the
% stage (where e uses it), computes e by is/2, and replaces the fact
% (retractall/1, then assertz/1). The query reads the current value. In a
% reposed run every stage is replayed and carried out in order. b/1 is
% declared dynamic, so that the database holds its clauses. The problem
% defines no relation, and has nothing to delay or constrain, so this one
% text serves every configuration (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: state replaced between stages with assertz/1 and
%     retract/1 (here retractall/1), declared with dynamic/1, which the
%     systems file names for that purpose (systems/swi-prolog/README.md,
%     "The core of plain"; ISO/IEC 13211-1, 7.4.2.1, 8.9.1, 8.9.3;
%     SWI-Prolog manual, section "Database"), the pattern of the harness
%     contract's replacing example, a query that reads the held value
%     (harnesses/swi-prolog/README.md, 2.1; qualification program
%     x11-replace.pl); b + k by is/2 (ISO 8.6); the stage's constants read
%     with memberchk/2, as in the harness contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
b_becomes(1, 10).
% stage 2
b_becomes_b_plus(2, 5).
% stage 3
b_becomes(3, 7).
% CONSTANTS END

:- dynamic b/1.

unknowns(main, ['B']).

% stage 1: b becomes k
stage(1, _, Cs) :-
    memberchk(b_becomes(1, V), Cs), retractall(b(_)), assertz(b(V)).
% stage 2: b becomes b + k, with b at its value before the stage
stage(2, _, Cs) :-
    memberchk(b_becomes_b_plus(2, K), Cs), b(B0), V is B0 + K,
    retractall(b(_)), assertz(b(V)).
% stage 3: b becomes k
stage(3, _, Cs) :-
    memberchk(b_becomes(3, V), Cs), retractall(b(_)), assertz(b(V)).

% the query: the current value of b
query(_, [B]) :- b(B).
