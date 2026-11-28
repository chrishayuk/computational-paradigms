% P11d. Irreversible effects, commitment, then a contradiction
% (problems/11-irreversible-effects.md). Queries for any one outcome.
% Stage 1: pick(x) and emit(x). Stage 2: commit. Stage 3: x /= <k>.
%
% Each stage is written as the problem states it, with nothing that defers
% emit: emit(x) is called wherever the conjunction reaches it, on whatever
% value x has then, replays included. The commit stage adds nothing when it
% is first posed: the system selects its outcome by the answer the harness
% collects, answers(1). When a later stage is posed by reposing, the commit
% stage is replayed as the information x = v, with v as first selected
% (harness contract, 2.3, h_commitment/1). x /= k is dif/2, as in this
% system's P05 programs; pick binds x first, so it is decided at once.
% coroutines, constraints and session share this text
% (programs/swi-prolog/README.md).
%
% PROVENANCE
%   author: implementation-swi-prolog, an agent (Claude Opus 5.5, claude-opus-5-5)
%   precursor seen: no (the absys E01-E09 programs were not seen)
%   idioms: a relation given by facts in a closed world, its facts the
%     constants of the stage that first uses them, in the order the problem
%     gives them, enumerated by backtracking with member/2 of
%     library(lists), as in the harness contract's example
%     (harnesses/swi-prolog/README.md, 2.7; SWI-Prolog manual, section
%     "library(lists)"), and as in this system's P05 programs; the other
%     constants read with memberchk/2, as in the same example; a conjunction
%     by ,/2 in the order written (ISO/IEC 13211-1, 7.8.5); emit(x) as the
%     harness's effects stub, emit/1 (harnesses/swi-prolog/README.md, 2.3);
%     x /= k by dif/2, which holds of every value, as the problem's /= does
%     (SWI-Prolog manual, section "Coroutining", dif/2; the dif of Prolog
%     II, Colmerauer, 1982); the commit replayed as x = v, read from the
%     harness's verbatim answer with term_string/3 and its variable_names
%     option, then called, as in the harness's commit example
%     (h_commitment/1; qualification program x02-commit.pl; SWI-Prolog
%     manual, section "term_string/3"), within an if-then-else, ->/2 and ;/2
%     (ISO 7.8.8)
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
pick(1).
pick(2).
pick(3).
% stage 3
not_equal_to(1).
% CONSTANTS END

unknowns(main, ['X']).

% stage 1: pick(x) and emit(x)
stage(1, [X], Cs) :- member(pick(X), Cs), emit(X).
% stage 2: commit
stage(2, [X], _) :- ( h_commitment(V) -> committed_value(V, X) ; true ).
% stage 3: x /= k
stage(3, [X], Cs) :- memberchk(not_equal_to(K), Cs), dif(X, K).

query(_, _).

% the commit stage: the system selects its current outcome by answering
% (answers(1)). When the stage is replayed, the outcome it first selected,
% v, is added as the information x = v: the harness passes the answer
% verbatim (h_commitment/1, e.g. "X = 1 "), and it is read back as the
% equations it states.
committed_value(V, X) :-
    term_string(T, V, [variable_names(Bs)]), memberchk('X' = X, Bs), call(T).
