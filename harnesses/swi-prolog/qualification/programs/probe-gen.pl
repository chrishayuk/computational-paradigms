% The systems file's choicepoint probe (systems/swi-prolog/probes/
% choicepoints.pl, gen(4, _)) as a made-up one-stage program.
% PROVENANCE
%   author: harness-swi-prolog; the goal is the probe's, verbatim
% END PROVENANCE
unknowns(main, ['L']).
p(1). p(2). p(3).
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
stage(1, [L], _) :- gen(4, L).
query(_, _).
