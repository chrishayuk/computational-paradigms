% P10d. State replacement, retraction of a constraint
% (problems/10-state-replacement.md).
% Stage 1: pick(x), as in P05. Stage 2: x > <k>. Stage 3: withdraw the
% relation of stage 2 (a retracting stage).
%
% A relation posed as a goal of a conjunction cannot be withdrawn from
% it, so the information of each stage is held in the database, where a
% later stage can remove it. Stage 1 asserts pick's closed world of facts
% as clauses of pick/1. Stage 2 asserts the comparison as a held
% relation, held(y, y > k), a fact that pairs the relation with its
% unknown. Stage 3 removes exactly that relation (retract/1, with stage
% 2's constant). The query solves over what is held: pick(x), then every
% held relation on x. x > k is compared by >/2. In a
% reposed run every stage, the withdrawal included, is replayed and
% carried out in order. pick/1 and held/2 are declared dynamic, so that
% the database holds their clauses and held/2 fails while it has none.
% plain and tabling share this text (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: information added and withdrawn between stages with assertz/1
%     and retract/1, declared with dynamic/1, which the systems file
%     names "for posing definitions and replacing state between stages"
%     (systems/swi-prolog/README.md, "The core of plain"; ISO/IEC
%     13211-1, 7.4.2.1, 8.9.1, 8.9.3; SWI-Prolog manual, section
%     "Database"); a closed world as facts in the database, each entry
%     taken by forall/2 and member/2 (as in this system's P06e programs;
%     SWI-Prolog manual, sections "forall/2" and "library(lists)"); a query
%     that reads what is held, as in the harness contract's replacing
%     example (harnesses/swi-prolog/README.md, 2.1; qualification program
%     x11-replace.pl); every held relation applied by forall/2 and call/1
%     (ISO 7.8.3); x > k by arithmetic comparison, >/2 (ISO 8.7); the
%     stage's constants read with memberchk/2, as in the harness
%     contract's example (2.7)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
pick(1).
pick(2).
pick(3).
% stage 2
greater_than(1).
% CONSTANTS END

:- dynamic pick/1, held/2.

unknowns(main, ['X']).

% stage 1: pick(x), over the closed world of the pick facts
stage(1, _, Cs) :- forall(member(pick(V), Cs), assertz(pick(V))).
% stage 2: x > k
stage(2, _, Cs) :- memberchk(greater_than(K), Cs), assertz(held(Y, Y > K)).
% stage 3: withdraw x > k, the relation of stage 2
stage(3, _, Cs) :- memberchk(greater_than(K), Cs), retract(held(_, _ > K)).

% the query: pick(x), and every relation held on x
query(_, [X]) :- pick(X), forall(held(X, R), call(R)).
