/*  SWI-Prolog harness, the Prolog side (cp-roles, spec-1.0, wave 1).

    Loaded by harnesses/swi-prolog/run, before the program, in a fresh
    `swipl` process. The Python driver (run) writes a control file of
    ctl(Key, Value) facts and starts

        swipl -f none --no-tty -q -g cp_harness:h_main(CtlFile) -t halt harness.pl

    This file never holds or computes anything a program is asked for. It
    passes stages in (by calling the program's stage/2, query/2 and
    spawned/3 in order), collects answers by backtracking (the system's
    standard mechanism), renders them with the toplevel's own code, reads
    state for observe(), enforces the budget, and reports events to the
    driver as JSON lines. Everything it does beyond that is listed in
    harnesses/swi-prolog/README.md, "Confounds".

    Steps. Every inference spent inside harness code that runs inside the
    measured computation (stage marks, answer points, the H predicates a
    program calls, the storage sampler) is excluded from the step count and
    from the budget: each such piece of code runs "paused" (h_paused/3),
    which reads the inference counter on entry and on exit, adds what it
    used to an exclusion counter, and moves the inference limit on by the
    same amount. The qualification checks that the steps reported equal
    the systems file's measurement (statistics(inferences) difference,
    minus one) of the program's own goals.
*/

:- module(cp_harness,
          [ h_param/2,            % +Name, -Value
            h_commitment/1,       % -Verbatim
            emit/1,               % +Message   (P11's effects stub)
            h_count/1,            % +Name      (problem operations)
            h_candidate/0,        %            (P12 candidates examined)
            h_held/2,             % +Name, +Count (problem-defined alternatives)
            h_wait/0              %            (session: wait for the next stage)
          ]).

:- use_module(library(lists), [member/2, append/3, nth1/3, sum_list/2]).
:- use_module(library(apply), [maplist/3, maplist/2, foldl/4]).
:- use_module(library(prolog_autoload), [autoload_all/0]).
:- use_module(library(process), [process_kill/2]).

:- dynamic ctl/2.
:- dynamic cnt/2.                % problem-operation counters, by computation
:- dynamic held/3.               % problem-defined alternatives, by computation

huge(1152921504606846976).       % 2^60: "no limit" when read back

                 /*******************************
                 *          ENTRY POINT         *
                 *******************************/

h_main(CtlFile) :-
    catch(h_main_(CtlFile), E,
          (   E = unwind(_) -> throw(E)      % halt/1 from the signal handler
          ;   h_fatal(E)
          )),
    h_halt(0).

h_fatal(E) :-
    (   catch(message_text(E, T), _, fail) -> true ; format(string(T), "~q", [E]) ),
    catch(ev(harness_fault, [text-T]), _, true),
    h_halt(3).

h_halt(S) :-
    catch(flush_output(user_output), _, true),
    catch(flush_output(user_error), _, true),
    halt(S).

h_main_(CtlFile) :-
    read_ctl(CtlFile),
    ctl(events, EvFile),
    open(EvFile, append, EvS, [encoding(utf8), buffer(line)]),
    nb_setval(h_events, EvS),
    (   ctl(spool, Spool), Spool \== none
    ->  open(Spool, append, SpS, [encoding(utf8), buffer(line)]),
        nb_setval(h_spool, SpS)
    ;   nb_setval(h_spool, none)
    ),
    current_prolog_flag(version, V),
    current_prolog_flag(optimise, O),
    current_prolog_flag(occurs_check, OC0),
    current_prolog_flag(unknown, U0),
    ev(start, [version-V, optimise-O, occurs_check_default-OC0, unknown_default-U0]),
    set_prolog_flag(answer_write_options,
                    [quoted(true), portray(true), max_depth(0), spacing(next_argument)]),
    set_prolog_flag(toplevel_print_anon, true),
    install_hooks,
    on_signal(usr1, _, cp_harness:on_usr1),
    (   ctl(config, session)
    ->  module_property(cp_harness, file(HF)),
        file_directory_name(HF, LibDir),
        atom_concat(LibDir, '/../S/session-wait.pl', SW),
        load_files(user:SW, [])
    ;   true
    ),
    ctl(program, Prog),
    load_program(Prog),
    run_plan,
    ev(done, []),
    close(EvS).

read_ctl(File) :-
    setup_call_cleanup(open(File, read, S, [encoding(utf8)]),
                       read_ctl_terms(S),
                       close(S)).
read_ctl_terms(S) :-
    read_term(S, T, []),
    (   T == end_of_file
    ->  true
    ;   assertz(T),
        read_ctl_terms(S)
    ).

%   The program is loaded into user, then every predicate its clauses can
%   reach is autoloaded, so that no library is loaded while a stage is
%   measured (systems file, "Units": autoloading adds inferences, and a
%   limit reached during autoloading leaves a library undefined).

load_program(Prog) :-
    catch(load_files(user:Prog, [if(true)]), E, true),   % the program without its constants block
    flush_output(user_output), flush_output(user_error),
    (   var(E)
    ->  current_prolog_flag(autoload, AL),
        catch(autoload_all, E2, true),   % it switches autoloading off; put it back
        set_prolog_flag(autoload, AL),
        (   var(E2) -> true
        ;   message_text(E2, T2), ev(note, [text-T2])
        ),
        current_prolog_flag(occurs_check, OC),
        current_prolog_flag(unknown, Unk),
        ev(loaded, [occurs_check-OC, unknown-Unk])
    ;   message_text(E, T),
        ev(load_error, [text-T]),
        h_halt(0)
    ).

                 /*******************************
                 *             EVENTS           *
                 *******************************/

%   ev(+Kind, +Pairs): one JSON object per line on the events stream.

ev(Kind, Pairs) :-
    nb_getval(h_events, S),
    get_time(T),
    json_out(S, [ev-Kind, t-T|Pairs]),
    nl(S),
    flush_output(S).

json_out(S, Pairs) :-
    is_list(Pairs), Pairs = [_-_|_], !,
    put_char(S, '{'),
    json_pairs(Pairs, S),
    put_char(S, '}').
json_out(S, obj([])) :- !, write(S, '{}').
json_out(S, obj(Pairs)) :- !, json_out(S, Pairs).
json_out(S, list(L)) :- !,
    put_char(S, '['), json_items(L, S), put_char(S, ']').
json_out(S, null) :- !, write(S, null).
json_out(S, true) :- !, write(S, true).
json_out(S, false) :- !, write(S, false).
json_out(S, N) :- integer(N), !, write(S, N).
json_out(S, N) :- float(N), !, format(S, "~15g", [N]).
json_out(S, X) :- json_string(S, X).

json_pairs([], _).
json_pairs([K-V|T], S) :-
    json_string(S, K), put_char(S, ':'), json_out(S, V),
    (   T == [] -> true ; put_char(S, ','), json_pairs(T, S) ).
json_items([], _).
json_items([H|T], S) :-
    json_out(S, H),
    (   T == [] -> true ; put_char(S, ','), json_items(T, S) ).

json_string(S, X) :-
    (   string(X) -> Str = X
    ;   atom(X) -> atom_string(X, Str)
    ;   format(string(Str), "~q", [X])
    ),
    string_codes(Str, Cs),
    put_char(S, '"'),
    maplist(json_char(S), Cs),
    put_char(S, '"').
json_char(S, 0'") :- !, write(S, '\\"').
json_char(S, 0'\\) :- !, write(S, '\\\\').
json_char(S, 0'\n) :- !, write(S, '\\n').
json_char(S, 0'\r) :- !, write(S, '\\r').
json_char(S, 0'\t) :- !, write(S, '\\t').
json_char(S, C) :- C < 0x20, !, format(S, "\\u~|~`0t~16r~4+", [C]).
json_char(S, C) :- put_code(S, C).

                 /*******************************
                 *       STEPS AND BUDGET       *
                 *******************************/

%   Per computation (main thread, or inside an engine, whose global
%   variables are its own):
%     h_base   raw inference count when the computation started
%     h_excl   (flag h_excl_<id>) inferences spent in paused harness code
%   Program steps now = raw - h_base - h_excl - (the paused code's entry).

comp_flag(Comp, Key, Flag) :- atomic_list_concat([Key, '_', Comp], Flag).

%   h_paused(+Pre, :Goal, +Kind)
%   Run Goal (a harness goal) without counting its inferences in the
%   program's steps or against the budget. Pre is the number of
%   inferences spent before the first statistics/2 call (the call ports of
%   the H predicate and of h_paused/3, and anything the caller did first).
%   Goal is called as call(Goal, Steps, End0, End): Steps is the
%   program's step count at entry; End0 the program step count at which
%   the current budget ends, End the one to continue with (a stage mark
%   sets a new one).
%
%   The budget. While program code runs, the system's inference limit
%   ('$inference_limit_false'/1 sets it, absolutely) stands at the raw
%   count where program step End + slack + 1 falls, slack being the most
%   inferences any harness entry spends before it lifts the limit (so that
%   entering harness code never trips it). Every harness entry then
%   checks the budget exactly: if Steps > End it raises
%   inference_limit_exceeded itself, as the system's limit would have.
%   So a stage is budget exactly when its program steps exceed its budget
%   at some point; between harness entries the system's limit stops it at
%   most slack inferences late.

h_paused(Pre, G, Kind) :-
    statistics(inferences, A),
    (   '$inference_limit_false'(1152921504606846976) -> true ; true ),
    nb_setval(h_in_pause, true),
    nb_getval(h_comp, Comp),
    comp_flag(Comp, h_excl, XF),
    flag(XF, X0, X0),
    nb_getval(h_base, Base),
    Steps is A - Pre - 1 - Base - X0,
    nb_getval(h_bend, End0),
    (   Steps > End0, Kind \= hook(_)
    ->  Over = true, End1 = End0, nb_setval(h_over_steps, Steps)
    ;   Over = false,
        (   catch(call(G, Steps, End0, End1), E,
                  ( E = unwind(_) -> throw(E) ; h_paused_fault(E), End1 = End0 ))
        ->  true
        ;   End1 = End0
        )
    ),
    nb_setval(h_bend, End1),
    nb_setval(h_in_pause, false),
    statistics(inferences, Z),
    post_cost(Post),
    Cost is Z - A + Pre + 1 + Post,
    flag(XF, X0, X0+Cost),
    slack(Slack),
    L is Base + X0 + Cost + End1 + Slack + 1,
    (   Over == true
    ->  throw(inference_limit_exceeded)    % the limit stays lifted
    ;   Kind == hook(inference_limit_exceeded)
    ->  true                               % the budget has run out: no limit
    ;   '$inference_limit_false'(L) -> true
    ;   true
    ).

%   The inferences h_paused/3 spends after its second statistics/2 call
%   (post_cost/1, flag/3, slack/1, '$inference_limit_false'/1), on
%   SWI-Prolog 11.0.1; the qualification checks it (steps with and
%   without H calls are the same).
post_cost(13).

%   The most inferences a harness entry spends before it lifts the limit
%   (Pre + statistics/2 + '$inference_limit_false'/1).
slack(8).

%   At the start of a computation: no budget yet (a stage mark gives one).
arm_limit :-
    huge(H),
    nb_setval(h_bend, H),
    statistics(inferences, A),
    L is A + H,
    set_limit(L).

h_paused_fault(E) :-
    catch(( message_text(E, T), ev(harness_fault, [text-T]) ), _, true).

%   Program steps at a point outside paused code (after a failure or an
%   exception, in the main thread). Pre: inferences since the program last
%   ran, up to and including this statistics/2 call.
steps_now(Pre, Steps) :-
    statistics(inferences, A),
    nb_getval(h_comp, Comp),
    comp_flag(Comp, h_excl, XF),
    flag(XF, X0, X0),
    nb_getval(h_base, Base),
    Steps is A - Pre - Base - X0,
    nb_getval(h_bend, End),
    (   Steps > End
    ->  nb_setval(h_over_steps, Steps),
        throw(inference_limit_exceeded)
    ;   true
    ).

set_limit(L) :- ( '$inference_limit_false'(L) -> true ; true ).

                 /*******************************
                 *      HOOKS: BUDGET, SAMPLER  *
                 *******************************/

:- multifile prolog:prolog_exception_hook/5.
:- dynamic prolog:prolog_exception_hook/5.

install_hooks :-
    asserta(( prolog:prolog_exception_hook(E, E, _Fr, _Catcher, _Dbg) :-
                  cp_harness:exception_seen(E), fail )),
    (   ctl(mode, storage), \+ ctl(config, tabling)   % QUESTIONS.md, S17
    ->  asserta(( prolog:heartbeat :- cp_harness:h_sample ))
    ;   true
    ).
:- multifile prolog:heartbeat/0.
:- dynamic prolog:heartbeat/0.

%   At the moment the budget runs out, or any exception is raised in the
%   computation, before the stacks are unwound, read the state: the
%   bindings held, residual goals, and (storage mode) the retained
%   choicepoints and the store. It is kept, and reported only if this
%   exception reaches the harness's catch/3 (an exception the program
%   catches itself is not reported). The exception is not changed, and
%   the inferences spent here are excluded like any harness code.
exception_seen(E) :-
    prolog_current_choice(Ch),
    nb_current(h_armed, true),
    \+ nb_current(h_in_pause, true),
    h_paused(7, exc_(E, Ch), hook(E)).    % the hook's, exception_seen/1's,
                                          % prolog_current_choice/1's and
                                          % nb_current/2's call ports counted
exc_(E, Ch, Steps0, End, End) :-
    (   nb_current(h_over_steps, OS), OS \== none
    ->  Steps = OS                       % raised by a harness entry's check
    ;   Steps = Steps0                   % raised in the program, or by the system's limit
    ),
    (   E == inference_limit_exceeded -> Why = budget ; Why = error ),
    nb_getval(h_comp, Comp),
    b_getval(h_vars, VB),
    (   nb_current(h_part, Part) -> true ; Part = 0 ),
    nb_getval(h_mark, Mark),
    state_pairs(VB, Mark, Ch, 'at-exception', Obs),
    copy_term(E, EC),
    nb_setval(h_last_exc, exc(EC, [comp-Comp, why-Why, steps-Steps, part-Part|Obs])).

%   At the harness's catch/3: report the state read when this exception
%   was raised.
report_exception(E) :-
    (   nb_current(h_last_exc, exc(E0, Pairs)), E0 =@= E
    ->  ev(at_exception, Pairs)
    ;   true
    ).

%   The safety limit: the driver sends SIGUSR1; at the next point where
%   the virtual machine handles signals, this reads the step count and the
%   state held, reports them, and ends the process with SIGKILL (halt/1
%   from inside an engine takes about two seconds to unwind). The driver
%   sends SIGKILL itself if the process has not ended 3 s later.
on_usr1(_) :-
    statistics(inferences, A),
    prolog_current_choice(Ch),
    set_limit(1152921504606846976),
    (   nb_current(h_armed, true), nb_current(h_comp, Comp), nb_current(h_base, Base)
    ->  comp_flag(Comp, h_excl, XF), flag(XF, X0, X0),
        Steps is A - Base - X0,
        (   nb_current(h_part, Part) -> true ; Part = 0 ),
        (   catch(( b_getval(h_vars, VB), nb_getval(h_mark, Mark),
                    state_pairs(VB, Mark, Ch, 'at-timeout', Obs) ), _, fail)
        ->  true
        ;   Obs = [where-'at-timeout']
        ),
        ev(at_timeout, [comp-Comp, steps-Steps, part-Part|Obs])
    ;   ev(at_timeout, [])
    ),
    catch(flush_output(user_output), _, true),
    catch(flush_output(user_error), _, true),
    current_prolog_flag(pid, Pid),
    process_kill(Pid, kill).


%   Storage mode only: a sampled maximum of retained choicepoints, stack
%   usage and table space, every N inferences (heartbeat flag), with
%   running maxima kept off the stacks in flag/3 (systems file, "Store").
h_sample :-
    prolog_current_choice(Ch),
    (   nb_current(h_in_pause, true)       % never inside harness code
    ->  true
    ;   \+ nb_current(h_armed, true)       % nor outside a computation
    ->  true
    ;   h_paused(7, sample_(Ch), sample)   % the hook's two ports, h_sample/0's,
    ).                                     % prolog_current_choice/1's, two
                                           % nb_current/2's and
                                           % nb_current/2's call ports
                                           % (the hook must not fail)
sample_(_, _, L, L) :-
    \+ nb_current(h_armed, true), !.
sample_(Ch, _Steps, L, L) :-
    nb_getval(h_comp, Comp),
    nb_getval(h_mark, Mark),
    cp_count(Ch, Mark, N, _),
    upd(Comp, cp, N),
    statistics(globalused, G), upd(Comp, globalused, G),
    statistics(localused, Lo), upd(Comp, localused, Lo),
    statistics(trailused, T), upd(Comp, trailused, T),
    (   ctl(config, tabling) -> statistics(table_space_used, TS), upd(Comp, table_space_used, TS) ; true ),
    comp_flag(Comp, smp_n, NF), flag(NF, K, K+1).
upd(Comp, Key, V) :-
    atomic_list_concat([smp, Key, Comp], '_', F),
    flag(F, Old, max(Old, V)).
sampled(Comp, Key, V) :-
    atomic_list_concat([smp, Key, Comp], '_', F),
    flag(F, V, V).
reset_samples(Comp) :-
    forall(member(K, [cp, globalused, localused, trailused, table_space_used]),
           ( atomic_list_concat([smp, K, Comp], '_', F), flag(F, _, 0) )),
    comp_flag(Comp, smp_n, NF), flag(NF, _, 0).

                 /*******************************
                 *          CHOICEPOINTS        *
                 *******************************/

%   Retained choicepoints: frames newer than the mark taken when the
%   computation started, by type (systems file, "Alternative").
cp_count(C, M, N, Types) :- cp_walk(C, M, 0, N, [], Types).
cp_walk(C, M, N0, N, T0, T) :-
    (   C =< M
    ->  N = N0, T = T0
    ;   N1 is N0+1,
        (   prolog_choice_attribute(C, type, Ty) -> true ; Ty = unknown ),
        cp_add(Ty, T0, T1),
        (   prolog_choice_attribute(C, parent, P)
        ->  cp_walk(P, M, N1, N, T1, T)
        ;   N = N1, T = T1
        )
    ).
cp_add(Ty, [], [Ty-1]) :- !.
cp_add(Ty, [Ty-K|R], [Ty-K1|R]) :- !, K1 is K+1.
cp_add(Ty, [X|R], [X|R1]) :- cp_add(Ty, R, R1).

                 /*******************************
                 *       RENDERING (TOPLEVEL)   *
                 *******************************/

%   The toplevel's own rendering of an answer: translate_bindings/4,
%   name_vars/3 and the query(yes/more) message, as write_bindings/4 in
%   boot/toplevel.pl does it, with answer_write_options max_depth(0) so
%   that nothing is elided. Done under \+ \+, so no binding survives.

render_answer(VB, Det, Text, Bindings) :-
    \+ \+ ( render_(VB, Det, T, B), nb_setval(h_render, T-B) ),
    nb_getval(h_render, Text-Bindings),
    nb_setval(h_render, none).

render_(VB, Det, Text, Bindings) :-
    '$toplevel':translate_bindings(VB, B1, [], user:Res),
    '$toplevel':name_vars(VB, B1, t(Res, true)),
    (   Det == true
    ->  Msg = query(yes(B1, true, Res))
    ;   Msg = query(more(B1, true, Res))
    ),
    message_string(Msg, Text),
    binding_texts(B1, Bindings).

binding_texts(B1, Pairs) :-
    current_prolog_flag(answer_write_options, Opts),
    findall(Name-VT,
            ( member(binding(Names, Value, _Subst), B1),
              member(Name, Names),
              format(string(VT), "~W", [Value, Opts])
            ),
            Pairs).

message_string(Msg, Text) :-
    phrase('$messages':translate_message(Msg), Lines),
    with_output_to(string(Text), print_message_lines(current_output, '', Lines)).

message_text(E, Text) :-
    (   catch(phrase('$messages':translate_message(E), Lines), _, fail)
    ->  with_output_to(string(Text), print_message_lines(current_output, kind(error), Lines))
    ;   format(string(Text), "~q", [E])
    ).

%   State at a point: rendering of the bindings held, attributed variables
%   reachable from the unknowns, residual goals, and in storage mode the
%   retained choicepoints and the store vector.
state_pairs(VB, Mark, Ch, Where, Pairs) :-
    (   ctl(mode, storage)                 % the store first, before the
    ->  store_pairs(SObj),                 % harness makes any data of its own
        cp_count(Ch, Mark, NCP, Types), pairs_obj(Types, TObj),
        Extra = [cps-NCP, cp_types-TObj, store-SObj]
    ;   Extra = [cps-null, cp_types-null, store-obj([])]
    ),
    term_attvars(VB, AVs), length(AVs, NAV),
    \+ \+ ( copy_term(VB, _, Gs), length(Gs, NG), nb_setval(h_ng, NG) ),
    nb_getval(h_ng, NG),
    render_answer(VB, false, Text, Bs),
    pairs_obj(Bs, BObj),
    Pairs = [where-Where, text-Text, bindings-BObj, attvars-NAV, residual_goals-NG|Extra].

pairs_obj(Ps, obj(Ps)).

store_pairs(obj(Ps)) :-
    garbage_collect,
    statistics(globalused, G), statistics(localused, L), statistics(trailused, T),
    (   ctl(config, tabling)
    ->  statistics(table_space_used, TS),
        aggregate_tables(NT, NA),
        Ps = [global_live_bytes-G, local_bytes-L, trail_bytes-T,
              table_space_used_bytes-TS, tables-NT, table_answers-NA]
    ;   Ps = [global_live_bytes-G, local_bytes-L, trail_bytes-T]
    ).

aggregate_tables(NT, NA) :-
    findall(C, ( current_table(_:_, Tr), trie_property(Tr, value_count(C)) ), Cs),
    length(Cs, NT), sum_list(Cs, NA).

                 /*******************************
                 *        H PREDICATES          *
                 *******************************/

%!  h_param(+Name, -Value)
%   The instance's parameters (n, order, answers, cap, spawn_order), as
%   stages.json gives them.
h_param(Name, Value) :-
    h_paused(2, param_(Name, V), param),
    Value = V.
param_(Name, V, _, L, L) :- ctl(params, Ps), memberchk(Name-V, Ps).

%!  h_commitment(-Verbatim)
%   Succeeds, with the answer the commit stage reported, verbatim, when the
%   stage being posed is a commit stage replayed with a selected value.
h_commitment(V) :-
    h_paused(2, commitment_(V0), commitment),
    V0 \== none,
    V = V0.
commitment_(V, _, L, L) :-
    (   nb_current(h_part, J), ctl(commitments, Cs), memberchk(J-V, Cs) -> true ; V = none ).

%!  emit(+M)
%   P11's effects stub: appends one entry to the log, and returns.
emit(M) :-
    h_paused(2, emit_(M), emit).
emit_(M, _, L, L) :-
    nb_getval(h_spool, S),
    (   S == none
    ->  ev(harness_fault, [text-"emit/1 called, but this problem has no effects log"])
    ;   current_prolog_flag(answer_write_options, Opts),
        format(string(Text), "~W", [M, Opts]),
        nb_getval(h_k, K),
        (   nb_current(h_part, J) -> true ; J = K ),
        nb_getval(h_how, How),
        (   How == reposed, J < K -> R = J ; R = null ),
        nb_getval(h_attempt, Att),
        ctl(log_kind, LK),
        json_out(S, [entry-Text, stage-K, attempt-Att, during_replay_of-R, log-LK]),
        nl(S), flush_output(S)
    ).

%!  h_count(+Name)
%   One application of a case of a relation the problem defines.
h_count(Name) :-
    h_paused(2, count_(Name), count).
count_(Name, _, L, L) :-
    nb_getval(h_comp, C),
    (   retract(cnt(C, Name-N0)) -> N is N0+1 ; N = 1 ),
    assertz(cnt(C, Name-N)).

%!  h_candidate
%   P12: one sequence s for which accept(s) is evaluated.
h_candidate :-
    h_paused(2, count_('$candidates_examined'), count).

%!  h_held(+Name, +Count)
%   Problem-defined alternatives held now (the last value at the stage
%   boundary is recorded).
h_held(Name, Count) :-
    h_paused(2, held_(Name, Count), held).
held_(Name, Count, _, L, L) :-
    nb_getval(h_comp, C),
    retractall(held(C, Name, _)),
    assertz(held(C, Name, Count)).

%!  h_wait
%   session only: the computation waits here for the next stage. The
%   harness records the stage as ended with the computation waiting, and
%   when it poses the next stage, h_wait/0 receives it into this
%   computation (marks it, calls stage/2 for it) and returns.
h_wait :-
    prolog_current_choice(Ch),
    h_paused(3, wait_(Ch, J0, Vars0-Cs0), wait),
    (   J0 == none
    ->  throw(error(permission_error(call, procedure, h_wait/0),
                    context(h_wait/0, 'h_wait/0 is for the session configuration')))
    ;   true
    ),
    user:stage(J0, Vars0, Cs0).

                 /*******************************
                 *        STAGE MARKS           *
                 *******************************/

%   h_m(+J): placed before stage(J, Vars) in the posed conjunction. On the
%   first entry it records the step count (the restart cost, when J is the
%   stage being posed in a reposed run), and gives stage J its budget from
%   here; on every entry it sets h_part (backtrackable) for emit/1.

h_m(J) :-
    h_paused(2, m_(J), mark).
m_(J, Steps, End0, End) :-
    b_setval(h_part, J),
    nb_getval(h_comp, Comp),
    comp_flag(Comp, h_entered, EF),
    flag(EF, E0, E0),
    (   J > E0
    ->  flag(EF, _, J),
        ctl(budget, B),
        End is Steps + B,
        ev(enter, [comp-Comp, stage-J, steps-Steps])
    ;   End = End0
    ).

                 /*******************************
                 *             PLANS            *
                 *******************************/

%   ctl(plan, reposed(K, Comps))   plain, tabling, coroutines, constraints:
%       stages 1..K posed together (replay 1..K-1), answers collected here.
%   ctl(plan, session(Stages))     session: an engine; each element
%       post(J, Collect) posts stage J (Collect = replay, point, here).
%   Comps: list of comp(Id, Kind, Cap) with Kind main or spawned(J).

run_plan :-
    ctl(plan, Plan),
    run_plan(Plan).

run_plan(reposed(K, Comps)) :-
    maplist(run_comp(K), Comps).
run_plan(session(Posts)) :-
    session_main(Posts).

%   One computation in the main thread: build the conjunction, take the
%   mark, run it under the budget, collect answers by backtracking.

run_comp(K, comp(Comp, Kind, Cap)) :-
    unknown_vars(Comp, VB, Vars),
    start_comp(Comp, K),
    build_goal(Kind, K, Vars, Goal),
    b_setval(h_vars, VB),
    b_setval(h_part, 0),
    nb_setval(h_cap, Cap),
    nb_setval(h_count, 0),
    collect(Comp, Goal, VB, Cap),
    true.

unknown_vars(Comp, VB, Vars) :-
    (   catch(user:unknowns(Comp, Names), _, fail), is_list(Names)
    ->  true
    ;   Names = []
    ),
    length(Names, N), length(Vars, N),
    pair_up(Names, Vars, VB).
pair_up([], [], []).
pair_up([N|Ns], [V|Vs], [N=V|Ps]) :- pair_up(Ns, Vs, Ps).

build_goal(main, K, Vars, Goal) :-
    numlist_(1, K, Js),
    foldl(conj_stage(Vars), Js, true, G0),
    conj(G0, user:query(K, Vars), Goal).
build_goal(spawned(J), _, Vars, (cp_harness:h_m(J), user:spawned(J, Comp, Vars, Cs))) :-
    nb_getval(h_comp, Comp),
    stage_constants(J, Cs).
conj_stage(Vars, J, G0, G) :-
    stage_constants(J, Cs),
    conj(G0, (cp_harness:h_m(J), user:stage(J, Vars, Cs)), G).

%   stage_constants(+J, -Entries): the entries of the program's CONSTANTS
%   block tagged for stages 1..J, in the block's order. The driver strips
%   the block from the program text before it is loaded, and gives the
%   process the text of a stage's entries only when that stage is posed
%   (ctl(constants, J-Text)); they are read here, when the stage's goal
%   is built or posted.
stage_constants(J, Cs) :-
    findall(I-T, ( ctl(constants, I-T), I =< J ), ITs0),
    msort(ITs0, ITs),
    foldl(read_constants, ITs, [], Rev),
    reverse(Rev, Cs).
read_constants(_-Text, Acc0, Acc) :-
    setup_call_cleanup(open_string(Text, S),
                       read_entries(S, Acc0, Acc),
                       close(S)).
read_entries(S, Acc0, Acc) :-
    read_term(S, T, []),
    (   T == end_of_file -> Acc = Acc0
    ;   read_entries(S, [T|Acc0], Acc)
    ).
numlist_(I, K, []) :- I > K, !.
numlist_(I, K, [I|T]) :- I1 is I+1, numlist_(I1, K, T).
conj(true, G, G) :- !.
conj(A, B, (A, B)).

start_comp(Comp, K) :-
    nb_setval(h_comp, Comp),
    nb_setval(h_k, K),
    ctl(posing_now, How), nb_setval(h_how, How),
    ctl(attempt, Att), nb_setval(h_attempt, Att),
    comp_flag(Comp, h_excl, XF), flag(XF, _, 0),
    comp_flag(Comp, h_entered, EF), flag(EF, _, 0),
    retractall(cnt(Comp, _)),
    retractall(held(Comp, _, _)),
    reset_samples(Comp),
    nb_setval(h_last_exc, none),
    nb_setval(h_in_pause, false),
    nb_setval(h_over_steps, none),
    huge(H), nb_setval(h_bend, H),
    nb_setval(h_base, 0),
    flush_output(user_output), flush_output(user_error),
    out_positions(OB, EB),
    ev(comp_start, [comp-Comp, stage-K, out_bytes-OB, err_bytes-EB]),
    (   ctl(mode, storage)
    ->  garbage_collect,
        statistics(globalused, G0), statistics(localused, L0), statistics(trailused, T0),
        ev(store_start, [comp-Comp, store-obj([global_live_bytes-G0, local_bytes-L0, trail_bytes-T0])])
    ;   true
    ).

out_positions(OB, EB) :-
    ( catch(byte_count(user_output, OB), _, fail) -> true ; OB = null ),
    ( catch(byte_count(user_error, EB), _, fail) -> true ; EB = null ).

%   The goal is compiled into one clause, so that the posed conjunction is
%   what a toplevel query would run: no harness glue between the stages
%   except the marks, whose inferences are excluded.
collect(Comp, Goal, VB, Cap) :-
    retractall(user:'$cp_query'(_)),
    assertz((user:'$cp_query'(VB) :- Goal)),
    (   ctl(mode, storage)
    ->  current_prolog_flag(heartbeat, HB0), nb_setval(h_hb0, HB0),
        ctl(heartbeat, HB), set_prolog_flag(heartbeat, HB)
    ;   true
    ),
    catch_frame(Comp, VB, Cap, Result),
    nb_setval(h_armed, false),
    (   ctl(mode, storage) -> nb_getval(h_hb0, HBr), set_prolog_flag(heartbeat, HBr) ; true ),
    set_limit(infinite),
    finish(Comp, VB, Result).

catch_frame(Comp, VB, Cap, Result) :-
    prolog_current_frame(F),
    nb_setval(h_catch_frame, F),
    catch(query_answers(Comp, VB, Cap, R0), E,
          ( E = unwind(_) -> throw(E) ; report_exception(E), R0 = exception(E) )),
    !,
    Result = R0.

query_answers(_Comp, VB, _Cap, Result) :-
    (   query_cond(VB)
    ->  nb_getval(h_stop_how, Result)
    ;   steps_now(2, S), Result = exhausted(S)
    ).

%   The mark is the newest choicepoint when the query starts (here the
%   if-then-else's own, in query_answers/4), so that what is newer at an
%   answer is the program's.
query_cond(VB) :-
    prolog_current_choice(M),
    nb_setval(h_mark, M),
    arm_limit,
    statistics(inferences, I0),
    B is I0 + 3,                % two nb_setval/2 and the call of '$cp_query'/1
    nb_setval(h_base, B),
    nb_setval(h_armed, true),
    user:'$cp_query'(VB),
    h_answer(VB, Stop),
    Stop == true.

%   h_answer(+VB, -Stop): the answer point. Render the answer, report it,
%   and stop (Stop = true) when the cap is reached or the goal exited
%   without choicepoints; otherwise fail into the goal for the next answer.
h_answer(VB, Stop) :-
    prolog_current_choice(Ch),
    h_paused(3, answer_(VB, Ch, Stop0), answer),
    Stop = Stop0.

answer_(VB, Ch, Stop, Steps, L, L) :-
    nb_getval(h_mark, M),
    (   Ch =< M -> Det = true ; Det = false ),
    nb_getval(h_count, I0), I is I0+1, nb_setval(h_count, I),
    nb_getval(h_cap, Cap),
    (   Det == true
    ->  Stop = true, End = det
    ;   I >= Cap
    ->  Stop = true, End = cap
    ;   Stop = false, End = none
    ),
    (   Stop == true                     % the boundary's state (store first)
    ->  state_pairs(VB, M, Ch, boundary, Obs),
        point_extra(Extra)
    ;   true
    ),
    render_answer(VB, Det, Text, Bs), pairs_obj(Bs, BObj),
    (   ctl(mode, storage) -> cp_count(Ch, M, NCP, _) ; NCP = null ),
    nb_getval(h_comp, Comp),
    ev(answer, [comp-Comp, index-I, text-Text, bindings-BObj, steps-Steps, det-Det, cps-NCP]),
    (   Stop == true
    ->  nb_setval(h_stop_how, stopped(End, Steps, Det, Obs, Extra))
    ;   true
    ).

point_extra([counts-CObj, held-HObj, samples-SObj]) :-
    nb_getval(h_comp, C),
    findall(N-V, cnt(C, N-V), Cs), CObj = obj(Cs),
    findall(N-V, held(C, N, V), Hs), HObj = obj(Hs),
    (   ctl(mode, storage)
    ->  findall(K-V, ( member(K, [cp, globalused, localused, trailused, table_space_used]),
                       sampled(C, K, V) ), Ss0),
        comp_flag(C, smp_n, NF), flag(NF, NS, NS),
        ctl(heartbeat, HB),
        SObj = obj([n-NS, interval-HB|Ss0])
    ;   SObj = null
    ).

finish(Comp, VB, Result) :-
    flush_output(user_output), flush_output(user_error),
    out_positions(OB, EB),
    (   Result = stopped(End, Steps, Det, Obs, Extra)
    ->  Pairs = [ended_by-End, steps-Steps, det-Det, observe-obj(Obs)|Extra]
    ;   Result = exhausted(Steps)
    ->  point_extra(Extra),
        (   ctl(mode, storage) -> store_pairs(Store) ; Store = obj([]) ),
        Pairs = [ended_by-exhausted, steps-Steps, det-false,
                 observe-obj([where-'after-failure', store-Store])|Extra]
    ;   Result = exception(E)
    ->  Steps0 = null,             % taken at the exception (at_exception event)
        point_extra(Extra),
        (   E == inference_limit_exceeded
        ->  End = budget, Text = null
        ;   End = error, message_text(E, Text)
        ),
        format(string(Term), "~q", [E]),
        Pairs = [ended_by-End, steps-Steps0, error_text-Text, error_term-Term|Extra]
    ),
    ev(comp_end, [comp-Comp, out_bytes-OB, err_bytes-EB|Pairs]),
    ignore(VB = VB).

                 /*******************************
                 *            SESSION           *
                 *******************************/

%   The main computation is an engine, created once; each stage is posted
%   into it with engine_post/3. Inside, the posted stages form one growing
%   conjunction: stage(1, Vars), ..., stage(L, Vars), L the latest stage
%   posted. When the computation reaches the end of stage L it yields to
%   the harness (a point) and waits for the next message. If it
%   backtracks into an earlier stage and comes forward again, the stages
%   after it that were already posted are called again from the record,
%   without a new message, as in any conjunction. Each message is
%   stage(J, Collect), where Collect says what to do at the end of J:
%     replay  a stage replayed in a reposed or separate run: yield at once
%     point   yield the state held (print, observe), without consuming it
%     here    call query(J, Vars) and collect answers by backtracking inside
%             the engine; used only where nothing extends the computation
%             afterwards (the instance's last stage, or a separate run)
%   h_wait/0, called by a program's supporting code, is the same advance
%   from inside a stage: it yields (the computation waits) only when no
%   posted stage is left to call.

session_main(Posts) :-
    unknown_vars(main, VB, Vars),
    nb_setval(h_comp, main),
    nb_getval(h_events, EvS),
    nb_getval(h_spool, SpS),
    engine_create(R, engine_main(VB, Vars, EvS, SpS, R), E, []),
    (   session_posts(Posts, E)
    ->  (   ctl(commands, Fifo), Fifo \== none
        ->  ev(ready, []),
            setup_call_cleanup(open(Fifo, read, CS, [encoding(utf8)]),
                               session_commands(CS, E),
                               close(CS))
        ;   true
        )
    ;   true
    ).

%   Commands from the driver, one term per line, read only when the
%   previous stage has ended: post(J, Collect, ctx(K, How, Attempt)), stop.
session_commands(CS, E) :-
    read_term(CS, Cmd, []),
    (   Cmd = post(J, Collect, Ctx, Text)
    ->  (   Text == "" -> true ; assertz(ctl(constants, J-Text)) ),   % arrives only now
        (   session_posts([post(J, Collect, Ctx)], E)
        ->  ev(ready, []),
            session_commands(CS, E)
        ;   true
        )
    ;   true
    ).

engine_main(VB, Vars, EvS, SpS, R) :-
    nb_setval(h_how, incremental),
    nb_setval(h_attempt, 1),
    nb_setval(h_events, EvS),
    nb_setval(h_spool, SpS),
    nb_setval(h_engine, true),
    nb_setval(h_comp, main),
    nb_setval(h_k, 0),
    nb_setval(h_latest, 0),
    nb_setval(h_collect, point),
    nb_setval(h_render, none),
    comp_flag(main, h_excl, XF), flag(XF, _, 0),
    comp_flag(main, h_entered, EF), flag(EF, _, 0),
    retractall(cnt(main, _)), retractall(held(main, _, _)),
    reset_samples(main),
    b_setval(h_vars, VB),
    b_setval(h_vars_list, Vars),
    b_setval(h_part, 0),
    b_setval(h_done, 0),
    nb_setval(h_last_exc, none),
    nb_setval(h_in_pause, false),
    nb_setval(h_over_steps, none),
    huge(H), nb_setval(h_bend, H),
    nb_setval(h_base, 0),
    nb_setval(h_armed, true),
    (   ctl(mode, storage) -> ctl(heartbeat, HB), set_prolog_flag(heartbeat, HB) ; true ),
    prolog_current_frame(F),
    nb_setval(h_catch_frame, F),
    catch(( engine_body(VB, Vars, R) ; engine_exhausted(R) ), Ex,
          ( Ex = unwind(_) -> throw(Ex) ; report_exception(Ex), R = '$h_exception'(Ex) )).

engine_exhausted('$h_exhausted'(S, Extra)) :-
    steps_now(3, S),
    point_extra(Extra).

engine_body(VB, Vars, R) :-
    prolog_current_choice(M),
    nb_setval(h_mark, M),
    engine_fetch(Msg),
    arm_limit,
    statistics(inferences, I0),
    B is I0 + 1,                % nb_setval/2
    nb_setval(h_base, B),
    engine_first(Msg, VB, Vars, R).

engine_first(Msg, VB, Vars, R) :-
    h_receive(3, Msg, J),       % engine_first/4's call port is counted here
    engine_step(J, VB, Vars, R).

%   engine_step(+J, ...): call stage J, then advance.
engine_step(J, VB, Vars, R) :-
    h_mark_stage(J, Cs),
    user:stage(J, Vars, Cs),
    h_after(VB, Next),
    (   Next = here(K)
    ->  user:query(K, Vars),
        h_eanswer(VB, Stop),
        Stop == true,
        R = '$h_stopped'
    ;   engine_step(Next, VB, Vars, R)
    ).

%   Paused: record a stage message as posted (latest, collect mode).
h_receive(Pre, Msg, J) :-
    h_paused(Pre, receive_(Msg, J0), receive),
    J = J0.
receive_(stage(J, Collect, ctx(K, How, Att, _Cap)), J, _, L, L) :-
    nb_setval(h_latest, J),
    nb_setval(h_collect, Collect),
    nb_setval(h_k, K),
    nb_setval(h_how, How),
    nb_setval(h_attempt, Att).

%   The mark, in an engine: as h_m/1, and the stage is now done up to J
%   (backtrackable).
h_mark_stage(J, Cs) :-
    h_paused(3, mstage_(J, Cs0), mark),   % engine_step's call port is counted here
    Cs = Cs0.
mstage_(J, Cs, Steps, L0, L) :-
    b_setval(h_done, J),
    stage_constants(J, Cs),
    m_(J, Steps, L0, L).

%   At the end of a stage's goal: the next stage to call, or here.
h_after(VB, Next) :-
    prolog_current_choice(Ch),
    h_paused(3, after_(VB, Ch, Next0), point),
    Next = Next0.
after_(VB, Ch, Next, Steps, L, L) :-
    b_getval(h_done, D),
    nb_getval(h_latest, Lt),
    (   D < Lt
    ->  Next is D+1
    ;   nb_getval(h_collect, Collect),
        (   Collect == here
        ->  Next = here(Lt)
        ;   point_yield(VB, Ch, Steps, '$h_point', Msg),
            receive_(Msg, Next, Steps, L, _)
        )
    ).

point_yield(VB, Ch, Steps, Kind, Msg) :-
    nb_getval(h_latest, K),
    nb_getval(h_collect, Collect),
    nb_getval(h_mark, M),
    (   Collect == replay
    ->  Obs = [], Extra = []
    ;   state_pairs(VB, M, Ch, Kind, Obs),
        point_extra(Extra)
    ),
    (   Ch =< M -> Det = true ; Det = false ),
    Reply =.. [Kind, K, Steps, Det, Obs, Extra],
    engine_yield(Reply),
    engine_fetch(Msg).

%   h_wait/0, inside an engine: advance to the next stage (waiting for it
%   if none is left to call), and mark it.
wait_(Ch, J, Vars, Steps, L0, L) :-
    (   nb_current(h_engine, true)
    ->  b_getval(h_done, D),
        nb_getval(h_latest, Lt),
        (   D < Lt
        ->  J is D+1
        ;   b_getval(h_vars, VB),
            point_yield(VB, Ch, Steps, '$h_waiting', Msg),
            receive_(Msg, J, Steps, L0, _)
        ),
        b_getval(h_vars_list, Vars0),
        mstage_(J, Cs, Steps, L0, L),
        Vars = Vars0-Cs
    ;   J = none, L = L0
    ).

h_eanswer(VB, Stop) :-
    prolog_current_choice(Ch),
    h_paused(3, eanswer_(VB, Ch, Stop0), answer),
    Stop = Stop0.
eanswer_(VB, Ch, Stop, Steps, L, L) :-
    nb_getval(h_mark, M),
    (   Ch =< M -> Det = true ; Det = false ),
    state_pairs(VB, M, Ch, boundary, Obs),
    render_answer(VB, Det, Text, Bs),
    (   ctl(mode, storage) -> cp_count(Ch, M, NCP, _) ; NCP = null ),
    point_extra(Extra),
    engine_yield('$h_answer'(Text, Bs, Steps, Det, NCP, Obs, Extra)),
    engine_fetch(Msg),
    (   Msg == '$h_more' -> Stop = false ; Stop = true ).

%   The main thread's side: post each stage and report what comes back.
%   Fails if the computation ended (answers collected, budget, error,
%   failure), so that nothing more is posted.
session_posts([], _).
session_posts([post(J, Collect, Ctx)|Ps], E) :-
    session_out(OB, EB),
    ev(post, [stage-J, collect-Collect, out_bytes-OB, err_bytes-EB]),
    engine_reply(E, stage(J, Collect, Ctx), Reply),
    Ctx = ctx(_, _, _, Cap),
    session_reply(Reply, J, Collect, E, Cap, Cont),
    Cont == true,
    session_posts(Ps, E).

engine_reply(E, Msg, Reply) :-
    (   catch(engine_post(E, Msg, Reply0), Ex,
              ( Ex = unwind(_) -> throw(Ex) ; Reply0 = '$h_exception'(Ex) ))
    ->  Reply = Reply0
    ;   Reply = '$h_failed'
    ).

session_reply('$h_point'(K, Steps, Det, Obs, Extra), J, Collect, _, _, true) :- !,
    session_out(OB, EB),
    ev(point, [stage-J, k-K, collect-Collect, steps-Steps, det-Det, observe-obj(Obs),
               out_bytes-OB, err_bytes-EB|Extra]).
session_reply('$h_waiting'(K, Steps, Det, Obs, Extra), J, Collect, _, _, true) :- !,
    session_out(OB, EB),
    ev(waiting, [stage-J, k-K, collect-Collect, steps-Steps, det-Det, observe-obj(Obs),
                 out_bytes-OB, err_bytes-EB|Extra]).
session_reply('$h_answer'(Text, Bs, Steps, Det, NCP, Obs, Extra), J, _, E, Cap, false) :- !,
    pairs_obj(Bs, BObj),
    ev(answer, [comp-main, stage-J, index-1, text-Text, bindings-BObj, steps-Steps, det-Det, cps-NCP]),
    session_more(1, Cap, Det, Steps, Obs, Extra, J, E).
session_reply(Other, J, _, _, _, false) :-
    session_end(Other, J).

session_more(I, Cap, Det, Steps, Obs, Extra, J, E) :-
    (   Det == true
    ->  session_out(OB, EB),
        ev(comp_end, [comp-main, stage-J, ended_by-det, steps-Steps, det-true, observe-obj(Obs),
                      out_bytes-OB, err_bytes-EB|Extra])
    ;   I >= Cap
    ->  session_out(OB, EB),
        ev(comp_end, [comp-main, stage-J, ended_by-cap, steps-Steps, det-false, observe-obj(Obs),
                      out_bytes-OB, err_bytes-EB|Extra])
    ;   engine_reply(E, '$h_more', Reply),
        (   Reply = '$h_answer'(Text, Bs, Steps1, Det1, NCP1, Obs1, Extra1)
        ->  I1 is I+1,
            pairs_obj(Bs, BObj),
            ev(answer, [comp-main, stage-J, index-I1, text-Text, bindings-BObj, steps-Steps1,
                        det-Det1, cps-NCP1]),
            session_more(I1, Cap, Det1, Steps1, Obs1, Extra1, J, E)
        ;   session_end(Reply, J)
        )
    ).

session_end(Reply, J) :-
    session_out(OB, EB),
    (   Reply = '$h_exhausted'(Steps, Extra)
    ->  ev(comp_end, [comp-main, stage-J, ended_by-exhausted, steps-Steps, det-false,
                      observe-obj([where-'after-failure']), out_bytes-OB, err_bytes-EB|Extra])
    ;   Reply = '$h_exception'(Ex)
    ->  (   Ex == inference_limit_exceeded
        ->  End = budget, Text = null
        ;   End = error, message_text(Ex, Text)
        ),
        format(string(Term), "~q", [Ex]),
        ev(comp_end, [comp-main, stage-J, ended_by-End, steps-null, error_text-Text, error_term-Term,
                      out_bytes-OB, err_bytes-EB])
    ;   format(string(T), "~q", [Reply]),
        ev(comp_end, [comp-main, stage-J, ended_by-error, steps-null,
                      error_text-"the session engine ended without a harness reply",
                      error_term-T, out_bytes-OB, err_bytes-EB])
    ).

session_out(OB, EB) :-
    flush_output(user_output), flush_output(user_error),
    out_positions(OB, EB).
