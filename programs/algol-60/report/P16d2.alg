begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), Boolean arrays (5.2), procedures with value parameters (4.7, 5.4), the for statement with step-until and while elements (4.6), conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), a program that reads each stage as it arrives, which counts as the same computation (systems file, The same computation), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, with a list for each unknown of the relations it occurs in and a queue of the unknowns newly given values, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS none. The relations of both stages are given by the instance's size n, from the instance line;
  comment P16d2. Integer unknowns x1 to xn and y1 to yn, two chains that share no unknown, posed as one computation, each unknown a Boolean that says whether it has a value and an integer that holds it, x_i being unknown i and y_i unknown n + i. Stage 1: every succ(x_i, x_i+1), and then every succ(y_i, y_i+1), for i = 1 to n - 1, ascending. Stage 2: x_n = x1. This is P16d with its stage 2 omitted and its stage 3 replaced, numbered 2 here as harnesses/stages.json numbers it. Each relation is held as posed, and is examined when it arrives and again when one of its places is given a value, never otherwise. succ(a, b) is the relation b = a + 1. Its evaluator gives b the value a + 1 when a is known, or a the value b - 1 when b is known, or tests b = a + 1 when both are, and is then decided, and when neither is known it waits. x_n = x1 gives either place the value of the other when one is known, or tests it when both are, and otherwise waits. A test that fails would be the contradiction, and would be reported as no solution, with nothing held withdrawn or changed. With no value known, nothing combines the two relations x_n = x1 and the chain between them, so the contradiction of x_n = x1 + n - 1 with x_n = x1 is not found: that would need elimination, which is not written. For each unknown the program keeps the list of the relations it occurs in, in the order they arrived, and a queue of the unknowns given values and not yet followed. After each relation is posed, the queue is emptied: for each unknown in it, every relation still held on its list is examined, in the order of the list. So the relations examined after a value arrives are those reached from it through the lists, and a chain that the value does not reach is not examined. Nothing eliminates unknowns between two waiting relations. The store is sized from n;
  integer n, cap, m, i, code, k, nx, nu, nrmax;
  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  nx := if n < 1 then 1 else n;
  nu := 2 × nx;
  nrmax := nu + 2;
  begin
  integer nr, nheld, nknown, no, qh, qt, kval, j, w, w2, sx, sxx, sxy, sw, sd, fx, mostx, u, o, r;
  Boolean inconsistent;
  integer array rk, ra, rb, rc, ex[1:nrmax], val, ohd, otl, qu[1:nu], orel, onext[1:2 × nrmax];
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
  comment the evaluator of relation r: kind 1 is succ(a, b), kind 3 is a = b;
  begin
    integer a, b;
    a := ra[r]; b := rb[r];
    ex[r] := ex[r] + 1;
    if rk[r] = 1 then
    begin
      sx := sx + 1;
      if a ≤ nx then sxx := sxx + 1 else sxy := sxy + 1;
      if ex[r] > mostx then mostx := ex[r];
      if kn[a] ∧ kn[b] then
      begin sd := sd + 1; if val[b] ≠ val[a] + 1 then inconsistent := true; decide(r) end
      else if kn[a] then
      begin sd := sd + 1; give(b, val[a] + 1); decide(r) end
      else if kn[b] then
      begin sd := sd + 1; give(a, val[b] - 1); decide(r) end
      else sw := sw + 1
    end
    else
    begin
      fx := fx + 1;
      if kn[a] ∧ kn[b] then
      begin if val[a] ≠ val[b] then inconsistent := true; decide(r) end
      else if kn[a] then
      begin give(b, val[a]); decide(r) end
      else if kn[b] then
      begin give(a, val[b]); decide(r) end
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
    nr := nr + 1;
    rk[nr] := kind; ra[nr] := a; rb[nr] := b; rc[nr] := c; ex[nr] := 0;
    held[nr] := true; nheld := nheld + 1;
    occur(a, nr);
    occur(b, nr);
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
  if u ≤ nx then begin outstring(1, "x"); num(u) end else begin outstring(1, "y"); num(u - nx) end uname;

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
    integer h, c;
    c := 0;
    for h := 1 step 1 until nr do
    begin
      if held[h] then
      begin
        if c > 0 then outstring(1, ", ");
        if c > 0 then begin if c - c ÷ 5 × 5 = 0 then outstring(1, "\n") end;
        if rk[h] = 1 then
        begin outstring(1, "succ("); uname(ra[h]); outstring(1, ", "); uname(rb[h]); outstring(1, ")") end
        else
        begin uname(ra[h]); outstring(1, " = "); uname(rb[h]) end;
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

  nr := nheld := nknown := no := sx := sxx := sxy := sw := sd := fx := mostx := 0;
  qh := 1; qt := 0;
  inconsistent := false;
  for u := 1 step 1 until nu do
  begin kn[u] := false; ohd[u] := 0; otl[u] := 0 end;

  for i := 1 while true do
  begin
    comment harness words: one message, and the stage it poses;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin
      comment stage 1: every succ(x_i, x_i+1), and then every succ(y_i, y_i+1), ascending;
      for j := 1 step 1 until n - 1 do pose(1, j, j + 1, 0);
      for j := 1 step 1 until n - 1 do pose(1, nx + j, nx + j + 1, 0)
    end
    else if k = 2 then
    begin
      comment stage 2: x_n = x1;
      pose(3, nx, 1, 0)
    end;

    comment the answer: the unknowns with values, and the relations still held;
    if ¬inconsistent then
    begin
      outstring(1, "[answer]");
      if nknown = 0 then outstring(1, "no unknown is known") else values;
      if nheld > 0 then begin outstring(1, ",\n"); outstring(1, "where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the relations held, the values known, and how often the relations of each chain were examined;
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution: a relation was found not to hold, and nothing held was withdrawn or changed\n");
    outstring(1, "held relations: ");
    if nheld = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    binds;
    if nheld > 0 then
    begin outstring(1, "[suspended held-relations "); num(nheld); outstring(1, "]\n") end;
    outstring(1, "unknowns known: "); num(nknown); outstring(1, " of "); num(nu); outstring(1, "\n");
    outstring(1, "[operations succ-examined "); num(sx); outstring(1, "]\n");
    outstring(1, "[operations succ-x-examined "); num(sxx); outstring(1, "]\n");
    outstring(1, "[operations succ-y-examined "); num(sxy); outstring(1, "]\n");
    outstring(1, "[operations succ-decided "); num(sd); outstring(1, "]\n");
    outstring(1, "[operations succ-waited "); num(sw); outstring(1, "]\n");
    outstring(1, "[operations equality-examined "); num(fx); outstring(1, "]\n");
    outstring(1, "most examinations of one succ relation: "); num(mostx); outstring(1, "\n");
    outstring(1, "[/observe]\n[end]")
  end
  end
end
