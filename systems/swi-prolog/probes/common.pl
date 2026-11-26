% Output helper shared by the probes.  Every result line has the form
%   C|key=value
% where C is I (expected to be platform-independent) or D (expected to
% depend on platform, build or memory layout).  run.sh adds the probe name.
:- module(common, [out/3, delta/2]).
out(i, K, V) :- !, format("I|~w=~q~n", [K, V]).
out(d, K, V) :- format("D|~w=~q~n", [K, V]).

% Inferences used by Goal: difference of two statistics/2 readings
% (includes 1 for call/1 and 1 for the second statistics/2 call).
:- meta_predicate delta(0, -).
delta(G, D) :- statistics(inferences, I0), call(G), statistics(inferences, I1), D is I1-I0.
