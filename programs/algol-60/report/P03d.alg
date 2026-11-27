begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: Lb Lc b1 ... bLb c1 ... cLc, the lengths of the known sequences b and c of conc(a, b, c), and then the elements of b and of c. Elements are integers, an atom being its integer code;
  comment P03d. conc(a, b, c) with b and c known, every a. ALGOL 60 procedures compute in one direction, so this direction is a separate procedure, prefix, written from the cases of conc, in order (a reformulation, METRICS.md rule 3). Case 1, conc(the empty sequence, b, b), applies when c equals b, and gives the answer a empty. Case 2, conc(h followed by a, b, h followed by c) if conc(a, b, c), applies when c is h followed by c1, and gives a = h followed by a1 for every answer a1 of conc(a1, b, c1). The heads taken by case 2 so far are kept in the array path, an extra argument of the search. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c];
  integer n, cap, m, i, code, k, lb, lc;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the lengths, which size the cells, and then the elements;
  ininteger(0, lb); ininteger(0, lc);
  begin
  integer top, b0, c0, answers, conc1, conc2;
  integer array hd, tl[1:lb + lc + 1];
  integer array path[1:lc + 1];

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

  Boolean procedure same(p, q);
    value p, q; integer p, q;
  comment the equality of two sequences;
  same := if p = 0 then q = 0 else if q = 0 then false else if hd[p] = hd[q] then same(tl[p], tl[q]) else false;

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

  procedure prefix(c, d);
    value c, d; integer c, d;
  comment every answer a of conc(a, b0, c), with b0 and c known, a being path[1], ..., path[d] followed by the a of this call;
  begin
    if same(b0, c) then
    begin
      conc1 := conc1 + 1;
      answers := answers + 1;
      outstring(1, "[answer]a = "); printpath(d); outstring(1, "[/answer]\n")
    end;
    if not (c = 0) then
    begin
      conc2 := conc2 + 1;
      path[d + 1] := hd[c];
      prefix(tl[c], d + 1)
    end
  end prefix;

  top := answers := conc1 := conc2 := 0;
  b0 := readseq(lb); c0 := readseq(lc);

  prefix(c0, 0);

  outstring(1, "[observe]");
  if answers = 0 then outstring(1, "no solution\n");
  outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
