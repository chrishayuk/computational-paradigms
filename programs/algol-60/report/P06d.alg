begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value parameters (4.7, 5.4), Boolean procedures and the Boolean operator of negation (3.4), the for statement (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: L1 L2 s1 ... sL1 t1 ... tL2, the two lengths, and then the elements of the known sequences s1 and s2 of setdiff(s1, s2, d). Elements are integers, an atom being its integer code;
  comment P06d. setdiff(s1, s2, d) with s1 and s2 known: d is computed from them by the cases of setdiff, in order, as a function, the direction this query uses, and mem is a Boolean procedure that tests mem(e, s) with both known, by its cases in order. Case 3 of setdiff tests its own conjunct not mem(h, s2) with the negation of the language. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c];
  integer n, cap, m, i, code, k, l1, l2;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the two lengths, which size the cells, and then the elements;
  ininteger(0, l1); ininteger(0, l2);
  begin
  integer top, s1, s2, d, mem1, mem2, sd1, sd2, sd3;
  integer array hd, tl[1:l1 + l1 + l2 + 1];

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

  Boolean procedure mem(e, s);
    value e, s; integer e, s;
  comment mem(e, s), tested by its cases, in order. Case 1: mem(e, the sequence e followed by t), for every sequence t. Case 2: mem(e, the sequence h followed by t) if mem(e, t). The empty sequence matches neither head;
  if s = 0 then mem := false
  else if hd[s] = e then
  begin mem1 := mem1 + 1; mem := true end
  else
  begin mem2 := mem2 + 1; mem := mem(e, tl[s]) end mem;

  integer procedure setdiff(s, t);
    value s, t; integer s, t;
  comment setdiff(s, t, d), computing d from s and t by its cases, in order. Case 1: setdiff(the empty sequence, t, the empty sequence). Case 2: setdiff(h followed by r, t, d) if mem(h, t) and setdiff(r, t, d). Case 3: setdiff(h followed by r, t, h followed by d) if not mem(h, t) and setdiff(r, t, d);
  if s = 0 then
  begin sd1 := sd1 + 1; setdiff := 0 end
  else if mem(hd[s], t) then
  begin sd2 := sd2 + 1; setdiff := setdiff(tl[s], t) end
  else if ¬mem(hd[s], t) then
  begin
    integer r;
    sd3 := sd3 + 1;
    r := setdiff(tl[s], t);
    setdiff := cons(hd[s], r)
  end setdiff;

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas;
  begin
    integer j;
    outstring(1, "(");
    for j := 0 while p ≠ 0 do
    begin outinteger(1, hd[p]); p := tl[p]; if p ≠ 0 then outstring(1, ", ") end;
    outstring(1, ")")
  end printseq;

  top := mem1 := mem2 := sd1 := sd2 := sd3 := 0;
  s1 := readseq(l1);
  s2 := readseq(l2);

  d := setdiff(s1, s2);

  outstring(1, "[answer]d = "); printseq(d); outstring(1, "[/answer]\n");
  outstring(1, "[observe]");
  outstring(1, "[operations setdiff/1 "); outinteger(1, sd1); outstring(1, "]\n");
  outstring(1, "[operations setdiff/2 "); outinteger(1, sd2); outstring(1, "]\n");
  outstring(1, "[operations setdiff/3 "); outinteger(1, sd3); outstring(1, "]\n");
  outstring(1, "[operations mem/1 "); outinteger(1, mem1); outstring(1, "]\n");
  outstring(1, "[operations mem/2 "); outinteger(1, mem2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
