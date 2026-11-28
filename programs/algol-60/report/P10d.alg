begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures (5.4), the for statement with step-until and while elements (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each comparison as posed, to be tested on the values of x, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: F f1 ... fF, the number of facts of pick and then the value of each fact, in order. A line 2: c, the integer of x greater than c. Stage 3, which withdraws the relation of stage 2, has no constants;
  comment P10d. One unknown x. Stage 1: pick(x), a closed world of facts. Stage 2: x greater than c2. Stage 3: withdraw the relation of stage 2. pick is given by its facts, which the program holds as given: when it is posed each fact, in order, gives x a value. Each comparison is held as posed by a Boolean that says whether it is in force. After every stage the values of x are those of the facts that pass every comparison in force, tested again from the facts. A withdrawal sets its comparison out of force. The comparison stays in the text, and nothing is restated;
  integer n, cap, m, i, code, k, j, nf, c2, alive, tested;
  Boolean picked, r2, w2;
  integer array xv[1:1000], pk[1:1000];
  Boolean array xa[1:1000];

  procedure test;
  comment every value of x that pick gives is tested by every comparison in force, in the order the comparisons were posed. A comparison is held until pick has given x its values;
  if picked then
  begin
    for j := 1 step 1 until nf do
    begin
      xa[j] := true;
      if r2 then begin tested := tested + 1; if ¬(xv[j] > c2) then xa[j] := false end
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

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  picked := r2 := w2 := false; nf := 0; tested := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin
      comment pick(x): each fact, in order, gives x one value;
      ininteger(0, nf);
      for j := 1 step 1 until nf do
      begin ininteger(0, xv[j]); pk[j] := 1 end;
      picked := true
    end
    else if k = 2 then begin ininteger(0, c2); r2 := true end
    else if k = 3 then begin comment withdraw the relation of stage 2;
      r2 := false; w2 := true end;

    test;

    comment the answers: every value of x, or, before pick, x and the comparisons held;
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
      if r2 then begin outstring(1, " held, where x gt "); outinteger(1, c2) end else outstring(1, " free");
      outstring(1, "[/answer]\n")
    end;

    comment observe: the values of x held, all at once, the comparisons in force and withdrawn, and the facts of pick applied;
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
    outstring(1, "comparisons in force: ");
    if r2 then begin outstring(1, "x gt "); outinteger(1, c2) end else outstring(1, "none");
    outstring(1, "\n");
    if w2 then begin outstring(1, "withdrawn: x gt "); outinteger(1, c2); outstring(1, "\n") end;
    if r2 ∧ ¬picked then outstring(1, "[suspended held-relations 1]\n");
    for j := 1 step 1 until nf do
    begin outstring(1, "[operations pick/"); digits(j); outstring(1, " "); outinteger(1, pk[j]); outstring(1, "]\n") end;
    outstring(1, "[operations x-gt-tested "); outinteger(1, tested); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
