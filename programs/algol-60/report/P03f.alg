begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value and name parameters (4.7, 5.4), name parameters to return results (4.7.3.2), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: Lb b1 ... bLb, the length and then the elements of the known sequence b of rev(a, b). Elements are integers, an atom being its integer code;
  comment P03f. rev(a, b) with b known, every a. ALGOL 60 procedures compute in one direction, so this direction is a separate procedure, unrev, written from the cases of rev, in order, with conc used in a direction of its own, lastsplit, written from the cases of conc (reformulations, METRICS.md rule 3). Case 1 of rev, rev(the empty sequence, the empty sequence), applies when b is empty, and gives the answer a empty. Case 2, rev(h followed by l, r) if rev(l, q) and conc(q, the sequence of h alone, r), has its conjuncts taken in the other order (a move), since r is known and q is not: lastsplit finds q and h from r by conc, and then every answer l of rev(l, q) gives the answer a = h followed by l. The heads taken by case 2 so far are kept in the array path, an extra argument of the search. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. A sequence of length L needs L cells to read it and fewer than L(L + 1)/2 for lastsplit;
  integer n, cap, m, i, code, k, lb;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the length, which sizes the cells, and then the elements;
  ininteger(0, lb);
  begin
  integer top, b0, answers, conc1, conc2, rev1, rev2;
  integer array hd, tl[1:lb + lb × (lb + 1) ÷ 2 + 1];
  integer array path[1:lb + 1];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer j, e, first, last, c;
    first := last := 0;
    for j := 1 step 1 until len do
    begin
      ininteger(0, e); c := cons(e, 0);
      if last = 0 then first := c else tl[last] := c;
      last := c
    end;
    readseq := first
  end readseq;

  Boolean procedure lastsplit(r, q, h);
    value r; integer r, q, h;
  comment conc(q, the sequence of h alone, r), with r known: true, with q and h given their values, where it has an answer, from the cases of conc, in order. Case 1, conc(the empty sequence, b, b), applies when r is the sequence of one element h, and gives q empty. Case 2, conc(g followed by a, b, g followed by c) if conc(a, b, c), applies when r is g followed by r1, and gives q = g followed by q1 for the answer q1, h of conc(q1, the sequence of h alone, r1). The sequence of h alone has one answer in r at most, so at most one case gives one;
  begin
    integer q1, h1;
    lastsplit := false;
    if not (r = 0) then
    begin
      if tl[r] = 0 then
      begin conc1 := conc1 + 1; q := 0; h := hd[r]; lastsplit := true end;
      if lastsplit(tl[r], q1, h1) then
      begin conc2 := conc2 + 1; q := cons(hd[r], q1); h := h1; lastsplit := true end
    end
  end lastsplit;

  procedure printpath(d);
    value d; integer d;
  comment output adapter: the sequence path[1], ..., path[d];
  begin
    integer j;
    outstring(1, "(");
    for j := 1 step 1 until d do
    begin outinteger(1, path[j]); if j < d then outstring(1, ", ") end;
    outstring(1, ")")
  end printpath;

  procedure unrev(r, d);
    value r, d; integer r, d;
  comment every answer a of rev(a, r), with r known, a being path[1], ..., path[d] followed by the a of this call;
  begin
    integer q, h;
    if r = 0 then
    begin
      rev1 := rev1 + 1;
      answers := answers + 1;
      outstring(1, "[answer]a = "); printpath(d); outstring(1, "[/answer]\n")
    end;
    if lastsplit(r, q, h) then
    begin
      rev2 := rev2 + 1;
      path[d + 1] := h;
      unrev(q, d + 1)
    end
  end unrev;

  top := answers := conc1 := conc2 := rev1 := rev2 := 0;
  b0 := readseq(lb);

  unrev(b0, 0);

  outstring(1, "[observe]");
  if answers = 0 then outstring(1, "no solution\n");
  outstring(1, "[operations rev/1 "); outinteger(1, rev1); outstring(1, "]\n");
  outstring(1, "[operations rev/2 "); outinteger(1, rev2); outstring(1, "]\n");
  outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
