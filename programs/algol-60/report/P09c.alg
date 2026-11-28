begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value and name parameters (4.7, 5.4), conditional statements and expressions (3.3, 4.5), the for statement (4.6), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: g, the integer of gen(g, s). The bound 5 and the three elements of sum3 belong to the definitions, and are in the program;
  comment P09c. One computation: gen(g, s) and sum3(s, total), in that order. gen computes s from n by its cases, in order, as a function, the direction the query uses. sum3 then computes total from s by its one case: s must be the sequence of p, q, r followed by some sequence m, and total is p + q + r. The conjuncts run one after the other: gen runs to its end before sum3 begins. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. gen(g, s) needs at most 6 - g cells;
  integer n, cap, m, i, code, k, g, cells;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constant;
  ininteger(0, g);
  cells := if g > 5 then 1 else 6 - g;
  begin
  integer top, s0, total, gen1, gen2, sum31;
  Boolean ok;
  integer array hd, tl[1:cells];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure gen(n);
    value n; integer n;
  comment gen(n, s), computing s from n by its cases, in order. Case 1: gen(n, the empty sequence) if n is greater than 5. Case 2: gen(n, the sequence of n alone ++ rest) if n is at most 5 and gen(n + 1, rest), its conjuncts in that order;
  if n > 5 then
  begin gen1 := gen1 + 1; gen := 0 end
  else if n ≤ 5 then
  begin
    integer rest;
    gen2 := gen2 + 1;
    rest := gen(n + 1);
    gen := cons(n, rest)
  end gen;

  Boolean procedure sum3(s, total);
    value s; integer s, total;
  comment sum3(s, total), by its one case, computing total from s, the direction the query uses: sum3(the sequence of p, q, r ++ m, total) if p + q + r = total, for every sequence m. It is false when s has fewer than three elements;
  if s = 0 then sum3 := false
  else if tl[s] = 0 then sum3 := false
  else if tl[tl[s]] = 0 then sum3 := false
  else
  begin
    sum31 := sum31 + 1;
    total := hd[s] + hd[tl[s]] + hd[tl[tl[s]]];
    sum3 := true
  end sum3;

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
  comment output adapter: a sequence, its elements in parentheses, separated by commas;
  begin
    integer j;
    outstring(1, "(");
    for j := 0 while p ≠ 0 do
    begin num(hd[p]); p := tl[p]; if p ≠ 0 then outstring(1, ", ") end;
    outstring(1, ")")
  end printseq;

  top := gen1 := gen2 := sum31 := 0;

  comment the query: gen(g, s) and sum3(s, total), in that order;
  s0 := gen(g);
  ok := sum3(s0, total);

  if ok then
  begin
    outstring(1, "[answer]total = "); num(total); outstring(1, ", s = "); printseq(s0); outstring(1, "[/answer]\n")
  end;

  comment observe: the values, the order in which the two conjuncts ran, and the applications of each case;
  outstring(1, "[observe]");
  if ¬ok then outstring(1, "no solution\n");
  outstring(1, "order: gen ran to its end, then sum3 began\n");
  outstring(1, "[bind s]"); printseq(s0); outstring(1, "[/bind]\n");
  if ok then begin outstring(1, "[bind total]"); num(total); outstring(1, "[/bind]\n") end;
  outstring(1, "[operations gen/1 "); outinteger(1, gen1); outstring(1, "]\n");
  outstring(1, "[operations gen/2 "); outinteger(1, gen2); outstring(1, "]\n");
  outstring(1, "[operations sum3/1 "); outinteger(1, sum31); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
