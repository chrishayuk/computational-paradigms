% P10c. State replacement, a snapshot (problems/10-state-replacement.md).
% Stage 1: b becomes <k>. Stage 2: d becomes <k> * b. Stage 3: b becomes
% b + <k>. Stage 4: b becomes <k>. Every stage replaces.
%
% b and d are named quantities, not unknowns: each one's current value,
% when it has one, is held in the database as a fact, b(V) or d(V).
% "q becomes e" reads the values e uses as they are before the stage,
% computes e by is/2, and replaces q's fact (retractall/1, then
% assertz/1). d's value is computed once, at stage 2, from b's value then.
% The query reads each quantity's current value; a quantity with no value
% yet (d, at stage 1) is left unknown. b/1 and d/1 are declared dynamic,
% so that the database holds their clauses and d/1 fails while it has
% none. The problem defines no relation, and has nothing to delay or
% constrain, so this one text serves every configuration
% (programs/swi-prolog/README.md).
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
%     x11-replace.pl); a value that may be absent read with if-then-else,
%     ->/2 and ;/2 (ISO 7.8.8); k * b and b + k by is/2 (ISO 8.6); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
b_becomes(1, 10).
% stage 2
d_becomes_times_b(2, 2).
% stage 3
b_becomes_b_plus(3, 5).
% stage 4
b_becomes(4, 7).
% CONSTANTS END

:- dynamic b/1, d/1.

unknowns(main, ['B', 'D']).

% stage 1: b becomes k
stage(1, _, Cs) :-
    memberchk(b_becomes(1, V), Cs), retractall(b(_)), assertz(b(V)).
% stage 2: d becomes k * b, with b at its value before the stage
stage(2, _, Cs) :-
    memberchk(d_becomes_times_b(2, K), Cs), b(B0), V is K * B0,
    retractall(d(_)), assertz(d(V)).
% stage 3: b becomes b + k, with b at its value before the stage
stage(3, _, Cs) :-
    memberchk(b_becomes_b_plus(3, K), Cs), b(B0), V is B0 + K,
    retractall(b(_)), assertz(b(V)).
% stage 4: b becomes k
stage(4, _, Cs) :-
    memberchk(b_becomes(4, V), Cs), retractall(b(_)), assertz(b(V)).

% the query: the current values of b and of d; d is left unknown while it
% has no value
query(_, [B, D]) :- b(B), ( d(V) -> D = V ; true ).
