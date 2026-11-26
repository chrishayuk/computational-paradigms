% Section 1: open choicepoints.
:- use_module(common).
:- use_module(cpcount).
:- use_module(library(lists)).
:- use_module(library(apply)).
:- use_module(library(aggregate)).
:- use_module(library(pairs)).

p(1). p(2). p(3).
gen(0, []) :- !.
gen(N, [X|Xs]) :- p(X), N1 is N-1, gen(N1, Xs).
r(X) :- X > 0.
r(X) :- X < -100.
c(a, 1). c(b, 2). c(a, 3).
d(1, x). d(2, y). d(3, x).

% Choicepoints already present under `swipl -g` (no mark).
harness :- cp_since_types(-1, Ts), length(Ts, N),
    out(i, harness_choicepoints, N), out(i, harness_types, Ts).

% Open choicepoints after the first answer, and total solutions.
show(Key, G0) :- copy_term(G0, G), prolog_current_choice(M), call(G), cp_since_types(M, Ts), !,
    length(Ts, N), aggregate_all(count, G0, S),
    out(i, Key, open(N)-types(Ts)-solutions(S)).

% Choicepoints at each of the 81 answers of gen(4,_), measured inside
% findall/3 (which itself contributes 2).
answers :- cp_mark(M), findall(N, (gen(4, _), cp_since(M, N)), Ns),
    length(Ns, Len), msort(Ns, S), clumped(S, H),
    out(i, gen4_answers, Len), out(i, gen4_histogram_cp_count, H).

% Inference cost of cp_since/2 when K choicepoints are open.
cost(Tag, K) :- cp_mark(M), length(L, K), maplist(p, L),
    statistics(inferences, I0), cp_since(M, N), statistics(inferences, I1),
    D is I1-I0, format(atom(Key), "~w_cost_depth_~d", [Tag, N]), out(i, Key, D), !.

main :- harness, answers,
    show('r(5)', r(5)), show('between(1,1000000,_)', between(1, 1000000, _)),
    show('c(a,_)', c(a, _)), show('c(b,_)', c(b, _)),
    show('d(_,y)', d(_, y)), show('d(_,x)', d(_, x)),
    show('member(_,[1,2,3])', member(_, [1,2,3])),
    show('nth1(_,[a,b,c],b)', nth1(_, [a,b,c], b)),
    forall(member(K, [0,10,100,1000]), cost(nodebug, K)),
    debug, forall(member(K, [0,10,100,1000]), cost(debug, K)), nodebug.
