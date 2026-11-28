begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), Boolean arrays (5.2), procedures with value parameters (4.7, 5.4), the for statement with step-until and while elements (4.6), conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), a program that reads each stage as it arrives, which counts as the same computation (systems file, The same computation), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, with a list for each unknown of the relations it occurs in and a queue of the unknowns newly given values, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 3: k, of x1 = k. Stages 1 and 2 have no constants: their relations are given by the instance's size n, from the instance line;
  comment P16b. Integer unknowns x1 to xn+1, and total, each a Boolean that says whether it has a value and an integer that holds it. There are four contributors and m = n/4, called q in the program, since m names the count of codes on the instance line. ALGOL 60 has no separate computations that share unknowns, so the four contributions are posed as one conjunction, in the order of the contributors, at stage 1 (harnesses/algol-60/QUESTIONS.md, A3). Stage 1: contributor c gives succ(x_i, x_i+1) for i = (c - 1)m + 1 to cm, ascending, for c = 1 to 4. Stage 2: total = x1 + x_m+1 + x_2m+1 + x_3m+1 + x_4m+1. Stage 3: x1 = k. Each relation is held as posed, and is examined when it arrives and again when one of its places is given a value, never otherwise. succ(a, b) is the relation b = a + 1. Its evaluator gives b the value a + 1 when a is known, or a the value b - 1 when b is known, or tests b = a + 1 when both are, and is then decided, and when neither is known it waits. The relation of total, a sum of five places, gives its sixth place its value when five of its six are known, or tests it when all six are, and otherwise waits. x1 = k gives x1 the value k, or tests it. For each unknown the program keeps the list of the relations it occurs in, in the order they arrived, and a queue of the unknowns given values and not yet followed. After each relation is posed, the queue is emptied: for each unknown in it, every relation still held on its list is examined, in the order of the list. Nothing eliminates unknowns between two waiting relations. The store is sized from n;
  integer n, cap, m, i, code, k, nu, nrmax, q;
  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  q := n ÷ 4;
  nu := 4 × q + 2;
  nrmax := nu + 2;
  begin
  integer nr, nheld, nknown, no, qh, qt, kval, j, c, w, w2, tot, sx, sw, sd, tx, fx, mostx, u, o, r;
  Boolean inconsistent;
  integer array rk, ra, rb, rc, ex[1:nrmax], val, ohd, otl, qu[1:nu], orel, onext[1:2 × nrmax], sp[1:5];
  Boolean array held[1:nrmax], kn[1:nu];

  procedure occur(u, r);
    value u, r; integer u, r;
  comment the relation r is put at the end of the list of unknown u;
  begin
    no := no + 1; orel[no] := r; onext[no] := 0;
    if ohd[u] = 0 then ohd[u] := no else onext[otl[u]] := no;
    otl[u] := no
  end occur;

  procedure give(u, v);
    value u, v; integer u, v;
  comment unknown u is given the value v, and joins the queue;
  begin
    val[u] := v; kn[u] := true; nknown := nknown + 1;
    qt := qt + 1; qu[qt] := u
  end give;

  procedure decide(r);
    value r; integer r;
  comment the relation r is decided, and is held no longer;
  begin held[r] := false; nheld := nheld - 1 end decide;

  procedure examine(r);
    value r; integer r;
  comment the evaluator of relation r: kind 1 is succ(a, b), kind 2 is a = c, kind 3 is a = the sum of the five places sp[1] to sp[5];
  begin
    integer a, b, t, s, miss, unk;
    a := ra[r]; b := rb[r];
    ex[r] := ex[r] + 1;
    if rk[r] = 1 then
    begin
      sx := sx + 1;
      if ex[r] > mostx then mostx := ex[r];
      if kn[a] ∧ kn[b] then
      begin sd := sd + 1; if val[b] ≠ val[a] + 1 then inconsistent := true; decide(r) end
      else if kn[a] then
      begin sd := sd + 1; give(b, val[a] + 1); decide(r) end
      else if kn[b] then
      begin sd := sd + 1; give(a, val[b] - 1); decide(r) end
      else sw := sw + 1
    end
    else if rk[r] = 2 then
    begin
      fx := fx + 1;
      if kn[a] then
      begin if val[a] ≠ rc[r] then inconsistent := true end
      else give(a, rc[r]);
      decide(r)
    end
    else
    begin
      tx := tx + 1;
      s := 0; unk := 0; miss := 0;
      for t := 1 step 1 until 5 do
      begin
        if kn[sp[t]] then s := s + val[sp[t]] else begin unk := unk + 1; miss := t end
      end;
      if unk = 0 then
      begin
        if kn[a] then begin if val[a] ≠ s then inconsistent := true end
        else give(a, s);
        decide(r)
      end
      else if unk = 1 then
      begin
        if kn[a] then begin give(sp[miss], val[a] - s); decide(r) end
      end
    end
  end examine;

  procedure propagate;
  comment the queue is emptied: for each unknown in it, in turn, every relation still held on its list is examined;
  for w := 0 while qh ≤ qt do
  begin
    u := qu[qh]; qh := qh + 1;
    o := ohd[u];
    for w2 := 0 while o ≠ 0 do
    begin
      r := orel[o];
      if held[r] then examine(r);
      o := onext[o]
    end
  end propagate;

  procedure pose(kind, a, b, c);
    value kind, a, b, c; integer kind, a, b, c;
  comment a relation arrives: it is held, put on the lists of its unknowns, examined, and what it gives is followed;
  begin
    integer t;
    nr := nr + 1;
    rk[nr] := kind; ra[nr] := a; rb[nr] := b; rc[nr] := c; ex[nr] := 0;
    held[nr] := true; nheld := nheld + 1;
    occur(a, nr);
    if kind = 1 then occur(b, nr);
    if kind = 3 then
    begin for t := 1 step 1 until 5 do occur(sp[t], nr) end;
    examine(nr);
    propagate
  end pose;

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

  procedure uname(u);
    value u; integer u;
  comment output adapter: the name of unknown u;
  if u = tot then outstring(1, "total") else begin outstring(1, "x"); num(u) end uname;

  procedure place(u);
    value u; integer u;
  comment output adapter: a place of a relation, its value if known, else the name of its unknown;
  if kn[u] then num(val[u]) else uname(u);

  procedure values;
  comment output adapter: every unknown with a value, in order, separated by commas, five to a line;
  begin
    integer v, c;
    c := 0;
    for v := 1 step 1 until nu do
    begin
      if kn[v] then
      begin
        if c > 0 then outstring(1, ", ");
        if c > 0 then begin if c - c ÷ 5 × 5 = 0 then outstring(1, "\n") end;
        uname(v); outstring(1, " = "); num(val[v]); c := c + 1
      end
    end
  end values;

  procedure relations;
  comment output adapter: every relation still held, in the order it arrived, separated by commas, five to a line;
  begin
    integer h, c, t;
    c := 0;
    for h := 1 step 1 until nr do
    begin
      if held[h] then
      begin
        if c > 0 then outstring(1, ", ");
        if c > 0 then begin if c - c ÷ 5 × 5 = 0 then outstring(1, "\n") end;
        if rk[h] = 1 then
        begin outstring(1, "succ("); uname(ra[h]); outstring(1, ", "); uname(rb[h]); outstring(1, ")") end
        else if rk[h] = 2 then
        begin uname(ra[h]); outstring(1, " = "); num(rc[h]) end
        else
        begin
          place(ra[h]); outstring(1, " = ");
          for t := 1 step 1 until 5 do
          begin place(sp[t]); if t < 5 then outstring(1, " + ") end
        end;
        c := c + 1
      end
    end
  end relations;

  procedure binds;
  comment output adapter: a bind tag for every unknown with a value;
  begin
    integer v;
    for v := 1 step 1 until nu do
    begin
      if kn[v] then
      begin outstring(1, "[bind "); uname(v); outstring(1, "]"); num(val[v]); outstring(1, "[/bind]\n") end
    end
  end binds;

  nr := nheld := nknown := no := sx := sw := sd := tx := fx := mostx := 0;
  qh := 1; qt := 0;
  tot := nu;
  inconsistent := false;
  for u := 1 step 1 until nu do
  begin kn[u] := false; ohd[u] := 0; otl[u] := 0 end;

  for i := 1 while true do
  begin
    comment harness words: one message, and the stage it poses;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin
      comment stage 1: the four contributions, one conjunction, contributor c giving succ(x_i, x_i+1) for i = (c - 1)m + 1 to cm, ascending;
      for c := 1 step 1 until 4 do
      begin for j := (c - 1) × q + 1 step 1 until c × q do pose(1, j, j + 1, 0) end
    end
    else if k = 2 then
    begin
      comment stage 2: total = x1 + x_m+1 + x_2m+1 + x_3m+1 + x_4m+1;
      for j := 1 step 1 until 5 do sp[j] := (j - 1) × q + 1;
      pose(3, tot, 0, 0)
    end
    else if k = 3 then
    begin
      comment stage 3: x1 = k, with k from the constants;
      ininteger(0, kval);
      pose(2, 1, 0, kval)
    end;

    comment the answer: the unknowns with values, and the relations still held;
    if ¬inconsistent then
    begin
      outstring(1, "[answer]");
      if nknown = 0 then outstring(1, "no unknown is known") else values;
      if nheld > 0 then begin outstring(1, ",\n"); outstring(1, "where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the relations held, the values known, and how often the relations were examined;
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "the four contributions were posed as one conjunction, in one computation\n");
    outstring(1, "held relations: ");
    if nheld = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    binds;
    if nheld > 0 then
    begin outstring(1, "[suspended held-relations "); num(nheld); outstring(1, "]\n") end;
    outstring(1, "unknowns known: "); num(nknown); outstring(1, " of "); num(nu); outstring(1, "\n");
    outstring(1, "[operations succ-examined "); num(sx); outstring(1, "]\n");
    outstring(1, "[operations succ-decided "); num(sd); outstring(1, "]\n");
    outstring(1, "[operations succ-waited "); num(sw); outstring(1, "]\n");
    outstring(1, "[operations total-examined "); num(tx); outstring(1, "]\n");
    outstring(1, "[operations equation-examined "); num(fx); outstring(1, "]\n");
    outstring(1, "most examinations of one succ relation: "); num(mostx); outstring(1, "\n");
    outstring(1, "[/observe]\n[end]")
  end
  end
end
