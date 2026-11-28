begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values, and problems/13-deterministic-scale.md, Representation), rev and conc as batch 1A's P03e transcribes them (programs/algol-60/README.md), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: k, the first place of range(k, n, s). n is the instance's size, from the instance line;
  comment P13c, prescribed. range(k, n, s) and rev(s, r), in that order. range computes s from k and n by its cases, in order, as a function, the direction the query uses. Case 1: range(m, n, the empty sequence) if m is greater than n. Case 2: range(m, n, the sequence of m alone ++ t) if m is at most n and range(m + 1, n, t). rev is as in P03, computing r from s by its cases, in order. Case 1: rev(the empty sequence, the empty sequence). Case 2: rev(the sequence of h alone ++ l, r) if rev(l, q) and conc(q, the sequence of h alone, r), its conjuncts in order. conc computes its third place from the first two by its cases, in order. Case 1: conc(the empty sequence, b, b). Case 2: conc(the sequence of h alone ++ a, b, the sequence of h alone ++ c) if conc(a, b, c). A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of hd[c] alone ++ the sequence tl[c], so that taking the tail is the one subscript tl[c], in constant time. No cell is ever given back, since ALGOL 60 has no reclaiming of store: range makes L cells for its L elements, and rev makes L more for the sequences of h alone and L(L - 1)/2 in conc, so the store is sized for L + L + L(L + 1)/2 cells, from k and n;
  integer n, cap, m, i, code, k, lo, len, size;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constant;
  ininteger(0, lo);
  len := if lo > n then 0 else n - lo + 1;
  size := len + len + len × (len + 1) ÷ 2 + 1;
  begin
  integer top, s0, r0, range1, range2, rev1, rev2, conc1, conc2;
  integer array hd, tl[1:size];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of h alone ++ the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure range(m, n);
    value m, n; integer m, n;
  comment range(m, n, s), computing s by its cases, in order;
  if m > n then
  begin range1 := range1 + 1; range := 0 end
  else
  begin
    integer t;
    range2 := range2 + 1;
    t := range(m + 1, n);
    range := cons(m, t)
  end range;

  integer procedure conc(a, b);
    value a, b; integer a, b;
  comment conc(a, b, c), computing c by its cases, in order;
  if a = 0 then
  begin conc1 := conc1 + 1; conc := b end
  else
  begin
    integer c;
    conc2 := conc2 + 1;
    c := conc(tl[a], b);
    conc := cons(hd[a], c)
  end conc;

  integer procedure rev(a);
    value a; integer a;
  comment rev(a, r), computing r by its cases, in order;
  if a = 0 then
  begin rev1 := rev1 + 1; rev := 0 end
  else
  begin
    integer q;
    rev2 := rev2 + 1;
    q := rev(tl[a]);
    rev := conc(q, cons(hd[a], 0))
  end rev;

  procedure num(v);
    value v; integer v;
  comment output adapter: an integer, a minus sign if it is negative and then its decimal digits, with no spaces;
  begin
    integer d;
    if v < 0 then begin outstring(1, "-"); num(-v) end
    else
    begin
      if v ≥ 10 then num(v ÷ 10);
      d := v - v ÷ 10 × 10;
      if d = 0 then outstring(1, "0") else if d = 1 then outstring(1, "1") else if d = 2 then outstring(1, "2")
      else if d = 3 then outstring(1, "3") else if d = 4 then outstring(1, "4") else if d = 5 then outstring(1, "5")
      else if d = 6 then outstring(1, "6") else if d = 7 then outstring(1, "7") else if d = 8 then outstring(1, "8")
      else outstring(1, "9")
    end
  end num;

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas, with a new line after every ten elements so that no line of the X1 passes its 144 positions;
  begin
    integer j, c;
    outstring(1, "(");
    c := 0;
    for j := 0 while p ≠ 0 do
    begin
      num(hd[p]); p := tl[p]; c := c + 1;
      if p ≠ 0 then outstring(1, ", ");
      if c = 10 then begin outstring(1, "\n"); c := 0 end
    end;
    outstring(1, ")")
  end printseq;

  top := range1 := range2 := rev1 := rev2 := conc1 := conc2 := 0;

  comment the query: range(k, n, s) and rev(s, r), in that order;
  s0 := range(lo, n);
  r0 := rev(s0);

  outstring(1, "[answer]s = "); printseq(s0); outstring(1, ",\n"); outstring(1, "r = "); printseq(r0); outstring(1, "[/answer]\n");
  comment observe: the applications of each case, and the store held after the answer;
  outstring(1, "[observe]");
  outstring(1, "cells held after the answer: "); num(top); outstring(1, ", the cells of s and r and of every sequence made by conc on the way, none given back\n");
  outstring(1, "[operations range/1 "); num(range1); outstring(1, "]\n");
  outstring(1, "[operations range/2 "); num(range2); outstring(1, "]\n");
  outstring(1, "[operations rev/1 "); num(rev1); outstring(1, "]\n");
  outstring(1, "[operations rev/2 "); num(rev2); outstring(1, "]\n");
  outstring(1, "[operations conc/1 "); num(conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); num(conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
