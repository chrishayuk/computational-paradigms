% P11a. Irreversible effects, the effect after the test (problems/11-irreversible-effects.md).
% One stage, a query for any one outcome: pick(x) and x >= <k> and emit(x),
% in that order. The outcome is committed when it is reported (answers(1)).
%
% The conjunction is written as the problem states it, with nothing that
% defers emit: emit(x) is called wherever the conjunction reaches it, on
% whatever value x has then. x >= k is a constraint of library(clpfd) over
% the integers, with no domain imposed and no labeling; pick binds x first,
% so it is decided at once. constraints and session share this text
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
%     x >= k as a constraint of library(clpfd), #>=/2, over the unbounded
%     integers, with no domain imposed and no labeling (SWI-Prolog manual,
%     section "library(clpfd)"; Triska, FLOPS 2012, LNCS 7294), as in this
%     system's P05 constraints programs
% END PROVENANCE

:- use_module(library(clpfd)).

% CONSTANTS BEGIN
% stage 1
pick(1).
pick(2).
pick(3).
at_least(2).
% CONSTANTS END

unknowns(main, ['X']).

% stage 1: pick(x) and x >= k and emit(x)
stage(1, [X], Cs) :-
    member(pick(X), Cs), memberchk(at_least(K), Cs), X #>= K, emit(X).

query(_, _).
