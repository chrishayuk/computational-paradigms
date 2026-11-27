% Made-up problem X01, for the no-anticipation check: stage 3's constant is
% a word that appears nowhere else. At every stage the program looks for it
% among all the atoms the process holds and in every string the harness
% holds, and prints LATE-ABSENT or LATE-PRESENT. Stages 1 and 2 must print
% LATE-ABSENT: the constant reaches the process only with stage 3.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
% CONSTANTS BEGIN
% stage 1
colour(red).
% stage 3
late(zqlatexyzzy).
% CONSTANTS END
unknowns(main, ['A', 'B']).
stage(K, [A, B], Cs) :- look(K), body(K, A, B, Cs).
body(1, A, _, Cs) :- memberchk(colour(A), Cs).
body(2, _, B, _) :- B = 2.
body(3, _, _, Cs) :- memberchk(late(_), Cs).
query(_, _).
% the word's codes, from the word reversed in the environment variable
% CP_QUAL_LATE_REV (set by qualification/run.py), so that nothing in this
% text, nor any analysis of it, can make the atom
target(Cs) :- getenv('CP_QUAL_LATE_REV', R), atom_codes(R, RC), reverse(RC, Cs).
look(K) :-
    target(Cs), string_codes(S, Cs),
    (   ( current_atom(A), atom(A), atom_string(A, SA), SA == S
        ; cp_harness:ctl(_, V), string(V), sub_string(V, _, _, _, S)
        ; cp_harness:ctl(constants, _-V2), sub_string(V2, _, _, _, S) )
    ->  W = 'LATE-PRESENT' ; W = 'LATE-ABSENT' ),
    format("stage ~w: ~w~n", [K, W]).
