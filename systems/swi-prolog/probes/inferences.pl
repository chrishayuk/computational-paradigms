% Section 5: inference counts.  Run by run.sh in three variants: plain,
% -O, and debug mode (main(debug) switches the debugger on first).
:- use_module(common).
:- use_module(library(statistics)).

p(1). p(2). p(3).
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
work :- gen(9, L), sum_list(L, S), S > 26, !.          % sum_list/2 is autoloaded
nrev([], []).
nrev([H|T], R) :- nrev(T, RT), append(RT, [H], R).     % append/3 is autoloaded
w2 :- numlist(1, 300, L), nrev(L, _).

% Smallest limit at which call_with_inference_limit/3 does not report
% inference_limit_exceeded.
minlimit(_, Lo, Hi, L) :- Lo >= Hi, !, L = Hi.
minlimit(G, Lo, Hi, L) :- Mid is (Lo+Hi)//2,
   (   catch(call_with_inference_limit(G, Mid, R), _, R = inference_limit_exceeded),
       R \== inference_limit_exceeded
   ->  minlimit(G, Lo, Mid, L)
   ;   Lo1 is Mid+1, minlimit(G, Lo1, Hi, L)
   ).

counts :-
   delta(work, Wc), delta(work, W1), delta(work, W2), delta(w2, Vc), delta(w2, V1), delta(true, T),
   out(d, work_cold, Wc), out(i, work_warm_1, W1), out(i, work_warm_2, W2),
   out(d, w2_cold, Vc), out(i, w2_warm, V1), out(i, delta_true, T),
   statistics(self_inferences, SI), statistics(inferences, II), DS is II-SI, out(i, inferences_minus_self, DS),
   delta(garbage_collect, DG), out(i, delta_garbage_collect, DG),
   call_time(work, Time), get_dict(inferences, Time, CT), out(i, call_time_work_inferences, CT).
limits :- minlimit(work, 1, 1000000, LW), minlimit(w2, 1, 1000000, L2),
   out(i, minlimit_work, LW), out(i, minlimit_w2, L2).

main(plain) :- counts, limits, flags.
main(optimise) :- counts, limits, flags.
main(debug) :- debug, counts, flags.
flags :- current_prolog_flag(optimise, O), current_prolog_flag(debug, D),
   out(i, flag_optimise, O), out(i, flag_debug, D).
