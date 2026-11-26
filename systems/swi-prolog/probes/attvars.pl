% Section 4: attributed variables and residual goals.  Each case is run
% twice; the first (cold) pass includes autoloading and is classed D.
:- use_module(common).
:- use_module(library(clpfd)).
:- use_module(library(dif)).
:- use_module(library(when)).
:- use_module(library(lists)).
:- use_module(library(apply)).

count(Pass, Tag, T) :-
    statistics(inferences, I0), term_attvars(T, AVs), length(AVs, NAV),
    statistics(inferences, I1), copy_term(T, _, Gs), length(Gs, NG),
    statistics(inferences, I2),
    findall(x, (member(V, AVs), frozen(V, G), G \== true), Fs), length(Fs, NF),
    statistics(inferences, I3),
    C1 is I1-I0-1, C2 is I2-I1-1, C3 is I3-I2-1,
    ( Pass == warm -> C = i ; C = d ),
    (   Pass == warm
    ->  atom_concat(Tag, '_attvars', K1), out(i, K1, NAV),
        atom_concat(Tag, '_residual_goals', K2), out(i, K2, NG),
        atom_concat(Tag, '_frozen_nontrivial', K3), out(i, K3, NF)
    ;   true
    ),
    atomic_list_concat([Pass, '_', Tag, '_inf_term_attvars'], K4), out(C, K4, C1),
    atomic_list_concat([Pass, '_', Tag, '_inf_copy_term'], K5), out(C, K5, C2),
    atomic_list_concat([Pass, '_', Tag, '_inf_frozen'], K6), out(C, K6, C3).

cases(P) :-
    count(P, none, f(_,_)),
    ( freeze(X1, writeln(x)), freeze(X1, true), freeze(Y1, writeln(y)), count(P, freeze, f(X1,Y1)) ),
    ( when(ground(X2-Y2), writeln(g)), count(P, when, f(X2,Y2)) ),
    ( dif(X3, Y3), dif(X3, a), count(P, dif, f(X3,Y3)) ),
    ( dif(f(X4,Z4), f(Y4,b)), count(P, dif_hidden, f(X4,Y4)), count(P, dif_with_z, f(X4,Y4,Z4)) ),
    ( X5 #> 3, X5 #< Y5, Y5 in 0..10, Z5 #= X5+Y5, count(P, clpfd, f(X5,Y5,Z5)) ),
    ( length(L6, 200), L6 ins 1..300, all_different(L6), count(P, clpfd_200_alldiff, L6) ).

hidden(X) :- freeze(_Lost, true), dif(X, Y), Y = b.
g200(L) :- length(L, 200), L ins 1..300, all_different(L).
crv :- hidden(_), g200(_),
   statistics(inferences, A0), hidden(X), statistics(inferences, A1), D0 is A1-A0-1,
   term_attvars(X, AV), length(AV, N0), out(i, hidden_inferences, D0), out(i, hidden_term_attvars, N0),
   statistics(inferences, B0), call_residue_vars(hidden(_), Vs), statistics(inferences, B1), D1 is B1-B0-1,
   length(Vs, N1), out(i, hidden_crv_inferences, D1), out(i, hidden_residue_vars, N1),
   statistics(inferences, C0), g200(L), statistics(inferences, C1), D2 is C1-C0-1,
   statistics(inferences, E0), call_residue_vars(g200(_), V2), statistics(inferences, E1), D3 is E1-E0-1,
   length(V2, N2), term_attvars(L, A2), length(A2, NA2),
   out(i, g200_inferences, D2), out(i, g200_crv_inferences, D3), out(i, g200_residue_vars, N2), out(i, g200_term_attvars, NA2).

main(counts) :- cases(cold), cases(warm).
main(residue) :- crv.
