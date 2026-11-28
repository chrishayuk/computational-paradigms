% P10b. State replacement, a standing relation (problems/10-state-replacement.md).
% Stage 1: d = <k> * b, at all times. Stages 2-4: the stages of P10a
% (b becomes <k>; b becomes b + <k>; b becomes <k>).
%
% b is a named quantity: its current value, when it has one, is held in
% the database as the fact b(V), and replaced as in P10a. d is not given
% values: stage 1 brings the relation that defines it, and the stage
% asserts that relation as a rule, d_of(b, d), between b's value and d's.
% The query reads b's current value (left unknown while b has none) and
% applies the standing relation to it, so that d follows every value b
% takes. The relation is computed by is/2, in the direction the stages
% use, d from b. With b unknown (stage 1), is/2 raises an instantiation
% error: plain cannot hold the relation. b/1 and d_of/2 are declared
% dynamic, so that the database holds their clauses and b/1 fails while
% it has none. plain and tabling share this text
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: state replaced between stages with assertz/1 and
%     retract/1 (here retractall/1), declared with dynamic/1, which the
%     systems file names "for posing definitions and replacing state
%     between stages" (systems/swi-prolog/README.md, "The core of plain";
%     ISO/IEC 13211-1, 7.4.2.1, 8.9.1, 8.9.3; SWI-Prolog manual, section
%     "Database"); the pattern of the harness contract's replacing
%     example, a query that reads the held value
%     (harnesses/swi-prolog/README.md, 2.1; qualification program
%     x11-replace.pl); a relation that holds at all times as a rule over
%     the stored facts, a derived relation of a deductive database
%     (Kowalski, Logic for Problem Solving, 1979; Gallaire and Minker
%     (eds.), Logic and Data Bases, 1978), asserted by the stage that
%     brings it; a value that may be absent read with if-then-else, ->/2
%     and ;/2 (ISO 7.8.8); k * b and b + k by is/2 (ISO 8.6); the stage's
%     constants read with memberchk/2, as in the harness contract's
%     example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
d_equals_times_b(1, 2).
% stage 2
b_becomes(2, 10).
% stage 3
b_becomes_b_plus(3, 5).
% stage 4
b_becomes(4, 7).
% CONSTANTS END

:- dynamic b/1, d_of/2.

unknowns(main, ['B', 'D']).

% stage 1: d = k * b, at all times
stage(1, _, Cs) :-
    memberchk(d_equals_times_b(1, K), Cs), assertz((d_of(B, D) :- D is K * B)).
% stage 2: b becomes k
stage(2, _, Cs) :-
    memberchk(b_becomes(2, V), Cs), retractall(b(_)), assertz(b(V)).
% stage 3: b becomes b + k, with b at its value before the stage
stage(3, _, Cs) :-
    memberchk(b_becomes_b_plus(3, K), Cs), b(B0), V is B0 + K,
    retractall(b(_)), assertz(b(V)).
% stage 4: b becomes k
stage(4, _, Cs) :-
    memberchk(b_becomes(4, V), Cs), retractall(b(_)), assertz(b(V)).

% the query: b's current value, left unknown while b has none, and d by
% the standing relation
query(_, [B, D]) :- ( b(V) -> B = V ; true ), d_of(B, D).
