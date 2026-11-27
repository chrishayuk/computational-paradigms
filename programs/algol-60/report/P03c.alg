begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: La Lc a1 ... aLa c1 ... cLc, the lengths of the known sequences a and c of conc(a, b, c), and then the elements of a and of c. Elements are integers, an atom being its integer code;
  comment P03c. conc(a, b, c) with a and c known, every b. ALGOL 60 procedures compute in one direction, so this direction is a separate procedure, strip, written from the cases of conc, in order (a reformulation, METRICS.md rule 3). Case 1, conc(the empty sequence, b, b), applies when a is empty, and gives the answer b = c. Case 2, conc(h followed by a, b, h followed by c) if conc(a, b, c), applies when a and c both begin with the same h, and gives every answer b of conc(the rest of a, b, the rest of c). A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c];
  integer n, cap, m, i, code, k, la, lc;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the lengths, which size the cells, and then the elements;
  ininteger(0, la); ininteger(0, lc);
  begin
  integer top, a0, c0, answers, conc1, conc2;
  integer array hd, tl[1:la + lc + 1];

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

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas;
  begin
    integer j;
    outstring(1, "(");
    for j := 0 while not (p = 0) do
    begin outinteger(1, hd[p]); p := tl[p]; if not (p = 0) then outstring(1, ", ") end;
    outstring(1, ")")
  end printseq;

  procedure strip(a, c);
    value a, c; integer a, c;
  comment every answer b of conc(a, b, c), with a and c known;
  begin
    if a = 0 then
    begin
      conc1 := conc1 + 1;
      answers := answers + 1;
      outstring(1, "[answer]b = "); printseq(c); outstring(1, "[/answer]\n")
    end;
    if not (a = 0) then
    begin
      if not (c = 0) then
      begin
        if hd[a] = hd[c] then
        begin conc2 := conc2 + 1; strip(tl[a], tl[c]) end
      end
    end
  end strip;

  top := answers := conc1 := conc2 := 0;
  a0 := readseq(la); c0 := readseq(lc);

  strip(a0, c0);

  outstring(1, "[observe]");
  if answers = 0 then outstring(1, "no solution\n");
  outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
