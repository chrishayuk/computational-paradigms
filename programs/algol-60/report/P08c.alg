begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), recursive procedures and function designators with parameters called by value and by name (4.7, 5.4), the for statement with step-until and while elements (4.6), conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of the application of a relation not yet wholly defined until it can be decided, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 2: L e1 ... eL, the length and then the elements of the known sequence s of rev(s, b). A line 3: L1 L2 p1 ... pL1 r1 ... rL2, the two lengths, and then the elements of the two sequences p and r of case 1 of rev, rev(p, r). Elements are integers. Stages 1 and 4 have none;
  comment P08c. One unknown sequence b. Stage 1: the definition of conc, as in P03. Stage 2: rev(s, b), with rev not yet defined. Stage 3: case 1 of rev, rev(p, r). Stage 4: case 2 of rev, rev(h followed by l, r) if rev(l, q) and conc(q, the sequence of h alone, r). ALGOL 60 has no definitions that arrive while a program runs: the procedures are in the text, and a Boolean for conc and for each case of rev says whether it has arrived. rev and conc compute their last place from the others, their cases in order, and say whether they found it (1), found that there is none (0), or could not tell, because a case they would need has not arrived (2). An application of rev that cannot be told is held as posed, and is neither true nor false: the fourth of the problem's four states, the open reading. It is examined again at every stage, with the cases that have arrived, and is decided when the whole of rev and conc has arrived. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. b is a Boolean that says whether it has a value and an integer that holds it;
  integer n, cap, m, i, code, k, j, top, sv, pv, rv, bv, held, pass, rev1, rev2, conc1, conc2;
  Boolean bk, q2, concdef, rev1def, rev2def, changed, inconsistent;
  integer array hd, tl[1:10000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer w, e, first, last, c;
    first := last := 0;
    for w := 1 step 1 until len do
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

  integer procedure conc(a, b, c);
    value a, b; integer a, b, c;
  comment conc(a, b, c), computing c from a and b by its cases, in order, once its definition has arrived. Case 1: conc(the empty sequence, b, b). Case 2: conc(h followed by a, b, h followed by c) if conc(a, b, c);
  if ¬concdef then conc := 2
  else if a = 0 then
  begin conc1 := conc1 + 1; c := b; conc := 1 end
  else
  begin
    integer t, d;
    conc2 := conc2 + 1;
    t := conc(tl[a], b, d);
    if t = 1 then c := cons(hd[a], d);
    conc := t
  end conc;

  integer procedure rev(a, r);
    value a; integer a, r;
  comment rev(a, r), computing r from a by the cases that have arrived, in order. Case 1: rev(p, r0), p and r0 being the two sequences of stage 3. Case 2: rev(h followed by l, r) if rev(l, q) and conc(q, the sequence of h alone, r), the conjuncts in that order. When no case that has arrived gives r, there is none if every case has arrived, and it cannot be told if one has not;
  begin
    integer st, t, q;
    st := 3;
    if rev1def then
    begin if same(a, pv) then begin rev1 := rev1 + 1; r := rv; st := 1 end end;
    if st ≠ 1 ∧ rev2def then
    begin
      if a ≠ 0 then
      begin
        rev2 := rev2 + 1;
        t := rev(tl[a], q);
        if t = 1 then t := conc(q, cons(hd[a], 0), r);
        if t ≠ 0 then st := t
      end
    end;
    if st = 3 then st := if rev1def ∧ rev2def then 0 else 2;
    rev := st
  end rev;

  procedure examine2;
  comment the evaluator of the application rev(s, b): b is computed from s by the cases of rev that have arrived, or tested if known. The application is held until the whole of rev and conc has arrived;
  begin
    integer t, r;
    t := rev(sv, r);
    if t = 1 then
    begin
      if bk then begin if ¬same(bv, r) then inconsistent := true end
      else begin bv := r; bk := true; changed := true end
    end
    else if t = 0 then inconsistent := true;
    if concdef ∧ rev1def ∧ rev2def then q2 := false
  end examine2;

  procedure propagate;
  comment every held relation is examined, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if q2 then examine2
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

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas;
  begin
    integer w;
    outstring(1, "(");
    for w := 0 while p ≠ 0 do
    begin printint(hd[p]); p := tl[p]; if p ≠ 0 then outstring(1, ", ") end;
    outstring(1, ")")
  end printseq;

  procedure relations;
  comment output adapter: the application held, with b put in its place if known;
  if q2 then
  begin
    outstring(1, "rev("); printseq(sv); outstring(1, ", ");
    if bk then printseq(bv) else outstring(1, "b");
    outstring(1, ")");
    if ¬(rev1def ∨ rev2def) then outstring(1, " awaiting the definition of rev")
    else outstring(1, " awaiting the rest of the definition of rev");
    if ¬concdef then outstring(1, " and conc")
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  bk := q2 := concdef := rev1def := rev2def := inconsistent := false;
  top := rev1 := rev2 := conc1 := conc2 := 0;
  sv := pv := rv := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then concdef := true
    else if k = 2 then
    begin
      ininteger(0, j); sv := readseq(j); q2 := true
    end
    else if k = 3 then
    begin
      integer l1, l2;
      ininteger(0, l1); ininteger(0, l2);
      pv := readseq(l1); rv := readseq(l2); rev1def := true
    end
    else if k = 4 then rev2def := true;

    propagate;

    comment the answer: b, and the application still held;
    if ¬inconsistent then
    begin
      outstring(1, "[answer]b");
      if bk then begin outstring(1, " = "); printseq(bv) end
      else if q2 then outstring(1, " held") else outstring(1, " free");
      if q2 then begin outstring(1, ", where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the application held, which parts of the definitions have arrived, the value known, and the applications of each case of rev and conc;
    held := if q2 then 1 else 0;
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "held relations: ");
    if held = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if concdef then outstring(1, "conc: defined") else outstring(1, "conc: not yet defined");
    if rev1def then outstring(1, ", rev case 1: defined") else outstring(1, ", rev case 1: not yet defined");
    if rev2def then outstring(1, ", rev case 2: defined\n") else outstring(1, ", rev case 2: not yet defined\n");
    if q2 then outstring(1, "rev(s, b): held as posed, neither true nor false, examined again at each stage\n");
    if bk then begin outstring(1, "[bind b]"); printseq(bv); outstring(1, "[/bind]\n") end;
    if q2 then outstring(1, "[suspended pending-applications 1]\n");
    outstring(1, "[operations rev/1 "); outinteger(1, rev1); outstring(1, "]\n");
    outstring(1, "[operations rev/2 "); outinteger(1, rev2); outstring(1, "]\n");
    outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
    outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
