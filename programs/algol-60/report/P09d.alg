begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), recursive procedures and function designators with value and name parameters (4.7, 5.4), conditional statements (4.5), the for statement (4.6), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: g, the integer of genu(g, s). The three elements of sum3 belong to its definition, and are in the program;
  comment P09d. One computation: genu(g, s) and sum3(s, total), in that order. genu computes s from n by its one case, as a function, the direction the query uses: the sequence of n alone followed by the s of genu(n + 1). sum3 then computes total from s by its one case: s must be the sequence of p, q, r followed by some sequence m, and total is p + q + r. The conjuncts run one after the other, so sum3 begins only when genu has returned. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. A cell is made only when genu(n + 1) has returned, and the store of 1000 cells is fixed in one place;
  integer n, cap, m, i, code, k, g, top, s0, total, genu1, sum31;
  Boolean ok;
  integer array hd, tl[1:1000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure genu(n);
    value n; integer n;
  comment genu(n, s), computing s from n by its one case: genu(n, the sequence of n alone ++ rest) if genu(n + 1, rest);
  begin
    integer rest;
    genu1 := genu1 + 1;
    rest := genu(n + 1);
    genu := cons(n, rest)
  end genu;

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

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constant;
  ininteger(0, g);
  top := genu1 := sum31 := 0;

  comment the query: genu(g, s) and sum3(s, total), in that order;
  s0 := genu(g);
  ok := sum3(s0, total);

  if ok then
  begin outstring(1, "[answer]total = "); outinteger(1, total); outstring(1, "[/answer]\n") end;

  comment observe: reached only if genu returns;
  outstring(1, "[observe]");
  if ¬ok then outstring(1, "no solution\n");
  outstring(1, "[operations genu/1 "); outinteger(1, genu1); outstring(1, "]\n");
  outstring(1, "[operations sum3/1 "); outinteger(1, sum31); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
