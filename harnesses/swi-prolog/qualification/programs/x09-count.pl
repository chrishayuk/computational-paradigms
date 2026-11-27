% Made-up problem X09: a list of n in an arrival order, with counters.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['R']).
stage(1, [R], _) :- h_param(n, N), h_param(order, [O]), build(O, N, R).
stage(2, [R], _) :- total(R, T), T > 0, h_held(partial_sums, 1).
build(up, N, R) :- up(1, N, R).
build(down, N, R) :- down(N, R).
up(I, N, []) :- I > N, !, h_count('up/1').
up(I, N, [I|R]) :- h_count('up/2'), h_candidate, I1 is I+1, up(I1, N, R).
down(0, []) :- !, h_count('down/1').
down(N, [N|R]) :- h_count('down/2'), N1 is N-1, down(N1, R).
total([], 0).
total([X|Xs], T) :- total(Xs, T0), T is T0+X.
query(_, _).
