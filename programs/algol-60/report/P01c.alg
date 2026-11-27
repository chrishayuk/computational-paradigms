begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of a relation until its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: L e1 ... eL, the length and then the elements of the known sequence a of the equation x = a ++ x. Elements are integers, an atom being its integer code;
  comment P01c. One unknown x, a sequence. One stage: x = a ++ x. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. ALGOL 60 has no unknowns: x is a Boolean that says whether it has a value and the sequence it holds. The equation is held as posed until x is known, when it would be tested, a ++ x being computed by the cases of conc. Nothing here gives x a value, so it is held. The program has no occurs check, since it has no unification, and makes no cyclic value;
  integer n, cap, m, i, code, k, len;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the length of a, which sizes the cells, and then its elements;
  ininteger(0, len);
  begin
  integer top, a1, xv, held, conc1, conc2;
  Boolean xk, r1, inconsistent;
  integer array hd, tl[1:2 × len + 1];

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

  procedure examine1;
  comment the evaluator of x = a1 ++ x: with x known, it is tested. With x unknown, it waits;
  if xk then
  begin
    if not same(xv, conc(a1, xv)) then inconsistent := true;
    r1 := false
  end examine1;

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

  procedure relations;
  comment output adapter: the relation held, with x put in its places if known;
  if r1 then
  begin
    if xk then printseq(xv) else outstring(1, "x");
    outstring(1, " = "); printseq(a1); outstring(1, " ++ ");
    if xk then printseq(xv) else outstring(1, "x")
  end relations;

  xk := r1 := inconsistent := false;
  top := conc1 := conc2 := 0;
  a1 := readseq(len);
  r1 := true;
  examine1;

  comment the answer: the unknown, and the relation still held;
  if not inconsistent then
  begin
    outstring(1, "[answer]x");
    if xk then begin outstring(1, " = "); printseq(xv) end
    else if r1 then outstring(1, " held") else outstring(1, " free");
    if r1 then begin outstring(1, ", where "); relations end;
    outstring(1, "[/answer]\n")
  end;

  comment observe: the relation held, the value known, how many relations wait, and the applications of each case of conc;
  held := if r1 then 1 else 0;
  outstring(1, "[observe]");
  if inconsistent then outstring(1, "no solution\n");
  outstring(1, "held relations: ");
  if held = 0 then outstring(1, "none") else relations;
  outstring(1, "\n");
  if xk then begin outstring(1, "[bind x]"); printseq(xv); outstring(1, "[/bind]\n") end;
  if held > 0 then
  begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
  outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
  outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
