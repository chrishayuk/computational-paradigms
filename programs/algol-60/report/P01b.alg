begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, recursive procedures and function designators with value parameters (4.7, 5.4), the for statement (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices for a sequence that is built up (systems file, Values), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: L e1 ... eL, the length and then the elements of the known sequence a of conc(a, s, t). A line 2: L e1 ... eL, the length and then the elements of the sequence of s = b. Elements are integers, an atom being its integer code;
  comment P01b. Unknowns s and t, sequences. Stage 1: conc(a, s, t). Stage 2: s = b. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. The cells are kept in arrays of a fixed size, cells, since a stage's sequence is read only when its stage is posed. Each unknown is a Boolean that says whether it has a value and the sequence it holds. Each relation is held as posed until enough of its places are known;
  integer cells;
  cells := 1000;
  begin
  integer n, cap, m, i, code, k, len, top, a1, b2, sv, tv, held, pass, conc1, conc2;
  Boolean sk, tk, r1, r2, changed, inconsistent;
  integer array hd, tl[1:cells];

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
  comment the evaluator of conc(a1, s, t): with s known, t is computed from a1 and s, or tested if known too. With s unknown it waits;
  if sk then
  begin
    integer c;
    c := conc(a1, sv);
    if tk then begin if not same(c, tv) then inconsistent := true end
    else begin tv := c; tk := true; changed := true end;
    r1 := false
  end examine1;

  procedure examine2;
  comment the evaluator of s = b2: s is tested if known, else given b2;
  begin
    if sk then begin if not same(sv, b2) then inconsistent := true end
    else begin sv := b2; sk := true; changed := true end;
    r2 := false
  end examine2;

  procedure propagate;
  comment every held relation is examined, in the order posed, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if r1 then examine1;
      if r2 then examine2
    end
  end propagate;

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
  comment output adapter: the relations held, with the values known put in their places;
  begin
    if r1 then
    begin
      outstring(1, "conc("); printseq(a1); outstring(1, ", ");
      if sk then printseq(sv) else outstring(1, "s");
      outstring(1, ", ");
      if tk then printseq(tv) else outstring(1, "t");
      outstring(1, ")")
    end;
    if r1 and r2 then outstring(1, ", ");
    if r2 then begin outstring(1, "s = "); printseq(b2) end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  sk := tk := r1 := r2 := inconsistent := false;
  top := conc1 := conc2 := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then begin ininteger(0, len); a1 := readseq(len); r1 := true end
    else if k = 2 then begin ininteger(0, len); b2 := readseq(len); r2 := true end;

    propagate;

    comment the answer: every unknown, and the relations still held;
    if not inconsistent then
    begin
      outstring(1, "[answer]s");
      if sk then begin outstring(1, " = "); printseq(sv) end
      else if r1 or r2 then outstring(1, " held") else outstring(1, " free");
      outstring(1, ", t");
      if tk then begin outstring(1, " = "); printseq(tv) end
      else if r1 then outstring(1, " held") else outstring(1, " free");
      if r1 or r2 then begin outstring(1, ", where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the relations held, the values known, how many relations wait, and the applications of each case of conc;
    held := (if r1 then 1 else 0) + (if r2 then 1 else 0);
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "held relations: ");
    if held = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if sk then begin outstring(1, "[bind s]"); printseq(sv); outstring(1, "[/bind]\n") end;
    if tk then begin outstring(1, "[bind t]"); printseq(tv); outstring(1, "[/bind]\n") end;
    if held > 0 then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
    outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
    outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
  end
end
