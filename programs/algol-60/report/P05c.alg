begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures (5.4), the for statement with step-until and while elements (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each equation until x has values to test, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: F f1 ... fF, the number of facts of pick and then the value of each fact, in order. A line 2: c, the integer of x = c. A line 3: c, the integer of x = c;
  comment P05c. One unknown x. Stage 1: pick(x), a closed world of facts. Stage 2: x = c2. Stage 3: x = c3. pick is given by its facts: when it is posed, each fact, in order, gives x a value, and the values are held all at once, each with a Boolean that says whether it is still a solution. Each equation is held as posed until x has values, and then tested on each of them. A value that fails a test is dropped, and is not kept;
  integer n, cap, m, i, code, k, j, nf, c2, c3, held, alive;
  Boolean picked, r2, r3;
  integer array xv[1:1000], pk[1:1000];
  Boolean array xa[1:1000];

  procedure test;
  comment every equation posed so far is tested on every value of x still held, in the order the equations were posed. An equation is held until pick has given x its values;
  if picked then
  begin
    for j := 1 step 1 until nf do
    begin
      if xa[j] then
      begin
        if r2 then begin if ¬(xv[j] = c2) then xa[j] := false end;
        if r3 then begin if ¬(xv[j] = c3) then xa[j] := false end
      end
    end
  end test;

  procedure digits(v);
    value v; integer v;
  comment output adapter: a natural number, its decimal digits with no sign and no spaces, for the name of a case;
  begin
    integer d;
    if v ≥ 10 then digits(v ÷ 10);
    d := v - v ÷ 10 × 10;
    if d = 0 then outstring(1, "0") else if d = 1 then outstring(1, "1") else if d = 2 then outstring(1, "2")
    else if d = 3 then outstring(1, "3") else if d = 4 then outstring(1, "4") else if d = 5 then outstring(1, "5")
    else if d = 6 then outstring(1, "6") else if d = 7 then outstring(1, "7") else if d = 8 then outstring(1, "8")
    else outstring(1, "9")
  end digits;

  procedure relations;
  comment output adapter: the equations held, which wait for x to have values;
  begin
    Boolean first;
    first := true;
    if r2 then begin outstring(1, "x = "); outinteger(1, c2); first := false end;
    if r3 then
    begin
      if ¬first then outstring(1, ", ");
      outstring(1, "x = "); outinteger(1, c3)
    end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  picked := r2 := r3 := false; nf := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin
      comment pick(x): each fact, in order, gives x one value;
      ininteger(0, nf);
      for j := 1 step 1 until nf do
      begin ininteger(0, xv[j]); xa[j] := true; pk[j] := 1 end;
      picked := true
    end
    else if k = 2 then begin ininteger(0, c2); r2 := true end
    else if k = 3 then begin ininteger(0, c3); r3 := true end;

    test;

    comment the answers: every value of x still held, or, before pick, x and the equations held;
    alive := 0;
    if picked then
    begin
      for j := 1 step 1 until nf do
      begin
        if xa[j] then
        begin
          alive := alive + 1;
          outstring(1, "[answer]x = "); outinteger(1, xv[j]); outstring(1, "[/answer]\n")
        end
      end
    end
    else
    begin
      outstring(1, "[answer]x");
      if r2 ∨ r3 then begin outstring(1, " held, where "); relations end else outstring(1, " free");
      outstring(1, "[/answer]\n")
    end;

    comment observe: the values of x held, all at once, the equations held, and the facts of pick applied;
    held := if picked then 0 else (if r2 then 1 else 0) + (if r3 then 1 else 0);
    outstring(1, "[observe]");
    if picked ∧ alive = 0 then outstring(1, "no solution\n");
    if picked then
    begin
      outstring(1, "values of x held, all at once:");
      for j := 1 step 1 until nf do
      begin if xa[j] then begin outstring(1, " "); outinteger(1, xv[j]) end end;
      outstring(1, "\n");
      outstring(1, "[problem-alternatives x "); outinteger(1, alive); outstring(1, "]\n")
    end;
    outstring(1, "held relations: ");
    if held = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if held > 0 then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
    for j := 1 step 1 until nf do
    begin outstring(1, "[operations pick/"); digits(j); outstring(1, " "); outinteger(1, pk[j]); outstring(1, "]\n") end;
    outstring(1, "[/observe]\n[end]")
  end
end
