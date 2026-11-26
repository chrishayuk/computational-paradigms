% Section 5: inferences used by the interactive toplevel between two
% queries.  run.sh pipes the two queries below into `swipl -f none -q toplevel.pl`.
%   statistics(inferences, A), nb_setval(tl_a, A), fail.
%   nb_getval(tl_a, A), statistics(inferences, B), D is B-A, format("D|between_queries=~d~n", [D]), fail.
