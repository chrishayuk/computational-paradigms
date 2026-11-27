% x09-count.pl without its counters: the steps must be the same.
% PROVENANCE
%   author: harness-swi-prolog, for the qualification; precursor seen: none
% END PROVENANCE
unknowns(main, ['R']).
stage(1, [R], _) :- h_param(n, N), h_param(order, [O]), build(O, N, R).
stage(2, [R], _) :- total(R, T), T > 0.
build(up, N, R) :- up(1, N, R).
build(down, N, R) :- down(N, R).
up(I, N, []) :- I > N, !.
up(I, N, [I|R]) :- I1 is I+1, up(I1, N, R).
down(0, []) :- !.
down(N, [N|R]) :- N1 is N-1, down(N1, R).
total([], 0).
total([X|Xs], T) :- total(Xs, T0), T is T0+X.
query(_, _).
