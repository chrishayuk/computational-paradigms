begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: La a1 ... aLa, the length and then the elements of the known sequence a of rev(a, b). Elements are integers, an atom being its integer code;
  comment P03e. rev(a, b) with a known: b is computed from a by the cases of rev, in order, as a function, the direction this query uses, and conc likewise computes its third place from the first two. Case 2 of rev takes its two conjuncts in order: q from rev(l, q), and then r from conc(q, the sequence of h alone, r). A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. A sequence of length L needs L cells to read it and L(L + 1)/2 for rev;
  integer n, cap, m, i, code, k, la;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the length, which sizes the cells, and then the elements;
  ininteger(0, la);
  begin
  integer top, a0, b0, conc1, conc2, rev1, rev2;
  integer array hd, tl[1:la + la × (la + 1) ÷ 2 + 1];

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

  integer procedure conc(a, b);
    value a, b; integer a, b;
  comment conc(a, b, c), computing c from a and b by its cases, in order. Case 1: conc(the empty sequence, b, b). Case 2: conc(h followed by a, b, h followed by c) if conc(a, b, c);
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
  comment rev(a, b), computing b from a by its cases, in order. Case 1: rev(the empty sequence, the empty sequence). Case 2: rev(h followed by l, r) if rev(l, q) and conc(q, the sequence of h alone, r);
  if a = 0 then
  begin rev1 := rev1 + 1; rev := 0 end
  else
  begin
    integer q;
    rev2 := rev2 + 1;
    q := rev(tl[a]);
    rev := conc(q, cons(hd[a], 0))
  end rev;

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

  top := conc1 := conc2 := rev1 := rev2 := 0;
  a0 := readseq(la);

  b0 := rev(a0);

  outstring(1, "[answer]b = "); printseq(b0); outstring(1, "[/answer]\n");
  outstring(1, "[observe]");
  outstring(1, "[operations rev/1 "); outinteger(1, rev1); outstring(1, "]\n");
  outstring(1, "[operations rev/2 "); outinteger(1, rev2); outstring(1, "]\n");
  outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
