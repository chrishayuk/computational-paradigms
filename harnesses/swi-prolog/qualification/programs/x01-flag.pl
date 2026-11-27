% Made-up problem X01 (not one of P01-P16): the two stripes of a flag.
% Stage 1: stripe a is a colour. Stage 2: stripe b is a colour other than
% a's. Stage 3: a is the given first colour.
%
% PROVENANCE
%   author: harness-swi-prolog (the harness author), for the qualification
%   precursor seen: none (a made-up problem)
%   idioms: conjunctive queries, ISO Prolog; member/2 and memberchk/2 of
%   library(lists) over the stage's constants
% END PROVENANCE

% CONSTANTS BEGIN
% stage 1
colour(red).
colour(green).
colour(blue).
% stage 3
first_colour(green).
% CONSTANTS END

unknowns(main, ['A', 'B']).

stage(1, [A, _], Cs) :- member(colour(A), Cs).
stage(2, [A, B], Cs) :- member(colour(B), Cs), B \== A.
stage(3, [A, _], Cs) :- memberchk(first_colour(A), Cs).

query(_, _).
