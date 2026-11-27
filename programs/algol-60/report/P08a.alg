begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement with step-until and while elements (4.6), conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation and of the application of a relation not yet defined until it can be decided, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 6: L e1 ... eL, the length and then the elements of the known sequence s of b = s ++ c. Elements are integers. No other stage has constants;
  comment P08a, and P08b, which is its stages 1 to 3. Unknown sequences a, b, c, and unknown elements x, y, z. Stage 1: a = the sequence of x, y, z. Stage 2: rev(a, b), with rev not yet defined. Stage 3: x = y. Stage 4: the definitions of rev and conc, as in P03, which arrive together. Stage 5: y = z. Stage 6: b = s ++ c. ALGOL 60 has no definitions that arrive while a program runs: the procedures rev and conc are in the text, and the Boolean defined says whether their definition has arrived. An application of rev before then is held as posed, awaiting the definition, and is neither true nor false: the fourth of the problem's four states, the open reading. When the definition has arrived it is decided as rev and conc compute it. An element of a sequence is an index into the arrays ek and ev, a Boolean that says whether it has a value and an integer that holds it: 1 is x, 2 is y, 3 is z, and the elements of s are further indices, each with its value. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of the element hd[c] followed by the sequence tl[c]. rev and conc move elements and never look at their values, so they work on elements that have none. Each unknown sequence is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until enough of its places are known, when it gives the remaining place its value or is tested. Every held relation is examined in the order posed, again and again, until a whole pass gives no unknown a value;
  integer n, cap, m, i, code, k, j, top, nel, av, bv, cv, sv, held, pass, rev1, rev2, conc1, conc2;
  Boolean ak, bk, ck, q1, q2, q3, q5, q6, defined, changed, inconsistent;
  integer array hd, tl, ev[1:1000];
  Boolean array ek[1:1000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of the element h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  Boolean procedure sameel(e, f);
    value e, f; integer e, f;
  comment the equality of two elements: the same unknown, or two values that are equal. Two different unknowns are not taken as equal: no test here meets one;
  sameel := if e = f then true else if ek[e] ∧ ek[f] then ev[e] = ev[f] else false;

  Boolean procedure same(p, q);
    value p, q; integer p, q;
  comment the equality of two sequences, element by element;
  same := if p = 0 then q = 0 else if q = 0 then false else if sameel(hd[p], hd[q]) then same(tl[p], tl[q]) else false;

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

  procedure equal(e, f);
    value e, f; integer e, f;
  comment the evaluator of an equation between two elements, held until one of them is known: it gives the other its value, or tests it when both are known. It is decided at once, in the evaluator of b = s ++ c, where one of them is always known;
  if ek[e] ∧ ek[f] then
  begin if ev[e] ≠ ev[f] then inconsistent := true end
  else if ek[e] then
  begin ev[f] := ev[e]; ek[f] := true; changed := true end
  else if ek[f] then
  begin ev[e] := ev[f]; ek[e] := true; changed := true end;

  procedure examine1;
  comment the evaluator of a = the sequence of x, y, z: with a unknown, a is given that value. With a known it would be tested, which no stage reaches;
  begin
    if ak then
    begin if ¬same(av, cons(1, cons(2, cons(3, 0)))) then inconsistent := true end
    else
    begin av := cons(1, cons(2, cons(3, 0))); ak := true; changed := true end;
    q1 := false
  end examine1;

  procedure examine2;
  comment the evaluator of the application rev(a, b): held while the definition of rev and conc has not arrived, and while a is unknown. Then b is computed from a by rev, or tested if known;
  if defined ∧ ak then
  begin
    integer r;
    r := rev(av);
    if bk then
    begin if ¬same(bv, r) then inconsistent := true end
    else
    begin bv := r; bk := true; changed := true end;
    q2 := false
  end examine2;

  procedure examine3;
  comment the evaluator of x = y, held until one of them is known;
  if ek[1] ∨ ek[2] then begin equal(1, 2); q3 := false end examine3;

  procedure examine5;
  comment the evaluator of y = z, held until one of them is known;
  if ek[2] ∨ ek[3] then begin equal(2, 3); q5 := false end examine5;

  procedure examine6;
  comment the evaluator of b = s ++ c. With b known, each element of s is equated with the element of b in its place, which gives that element its value or tests it, and c is the rest of b, or is tested with it. With b unknown and c known, b is s ++ c. With both unknown, it waits;
  if bk then
  begin
    integer p, e, w;
    p := bv; e := sv;
    for w := 0 while e ≠ 0 ∧ ¬inconsistent do
    begin
      if p = 0 then inconsistent := true
      else begin equal(hd[p], hd[e]); p := tl[p]; e := tl[e] end
    end;
    if ¬inconsistent then
    begin
      if ck then
      begin if ¬same(cv, p) then inconsistent := true end
      else
      begin cv := p; ck := true; changed := true end
    end;
    q6 := false
  end
  else if ck then
  begin
    integer w, e, first, last, c;
    first := last := 0; e := sv;
    for w := 0 while e ≠ 0 do
    begin
      c := cons(hd[e], 0);
      if last = 0 then first := c else tl[last] := c;
      last := c; e := tl[e]
    end;
    if last = 0 then bv := cv else begin tl[last] := cv; bv := first end;
    bk := true; changed := true; q6 := false
  end examine6;

  procedure propagate;
  comment every held relation is examined, in the order posed, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if q1 then examine1;
      if q2 then examine2;
      if q3 then examine3;
      if q5 then examine5;
      if q6 then examine6
    end
  end propagate;

  procedure digits(v);
    value v; integer v;
  comment output adapter: a natural number, its decimal digits with no sign and no spaces;
  begin
    integer d;
    if v ≥ 10 then digits(v ÷ 10);
    d := v - v ÷ 10 × 10;
    if d = 0 then outstring(1, "0") else if d = 1 then outstring(1, "1") else if d = 2 then outstring(1, "2")
    else if d = 3 then outstring(1, "3") else if d = 4 then outstring(1, "4") else if d = 5 then outstring(1, "5")
    else if d = 6 then outstring(1, "6") else if d = 7 then outstring(1, "7") else if d = 8 then outstring(1, "8")
    else outstring(1, "9")
  end digits;

  procedure printint(v);
    value v; integer v;
  comment output adapter: an integer, its sign if negative and its digits, with no padding, so that an answer with many values stays on one line;
  if v < 0 then begin outstring(1, "-"); digits(-v) end else digits(v);

  procedure printel(e);
    value e; integer e;
  comment output adapter: an element, its value if known, else the name of its unknown;
  if ek[e] then printint(ev[e]) else if e = 1 then outstring(1, "x") else if e = 2 then outstring(1, "y") else outstring(1, "z");

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas;
  begin
    integer w;
    outstring(1, "(");
    for w := 0 while p ≠ 0 do
    begin printel(hd[p]); p := tl[p]; if p ≠ 0 then outstring(1, ", ") end;
    outstring(1, ")")
  end printseq;

  procedure seqplace(known, v, name);
    value known, v, name; Boolean known; integer v, name;
  comment output adapter: a sequence in a relation, its value if known, else the name of its unknown, 1 for a, 2 for b, 3 for c;
  if known then printseq(v) else if name = 1 then outstring(1, "a") else if name = 2 then outstring(1, "b") else outstring(1, "c");

  procedure seqstate(known, v, inheld, name);
    value known, v, inheld, name; Boolean known, inheld; integer v, name;
  comment output adapter: an unknown sequence, as its value, or held by a relation, or free;
  begin
    if name = 1 then outstring(1, "a") else if name = 2 then outstring(1, "b") else outstring(1, "c");
    if known then begin outstring(1, " = "); printseq(v) end
    else if inheld then outstring(1, " held") else outstring(1, " free")
  end seqstate;

  procedure elstate(e, inheld);
    value e, inheld; integer e; Boolean inheld;
  comment output adapter: an unknown element, as its value, or held by a relation, or free;
  begin
    if e = 1 then outstring(1, "x") else if e = 2 then outstring(1, "y") else outstring(1, "z");
    if ek[e] then begin outstring(1, " = "); printint(ev[e]) end
    else if inheld then outstring(1, " held") else outstring(1, " free")
  end elstate;

  procedure relations;
  comment output adapter: the relations held, in the order posed, separated by commas, with the values known put in their places;
  begin
    Boolean first;
    first := true;
    if q1 then begin seqplace(ak, av, 1); outstring(1, " = (x, y, z)"); first := false end;
    if q2 then
    begin
      if ¬first then outstring(1, ", ");
      outstring(1, "rev("); seqplace(ak, av, 1); outstring(1, ", "); seqplace(bk, bv, 2); outstring(1, ")");
      if ¬defined then outstring(1, " awaiting its definition");
      first := false
    end;
    if q3 then
    begin if ¬first then outstring(1, ", "); printel(1); outstring(1, " = "); printel(2); first := false end;
    if q5 then
    begin if ¬first then outstring(1, ", "); printel(2); outstring(1, " = "); printel(3); first := false end;
    if q6 then
    begin
      if ¬first then outstring(1, ", ");
      seqplace(bk, bv, 2); outstring(1, " = "); printseq(sv); outstring(1, " ++ "); seqplace(ck, cv, 3)
    end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ak := bk := ck := q1 := q2 := q3 := q5 := q6 := defined := inconsistent := false;
  top := rev1 := rev2 := conc1 := conc2 := 0;
  for j := 1 step 1 until 3 do ek[j] := false;
  nel := 3; sv := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then q1 := true
    else if k = 2 then q2 := true
    else if k = 3 then q3 := true
    else if k = 4 then defined := true
    else if k = 5 then q5 := true
    else if k = 6 then
    begin
      comment the sequence s: each element, in order, is a new element with its value;
      integer len, e, first, last, c;
      ininteger(0, len);
      first := last := 0;
      for j := 1 step 1 until len do
      begin
        ininteger(0, e); nel := nel + 1; ev[nel] := e; ek[nel] := true;
        c := cons(nel, 0);
        if last = 0 then first := c else tl[last] := c;
        last := c
      end;
      sv := first; q6 := true
    end;

    propagate;

    comment the answer: every unknown, and the relations still held;
    if ¬inconsistent then
    begin
      outstring(1, "[answer]");
      seqstate(ak, av, q1 ∨ q2, 1); outstring(1, ", ");
      seqstate(bk, bv, q2 ∨ q6, 2); outstring(1, ", ");
      seqstate(ck, cv, q6, 3); outstring(1, ", ");
      elstate(1, q3); outstring(1, ", ");
      elstate(2, q3 ∨ q5); outstring(1, ", ");
      elstate(3, q5);
      if q1 ∨ q2 ∨ q3 ∨ q5 ∨ q6 then begin outstring(1, ", where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the relations held, the application awaiting its definition, the values known, and the applications of each case of rev and conc;
    held := (if q1 then 1 else 0) + (if q3 then 1 else 0) + (if q5 then 1 else 0) + (if q6 then 1 else 0);
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "held relations: ");
    if held = 0 ∧ ¬q2 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if defined then outstring(1, "rev and conc: defined\n") else outstring(1, "rev and conc: not yet defined\n");
    if q2 ∧ ¬defined then outstring(1, "rev(a, b): held as posed, awaiting the definition of rev, neither true nor false\n");
    if ak then begin outstring(1, "[bind a]"); printseq(av); outstring(1, "[/bind]\n") end;
    if bk then begin outstring(1, "[bind b]"); printseq(bv); outstring(1, "[/bind]\n") end;
    if ck then begin outstring(1, "[bind c]"); printseq(cv); outstring(1, "[/bind]\n") end;
    if ek[1] then begin outstring(1, "[bind x]"); outinteger(1, ev[1]); outstring(1, "[/bind]\n") end;
    if ek[2] then begin outstring(1, "[bind y]"); outinteger(1, ev[2]); outstring(1, "[/bind]\n") end;
    if ek[3] then begin outstring(1, "[bind z]"); outinteger(1, ev[3]); outstring(1, "[/bind]\n") end;
    if q2 then outstring(1, "[suspended pending-applications 1]\n");
    if held > 0 then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
    outstring(1, "[operations rev/1 "); outinteger(1, rev1); outstring(1, "]\n");
    outstring(1, "[operations rev/2 "); outinteger(1, rev2); outstring(1, "]\n");
    outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
    outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
