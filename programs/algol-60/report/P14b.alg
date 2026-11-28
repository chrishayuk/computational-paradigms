begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive Boolean procedures with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), atoms as integer codes and sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: L c1 ... cL, the length and then the messages of the one sequence, each as its code, 1 for INC and 2 for READ. The READ messages bind the unknowns r1, r2 and so on, in the order they come in the sequence;
  comment P14b. run(m, 0), with m the sequence of the stage, by the cases of run, in order, as a Boolean procedure that walks the sequence and gives each READ's unknown its value, the direction the query uses. Case 1: run(the empty sequence, c). Case 2: run(the sequence of INC alone ++ s, c) if run(s, c + 1). Case 3: run(the sequence of READ(r) alone ++ s, c) if r = c and run(s, c), its conjuncts in order. A message that is neither INC nor READ has no case, and run is false for it. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of hd[c] alone ++ the sequence tl[c]. The unknowns r1, r2 and so on are an integer array, as many as the messages;
  integer n, cap, m, i, code, k, len;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the length, which sizes the cells, and then the messages;
  ininteger(0, len);
  begin
  integer top, s0, nr, run1, run2, run3;
  Boolean ok;
  integer array hd, tl, rv[1:len + 1];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of h alone ++ the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer j, e, first, last, cl;
    first := last := 0;
    for j := 1 step 1 until len do
    begin
      ininteger(0, e); cl := cons(e, 0);
      if last = 0 then first := cl else tl[last] := cl;
      last := cl
    end;
    readseq := first
  end readseq;

  Boolean procedure run(s, c);
    value s, c; integer s, c;
  comment run(s, c), by its cases, in order;
  if s = 0 then
  begin
    comment case 1;
    run1 := run1 + 1;
    run := true
  end
  else if hd[s] = 1 then
  begin
    comment case 2;
    run2 := run2 + 1;
    run := run(tl[s], c + 1)
  end
  else if hd[s] = 2 then
  begin
    comment case 3;
    run3 := run3 + 1;
    nr := nr + 1;
    rv[nr] := c;
    run := run(tl[s], c)
  end
  else run := false;

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

  top := nr := run1 := run2 := run3 := 0;
  s0 := readseq(len);

  comment the query: run(m, 0);
  ok := run(s0, 0);

  comment the answer: every unknown the READ messages have bound;
  if ok then
  begin
    outstring(1, "[answer]");
    if nr = 0 then outstring(1, "no unknowns")
    else
    begin
      integer j;
      for j := 1 step 1 until nr do
      begin
        outstring(1, "r"); num(j); outstring(1, " = "); num(rv[j]);
        if j < nr then outstring(1, ", ")
      end
    end;
    outstring(1, "[/answer]\n")
  end;

  comment observe: the unknowns bound, and the applications of each case of run;
  outstring(1, "[observe]");
  if ¬ok then outstring(1, "no solution: a message with no case of run\n");
  outstring(1, "the count was the second place of run, passed down the recursion, and nothing is held after it\n");
  if ok then
  begin
    integer j;
    for j := 1 step 1 until nr do
    begin outstring(1, "[bind r"); num(j); outstring(1, "]"); num(rv[j]); outstring(1, "[/bind]\n") end
  end;
  outstring(1, "[operations run/1 "); num(run1); outstring(1, "]\n");
  outstring(1, "[operations run/2 "); num(run2); outstring(1, "]\n");
  outstring(1, "[operations run/3 "); num(run3); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
