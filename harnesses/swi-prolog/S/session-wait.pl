/*  S mechanism of the session configuration (systems/swi-prolog/README.md:
    "session: constraints, and engines, with supporting code that makes an
    application wait for an undefined procedure"; METRICS.md, class S).

    Loaded by the harness before the program, in session only, and listed
    with its size in harnesses/swi-prolog/S-mechanisms.md. It is
    supporting code (S), not harness code (H): its inferences count in the
    program's steps. Its one harness call is h_wait/0 (H).

    When the session's computation calls a procedure that has no
    definition, SWI-Prolog consults user:exception(undefined_predicate,
    PI, Action) before it raises the existence error. This hook gives the
    procedure one waiting clause and retries the call. The waiting clause
    waits (h_wait/0: the stage ends with the computation waiting, and the
    next stage is received into the same computation) until a stage has
    given the procedure a clause of its own; then it removes itself and
    calls the procedure. Outside the session's engine (a spawned
    computation runs as a separate query in the main thread) the hook does
    nothing, and the system raises its error as usual.

    The hook cannot wait itself: it is called from C, and an engine cannot
    yield from inside such a call.
*/

:- module(cp_session_wait, [waiting/1]).

:- multifile user:exception/3.
:- dynamic user:exception/3.

user:exception(undefined_predicate, PI, retry) :-
    nb_current(h_engine, true),
    (   PI = M:N/A -> true ; PI = N/A, M = user ),
    functor(H, N, A),
    \+ clause(M:H, cp_session_wait:waiting(_)),
    assertz((M:H :- cp_session_wait:waiting(M:H))).

%   The waiting clause.
waiting(MH) :-
    (   own_clause(MH)
    ->  ignore(retract((MH :- cp_session_wait:waiting(_)))),
        call(MH)
    ;   cp_harness:h_wait,
        waiting(MH)
    ).

own_clause(MH) :-
    clause(MH, B),
    B \= cp_session_wait:waiting(_),
    !.
