/*  harnesses/swi-prolog/check CONFIGURATION PROGRAM  (cp-roles, spec-1.0)

    A syntax and static check that executes nothing of the program. It
    reads the program's terms with read_term/3 (the reader SWI-Prolog's
    compiler uses), reports syntax errors verbatim as SWI-Prolog's message
    system words them, and then checks the terms it read without calling
    any of them:

      - no clause is compiled or asserted, no directive is executed, no
        goal of the program is called, nothing is posed;
      - three kinds of directive are interpreted for their effect on
        reading only: op/3 (applied to a scratch module), and
        use_module/1,2 and ensure_loaded/1 of library(...) files (the
        library is loaded into the scratch module, so that its operators,
        such as clpfd's #=, are known and its exports count as defined).
        Loading a library runs the library's own code, never the
        program's;
      - every other directive is listed as not executed.

    Then, statically: singleton variables (as the compiler would warn),
    calls to procedures that nothing defines (the program's clauses and
    dynamic declarations, built-ins, the libraries it loads, the
    autoload index, the harness's H predicates), the harness contract
    (unknowns/2, stage/3, query/2, spawned/4), the CONSTANTS block (its
    form: one pair of markers, "% stage K" sections in increasing order,
    facts only; its entries are not counted as program clauses), the
    PROVENANCE comment, and mechanisms that the configuration does not
    have (systems/swi-prolog/README.md).

    Exit status: 0 no error; 1 errors (syntax errors, a malformed block, or no stage/3 and no
    spawned/4); 2 usage.
*/

:- module(cp_check, [main/0]).

:- use_module(library(lists)).
:- use_module(library(apply)).
:- use_module(library(readutil)).

:- dynamic defined/2, called/4, directive_seen/3, error_count/1, used_mech/3, clause_count/1, block_range/2, block_entries/1.

configs([plain, tabling, coroutines, constraints, session]).

main :-
    current_prolog_flag(argv, Argv),
    (   Argv = [C0, P0|_]
    ->  atom_string(C, C0), atom_string(P, P0)
    ;   format(user_error, "usage: check CONFIGURATION PROGRAM~n", []), halt(2)
    ),
    configs(Cs),
    (   memberchk(C, Cs) -> true
    ;   format(user_error, "check: unknown configuration ~w (one of ~w)~n", [C, Cs]), halt(2)
    ),
    (   exists_file(P) -> true
    ;   format(user_error, "check: no file ~w~n", [P]), halt(2)
    ),
    assertz(error_count(0)), assertz(clause_count(0)),
    format("check: ~w, configuration ~w (SWI-Prolog ~w). Nothing of the program is executed.~n",
           [P, C, '11.0.1']),
    absolute_file_name(P, Abs),
    block_lines(Abs),
    read_program(Abs),
    static_checks(C, Abs),
    error_count(N),
    (   N =:= 0
    ->  format("check: no errors~n", []), halt(0)
    ;   format("check: ~d error(s)~n", [N]), halt(1)
    ).

bump :- retract(error_count(N)), N1 is N+1, assertz(error_count(N1)).

%   A scratch module for reading: operators declared by op/3 and by loaded
%   libraries live here, never in user.
scratch(cp_check_program).

read_program(File) :-
    scratch(M),
    (   current_module(M) -> true ; set_module(M:class(temporary)) ),
    setup_call_cleanup(open(File, read, S, [encoding(utf8)]),
                       read_terms(S, File, M),
                       close(S)).

read_terms(S, File, M) :-
    catch(read_term(S, T, [module(M), variable_names(Vs), singletons(Ss),
                           term_position(Pos), syntax_errors(error)]),
          E, true),
    (   nonvar(E)
    ->  print_message(error, E),       % SWI-Prolog's own wording, verbatim
        bump,
        (   E = error(syntax_error(_), _) -> read_terms(S, File, M)
        ;   true
        )
    ;   T == end_of_file
    ->  true
    ;   stream_position_data(line_count, Pos, Line),
        term(T, Vs, Ss, File, Line, M),
        read_terms(S, File, M)
    ).

term(T, _, _, File, Line, _) :-
    block_range(B, E), Line > B, Line < E, !,
    block_entry(T, File, Line).
term((:- D), _, _, File, Line, M) :- !,
    directive(D, File, Line, M).
term((?- D), _, _, File, Line, M) :- !,
    directive(D, File, Line, M).
term(T, Vs, Ss, File, Line, _M) :-
    retract(clause_count(C0)), C1 is C0+1, assertz(clause_count(C1)),
    singletons(Ss, Vs, File, Line),
    (   T = (H :- B) -> true ; T = (H --> B0) -> B = dcg(B0) ; H = T, B = true ),
    (   callable(H)
    ->  functor(H, N, A0),
        (   T = (_ --> _) -> A is A0+2 ; A = A0 ),
        assertz(defined(N/A, Line)),
        (   B = dcg(_) -> true ; body_calls(B, N/A, File, Line) ),
        mechanisms_in(B, Line)
    ;   format(user_error, "ERROR: ~w:~d: a clause whose head is not callable: ~q~n", [File, Line, T]),
        bump
    ).

singletons([], _, _, _) :- !.
singletons(Ss, _, File, Line) :-
    findall(N, ( member(N=_, Ss), \+ sub_atom(N, 0, _, _, '_') ), Ns),
    (   Ns == [] -> true
    ;   format(user_error, "Warning: ~w:~d:~nWarning:    Singleton variables: ~w~n", [File, Line, Ns])
    ).

%   Directives: op/3 and library loading are interpreted for reading;
%   everything else is listed and not executed.
directive(D, File, Line, M) :-
    assertz(directive_seen(D, File, Line)),
    (   D = op(P, T, Ns)
    ->  catch(op(P, T, M:Ns), E, (print_message(error, E), bump)),
        format("  ~w:~d: op/3 applied for reading only~n", [File, Line])
    ;   library_directive(D, Lib)
    ->  catch(( use_module(M:library(Lib)) ), E,
              (print_message(error, E), bump)),
        format("  ~w:~d: library(~w) loaded for its operators and exports (the library's code, not the program's)~n",
               [File, Line, Lib]),
        assertz(used_mech(library(Lib), Line, directive))
    ;   D = dynamic(Spec)
    ->  forall(pi_member(Spec, PI), assertz(defined(PI, Line))),
        format("  ~w:~d: :- dynamic ~q (declaration noted, not executed)~n", [File, Line, Spec])
    ;   D = discontiguous(_)
    ->  true
    ;   D = table(Spec)
    ->  assertz(used_mech(table, Line, directive)),
        forall(pi_member(Spec, PI), assertz(used_mech(tabled(PI), Line, directive))),
        format("  ~w:~d: :- table ~q (noted, not executed)~n", [File, Line, Spec])
    ;   format("  ~w:~d: directive NOT executed by check: ~q~n", [File, Line, D])
    ).

library_directive(use_module(library(L)), L).
library_directive(use_module(library(L), _), L).
library_directive(ensure_loaded(library(L)), L).
library_directive(autoload(library(L)), L).
library_directive(autoload(library(L), _), L).

pi_member(Spec, _) :- var(Spec), !, fail.
pi_member((A, B), PI) :- !, ( pi_member(A, PI) ; pi_member(B, PI) ).
pi_member([H|T], PI) :- !, ( pi_member(H, PI) ; pi_member(T, PI) ).
pi_member(_:S, PI) :- !, pi_member(S, PI).
pi_member(S as _, PI) :- !, pi_member(S, PI).
pi_member(N/A, N/A) :- atom(N), integer(A).
pi_member(N//A, N/A2) :- atom(N), integer(A), A2 is A+2.

%   Calls in a body, through the control constructs and the meta-calls
%   whose argument is a goal.
body_calls(V, _, _, _) :- var(V), !.
body_calls(_:G, C, F, L) :- !, body_calls(G, C, F, L).
body_calls((A, B), C, F, L) :- !, body_calls(A, C, F, L), body_calls(B, C, F, L).
body_calls((A ; B), C, F, L) :- !, body_calls(A, C, F, L), body_calls(B, C, F, L).
body_calls((A -> B), C, F, L) :- !, body_calls(A, C, F, L), body_calls(B, C, F, L).
body_calls((A *-> B), C, F, L) :- !, body_calls(A, C, F, L), body_calls(B, C, F, L).
body_calls(\+ A, C, F, L) :- !, body_calls(A, C, F, L).
body_calls(G, C, F, L) :-
    callable(G),
    functor(G, N, A),
    assertz(called(N/A, C, F, L)),
    forall(meta_arg(G, Sub), body_calls(Sub, C, F, L)).

meta_arg(call(G), G).
meta_arg(once(G), G).
meta_arg(ignore(G), G).
meta_arg(forall(A, B), G) :- ( G = A ; G = B ).
meta_arg(findall(_, G, _), G).
meta_arg(findall(_, G, _, _), G).
meta_arg(bagof(_, G, _), G1) :- strip_carets(G, G1).
meta_arg(setof(_, G, _), G1) :- strip_carets(G, G1).
meta_arg(aggregate_all(_, G, _), G).
meta_arg(catch(G, _, R), X) :- ( X = G ; X = R ).
meta_arg(call_cleanup(G, R), X) :- ( X = G ; X = R ).
meta_arg(setup_call_cleanup(S, G, R), X) :- ( X = S ; X = G ; X = R ).
meta_arg(freeze(_, G), G).
meta_arg(when(_, G), G).
meta_arg(call_with_inference_limit(G, _, _), G).
meta_arg(engine_create(_, G, _), G).
meta_arg(engine_create(_, G, _, _), G).
meta_arg(tnot(G), G).

strip_carets(V, V) :- var(V), !.
strip_carets(_^G, G1) :- !, strip_carets(G, G1).
strip_carets(G, G).

%   Mechanisms by configuration (systems/swi-prolog/README.md).
mechanism(freeze/2, coroutining).
mechanism(when/2, coroutining).
mechanism(dif/2, coroutining).
mechanism(frozen/2, coroutining).
mechanism(engine_create/3, engines).
mechanism(engine_create/4, engines).
mechanism(engine_post/2, engines).
mechanism(engine_post/3, engines).
mechanism(engine_fetch/1, engines).
mechanism(engine_yield/1, engines).
mechanism(engine_next/2, engines).
mechanism(engine_destroy/1, engines).
mechanism(h_wait/0, engines).
mechanism(tnot/1, tabling).

mechanisms_in(_, _).

has(plain, []).
has(tabling, [tabling]).
has(coroutines, [coroutining]).
has(constraints, [coroutining, constraints]).
has(session, [coroutining, constraints, engines]).

static_checks(Config, File) :-
    contract(File),
    undefined_calls(File),
    configuration_mechanisms(Config, File),
    constants_block(File),
    provenance(File).

contract(File) :-
    forall(( member(PI, [stage/2, spawned/3]), defined(PI, L) ),
           ( format(user_error, "ERROR: ~w:~d: ~q is defined; the harness calls stage/3 (and spawned/4), whose last argument is the stage's constants~n", [File, L, PI]),
             bump )),
    forall(member(PI-What, [unknowns/2-"the computations' unknowns",
                            stage/3-"each stage's information, with its constants",
                            query/2-"the query after each stage",
                            spawned/4-"the goal of a spawned computation (P09 only)"]),
           (   defined(PI, _) -> format("  contract: ~w defined (~s)~n", [PI, What])
           ;   format("  contract: ~w not defined (~s)~n", [PI, What])
           )),
    (   ( defined(stage/3, _) ; defined(spawned/4, _) ) -> true
    ;   format(user_error, "ERROR: ~w: neither stage/3 nor spawned/4 is defined: nothing can be posed~n", [File]),
        bump
    ),
    (   defined(stage/3, _), \+ defined(query/2, _)
    ->  format(user_error, "ERROR: ~w: stage/3 is defined but query/2 is not; the harness calls query(K, Vars) after stage K~n", [File]),
        bump
    ;   true
    ),
    (   ( defined(stage/3, _) ; defined(spawned/4, _) ), \+ defined(unknowns/2, _)
    ->  format(user_error, "Warning: ~w: unknowns/2 is not defined: every computation has no unknowns, and answers show only residual goals~n", [File])
    ;   true
    ).

h_pred(h_param/2). h_pred(h_commitment/1). h_pred(emit/1). h_pred(h_count/1).
h_pred(h_candidate/0). h_pred(h_held/2). h_pred(h_wait/0).

undefined_calls(_File) :-
    scratch(M),
    forall(( called(PI, In, F, L), \+ known(PI, M) ),
           format(user_error, "Warning: ~w:~d: ~q calls ~q, which nothing defines (not executed; it would raise an existence error, as the unknown flag is error)~n", [F, L, In, PI])).

known(PI, _) :- defined(PI, _), !.
known(PI, _) :- h_pred(PI), !.
known(N/A, M) :-
    functor(G, N, A),
    (   predicate_property(system:G, defined)
    ;   predicate_property(M:G, imported_from(_))
    ;   predicate_property(M:G, defined)
    ;   '$find_library'(user, N, A, _, _)
    ;   control(N/A)
    ), !.

control((',')/2). control((;)/2). control((->)/2). control((*->)/2). control((\+)/1).
control(!/0). control(true/0). control(fail/0). control(false/0). control((=)/2).
control((:)/2). control(call/_).

configuration_mechanisms(Config, File) :-
    has(Config, Has),
    forall(( called(PI, In, F, L), mechanism(PI, Mech), \+ memberchk(Mech, Has) ),
           format(user_error, "Warning: ~w:~d: ~q calls ~q (~w), which configuration ~w does not have~n",
                  [F, L, In, PI, Mech, Config])),
    forall(( used_mech(table, L, _), \+ memberchk(tabling, Has) ),
           format(user_error, "Warning: ~w:~d: a table directive, which configuration ~w does not have~n", [File, L, Config])),
    forall(( used_mech(library(Lib), L, _), lib_mech(Lib, Mech), \+ memberchk(Mech, Has) ),
           format(user_error, "Warning: ~w:~d: library(~w) (~w), which configuration ~w does not have~n",
                  [File, L, Lib, Mech, Config])).

lib_mech(clpfd, constraints).
lib_mech(clpq, constraints).
lib_mech(clpr, constraints).
lib_mech(clpb, constraints).
lib_mech(chr, constraints).
lib_mech(when, coroutining).
lib_mech(dif, coroutining).
lib_mech(tabling, tabling).

%   The marked constants block (README, "Constants"): found before the
%   program is read, so that its entries are checked as entries, and never
%   counted as the program's clauses (the harness does not load them).
block_lines(File) :-
    read_file_to_string(File, Text, [encoding(utf8)]),
    split_string(Text, "\n", "", Lines),
    findall(I, ( nth1(I, Lines, L), sub_string(L, _, _, _, "CONSTANTS BEGIN"), comment_line(L) ), Bs),
    findall(I, ( nth1(I, Lines, L), sub_string(L, _, _, _, "CONSTANTS END"), comment_line(L) ), Es),
    (   Bs == [], Es == []
    ->  true
    ;   Bs = [B], Es = [E], B < E
    ->  assertz(block_range(B, E)),
        block_sections(Lines, B, E, File)
    ;   format(user_error, "ERROR: ~w: the CONSTANTS BEGIN / CONSTANTS END comment lines must be one pair, in that order (found BEGIN at ~w, END at ~w)~n", [File, Bs, Es]),
        bump
    ).

block_sections(Lines, B, E, File) :-
    findall(I-L, ( nth1(I, Lines, L), I > B, I < E ), In),
    sections(In, 0, File, Stages),
    assertz(block_entries(Stages)).

sections([], _, _, []).
sections([I-L|T], Cur, File, Ss) :-
    (   stage_header(L, K)
    ->  (   K > Cur -> true
        ;   format(user_error, "ERROR: ~w:~d: '% stage ~d' after stage ~d: the block's stages must increase~n", [File, I, K, Cur]), bump
        ),
        Ss = [K|Ss1], sections(T, K, File, Ss1)
    ;   ( blank_line(L) ; comment_line(L) )
    ->  sections(T, Cur, File, Ss)
    ;   (   Cur =:= 0
        ->  format(user_error, "ERROR: ~w:~d: an entry of the CONSTANTS block before any '% stage K' line~n", [File, I]), bump
        ;   true
        ),
        sections(T, Cur, File, Ss)
    ).

stage_header(L, K) :-
    split_string(L, " \t", " \t", Ws0), exclude(==(""), Ws0, ["%", "stage", N]),
    number_string(K, N), integer(K), K >= 1.
blank_line(L) :- split_string(L, "", " \t\r", [""]).
comment_line(L) :- split_string(L, "", " \t", [S]), sub_string(S, 0, 1, _, "%").

%   An entry of the block: a fact (no directive, no rule).
block_entry((:- D), File, Line) :- !,
    format(user_error, "ERROR: ~w:~d: a directive inside the CONSTANTS block: ~q (it holds only constants, as facts)~n", [File, Line, D]),
    bump.
block_entry((H :- _), File, Line) :- !,
    format(user_error, "ERROR: ~w:~d: a rule inside the CONSTANTS block, for ~q (it holds only constants, as facts)~n", [File, Line, H]),
    bump.
block_entry(_, _, _).

constants_block(_File) :-
    (   block_range(B, E)
    ->  block_entries(Ss),
        format("  constants: one block, lines ~d-~d, stages ~w (recorded as constants: block; each stage's entries reach the program only as the last argument of stage/3 from that stage on)~n", [B, E, Ss])
    ;   format("  constants: no CONSTANTS block (recorded as constants: none)~n", [])
    ).

provenance(File) :-
    read_file_to_string(File, Text, [encoding(utf8)]),
    (   sub_string(Text, _, _, _, "PROVENANCE")
    ->  format("  provenance: a PROVENANCE comment is present~n", [])
    ;   format(user_error, "Warning: ~w: no PROVENANCE comment (README, \"Provenance\")~n", [File])
    ).
