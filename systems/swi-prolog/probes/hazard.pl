% Section 5.4: an inference limit reached while library(lists) is being
% autoloaded.  This file must load no library itself, so that sum_list/2
% really is autoloaded on first call.
:- use_module(common).
p(1). p(2). p(3).
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
work :- gen(9, L), sum_list(L, S), S > 26, !.
main(plain) :-
   call_with_inference_limit(work, 1000, R1), out(i, cold_limited_result, R1),
   catch((call_with_inference_limit(work, 1000, R2), X = R2), error(E, _), X = E),
   out(i, second_limited_result, X).
% In debug mode the cold result was `!` although work/0 did not complete, and
% the C runtime printed a warning on stderr.  Classed D: whether it happens
% depends on where in the autoload the limit falls.
main(debug) :- debug,
   call_with_inference_limit(work, 1000, R1), out(d, cold_limited_result_debug, R1).
