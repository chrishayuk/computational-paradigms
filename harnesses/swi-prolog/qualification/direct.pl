/*  Direct measurement for the qualification: the made-up program run in
    SWI-Prolog without the harness, measured as the systems file qualifies
    it (systems/swi-prolog/README.md, "Units"; measurement.md).

        swipl -f none -q direct.pl PROGRAM K CAP

    Loads PROGRAM (which must not call H predicates other than none), and
    poses stages 1..K and query(K) as one conjunction written into one
    clause, so that nothing but the program's goals lies between the two
    statistics/2 calls. Prints one line per figure, key=value:

      first     steps to the first answer: statistics(inferences)
                difference minus one, around the conjunction
      minlimit  the smallest limit under which call_with_inference_limit/3
                lets '$q'(Vars) reach its first answer, found by bisection
                (expected: first + 1, the call port of '$q'/1)
      at        steps at each answer (up to CAP): the smallest limit under
                which call_with_inference_limit/3 lets the query reach its
                i-th answer (a flag/3 counter stops it there), less the limit
                for the first answer, plus first, less (i-1) passes of the
                counter (counter_cost, measured with statistics/2)
      end       steps when the enumeration is exhausted (statistics/2
                difference minus one around ( Conj, fail ; true )), or cap
      cps       retained choicepoints at each answer: the probe's own
                counter (systems/swi-prolog/probes/cpcount.pl), from a mark
                taken where the query starts
      attvars, residual_goals  at the first answer (term_attvars/2,
                copy_term/3), as the harness's observe() reads them
      global_live_delta  bytes of live global data (garbage_collect/0,
                statistics(globalused)) at the first answer, minus before
      tables, table_answers  (when the program tables) after exhaustion
*/

:- initialization(main, main).
:- use_module('../../../systems/swi-prolog/probes/cpcount').
:- use_module(library(prolog_autoload)).

main :-
    current_prolog_flag(argv, Argv),
    append(_, [Prog, KA, CapA], Argv), !,
    atom_number(KA, K), atom_number(CapA, Cap),
    block(Prog, Stripped, Consts),           % the constants block, as the harness reads it
    tmp_file_stream(text, Tmp, TS), write(TS, Stripped), close(TS),
    atom_concat(Tmp, '.pl', TmpPl), rename_file(Tmp, TmpPl),
    load_files(user:TmpPl, []),
    nb_setval(consts, Consts),
    current_prolog_flag(autoload, AL), autoload_all, set_prolog_flag(autoload, AL),
    ( catch(user:unknowns(main, Names), _, fail) -> true ; Names = [] ),
    length(Names, N), length(Vars, N),
    out(names, Names),
    conjunction(K, Vars, Conj),
    (   getenv('DIRECT_END_ONLY', _)       % the enumeration to its end, first in a fresh process
    ->  assertz((mend0(D) :- statistics(inferences, A), ( Conj, fail ; true ), statistics(inferences, B), D is B-A-1)),
        mend0(D0), out(end_cold, D0), halt(0)
    ;   true
    ),
    % steps to the first answer, inline
    assertz((m1(V, D) :- statistics(inferences, A), V = Vars, Conj, statistics(inferences, B), D is B-A-1)),
    copy_term(m1(_, _), M1), ( call(M1) -> arg(2, M1, First) ; First = none ),
    out(first, First),
    % the call_with_inference_limit/3 agreement
    assertz(('$q'(Vars) :- Conj)),
    copy_term(Vars, Vq),
    minlimit(user:'$q'(Vq), 1, 100000000, ML), out(minlimit, ML),
    % every answer, by the systems file's other qualified measure: the
    % smallest limit under which call_with_inference_limit/3 lets the
    % query reach its i-th answer (a counter, flag/3, stops it there; the
    % counter's own cost k per answer is found from the first answer,
    % whose steps the statistics/2 difference gives); and the smallest
    % limit under which the whole enumeration ends
    flag(dq_cnt, _, 0),
    statistics(inferences, Ka), flag(dq_cnt, _, 0), statistics(inferences, Kb), Reset is Kb - Ka - 1,
    statistics(inferences, Kc), flag(dq_cnt, Nk, Nk+1), Nk+1 >= 0, statistics(inferences, Kd), K0 is Kd - Kc - 1,
    answer_limits(1, Cap, Vars, Conj, First, K0, Ds),
    out(counter_cost, K0), ignore(Reset = Reset),
    out(at, Ds),
    assertz((mend(D) :- statistics(inferences, A), ( Conj, fail ; true ), statistics(inferences, B), D is B-A-1)),
    copy_term(mend(_), ME), call(ME), arg(1, ME, End0),
    length(Ds, NAns),
    (   NAns >= Cap -> End = cap ; End = End0 ),
    out(end, End),
    % choicepoints at each answer, the probe's counter
    assertz((mcp(Cap, Ns) :- nb_setval(r, []), nb_setval(c, 0),
                ( cpq(Vars, Cap) -> true ; true ),
                nb_getval(r, Ns0), reverse(Ns0, Ns))),
    assertz((cpq(Vars, Cap) :- prolog_current_choice(Mk), Conj, cp_since(Mk, NC),
                nb_getval(r, L0), nb_setval(r, [NC|L0]),
                nb_getval(c, C0), C is C0+1, nb_setval(c, C), C >= Cap)),
    mcp(Cap, Ns), out(cps, Ns),
    % attributed variables, residual goals and live global data at the first answer
    garbage_collect, statistics(globalused, G0),
    (   copy_term(Vars-Conj, V2-C2), call(C2)
    ->  term_attvars(V2, AVs), length(AVs, NAV),
        copy_term(V2, _, Gs), length(Gs, NG),
        garbage_collect, statistics(globalused, G1), GD is G1 - G0,
        out(attvars, NAV), out(residual_goals, NG), out(global_live_delta, GD),
        ignore(V2 = V2)
    ;   out(attvars, none)
    ),
    (   current_table(_:_, _)
    ->  copy_term(Vars-Conj, _-C3), forall(call(C3), true),
        findall(Cn, ( current_table(_:_, Tr), trie_property(Tr, value_count(Cn)) ), Cs),
        length(Cs, NT), sum_list(Cs, NTA),
        statistics(table_space_used, TSU),
        out(tables, NT), out(table_answers, NTA), out(table_space_used_bytes, TSU)
    ;   true
    ).

conjunction(K, Vars, Conj) :-
    stages(1, K, Vars, G1),
    Conj = (G1, user:query(K, Vars)),
    forall(between(1, K, J), ( consts_upto(J, CJ), format("consts~w=~q~n", [J, CJ]) )).
stages(K, K, Vars, user:stage(K, Vars, C)) :- !, consts_upto(K, C).
stages(J, K, Vars, (user:stage(J, Vars, C), G)) :- consts_upto(J, C), J1 is J+1, stages(J1, K, Vars, G).

consts_upto(K, C) :- nb_getval(consts, All), findall(T, ( member(J-T, All), J =< K ), C).

%   block(+File, -TextWithoutBlock, -[Stage-Entry]): the CONSTANTS block,
%   with its '% stage K' sections (harnesses/swi-prolog/README.md).
block(File, Stripped, Consts) :-
    read_file_to_string(File, Text, []),
    split_string(Text, "\n", "", Lines),
    (   nth1(B, Lines, LB), sub_string(LB, _, _, _, "CONSTANTS BEGIN"),
        nth1(E, Lines, LE), sub_string(LE, _, _, _, "CONSTANTS END")
    ->  findall(L, ( nth1(I, Lines, L0), ( I >= B, I =< E -> L = "" ; L = L0 ) ), SL),
        atomic_list_concat(SL, '\n', Stripped),
        findall(I-L, ( nth1(I, Lines, L), I > B, I < E ), In),
        sections(In, 0, Consts)
    ;   Stripped = Text, Consts = []
    ).
sections([], _, []).
sections([_-L|T], Cur, Cs) :-
    (   split_string(L, " \t", " \t", Ws), exclude(==(""), Ws, ["%", "stage", N])
    ->  number_string(K, N), sections(T, K, Cs)
    ;   split_string(L, "", " \t", [S]), ( S == "" ; sub_string(S, 0, 1, _, "%") )
    ->  sections(T, Cur, Cs)
    ;   term_strings(L, Ts), findall(Cur-X, member(X, Ts), Here),
        sections(T, Cur, Rest), append(Here, Rest, Cs)
    ).
term_strings(L, Ts) :-
    setup_call_cleanup(open_string(L, S), rd(S, Ts), close(S)).
rd(S, Ts) :- read_term(S, T, []), ( T == end_of_file -> Ts = [] ; Ts = [T|R], rd(S, R) ).

minlimit(_, Lo, Hi, L) :- Lo >= Hi, !, L = Hi.
minlimit(G, Lo, Hi, L) :-
    Mid is (Lo+Hi)//2,
    (   \+ \+ ( catch(call_with_inference_limit(G, Mid, R), _, R = inference_limit_exceeded),
                 R \== inference_limit_exceeded )
    ->  minlimit(G, Lo, Mid, L)
    ;   Lo1 is Mid+1, minlimit(G, Lo1, Hi, L)
    ).

out(K, V) :- format("~w=~q~n", [K, V]).

%   answer_limits(+I, +Cap, +Vars, +Conj, +First, -K, -Ds)
answer_limits(I, Cap, Vars, Conj, First, K, Ds) :-
    ignore(First = First),
    (   I > Cap
    ->  Ds = []
    ;   copy_term(Vars-Conj, _-C1),
        G = ( flag(dq_cnt, _, 0), call(C1), flag(dq_cnt, N0, N0+1), N0+1 >= I ),
        (   \+ \+ call(G)
        ->  minlimit(G, 1, 100000000, L),
            (   I =:= 1 -> nb_setval(dq_l1, L) ; true ),
            nb_getval(dq_l1, L1),
            D is First + (L - L1) - (I-1)*K,   % the first answer's steps, and the
                                               % limit's growth less I-1 counter passes
            Ds = [D|Ds1],
            I1 is I+1,
            answer_limits(I1, Cap, Vars, Conj, First, K, Ds1)
        ;   Ds = []
        )
    ).
