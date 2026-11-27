% A program whose every directive, goal and clause would leave a trace if
% it ran (a line EXECUTED-... on standard output, and the file
% named by CP_QUAL_TRACE, programs/noexec-trace.txt): check must leave none
% (qualification, "check executes nothing").
:- getenv('CP_QUAL_TRACE', F), assertz(trace_file(F)).   % run.py sets it
:- initialization(trace_it(initialization)).
:- trace_it(directive).
trace_it(Where) :-
    atom_concat('EXE', 'CUTED-', M0), atom_concat(M0, Where, M),
    writeln(M),
    trace_file(F), open(F, append, S), writeln(S, M), close(S).
unknowns(main, ['X']).
stage(1, [X], _) :- trace_it(stage), X = 1.
query(_, _) :- trace_it(query).
